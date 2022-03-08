from awpy.parser import DemoParser
import matplotlib.pyplot as plt
from awpy.visualization.plot import plot_map, position_transform
from awpy.data import MAP_DATA
from configparser import ConfigParser
import json

SMOKE_DIAMETER_UNITS = 288

# Read config.ini file
config = ConfigParser()
config.read("config.ini")
demo_dir = config["Data Set"]["demo_directory"]


def plot_all_smokes(rounds, map_name, map_type="simpleradar", dark=True):
    f, a = plot_map(map_name=map_name, map_type=map_type, dark=dark)
    smoke_diameter_scaled = SMOKE_DIAMETER_UNITS / MAP_DATA[map_name]["scale"]
    for r in rounds:
        if r["grenades"]:
            for g in r["grenades"]:
                end_x = position_transform(map_name, g["grenadeX"], "x")
                end_y = position_transform(map_name, g["grenadeY"], "y")
                if g["grenadeType"] == "Smoke Grenade":
                    smoke_circle = plt.Circle(
                        (end_x, end_y), smoke_diameter_scaled / 2, alpha=0.1, color="blue")
                    a.add_artist(smoke_circle)
    return f


def draw_introduction_figures():
    pass
    # overpass_game = DemoParser.read_json(
    #     demo_dir + "misc\\introduction_demos\\")


def draw_doorways():
    entrances_file = open("de_mirage_entrances.json")
    entrances_data = json.load(entrances_file)
    fig, a = plot_map(map_name="de_mirage", map_type="simpleradar")
    fig.set_size_inches(18.5, 10.5)

    for entrance in entrances_data.values():
        x1 = position_transform("de_mirage", entrance["x1"], "x")
        x2 = position_transform("de_mirage", entrance["x2"], "x")
        y1 = position_transform("de_mirage", entrance["y1"], "y")
        y2 = position_transform("de_mirage", entrance["y2"], "y")
        a.plot([x1, x2], [y1, y2], color="#FF10F0", linewidth=2.5)
        a.scatter(x1, y1, color="#FF10F0")
        a.scatter(x2, y2, color="#FF10F0")
    fig.savefig(config["Outputs"]["image_save_location"] +
                '\\doorway_locations.png', dpi=100)
    plt.show()


# location = demo_dir + "\\misc\\introduction_demos\\"
# demo_parser_1 = DemoParser(
#     demofile=location + "natus-vincere-vs-g2-m1-inferno.dem", outpath=location)
# demo_parser_2 = DemoParser(
#     demofile=location + "natus-vincere-vs-g2-m2-mirage.dem", outpath=location)
# demo1, demo2 = demo_parser_1.parse_demo(), demo_parser_2.parse_demo()
draw_doorways()
