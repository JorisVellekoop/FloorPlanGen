import random
import squarify
import matplotlib.pyplot as plt


class FloorPlanGenerator:
    def __init__(self, floor_plan_size=10.0, min_rooms=3, max_rooms=5, door_size=1.5, room_size_ratio=4.0, max_iteration=5):
        self.floor_plan_size = floor_plan_size
        self.min_rooms = min_rooms
        self.max_rooms = max_rooms
        self.rooms = 0
        self.door_size = door_size
        self.room_size_ratio = room_size_ratio
        self.max_iteration = max_iteration

        self.room_sizes = []
        self.values = []
        self.rects = []

        self.edge_pairs = []
        self.edges = []
        self.edge_sizes = []
        self.edge_orientations = []
        self.connected_edges = []

        self.treemap_viable = False

    def reset(self):
        self.rooms = random.randint(self.min_rooms, self.max_rooms)
        self.room_sizes = [random.uniform(1, self.room_size_ratio) for _ in range(self.rooms)]

        self.values = []
        self.rects = []

        self.edges = []
        self.edge_sizes = []
        self.edge_orientations = []

        self.edge_pairs = []
        self.connected_edges = []

        self.treemap_viable = False

    def generate_squarified_treemap(self):
        self.values = squarify.normalize_sizes(self.room_sizes, self.floor_plan_size, self.floor_plan_size)
        self.rects = squarify.squarify(self.values, 0, 0, self.floor_plan_size, self.floor_plan_size)

        # change values to absolute coordinates
        for rect in self.rects:
            rect["dx"] += rect["x"]
            rect["dy"] += rect["y"]

    def get_edge_pairs(self):
        for index1, rect1 in enumerate(self.rects):
            for index2, rect2 in enumerate(self.rects[index1 + 1:]):
                if rect1["x"] == rect2["dx"]:
                    if rect1["dy"] > rect2["y"] and rect2["dy"] > rect1["y"]:
                        self.edge_pairs.append([index1, index1 + index2 + 1])
                        self.edges.append([[rect1["x"], max(rect1["y"], rect2["y"])],
                                           [rect1["x"], min(rect1["dy"], rect2["dy"])]])
                        self.edge_sizes.append(self.edges[-1][1][1] - self.edges[-1][0][1])
                        self.edge_orientations.append("vertical")

                elif rect1["dx"] == rect2["x"]:
                    if rect1["dy"] > rect2["y"] and rect2["dy"] > rect1["y"]:
                        self.edge_pairs.append([index1, index1 + index2 + 1])
                        self.edges.append([[rect1["dx"], max(rect1["y"], rect2["y"])],
                                           [rect1["dx"], min(rect1["dy"], rect2["dy"])]])
                        self.edge_sizes.append(self.edges[-1][1][1] - self.edges[-1][0][1])
                        self.edge_orientations.append("vertical")

                elif rect1["y"] == rect2["dy"]:
                    if rect1["dx"] > rect2["x"] and rect2["dx"] > rect1["x"]:
                        self.edge_pairs.append([index1, index1 + index2 + 1])
                        self.edges.append([[max(rect1["x"], rect2["x"]), rect1["y"]],
                                           [min(rect1["dx"], rect2["dx"]), rect1["y"]]])
                        self.edge_sizes.append(self.edges[-1][1][0] - self.edges[-1][0][0])
                        self.edge_orientations.append("horizontal")

                elif rect1["dy"] == rect2["y"]:
                    if rect1["dx"] > rect2["x"] and rect2["dx"] > rect1["x"]:
                        self.edge_pairs.append([index1, index1 + index2 + 1])
                        self.edges.append([[max(rect1["x"], rect2["x"]), rect1["dy"]],
                                           [min(rect1["dx"], rect2["dx"]), rect1["dy"]]])
                        self.edge_sizes.append(self.edges[-1][1][0] - self.edges[-1][0][0])
                        self.edge_orientations.append("horizontal")

        return self.edge_pairs, self.edges, self.edge_sizes, self.edge_orientations

    def get_connectable_edges(self):
        connected_rooms = {self.values.index(max(self.values))}
        new_rooms = {self.values.index(max(self.values))}

        while len(connected_rooms) != self.rooms:
            if len(new_rooms) == 0:
                return
            for room in new_rooms.copy():
                for edge_pair, edge_size, edge in zip(self.edge_pairs, self.edge_sizes, self.edges):
                    if room in edge_pair and (edge_pair[0] not in connected_rooms or edge_pair[1] not in connected_rooms):
                        if edge_size > self.door_size:
                            connected_rooms.update(edge_pair)
                            new_rooms.update(edge_pair)
                            self.connected_edges.append(edge)
                new_rooms.remove(room)

        self.treemap_viable = True

        return self.connected_edges

    def add_doorways(self):
        for edge in self.connected_edges:
            index = self.edges.index(edge)
            if self.edge_orientations[index] == "vertical":
                # Randomly place door and split edge accordingly
                door_position = random.uniform(edge[0][1] + self.door_size / 2, edge[1][1] - self.door_size / 2)
                self.edges.append([edge[0], [edge[0][0], door_position - self.door_size / 2]])
                self.edges.append([[edge[0][0], door_position + self.door_size / 2], edge[1]])
                # Update edge sizes
                self.edge_sizes.append(door_position - self.door_size / 2 - edge[0][1])
                self.edge_sizes.append(edge[1][1] - door_position - self.door_size / 2)
                # Update edge orientations
                self.edge_orientations.extend(["vertical", "vertical"])
                # Remove original edge
                self.edge_sizes.pop(index)
                self.edge_orientations.pop(index)
                self.edges.remove(edge)

            elif self.edge_orientations[index] == "horizontal":
                # Randomly place door and split edge accordingly
                door_position = random.uniform(edge[0][0] + self.door_size / 2, edge[1][0] - self.door_size / 2)
                self.edges.append([edge[0], [door_position - self.door_size / 2, edge[0][1]]])
                self.edges.append([[door_position + self.door_size / 2, edge[0][1]], edge[1]])
                # Update edge sizes
                self.edge_sizes.append(door_position - self.door_size / 2 - edge[0][0])
                self.edge_sizes.append(edge[1][0] - door_position - self.door_size / 2)
                # Update edge orientations
                self.edge_orientations.extend(["horizontal", "horizontal"])
                # Remove original edge
                self.edge_sizes.pop(index)
                self.edge_orientations.pop(index)
                self.edges.remove(edge)

        return self.edges

    def add_perimeter(self):
        self.edges.extend([[[0, 0], [0, self.floor_plan_size]],
                           [[0, 0], [self.floor_plan_size, 0]],
                           [[self.floor_plan_size, 0], [self.floor_plan_size, self.floor_plan_size]],
                           [[0, self.floor_plan_size], [self.floor_plan_size, self.floor_plan_size]]])
        self.edge_orientations.extend(["vertical", "horizontal", "vertical", "horizontal"])
        self.edge_sizes.extend([self.floor_plan_size, self.floor_plan_size, self.floor_plan_size, self.floor_plan_size])
        return self.edges

    def generate(self):
        self.reset()
        for i in range(self.max_iteration):
            self.generate_squarified_treemap()
            self.get_edge_pairs()
            self.get_connectable_edges()
            if self.treemap_viable:
                break

        if not self.treemap_viable:
            print("error: unable to find a viable floor plan")

        self.add_doorways()
        self.add_perimeter()

        return self.edges

    def compute_center_edges(self):
        positions = []
        for edge in self.edges:
            positions.append([(edge[0][0]+edge[1][0])/2, (edge[0][1]+edge[1][1])/2])

        return positions

    def get_edge_properties(self):
        return self.compute_center_edges(), self.edge_orientations, self.edge_sizes

    def get_random_spawn_location(self, margin=1.0):
        for _ in range(100):
            x = random.uniform(margin, self.floor_plan_size-margin)
            y = random.uniform(margin, self.floor_plan_size-margin)
            for rect in self.rects:
                if rect["x"] + margin < x < rect["dx"] - margin and rect["y"] + margin < y < rect["dy"] - margin:
                    return [x, y]

        return print("no spawn location found")

    def get_random_pointgoal(self, min_dist=3.0, other_room=True, margin=1.0):
        # todo: spawn possibility currently not uniform
        if other_room and self.rooms > 1:
            for _ in range(100):
                rooms = random.sample(range(self.rooms), 2)
                points = []
                for room in rooms:
                    points.append([random.uniform(self.rects[room]["x"]+margin, self.rects[room]["dx"]-margin),
                                   random.uniform(self.rects[room]["y"]+margin, self.rects[room]["dy"]-margin)])

                if ((points[0][0] - points[1][0]) ** 2 + (points[0][1] - points[1][1]) ** 2)**0.5 >= min_dist:
                    return points

            return print("no spawn location found")

        else:
            for _ in range(100):
                points = [self.get_random_spawn_location(margin=margin), self.get_random_spawn_location(margin=margin)]

                if ((points[0][0] - points[1][0]) ** 2 + (points[0][1] - points[1][1]) ** 2) ** 0.5 >= min_dist:
                    return points

            return print("no spawn location found")



    def plot(self):
        for edge in self.edges:
            plt.plot([edge[0][0], edge[1][0]], [edge[0][1], edge[1][1]], 'k-')
        plt.axis("equal")
        plt.show()

        return


if __name__ == "__main__":
    FPG = FloorPlanGenerator(floor_plan_size=10, min_rooms=4, max_rooms=4, room_size_ratio=4)
    for _ in range(10):
        FPG.generate()
        if FPG.treemap_viable:
            # pointgoal = FPG.get_random_pointgoal(other_room=True)
            # for point in pointgoal:
            #     plt.plot(point[0], point[1], "o")
            FPG.plot()

