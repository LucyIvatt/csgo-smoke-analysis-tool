import json
from pygame.math import Vector2
import matplotlib.pyplot as plt
from configparser import ConfigParser
import math
import logging
import numpy as np

logging.basicConfig(level=logging.INFO, filename='logs//analysis.log',
                    filemode='w', format='%(name)s - %(levelname)s - %(message)s')

# Read config.ini file
config = ConfigParser()
config.read("config.ini")
DATASET_FILE = config["Data"]["demo_directory"] + "\\dataset.json"


def point_within_circle(point, circle_centre, radius):
    return (point.x - circle_centre.x)**2 + (point.y - circle_centre.y)**2 < radius**2


class Smoke():
    def __init__(self, thrower, team, side, round_num, time_thrown, round_won, x, y, z):
        self.thrower = thrower
        self.team = team
        self.side = side
        self.round_num = round_num
        self.time_thrown = time_thrown
        self.round_won = round_won

        self.vector = Vector2(x, y)
        self.z = z
        self.radius = int(config["Data"]["smoke_radius_units"])

        self.doorway = None
        self.coverage = None

    def __str__(self):
        return f"Smoke[(x, y, z) => ({self.vector.x}, {self.vector.y}, {self.z})]"

    def in_game_draw_command(self):
        return f"drawcross {self.vector.x} {self.vector.y} {self.z}"

    def point_in_smoke(self, p):
        '''Used to determine check if doorway end points are within the smoke.'''
        return point_within_circle(p, self.vector, self.radius)

    def distance_from_midpoint(self, doorway, meters=False):
        '''Finds distances between smoke and doorway midpoints when target radii overlap'''
        dist_units = self.vector.distance_to(doorway.midpoint)
        return 0.01905 * dist_units if meters else dist_units

    def calculate_coverage(self):
        logging.info(
            f"Calculating Coverage for {self} - {self.doorway}")

        # Checks if both coordinates are within the circle
        d1_in_smoke = self.point_in_smoke(self.doorway.vector1)
        d2_in_smoke = self.point_in_smoke(self.doorway.vector2)

        if d1_in_smoke and d2_in_smoke:
            self.coverage = 100
            logging.info(f"Doorway entirely within smoke - {self.coverage=}")
        else:
            # Coefficients
            V = self.doorway.vector2-self.doorway.vector1
            a = V.dot(V)
            b = 2 * V.dot(self.doorway.vector1 - self.vector)
            c = self.doorway.vector1.dot(self.doorway.vector1) + self.vector.dot(self.vector) - \
                2 * self.doorway.vector1.dot(self.vector) - self.radius**2

            # Discriminant
            disc = b**2 - 4 * a * c
            if disc < 0:
                self.coverage = 0
                logging.info(
                    f"Smoke doesn't intersect doorway - {self.coverage=}")
            else:
                sqrt_disc = math.sqrt(disc)
                t1 = (-b + sqrt_disc) / (2 * a)
                t2 = (-b - sqrt_disc) / (2 * a)

                if not (0 <= t1 <= 1 or 0 <= t2 <= 1):
                    self.coverage = 0
                    logging.info(
                        f"Smoke does not intersect the doorway at any point (would if doorway extended) ")
                elif t1 == t2:
                    self.coverage = 0
                    logging.info(
                        f"Doorway is at a tangent to the smoke grenade - {self.coverage=}")
                else:
                    point_1 = self.doorway.vector1 + t1 * V
                    point_2 = self.doorway.vector1 + t2 * V

                    if 0 <= t1 <= 1 and not 0 <= t2 <= 1:
                        point_2 = self.doorway.vector1 if d1_in_smoke else self.doorway.vector2
                    elif not 0 <= t1 <= 1 and 0 <= t2 <= 1:
                        point_1 = self.doorway.vector1 if d1_in_smoke else self.doorway.vector2

                    coverage_in_units = point_1.distance_to(point_2)
                    self.coverage = (coverage_in_units /
                                     self.doorway.length) * 100

                    logging.debug("Points of intersection:")
                    logging.debug(f"Point 1: {point_1} t1: {t1}")
                    logging.debug(f"Point 2: {point_2} t2: {t2}")
                    logging.debug(f"Coverage in units: {coverage_in_units}")

                    logging.info(
                        f"Doorway partially covered -  {self.coverage=}")


class Doorway():
    def __init__(self, name, x1, y1, x2, y2, z):
        self.name = name
        self.z = z

        self.vector1 = Vector2(x1, y1)
        self.vector2 = Vector2(x2, y2)

        self.midpoint = Vector2((x1 + x2) / 2, (y1 + y2) / 2)

        self.target_radius = int(config["Data"]["detection_radius_units"])
        self.z_tolerance = int(config["Data"]["height_tolerance_units"])
        self.smokes = []

        self.length = self.vector1.distance_to(self.vector2)

    def __str__(self):
        return f"Doorway({self.name.capitalize()})"

    def in_game_draw_command(self):
        coord1_str = f"{self.vector1.x} {self.vector1.y} {self.z}"
        coord2_str = f"{self.vector2.x} {self.vector2.y} {self.z}"
        return f"drawline {coord1_str} {coord2_str}"

    def smoke_in_target_range(self, smoke):
        logging.debug(f"Checking if {smoke} in range of {self.name}")
        if point_within_circle(smoke.vector, self.midpoint, self.target_radius):
            if smoke.z >= self.z - self.z_tolerance and smoke.z <= self.z + self.z_tolerance:
                logging.debug("Smoke in target radius and height tolerance")
                return True
            else:
                logging.debug(
                    "Smoke in target radius and but NOT height tolerance skipping...")
        else:
            logging.debug("Smoke NOT within target radius, skipping...")
        return False


def load_doorway_data():
    entrances_file = open("mirage_entrances.json")
    entrances_data = json.load(entrances_file)
    doorways = []

    for entrance, data in entrances_data.items():
        doorways.append(
            Doorway(name=entrance,
                    x1=data["x1"],
                    y1=data["y1"],
                    x2=data["x2"],
                    y2=data["y2"],
                    z=data["z"] - 64.093811))
    return doorways


def load_smoke_data():
    with open(DATASET_FILE, 'r') as f:
        dataset = json.load(f)

    smokes = []
    for s in dataset:
        smokes.append(Smoke(s["throwerName"],
                            s["throwerTeam"],
                            s["throwerSide"],
                            s["roundNum"],
                            s["throwTime"],
                            s["roundWon"],
                            s["grenadeX"],
                            s["grenadeY"],
                            s["grenadeZ"]
                            ))
    return smokes


def assign_doorways(smokes, doorways):
    logging.info("Assigning Doorways...")
    invalid_smokes = []
    for smoke in smokes:
        valid_doorways = [
            doorway for doorway in doorways if doorway.smoke_in_target_range(smoke)]
        if len(valid_doorways) == 0:
            logging.info(
                f"{smoke} is not in range of any common doorway, skipping...")
            invalid_smokes.append(smoke)
        else:
            if len(valid_doorways) == 1:
                logging.info(
                    f"{smoke} in target zone of {valid_doorways[0].name}...")
                smoke.doorway = valid_doorways[0]
                valid_doorways[0].smokes.append(smoke)
            else:
                logging.info(
                    f"{smoke} in range of multiple doorways, using distance to doorway midpoints")
                distance_to_midpoints = [smoke.distance_from_midpoint(
                    doorway) for doorway in valid_doorways]
                smoke.doorway = valid_doorways[np.argmin(
                    distance_to_midpoints)]
                valid_doorways[np.argmin(
                    distance_to_midpoints)].smokes.append(smoke)

            smoke.calculate_coverage()
    return invalid_smokes


def draw_abstract_representation(doorway, smoke, plot_radius=False):
    plt.rcParams.update({'font.size': 16})
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Helvetica']
    fig1 = plt.figure()
    fig1.set_size_inches(12, 12)
    ax1 = fig1.add_subplot(111, aspect='equal')

    spacing = 6

    # Plots the doorway
    x_values = [doorway.vector1.x, doorway.vector2.x]
    y_values = [doorway.vector1.y, doorway.vector2.y]
    ax1.plot(x_values, y_values, 'bo', linestyle='dashed')
    ax1.text(doorway.vector1.x + spacing, doorway.vector1.y,
             f"D1\n({doorway.vector1.x}, {doorway.vector1.y})", horizontalalignment='left',
             verticalalignment='center')
    ax1.text(doorway.vector2.x + spacing, doorway.vector2.y,
             f"D2\n({doorway.vector2.x}, {doorway.vector2.y})", horizontalalignment='left',
             verticalalignment='center')

    # Plots the radius line
    if plot_radius:
        x_values = [smoke.vector.x, smoke.vector.x-smoke.radius]
        y_values = [smoke.vector.y, smoke.vector.y]
        ax1.plot(x_values, y_values, marker="o",
                 color='grey', linestyle="solid")
        ax1.text(smoke.vector.x - smoke.radius/2, smoke.vector.y - spacing*2,
                 f"Smoke radius\n({smoke.radius} units)", horizontalalignment='center',
                 verticalalignment='center')

    # Plots the smoke
    plt.plot(smoke.vector.x, smoke.vector.y, marker="o", markersize=5, markeredgecolor="black",
             markerfacecolor="black")

    smoke_circle = plt.Circle(
        (smoke.vector.x, smoke.vector.y), smoke.radius, alpha=1, color="black", linewidth=4, fill=False)
    ax1.text(smoke.vector.x, smoke.vector.y+spacing*2, f"Smoke\n({smoke.vector.x}, {smoke.vector.y})", horizontalalignment='center',
             verticalalignment='center')

    ax1.add_patch(smoke_circle)
    ax1.autoscale_view()

    plt.show()


smokes = load_smoke_data()
doorways = load_doorway_data()
invalid_smokes = assign_doorways(smokes[:500], doorways)

for doorway in doorways:
    coverages = [smoke.coverage for smoke in doorway.smokes]
    print(f"{doorway.name} - {coverages}")
