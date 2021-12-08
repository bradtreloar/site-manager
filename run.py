from argparse import ArgumentParser
import argparse
from datetime import datetime, timedelta
import logging
from multiprocessing.pool import ThreadPool
import os
from time import perf_counter
import yaml

from manager.commands import Commands
from manager.database import session
from manager.sites import import_sites


def main():
    start_at = perf_counter()
    args = get_args()
    with open(args.config) as file:
        config = yaml.safe_load(file)
    logging.basicConfig(
        filename=config["logging"]["path"],
        format="%(asctime)s %(levelname)s: %(message)s",
        level=logging.DEBUG if args.debug else logging.INFO)
    db_session = session(config["database"])
    import_sites(config["sites"], config["webauth"], db_session)
    try:
        command = getattr(Commands, args.command)
        command(config, db_session)()
        end_at = perf_counter()
        duration = (end_at - start_at) * 1000
        logging.info(f"{args.command} ({int(duration)}ms)")
    except AttributeError:
        print("Error: Command does not exist: " + args.command)
        logging.error("Command does not exist: " + args.command)


def get_args():
    parser = ArgumentParser()
    parser.add_argument('command',
                        help='the command to execute')
    parser.add_argument('--config',
                        help='path to config',
                        default="./config.yml")
    parser.add_argument('--debug',
                        help='print debugging logs',
                        dest='debug', action='store_true')
    return parser.parse_args()


if __name__ == "__main__":
    main()
