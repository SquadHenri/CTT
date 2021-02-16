import csv as csv
from functions import getTravelDistance
import math


def get_containers():
    container_dict = {}
    with open("../data/currentContainers.csv", encoding="utf-8-sig") as containers:
        data = csv.reader(containers, delimiter=",")
        next(data)
        for row in data:
            position = row[3]
            position = position.split(".")
            position = [int(x) for x in position]
            container_dict[row[1]] = position
    return container_dict

# data not available yet
def get_wagons():
    return {"a": [10,0], "b": [20,0], "c": [30,0], "d": [40,0]}

def calculate_distances(containers, wagons):
    distances = {}
    for key in containers.keys():
        position = containers[key]
        dist_list = []
        for wagon in wagons.keys():
            dist_list.append((wagon, getTravelDistance(position, wagons[wagon])))
        distances[key] = min(dist_list, key= lambda t: t[1])
    return distances

containers_data = get_containers()
wagons_data = get_wagons()
print(calculate_distances(containers_data, wagons_data))

# Sets the location of the wagon takes a list of all the containers in the train
def set_location(wagons):
    len = 0
    y_val = 0
    for wagon in wagons:
        if len < 320:
            wagon.location = [math.ceil((len + 0.5 * wagon.length)/6.1), y_val]
            len += wagon.length
        else:
            len = 0
            y_val = -1
            wagon.location = [math.ceil((len + 0.5 * wagon.length)/6/1), y_val]
            len += wagon.length
