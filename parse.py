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
DATASET_FILE = "data\\dataset.json"


def generate_dataset():
    logging.info(f"Generating .json Dataset...")
    dataset = []

    for file in os.listdir(DEMO_DIR):
        if file.endswith(".dem"):

            logging.info(f"Extracting smokes from {file}")

            smokes = extract_smokes(DEMO_DIR + "\\" + file)
            dataset += smokes

    with open(DATASET_FILE, 'w') as f:
        json.dump(dataset, f, indent=2)


def extract_smokes(demo_file):
    demo_id = demo_file.split("\\")[-1].replace(".dem", "")
    demo_parser = DemoParser(
        demofile=demo_file, demo_id=demo_id, parse_rate=128, outpath=DEMO_DIR)
    demo = demo_parser.parse()
    extracted_smokes = []
    for r in demo["gameRounds"]:
        if not r["isWarmup"]:
            smoke_grenades = [grenade for grenade in r["grenades"]
                              if grenade["grenadeType"] == "Smoke Grenade"]
            for smoke in smoke_grenades:
                entry = {}
                entry["demoID"] = demo_id
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
    return extracted_smokes


generate_dataset()
