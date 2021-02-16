import csv as csv
from functions import getTravelDistance
import math
from model.Container import Container
from model.Wagon import Wagon

# creates a list of container objects. It contains all the containers of train 1.
def get_containers_1():
    containers = []

    # open file
    with open("data/trein1/loading_container.csv", encoding="utf-8-sig") as container_file:
        data = csv.reader(container_file, delimiter=",")
        for row in data:
            # initialize variables
            c_id = row[0]
            c_teu = int(row[1])
            c_type = row[2]
            gross_weight = float(row[3].replace(".", "").replace(",", "."))
            net_weight = float(row[4])
            c_pos = get_pos(row[5])
            c_good = row[7]
            # create object
            container = Container(c_id, gross_weight, net_weight, c_teu * 20, c_pos, c_good, 1, c_type)
            # add object to container list
            containers.append(container)
    return containers

# creates a list of wagon objects. It contains all the wagons of train 1.
def get_wagons_1():
    wagons = []

    # open file
    with open("data/trein1/wagonlijst.csv", encoding="utf-8-sig") as wagon_file:
        data = csv.reader(wagon_file, delimiter=";")
        #skip first 10 rows, because they contain different data
        for i in range(11):
            next(data)
        for row in data:
            # initialize variables
            w_id = row[1]
            w_type = row[2]
            w_length = float(row[3].replace(",", "."))
            w_axes = int(row[4])
            # create object
            wagon = Wagon(w_id, -1, w_length, -1, -1)
            # add object to wagon list
            wagons.append(wagon)
    # set the proper location for every wagon
    wagons = set_location(wagons)
    return wagons

# creates a list that represents the coordinates of a container.
# it takes "##.##.##" as an input and returns [##, ##, ##]
def get_pos(position):
    position = position.split(" ")
    position = position[0].split(".")

    try:
        return [int(x) for x in position]
    except ValueError:
        return position

# function that gets all containers that are currently on the terminal (not on a loading list or something)
def get_containers():
    container_dict = {}
    with open("data/currentContainers.csv", encoding="utf-8-sig") as containers:
        data = csv.reader(containers, delimiter=",")
        next(data)
        for row in data:
            position = row[3]
            position = get_pos(position)
            container_dict[row[1]] = position
    return container_dict

# functions that creates fictional wagons
def get_wagons():
    return {"a": [10,0], "b": [20,0], "c": [30,0], "d": [40,0]}

# calculates the distance to the closest wagon for every container
def calculate_distances(containers, wagons):
    distances = {}
    for key in containers.keys():
        position = containers[key]
        dist_list = []
        for wagon in wagons.keys():
            dist_list.append((wagon, getTravelDistance(position, wagons[wagon])))
        distances[key] = min(dist_list, key= lambda t: t[1])
    return distances

#containers_data = get_containers()
#wagons_data = get_wagons()
#print(calculate_distances(containers_data, wagons_data))

# Sets the location of the wagon takes a list of all the containers in the train
def set_location(wagons):
    len = 0
    y_val = 0
    result = []
    for wagon in wagons:
        if (len + wagon.length) < 320:
            wagon.position = [math.ceil((len + 0.5 * wagon.length)/6.1), y_val]
            len += wagon.length
        else:
            len = 0
            y_val = -1
            wagon.position = [math.ceil((len + 0.5 * wagon.length)/6/1), y_val]
            len += wagon.length
        result.append(wagon)
    return result

containers_data = get_containers()
wagons_data = get_wagons()
print(calculate_distances(containers_data, wagons_data))

# create a list of all containers
containers = get_containers_1()

# create a list of all wagons
wagons = get_wagons_1()

