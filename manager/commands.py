
from datetime import datetime
import logging
from time import perf_counter

from manager.backup import backup_drupal_site, backup_wordpress_site
from manager.notifications.mail import Mailer, render_template
from manager.status.monitoring import check_https_status, print_https_status_list
from manager.status.models import SiteStatus, StatusLogEntry, StatusLogType
from manager.sites import Site, SiteSSHConfig


class CommandBase:

    def __init__(self, config, db_session):
        self.config = config
        self.db_session = db_session
        self.mailer = Mailer(config["mail"])

    def __call__(self):
        self.execute()


class Commands:

    class help(CommandBase):
        """Displays help text."""

        def execute(self):
            print()
            print("Available commands:")
            print()
            commands = []
            for attr_name in dir(Commands):
                attr = getattr(Commands, attr_name)
                if type(attr).__name__ == "type" and attr.__base__.__name__ == "CommandBase":
                    commands.append(attr)
            for command in commands:
                print(f"{command.__name__:<24}{command.__doc__}")
            print()

    class update_https_status(CommandBase):
        """Checks status of each website and notifies sysadmin when a website is down or inaccessible."""

        def execute(self):
            sites = self.db_session.query(Site).filter(
                Site.is_active
            ).all()
            results = [check_https_status({
                "site_id": site.id,
                "site_url": "https://" + site.host,
                "site_latest_status": site.latest_status,
            }) for site in sites]
            for result in results:
                site = self.db_session.query(Site).get(result["site_id"])
                result["site"] = site
                if result["status_changed"]:
                    status_log_entry = StatusLogEntry(
                        site=site,
                        type=StatusLogType.HTTPS,
                        status=result["status"],
                        created=datetime.now(),
                    )
                    self.db_session.add(status_log_entry)
                    if result["notify"]:
                        self.notify_status_change(result)
            self.db_session.commit()

        def notify_status_change(self, result):
            status_colors = {"up": "green", "down": "red", "unknown": "orange"}
            data = {
                "site": result["site"],
                "status_value": result["status"].value,
                "status_color": status_colors[result["status"].value],
                "status_details": [
                    ("URL",
                     '<a href="{}">{}</a>'.format(result["site_url"])),
                    ("Request time", result["request_time"]),
                ]
            }
            if "error" in result.keys():
                data["status_details"].append(("Error", result["error"]))
            message_subject = "{status}: {host}".format(
                status=result["status"].value.upper(),
                host=result["site"].host,
            )
            message_body = render_template("status.status_changed", data)
            self.mailer.notify(message_subject, message_body)

    class show_https_status(CommandBase):
        """Displays most recent status of each website."""

        def execute(self):
            sites = self.db_session.query(Site).filter(
                Site.is_active
            ).all()
            print_https_status_list(sites)

    class send_status_report(CommandBase):
        """Sends email report listing website status details."""

        def execute(self):
            sites = self.db_session.query(Site).filter(
                Site.is_active
            ).all()
            status_colors = {
                SiteStatus.UP: ("white", "green"),
                SiteStatus.DOWN: ("white", "red"),
                SiteStatus.UNKNOWN: ("black", "yellow"),
            }

            def table_rows():
                for site in sites:
                    entry = site.latest_status_log_entry
                    yield {
                        "site_host": site.host,
                        "status_value": entry.status.value,
                        "status_color": status_colors[entry.status],
                        "status_duration": datetime.now() - entry.created,
                    }

            message_body = render_template("status.status_report", {
                "table_rows": list(table_rows()),
            })
            self.mailer.notify("Status report", message_body)

    class backup_apps(CommandBase):
        """Backs up apps to Amazon S3"""

        BACKUP_FUNCTIONS = {
            "wordpress": backup_wordpress_site,
            "drupal": backup_drupal_site,
        }

        def execute(self):
            sites = self.db_session.query(Site).join(SiteSSHConfig).filter(
                Site.is_active,
                Site.app is not None
            ).all()
            for site in sites:
                logging.debug(f"started backup: {site.app}, {site.host}")
                start_at = perf_counter()
                self.BACKUP_FUNCTIONS[site.app](
                    site.id,
                    site.host,
                    site.ssh_config.to_dict(),
                    "sitebackup-" + site.host,
                    self.config["aws"])
                duration = (perf_counter() - start_at) * 1000
                logging.info(f"{site.app} {site.host}, ({int(duration)}ms)")


class CommandError(BaseException):
    pass
