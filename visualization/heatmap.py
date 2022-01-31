from csgo.parser import DemoParser
import matplotlib.pyplot as plt
from csgo.visualization.plot import plot_map, position_transform
from constants import DEMO_DIR

# https://github.com/pnxenopoulos/csgo#setup


# Set parse_rate to a power of 2 between 2^0 and 2^7. It indicates the spacing between parsed ticks. Larger numbers result in fewer frames recorded. 128 indicates a frame per second on professional game demos.
demo_parser = DemoParser(demofile=DEMO_DIR + "\\g2-vs-nip-inferno.dem",
                         demo_id="g2-vs-nip-inferno", parse_rate=128)


# Parse the demofile, output results to dictionary with df name as key
data = demo_parser.parse()
