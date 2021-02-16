import csv as csv
from functions import getTravelDistance
from model.Container import Container
from model.Wagon import Wagon

def get_containers_1():
    containers = []
    with open("data/trein1/loading_container.csv", encoding="utf-8-sig") as container_file:
        data = csv.reader(container_file, delimiter=",")
        for row in data:
            c_id = row[0]
            c_teu = int(row[1])
            c_type = row[2]
            gross_weight = row[3]
            net_weight = row[4]
            c_pos = get_pos(row[5])
            c_good = row[7]
            container = Container(c_id, gross_weight, net_weight, c_teu * 20, c_pos, c_good, 1, c_type)
            containers.append(container)
    return containers

def get_wagons_1():
    wagons = []
    with open("data/trein1/wagonlijst.csv", encoding="utf-8-sig") as wagon_file:
        data = csv.reader(wagon_file, delimiter=";")
        for i in range(11):
            next(data)
        for row in data:
            w_id = row[1]
            w_type = row[2]
            w_length = row[3]
            w_axes = row[4]
            wagon = Wagon(w_id, -1, w_length, -1, -1)
            wagons.append(wagon)
    return wagons

def get_pos(position):
    position = position.split(" ")
    position = position[0].split(".")

    try:
        return [int(x) for x in position]
    except ValueError:
        return position

def get_containers():
    container_dict = {}
    with open("data/currentContainers.csv", encoding="utf-8-sig") as containers:
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


print(get_wagons_1())

#containers = get_containers_1()
#for container in containers:
#    print(container.get_position())

#containers_data = get_containers()
#wagons_data = get_wagons()
#print(calculate_distances(containers_data, wagons_data))