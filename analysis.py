import json
from pygame.math import Vector2


class Doorway():
    def __init__(self, name, x1, y1, x2, y2, z):
        self.name = name
        self.z = z

        self.coord1_vector = Vector2(x1, y1)
        self.coord2_vector = Vector2(x2, y2)
        self.midpoint = Vector2((x1 + x2) / 2, (y1 + y2) / 2)

    def __str__(self):
        return f"Doorway({self.name.capitalize()} -> (x1, y1)={self.coord1_vector}, (x2_y2)={self.coord2_vector}, (midx, midy)={self.midpoint}, z={self.z})"

    def distance_from_midpoint(self, smoke_x, smoke_y, meters=False):
        smoke_vector = Vector2(smoke_x, smoke_y)
        dist_units = smoke_vector.distance_to(self.midpoint)

        if meters:
            unit_to_meter_scalar = 0.01905  # 1 unit = 0.01905 meters.
            dist_meters = dist_units * unit_to_meter_scalar
            return dist_meters
        else:
            return dist_units


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


doorways = load_doorway_data()
print(doorways[0].distance_from_midpoint(-700, -1270))
