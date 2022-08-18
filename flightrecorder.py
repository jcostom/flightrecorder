#!/usr/bin/env python3

# With great power comes great responsibility. This script can be used
# to do really bad things. Don't be a jerk. If you want to do fun things
# like mail an AirTag around the world and see where it goes, cool.
# If you want to troubleshoot why your packages are taking a long time
# to make it from point A to point B, cool. But if you're going to use
# this for evil, you do not have permission to use this code.
#
# Be excellent to each other. Party on, dudes.

import csv
import json
from shutil import copyfile
from datetime import datetime
import subprocess
import os
from time import sleep
import logging
import argparse

parser = argparse.ArgumentParser(
    prog='flightrecorder.py',
    description='Recording location info from AirTags.'
)
parser.add_argument("-s", "--serial", action="store", required=False,
                    help="Specify serial number of a single AirTag to track. Omit to track all.")  # noqa: E501
args = parser.parse_args()

if args.serial:
    print(f"args.serial is {args.serial}")

# this is the JSON file that contains the AirTag location info
# as long as Find My is open, it gets updated roughly ever minute
HOME = os.getenv('HOME')
JSON_FILE = f"{HOME}/Library/Caches/com.apple.findmy.fmipcore/Items.data"

# location for temp JSON file and CSV output files
TMP_FILE = "./tmp_items.json"
CSV_FILE = "./tracking_info.csv"

# fields we care about tracking - there's a ton more, but these are
# enough to get what we're after
CSV_FIELDS = ['datetime', 'name', 'serialNumber', 'batteryStatus', 'positionType', 'latitude', 'longitude', 'timestamp', 'locationIsOld']  # noqa: E501

# we're going to check the JSON file for updates on this interval
SLEEP_TIMER = 60

# initializing the last updated timer
JSON_LAST_CHANGED = 0

VER = "0.2"
USER_AGENT = f"flightrecorder.py/{VER}"

# Setup logger
logger = logging.getLogger()
ch = logging.StreamHandler()
logger.setLevel(logging.INFO)
ch.setLevel(logging.INFO)
formatter = logging.Formatter('[%(levelname)s] %(asctime)s %(message)s',
                              datefmt='[%d %b %Y %H:%M:%S %Z]')
ch.setFormatter(formatter)
logger.addHandler(ch)


def is_find_my_dead() -> bool:
    num_pids = int(subprocess.getoutput('ps aux|grep "FindMy.app/Contents/MacOS/FindM[y]"|wc -l'))  # noqa: E501
    logger.info(f"FindMy process check result was: {num_pids}.")
    if num_pids > 0:
        # non-zero = It's Alive!
        return False
    else:
        # zero == He's dead, Jim
        return True


def start_find_my() -> None:
    logger.info("Launching FindMy App")
    subprocess.run(["open", "/System/Applications/FindMy.app"])


def init_csv_file(filename: str, fields: list[str]) -> None:
    with open(filename, "w+", newline='') as csvfile:
        # instantiate writer object, setup for Excel compatibility
        csvwriter = csv.writer(csvfile, dialect='excel')
        # write header row w/ field names
        csvwriter.writerow(fields)


def update_location_data(json_last_changed: float) -> float:
    logger.info("Reading Location Data...")
    try:
        current_time = os.path.getmtime(JSON_FILE)
        logger.info(f"{JSON_FILE} mtime is: {current_time}")
        logger.info(f"last time we looked at was {json_last_changed}")
        if not current_time > json_last_changed:
            logger.info("JSON File hasn't changed, skipping this round.")
            return json_last_changed
        json_last_changed = current_time
        copyfile(JSON_FILE, TMP_FILE)
    except Exception as e:
        logger.info(f"Unable to copy file, check file and app permissions: {e}")  # noqa: E501
        exit(2)

    with open(TMP_FILE) as jf:
        data = json.load(jf)
        new_rows = []
        for t in data:
            print(".", end='')
            name = t["name"]
            serialNumber = t["serialNumber"]
            batteryStatus = t["batteryStatus"]
            positionType = t["location"]["positionType"]
            latitude = t["location"]["latitude"]
            longitude = t["location"]["longitude"]
            timestamp = t["location"]["timeStamp"]
            locationIsOld = t["location"]["isOld"]

            if ((args.serial) and (args.serial != serialNumber)):
                pass
            else:
                when = datetime.now().strftime("%Y-%m-%d %T")
                new_rows.append([when, name, serialNumber, batteryStatus,
                                 positionType, latitude,
                                 longitude, timestamp,
                                 locationIsOld])

    with open(CSV_FILE, 'a') as csvfile:
        csvwriter = csv.writer(csvfile, dialect='excel')
        csvwriter.writerows(new_rows)
    logger.info("Done, sleeping.")
    return json_last_changed


while True:
    # Is FindMy.app Running? If not launch it.
    if is_find_my_dead():
        start_find_my()
    # Does output file already exist? If not, initialize it.
    if not os.path.isfile(CSV_FILE):
        init_csv_file(CSV_FILE, CSV_FIELDS)
    # read JSON file
    JSON_LAST_CHANGED = update_location_data(JSON_LAST_CHANGED)

    sleep(SLEEP_TIMER)
