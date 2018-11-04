#!/usr/bin/env python
import os
import sys
import argparse


BASE_DIR = os.path.dirname(os.getcwd())
sys.path.append(BASE_DIR)

from core.handler import Handler


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='collect client info')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-c', '--collect-data', action="store_true", help="collect client data")
    group.add_argument('-r', '--report-data', action="store_true", help="collect and report client data")
    args = parser.parse_args()
    if args.collect_data:
        Handler.collect_data()
    elif args.report_data:
        Handler.report_data()
    else:
        print('Do Nothing! please add -h argument to get help.')

