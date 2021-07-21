
from manager.notifications.mail import Mailer, Renderer
from manager.uptime import test_https_response


class CommandBase:

    def __init__(self, config):
        self.config = config
        self.sites = []
        for host, site in config["sites"].items():
            site["host"] = host
            self.sites.append(site)
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

    class monitor_uptime(CommandBase):
        """Monitors website uptime and alerts sysadmin when websites are offline."""

        def execute(self):
            for site in self.sites:
                result = test_https_response(site)
                print(site["host"])
                print("  status_code: {}".format(result["status_code"]))
                print("  duration: {}".format(result["duration"]))


class CommandError(BaseException):
    pass
