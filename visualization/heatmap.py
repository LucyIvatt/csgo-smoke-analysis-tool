from csgo.parser import DemoParser
import matplotlib.pyplot as plt
from csgo.visualization.plot import plot_nades, plot_map, position_transform
from configparser import ConfigParser

# Read config.ini file
config = ConfigParser()
config.read("config.ini")
demo_dir = config["Locations"]["demo_dir"]


def plot_smokes(
    rounds, nades=[], map_name="de_ancient", map_type="original", dark=False
):
    """Plots grenade trajectories.
    Args:
        rounds (list): List of round objects from a parsed demo
        nades (list): List of grenade types to plot
        side (string): Specify side to plot grenades. Either "CT" or "T".
        map_name (string): Map to search
        map_type (string): "original" or "simpleradar"
        dark (boolean): Only for use with map_type="simpleradar". Indicates if you want to use the SimpleRadar dark map type
    Returns:
        matplotlib fig and ax
    """
    f, a = plot_map(map_name=map_name, map_type=map_type, dark=dark)
    for r in rounds:
        if r["grenades"]:
            for g in r["grenades"]:
                end_x = position_transform(map_name, g["grenadeX"], "x")
                end_y = position_transform(map_name, g["grenadeY"], "y")
                if g["grenadeType"] in nades:
                    if g["grenadeType"] == "Smoke Grenade":
                        smoke_circle = plt.Circle(
                            (end_x, end_y), 20, alpha=0.1, color="red")
                        a.add_artist(smoke_circle)


# Set parse_rate to a power of 2 between 2^0 and 2^7. It indicates the spacing between parsed ticks. Larger numbers result in fewer frames recorded. 128 indicates a frame per second on professional game demos.
demo_parser = DemoParser(demofile=demo_dir + "\\g2-vs-nip-inferno.dem",
                         demo_id="g2-vs-nip-inferno", parse_rate=128)

# Parse the demofile, output results to dictionary with df name as key
d = demo_parser.parse()

plot_smokes(rounds=d["gameRounds"], nades=[
    "Smoke Grenade"], map_name="de_inferno")
plt.show()
