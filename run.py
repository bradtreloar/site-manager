from argparse import ArgumentParser
from datetime import datetime, timedelta
from multiprocessing.pool import ThreadPool
import os
import yaml

from manager.commands import Commands
from manager.database import session
from manager.sites import import_sites


def main():
    args = get_args()
    with open(args.config) as file:
        config = yaml.safe_load(file)
    db_session = session(config["database"])
    import_sites(config["sites"], config["webauth"], db_session)
    try:
        command = getattr(Commands, args.command)
        command(config, db_session)()
    except AttributeError:
        print("Error: Command does not exist: " + args.command)


def get_args():
    parser = ArgumentParser()
    parser.add_argument('command',
                        help='the command to execute')
    parser.add_argument('--config',
                        help='path to config',
                        default="./config.yml")
    return parser.parse_args()


if __name__ == "__main__":
    main()
