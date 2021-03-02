import csv as csv
import math
import tkinter as tk
import pandas as pd
from tkinter import filedialog
from functions import getTravelDistance
from model.Train import Train
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
            w_pos = int(row[0])
            w_id = row[1]
            w_type = row[2]
            w_length = float(row[3].replace(",", "."))
            w_axes = int(row[4])
            # create object
            wagon = Wagon(w_id, -1, w_length, -1, w_pos)
            # add object to wagon list
            wagons.append(wagon)
    # set the proper location for every wagon
    wagons = set_location(wagons)
    return wagons

# get all the wagons based on a file uploaded by the user
def get_containers_prompt():
    containers = []

    # get the desired file
    path = filedialog.askopenfilename()
    tk.Tk().withdraw()

    print("Chosen container file: ", path)

    # if the file is an excel file, we will convert it to .csv and save it.
    if path.endswith(".xls") or path.endswith(".xlsx") or path.endswith(".xlsm") or path.endswith(".xlsb"):
        path = convert_csv(path)

    # open file
    with open(path, encoding="utf-8-sig") as container_file:
        data = csv.reader(container_file, delimiter=";")
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

# get all the wagons based on a file uploaded by the user
def get_wagons_prompt(reverse):
    wagons = []
    
    # get the desired file
    path = filedialog.askopenfilename()
    tk.Tk().withdraw()

    print("Chosen wagon file: ", path)
    
    # if the file is an excel file, we will convert it to .csv and save it.
    if path.endswith(".xls") or path.endswith(".xlsx") or path.endswith(".xlsm") or path.endswith(".xlsb"):
        path = convert_csv(path)

    # open file
    with open(path, encoding="utf-8") as wagon_file:
        data = csv.reader(wagon_file, delimiter=";")
        #skip first 10 rows, because they contain different data
        for i in range(11):
            next(data)
        for row in data:
            # initialize variables
            w_pos = int(row[0])
            w_id = row[1]
            w_type = row[2]
            w_length = float(row[3].replace(",", "."))
            w_axes = int(row[4])
            # create object
            wagon = Wagon(w_id, -1, w_length, -1, w_pos)
            # add object to wagon list
            wagons.append(wagon)
    
    if reverse:
        wagons.reverse()
        for i, wagon in enumerate(wagons):
            wagon.position = i + 1

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

# does almost the same as calculate_distances, but this time it works for the real data.
def calculate_distances_1(containers, wagons):
    distances = {}
    for container in containers:
        c_location = container.get_position()
        if (len(c_location) == 3) and (c_location[0] <= 52) and (c_location[1] <= 7):
            dist_list = []
            for wagon in wagons:
                w_location = wagon.get_location()
                dist_list.append((wagon.wagonID, getTravelDistance(c_location, w_location)))
            distances[container.get_containerID()] = min(dist_list, key= lambda t: t[1])
            #distances[container.get_containerID()] = dist_list
        else:
            distances[container.get_containerID()] = "Container not located at track"
    return distances

# functions that creates fictional wagons
def get_wagons():
    return {"a": [10,0], "b": [20,0], "c": [30,0], "d": [40,0]}

# uses get_wagons_1() to create a train object
def create_train():
    return Train(get_wagons_1())


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
    xlen = 0
    y_val = 0
    result = []
    for wagon in wagons:

        if (xlen + wagon.length_capacity) < 320:
            wagon.location = [math.ceil((xlen + 0.5 * wagon.length_capacity)/6.1), y_val]
            xlen += wagon.length_capacity

        else:
            xlen = 0
            y_val = -1
            wagon.location = [math.ceil((xlen + 0.5 * wagon.length_capacity)/6/1), y_val]
            xlen += wagon.length_capacity

        result.append(wagon)
# See where the last wagon in located to calculate the shift the 2nd row of wagons hast to make
    shift_wagon = wagons[len(wagons)-1]
    shift_wagon_xloc = shift_wagon.location[0]
    shift_wagon_length = shift_wagon.length_capacity
    x_shift = (52 - math.ceil(shift_wagon_length / 2 / 6.1)) - shift_wagon_xloc

    for wagon in wagons:
        if wagon.location[1] == -1:
            wagon.location[0] += x_shift


    return result

# converts the file located at 'path' to a csv file.
# === REQUIRES pip install openpyxl ===
def convert_csv(path):
    xls_file = pd.read_excel(path)
    path = filedialog.asksaveasfilename(defaultextension='.csv')
    xls_file.to_csv(path, index = None, header=True, sep=";")
    return path

# asks the user if the wagon set is reversed.
def is_reversed():
    while True:
        reverse = input("Is the wagonset reversed? (y/n): ")
        if reverse.lower() == "y" or reverse.lower == "yes":
            return True
        elif reverse.lower() == "n" or reverse.lower == "no":
            return False
        else:
            print("Wrong argument, type \"y\" or \"n\".")

# This only gets executed if you run python getContainersFromCSV.py
# So if you run a file that uses this file, then it won't get executed
if __name__ == '__main__':

    # checks if the wagon set is reversed
    reverse = is_reversed()

    # fake data
    #containers = get_containers()
    #wagons = get_wagons()

    # train 1 data
    containers = get_containers_1()
    wagons = get_wagons_1()

    # data with prompt file
    #containers = get_containers_prompt()

    #for container in containers:
    #    print(container.__repr__())

    #wagons = get_wagons_prompt(reverse)
    for container in containers:
        print(container.__repr__())

    for wagon in wagons:
        print(wagon.__repr__())
    
    print(calculate_distances_1(containers, wagons))
    
    #print(calculate_distances_1(containers, wagons))