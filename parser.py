from awpy.parser import DemoParser
from configparser import ConfigParser

# Read config.ini file
config = ConfigParser()
config.read("config.ini")
demo_dir = config["Data"]["demo_directory"]


# Set parse_rate to a power of 2 between 2^0 and 2^7. It indicates the spacing between parsed ticks. Larger numbers result in fewer frames recorded. 128 indicates a frame per second on professional game demos.
# demo_parser = DemoParser(demofile=demo_dir + "\\g2-vs-nip-inferno.dem",
#                          demo_id="g2-vs-nip-inferno", parse_rate=128)


# Parse the demofile, output results to dictionary with df name as key
parser = DemoParser()
data = parser.read_json(
    f"{demo_dir}//misc//introduction_demos//natus-vincere-vs-g2-m1-inferno.json")

# print first grenade from round 4
print(data["gameRounds"][4]['grenades'][0])
print(type(data["gameRounds"][4]['grenades']))
