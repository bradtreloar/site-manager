
from datetime import datetime

from manager.backup import backup_drupal_site, backup_wordpress_site

from manager.database import session
from manager.logging import Logger
from manager.notifications.mail import Mailer, Renderer
from manager.status.monitoring import check_https_status, print_https_status_list
from manager.status.models import SiteStatus, StatusLogEntry, StatusLogType
from manager.sites import Site, SiteSSHConfig, import_sites


class CommandBase:

    def __init__(self, config):
        self.config = config
        self.db_session = session(config["database"])
        import_sites(config, self.db_session)
        self.mailer = Mailer(config["mail"])
        self.renderer = Renderer()
        self.logger = Logger(config["logging"])

    def do_execute(self):
        start_at = datetime.now()
        self.execute()
        end_at = datetime.now()
        duration = int((end_at - start_at).microseconds / 1000)
        self.logger.log("{} ({}ms)".format(self.__class__.__name__, duration))


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
                print("{:<24}{}".format(command.__name__, command.__doc__))
            print()

    class update_https_status(CommandBase):
        """Checks status of each website and notifies sysadmin when a website is down or inaccessible."""

        def execute(self):
            sites = self.db_session.query(Site).filter(
                Site.is_active
            ).all()

            def run_task(site):
                return check_https_status({
                    "site_id": site.id,
                    "site_url": "https://" + site.host,
                    "site_latest_status": site.latest_status,
                })

            results = [run_task(site) for site in sites]
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
                     '<a href="{0}">{0}</a>'.format(result["site_url"])),
                    ("Request time", result["request_time"]),
                ]
            }
            if "error" in result.keys():
                data["status_details"].append(("Error", result["error"]))
            message_subject = "{status}: {host}".format(
                status=result["status"].value.upper(),
                host=result["site"].host,
            )
            message_body = self.renderer.render("status.status_changed", data)
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

            message_body = self.renderer.render("status.status_report", {
                "table_rows": list(table_rows()),
            })
            self.mailer.notify("Status report", message_body)

    class backup_wordpress(CommandBase):
        """Backs up Wordpress websites to Amazon S3"""

        def execute(self):
            sites = self.db_session.query(Site).join(SiteSSHConfig).filter(
                Site.is_active,
                Site.app == "wordpress"
            ).all()

            def task_args(site):
                return ({
                    "site_id": site.id,
                    "site_host": site.host,
                    "backup_bucket": "sitebackup-" + site.host,
                    "ssh_config": site.ssh_config.to_dict(),
                }, self.config["aws"])

            for site in sites:
                backup_wordpress_site(task_args(site))

    class backup_drupal(CommandBase):
        """Backs up Drupal websites to Amazon S3"""

        def execute(self):
            sites = self.db_session.query(Site).join(SiteSSHConfig).filter(
                Site.is_active,
                Site.app == "drupal"
            ).all()

            def task_args(site):
                return ({
                    "site_id": site.id,
                    "site_host": site.host,
                    "backup_bucket": "sitebackup-" + site.host,
                    "ssh_config": site.ssh_config.to_dict(),
                }, self.config["aws"])

            for site in sites:
                backup_drupal_site(task_args(site))


class CommandError(BaseException):
    pass
