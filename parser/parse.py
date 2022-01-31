from csgo.parser import DemoParser
from constants import DEMO_DIR

# https://github.com/pnxenopoulos/csgo#setup


# Set parse_rate to a power of 2 between 2^0 and 2^7. It indicates the spacing between parsed ticks. Larger numbers result in fewer frames recorded. 128 indicates a frame per second on professional game demos.
demo_parser = DemoParser(demofile=DEMO_DIR + "\\g2-vs-nip-inferno.dem",
                         demo_id="g2-vs-nip-inferno", parse_rate=128)


# Parse the demofile, output results to dictionary with df name as key
data = demo_parser.parse()

# prints a specific rounds grenade throws
print(data["gameRounds"][4]['grenades'])


# The following keys exist
# data["matchID"]
# data["clientName"]
# data["mapName"]
# data["tickRate"]
# data["playbackTicks"]
# data["parserParameters"]
# data["serverVars"]
# data["matchPhases"]
# data["parsedPlaceNames"]
# data["matchmakingRanks"]
# # From this value, you can extract player events via: data['gameRounds'][i]['kills'], etc.
# data["gameRounds"]

# You can also parse the data into dataframes using
# data_df = demo_parser.parse(return_type="df")


# You can also access the data in the file demoId_mapName.json, which is written in your working directory
