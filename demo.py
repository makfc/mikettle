#!/usr/bin/env python3
"""Demo file showing how to use the mikettle library."""

import argparse
import re

import sys
import logging

import time
import datetime
import os

from mikettle.mikettle import MiKettle
from mikettle.mikettle import (
  MI_ACTION,
  MI_MODE,
  MI_SET_TEMPERATURE,
  MI_CURRENT_TEMPERATURE,
  MI_KW_TYPE,
  MI_KW_TIME
)

def valid_mikettle_mac(mac, pat=re.compile(r"[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}")):
    """Check for valid mac adresses."""
    if not pat.match(mac.upper()):
        raise argparse.ArgumentTypeError('The MAC address "{}" seems to be in the wrong format'.format(mac))
    return mac


def valid_product_id(product_id):
    try:
        product_id = int(product_id)
    except Exception:
        raise argparse.ArgumentTypeError('The Product Id "{}" seems to be in the wrong format'.format(product_id))
    return product_id


def connect(args):
    """Connect to Mi Kettle."""

    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)

    last_exception_time = datetime.datetime(1, 1, 1, 0, 0)
    sec = 5

    try:
        kettle = MiKettle(args.mac, args.product_id)
        print("Authenticating")
        print("Getting data from mi Kettle")
        # print("FW: {}".format(kettle.firmware_version()))
        # print("Name: {}".format(kettle.name()))

        # print("Current temperature: {}".format(kettle.parameter_value(MI_CURRENT_TEMPERATURE)))
        kettle.fill_cache()
        while True:
            if not kettle.waitForNotifications():
                break
            print("Notification")
    except Exception as error:
        now = datetime.datetime.now()
        span = now - last_exception_time
        last_exception_time = now
        if (span.total_seconds() <= sec + 2):
            sec += 5
        print("Read failed", error)
        print(f"wait {sec}s...")
        time.sleep(sec)
    os.execl(sys.executable, sys.executable, *sys.argv)


def main():
    """Main function.

    Mostly parsing the command line arguments.
    """
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='sub-command help', )

    parser_poll = subparsers.add_parser('connect', help='connect to mi kettle and receive data')
    parser_poll.add_argument('mac', type=valid_mikettle_mac)
    parser_poll.add_argument('product_id', type=valid_product_id)
    parser_poll.set_defaults(func=connect)

    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == '__main__':
    main()
