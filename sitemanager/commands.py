
import asyncio
from datetime import datetime, timezone
import logging
from time import perf_counter

from sitemanager.backup import backup_app
from sitemanager.database import get_db_session
from sitemanager.enums import SiteStatus, StatusLogType
from sitemanager.mail import Mailer
from sitemanager.models import Site, SiteSSH, StatusLogEntry
from sitemanager.sites import import_sites
from sitemanager.templates.render import render_template
from sitemanager.monitoring import (
    check_https_status, print_https_status_list)


class CommandBase:

    def __init__(self, config):
        self.config = config
        self.db_session = get_db_session(config["database"])
        self.mailer = Mailer(config["mail"])

    def __call__(self):
        command_name = self.__class__.__name__
        print(f"=> {command_name}")
        logging.info(f"Command started: {command_name}")
        start_time = perf_counter()
        import_sites(
            self.config["sites"],
            self.db_session)
        self.execute()
        duration = int((perf_counter() - start_time) * 1000)
        logging.info(
            f"Command complete: {command_name} ({duration}ms)")

    def get_active_sites(self):
        return self.db_session.query(Site).filter(
            Site.is_active
        ).all()

    def get_active_app_sites_with_ssh_config(self):
        return self.db_session.query(Site).join(SiteSSH).filter(
            Site.is_active,
            Site.app is not None
        ).all()

    @classmethod
    def name(cls):
        return cls.__name__

    @classmethod
    def description(cls):
        return " ".join(cls.__doc__.strip("\n").strip().split())


class Commands:

    class help(CommandBase):
        """
        Displays help text.
        """

        def execute(self):
            print()
            print("Available commands:")
            print()
            for command in commands():
                print(f"{command.name():<24}{command.description()}")
            print()

    class update_https_status(CommandBase):
        """
        Checks status of each website and notifies sysadmin when a website is 
        down or inaccessible.
        """

        def execute(self):
            sites = self.get_active_sites()

            async def get_results():
                results = []
                for site in sites:
                    result = await check_https_status(site)
                    results.append(result)
                return results

            event_loop = asyncio.new_event_loop()
            results = event_loop.run_until_complete(get_results())
            for result in results:
                if result["status_changed"]:
                    status_log_entry = StatusLogEntry(
                        site=result["site"],
                        type=StatusLogType.HTTPS,
                        status=result["status"],
                        created=datetime.now(timezone.utc),
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
            if "error" in result:
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
            sites = self.get_active_sites()
            print_https_status_list(sites)

    class send_status_report(CommandBase):
        """Sends email report listing website status details."""

        def execute(self):
            sites = self.get_active_sites()
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
                        "status_duration": datetime.now(timezone.utc) - entry.created,
                    }

            message_body = render_template("status.status_report", {
                "table_rows": list(table_rows()),
            })
            self.mailer.notify("Status report", message_body)

    class backup_apps(CommandBase):
        """Backs up apps to Amazon S3"""

        def execute(self):
            sites = self.get_active_app_sites_with_ssh_config()
            for site in sites:
                logging.debug(f"started backup: {site.app}, {site.host}")
                start_at = perf_counter()
                backup_app(site, self.config["backup"], self.config["aws"])
                duration = (perf_counter() - start_at) * 1000
                logging.info(f"{site.app} {site.host}, ({int(duration)}ms)")


def commands():
    """
    Generates a list of commands.
    """
    for attr_name in dir(Commands):
        attr = getattr(Commands, attr_name)
        if type(attr).__name__ == "type" and attr.__base__.__name__ == "CommandBase":
            yield attr


def get_command(command_name):
    """
    Fetch a command given its name or alias.
    """
    for command in commands():
        if command_name == command.__name__:
            return command


def configure_logging(filepath, show_debug_logs=False):
    logging_level = logging.DEBUG if show_debug_logs else logging.INFO
    logging.basicConfig(
        filename=filepath,
        format="%(asctime)s %(levelname)s: %(message)s",
        level=logging_level)
