import time
import json
import logging
import os

from awpy.parser import DemoParser
from configparser import ConfigParser

logging.basicConfig(level=logging.INFO, filename='logs//parser.log',
                    filemode='w', format='%(name)s - %(levelname)s - %(message)s')

# Read config.ini file
config = ConfigParser()
config.read("config.ini")

DEMO_DIR = config["Data"]["demo_directory"] + "\\mirage_demos"
DATASET_FILE = config["Data"]["demo_directory"] + "\\dataset.json"
DATASET_STATS_FILE = config["Data"]["demo_directory"] + "\\dataset_stats.json"


def generate_dataset():
    logging.info(f"Generating .json Dataset...")

    stats = {"demoCount": 0, "roundCount": 0, "smokeCount": 0}
    dataset = []

    for file in os.listdir(DEMO_DIR):
        if file.endswith(".dem"):

            logging.info(f"Extracting smokes from {file}")

            smokes, num_rounds = extract_smokes(DEMO_DIR + "\\" + file)
            stats["demoCount"] += 1
            stats["roundCount"] += num_rounds
            stats["smokeCount"] += len(smokes)
            dataset.append(smokes)

    with open(DATASET_FILE, 'w') as f:
        json.dump(dataset, f, indent=2)

    with open(DATASET_STATS_FILE, 'w') as f:
        json.dump(stats, f, indent=2)


def extract_smokes(demo_file):
    demo_id = demo_file.split("\\")[-1].replace(".dem", "")
    demo_parser = DemoParser(
        demofile=demo_file, demo_id=demo_id, parse_rate=128, outpath=DEMO_DIR)
    demo = demo_parser.parse()
    extracted_smokes = []
    num_rounds = 0
    for r in demo["gameRounds"]:
        if not r["isWarmup"]:
            num_rounds += 1
            smoke_grenades = [grenade for grenade in r["grenades"]
                              if grenade["grenadeType"] == "Smoke Grenade"]

            for smoke in smoke_grenades:
                entry = {}
                entry["throwerName"] = smoke["throwerName"]
                entry["throwerTeam"] = smoke["throwerTeam"]
                entry["throwerSide"] = smoke["throwerSide"]
                entry["roundNum"] = r["roundNum"]
                entry["throwTime"] = smoke["throwClockTime"]
                entry["grenadeX"] = smoke["grenadeX"]
                entry["grenadeY"] = smoke["grenadeY"]
                entry["grenadeZ"] = smoke["grenadeZ"]
                entry["roundWon"] = True if r["winningSide"] == smoke["throwerSide"] else False
                extracted_smokes.append(entry)
    return extracted_smokes, num_rounds


generate_dataset()
