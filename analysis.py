import json
from pygame.math import Vector2
import matplotlib.pyplot as plt
from configparser import ConfigParser
import math

# Read config.ini file
config = ConfigParser()
config.read("config.ini")


class Smoke():
    def __init__(self, x, y, z, radius=config["Data"]["smoke_radius_units"]):
        self.vector = Vector2(x, y)
        self.z = z
        self.radius = int(radius)

    def coordinate_in_smoke(self, x, y):
        return (x - self.vector.x)**2 + (y - self.vector.y)**2 < self.radius**2


class Doorway():
    def __init__(self, name, x1, y1, x2, y2, z):
        self.name = name
        self.z = z

        self.vector1 = Vector2(x1, y1)
        self.vector2 = Vector2(x2, y2)
        self.midpoint = Vector2((x1 + x2) / 2, (y1 + y2) / 2)

        self.length = self.vector1.distance_to(self.vector2)

    def __str__(self):
        return f"Doorway({self.name.capitalize()} -> (x1, y1)={self.vector1}, (x2_y2)={self.vector2}, (midx, midy)={self.midpoint}, z={self.z})"

    def distance_from_midpoint(self, smoke_x, smoke_y, meters=False):
        smoke_vector = Vector2(smoke_x, smoke_y)
        dist_units = smoke_vector.distance_to(self.midpoint)

        if meters:
            unit_to_meter_scalar = 0.01905  # 1 unit = 0.01905 meters.
            dist_meters = dist_units * unit_to_meter_scalar
            return dist_meters
        else:
            return dist_units

    def draw_abstract_representation(self, smoke, plot_radius=False):
        plt.rcParams.update({'font.size': 16})
        fig1 = plt.figure()
        fig1.set_size_inches(12, 12)
        ax1 = fig1.add_subplot(111, aspect='equal')

        spacing = 6

        # Plots the doorway
        x_values = [self.vector1.x, self.vector2.x]
        y_values = [self.vector1.y, self.vector2.y]
        ax1.plot(x_values, y_values, 'bo', linestyle='dashed')
        ax1.text(self.vector1.x + spacing, self.vector1.y,
                 f"D1\n({self.vector1.x}, {self.vector1.y})", horizontalalignment='left',
                 verticalalignment='center')
        ax1.text(self.vector2.x + spacing, self.vector2.y,
                 f"D2\n({self.vector2.x}, {self.vector2.y})", horizontalalignment='left',
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

    def calculate_coverage(self, smoke):
        # Test code to calculate points of intersection
        # Checks if both coordinates are within the circle
        d1_in_smoke = smoke.coordinate_in_smoke(self.vector1.x, self.vector1.y)
        d2_in_smoke = smoke.coordinate_in_smoke(self.vector2.x, self.vector2.y)

        print(f"D1 in circle? {d1_in_smoke}")
        print(f"D2 in circle? {d2_in_smoke}")

        if d1_in_smoke and d2_in_smoke:
            print("Doorway fully within smoke - 100%")
        else:
            # coefficients for quadratic equation
            V = self.vector2-self.vector1

            a = V.dot(V)
            b = 2 * V.dot(self.vector1 - smoke.vector)
            c = self.vector1.dot(self.vector1) + smoke.vector.dot(smoke.vector) - \
                2 * self.vector1.dot(smoke.vector) - smoke.radius**2

            # Calculates discriminant
            disc = b**2 - 4 * a * c
            if disc < 0:
                print("Smoke does not intersect the doorway at any point - 0%")
            else:
                sqrt_disc = math.sqrt(disc)
                t1 = (-b + sqrt_disc) / (2 * a)
                t2 = (-b - sqrt_disc) / (2 * a)
                if not (0 <= t1 <= 1 or 0 <= t2 <= 1):
                    print(
                        "Smoke does not intersect the doorway at any point - would if doorway extended - 0%")
                elif t1 == t2:
                    print("Doorway is at a tangent to the smoke grenade - 0%")
                else:
                    point_1 = self.vector1 + t1 * V
                    point_2 = self.vector1 + t2 * V

                    if 0 <= t1 <= 1 and not 0 <= t2 <= 1:
                        point_2 = self.vector1 if d1_in_smoke else self.vector2
                    elif not 0 <= t1 <= 1 and 0 <= t2 <= 1:
                        point_1 = self.vector1 if d1_in_smoke else self.vector2

                    coverage_in_units = point_1.distance_to(point_2)
                    percentage_coverage = (
                        coverage_in_units / self.length) * 100

                    print("Points of intersection:")
                    print(f"Point 1: {point_1} t1: {t1}")
                    print(f"Point 2: {point_2} t2: {t2}")
                    print(f"Coverage in units: {coverage_in_units}")
                    print(f"Percentage coverage {percentage_coverage}")


def point_within_circle(point_x, point_y, circle_x, circle_y, radius):
    return (point_x - circle_x)**2 + (point_y - circle_y)**2 < radius**2


def draw_example():
    test_doorway = Doorway("Test", 150, 50, 250, 250, None)
    test_smoke = Smoke(200, 200, None)
    test_doorway.draw_abstract_representation(test_smoke, plot_radius=True)
    plt.show()


def load_doorway_data():
    entrances_file = open("de_mirage_entrances.json")
    entrances_data = json.load(entrances_file)
    doorways = []

    for entrance, data in entrances_data.items():
        doorways.append(
            Doorway(entrance, x1=data["x1"],
                    y1=data["y1"],
                    x2=data["x2"],
                    y2=data["y2"],
                    z=data["z"]))
    return doorways
