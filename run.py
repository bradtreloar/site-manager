from argparse import ArgumentParser
import logging
from os import PathLike
import sys
from time import perf_counter
import yaml

from sitemanager.commands import get_command
from sitemanager.database import get_db_session
from sitemanager.sites import import_sites

# Suppress warnings.
if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")


def main():
    cli_args = get_commandline_args()
    command_name = normalize_command_name(cli_args.command_name)
    command = get_command(command_name)
    if command:
        config = get_config(cli_args.config_filepath)
        command(config)()
    else:
        print("Error: Command not found: " + command_name)


def get_commandline_args():
    parser = ArgumentParser()
    parser.add_argument(
        "command_name",
        help="The command to execute.")
    parser.add_argument(
        "--config",
        help="The path to the config file.",
        default="config.yml",
        dest="config_filepath")
    parser.add_argument(
        "--debug",
        help="Print debugging logs.",
        dest="show_debug_logs",
        action="store_true")
    return parser.parse_args()


def get_config(filepath: PathLike):
    with open(filepath) as file:
        return yaml.safe_load(file)


def normalize_command_name(command_name):
    return command_name.replace("-", "_")


if __name__ == "__main__":
    main()
