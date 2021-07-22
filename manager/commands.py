
from datetime import datetime
from multiprocessing.pool import ThreadPool
from termcolor import colored

from manager.status.models import SiteStatus, StatusLogType
from manager.database import session
from manager.notifications.mail import Mailer, Renderer
from manager.status import check_https_status
from manager.status.models import StatusLogEntry
from manager.sites import Site, import_sites


class CommandBase:

    def __init__(self, config):
        self.config = config
        self.db_session = session(config["database"])
        import_sites(config["sites"], self.db_session)
        self.mailer = Mailer(config["mail"])
        self.renderer = Renderer()


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
            sites_info = [{
                "site_id": site.id,
                "site_url": "https://" + site.host,
                "site_latest_status": site.latest_status,
            } for site in sites]
            results = ThreadPool().imap_unordered(
                check_https_status, sites_info)
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
            status_colors = {
                SiteStatus.UP: ("grey", "on_green"),
                SiteStatus.DOWN: ("white", "on_red"),
                SiteStatus.UNKNOWN: ("grey", "on_yellow"),
            }
            print()
            for site in sites:
                status = site.latest_status
                try:
                    status_age = (datetime.now() -
                                  site.latest_status_log_entry.created)
                except AttributeError:
                    status_age = ""
                print("{0:.<40} {1} for {2}".format(
                    site.host,
                    colored(" {} ".format(
                        status.value.upper()), *status_colors[status]),
                    status_age))
            print()


class CommandError(BaseException):
    pass
