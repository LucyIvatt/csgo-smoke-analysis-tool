from csgo.parser import DemoParser
import matplotlib.pyplot as plt
from csgo.visualization.plot import plot_nades, plot_map
from configparser import ConfigParser

# Read config.ini file
config = ConfigParser()
config.read("config.ini")
demo_dir = config["Locations"]["demo_dir"]


# https://github.com/pnxenopoulos/csgo#setup


# Set parse_rate to a power of 2 between 2^0 and 2^7. It indicates the spacing between parsed ticks. Larger numbers result in fewer frames recorded. 128 indicates a frame per second on professional game demos.
demo_parser = DemoParser(demofile=demo_dir + "\\g2-vs-nip-inferno.dem",
                         demo_id="g2-vs-nip-inferno", parse_rate=128)


# Parse the demofile, output results to dictionary with df name as key
data = demo_parser.parse()

f, a = plot_map(map_name="de_dust2", map_type="original")
plot_nades(rounds=d["gameRounds"][7:10], nades=["Flashbang", "HE Grenade", "Smoke Grenade",
           "Molotov", "Incendiary Grenade"], side="CT", map_name="de_dust2", map_type="simple")
plt.show()
