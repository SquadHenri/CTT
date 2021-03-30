import itertools as it
import math
import json
from statistics import mean
import matplotlib.pyplot as plt

import math
import random
import numpy as np
import json
import pandas as pd
from datetime import date, datetime


# OR-TOOLS
from ortools.sat.python import cp_model
import collections
import math as math
from timeit import default_timer as timer


# Our files
from numpy.lib.function_base import place
import pandas


class Color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'


class Container():
    def __init__(self, containerID, gross_weight, net_weight, foot, position, goods, priority, typeid, hazard_class):
        self.containerID = containerID # name of the container
        self.gross_weight = gross_weight # weight of the container and the goods in kg
        self.foot = foot # length of the contianer in Foot
        self.position = self.calc_pos(position) # position of the container (on the dock or train)
        self.goods = goods # What is in the container (used for dangerous goods)
        self.priority = priority # ctt does not set a priority so this might be left unused
        self.net_weight = net_weight # Weight of the goods without the container (do not use this)
        self.typeid = typeid # Type of the container (len in feet and a letter combo)
        self.hazard_class = hazard_class # None means it is not hazardous, 1,2,3 means it is


    def __str__(self):
        return f'Container {self.containerID},'\
             f' priority: {self.priority}, gross_weight: {self.gross_weight}, foot: {self.foot}, position: {self.position}'

    def __repr__(self):
        return f'Container {self.containerID}, '\
                f'priority: {self.priority}, gross_weight: {self.gross_weight}, '\
                f'foot: {self.foot}, position: {self.position}, goods: {self.goods},'\
                f'net_weight: {self.net_weight}, typeid: {self.typeid}'

    def to_JSON(self):
        container_dict = {}
        container_dict["container_id"] = self.get_containerID()
        container_dict["gross_weight"] = self.get_gross_weight()
        container_dict["length"] = self.get_length()
        container_dict["hazard_class"] = self.get_hazard_class()
        return container_dict

    # Transform the position of the container into a list with coordinates.
    def calc_pos(self, position):
        if position is None:
            return []
        position = position.split(" ")
        position = position[0].split(".")

        try:
            return [int(x) for x in position]
        except ValueError:
            return position

    def get_travel_distance(c_cord, w_cord):

        # factorize the difference in length of x and y
        x_fact = 6.5
        y_fact = 3

        # calculate the distance over the x-axis between a container and a wagon
        x_dist = (c_cord[0] - w_cord[0]) * x_fact
        # calculate the distance over the y-axis between a container and a wagon
        y_dist = (c_cord[1] - w_cord[1]) * y_fact

        # calculate the distance using Pythagoras
        dist = math.sqrt(math.pow(x_dist, 2) + math.pow(y_dist, 2))

        return dist

    # Getter for container position coordinates
    # Container ID used to identify the container at hand
    def get_containerID(self):
        return self.containerID

    # The weight of the container excluding the container itself
    def get_net_weight(self):
        return self.net_weight

    # The weight of the container including the container itself
    def get_gross_weight(self):
        return self.gross_weight    

    # The Length of the container in Foot,
    # This is done in foot since some containers have a length that is different from 1 or 1,5
    def get_length(self):
        return self.foot

    # The type of goods that is in the container
    def get_goods(self):
        return self.goods

    # The Position of the container 
    def get_position(self):
        return self.position

    # if the priority of a container is higher than normal this will differ from 1
    def get_priority(self):
        return self.priority

    # The type of the container
    def get_type(self):
        return self.typeid

    # The hazard class of this container, an int that is of value
    # 1,2,3 for the hazard classes, or None if is not hazardous
    def get_hazard_class(self):
        return self.hazard_class

    def set_hazard_class(self, value):
        self.hazard_class = value




class Wagon():

    """
        A class used to represent a Wagon

        Parameters
        ----------
        wagonID : str
            The id of the wagon from the database
        weight_capacity: int(Kilogram)
            The total container weight the wagon can handle in KG
        length_capacity: int(Feet)
            The total length of containers that can fit on the wagon. in Feet. 
        total_length: int(TEU?)
            The total length of the wagon in TEU
        contents: int(what represents what?)
            The hazard class of the wagon. Is this even used?
        position: int(?)
            The placement in the train. Is this even used?
        location: list of two ints. [x,y]. 
            The location of the wagon in the loading bay. Should this not be a tuple?
        number_of_axles: int
            The number of axles on this train
        containers: list of Containers
            In order, each container is a container placed on the wagon. The solution of the train 
            algorithm should return a train object where the wagon has a list of containers similar to the solution
        
    """

    def __init__(self, wagonID, weight_capacity, length_capacity, contents, position, number_of_axles, total_length, wagon_weight, call, containers = None, max_axle_load = None):
        self.wagonID = wagonID 
        self.weight_capacity = weight_capacity 
        self.length_capacity = length_capacity
        self.total_length = total_length 
        self.slots = [[0 for i in range(0,int(total_length * 20))]] 
        #self.slots = [[0 for i in range(int(length_capacity * 2))]]
        self.contents = contents 
        self.position = position
        self.call = call  
        self.location = None 
        self.number_of_axles = number_of_axles
        self.wagon_weight = wagon_weight
        self.is_copy = False
        self.wagon_dictionairy = self.get_wagon_dictionairy()

        # Can be None
        self.containers = containers
        # Maximum aslast
        if max_axle_load:
            self.max_axle_load = max_axle_load
        else:
            self.max_axle_load = 22000

    # Convert Wagon to string
    # Print relevant information only, __repr__ is used to print every detail
    def __str__(self):
        return f'Wagon {self.wagonID}, weight capacity: {self.weight_capacity}, '\
             f'length capacity: {self.length_capacity}, position: {self.position}, location: {self.location}'

    # prints all values from the wagon
    def __repr__(self):
        return f'Wagon {self.wagonID}, weight capacity: {self.weight_capacity}, '\
             f'length_capacity: {self.length_capacity}, contents: {self.contents}, '\
             f'position: {self.position}, location: {self.location}'

    # Prints relevant wagon information for the solution, expects self.containers to be filled'
    # Returns the weight, length and travel distance of the containers
    def print_solution(self):
        if not self.containers:
            print(self)
            print("\t\tWagon does not have containers")
            return
        # Print information on the wagon
        print(self)
        offset = 0
        for container in self.containers:
            print(offset, '-', offset+container.get_length(),':\t', container)
            offset += container.get_length()
        
    def get_wagon_dictionairy(self):
        dictionairy_json_string = """{
                                        "404": {
                                            "lenght": 40,
                                            "nr of axles": 4,
                                            "shift dist(m)": 2.15,
                                            "axle dist": 8.07
                                        },
                                        "474": {
                                            "lenght": 47,
                                            "nr of axles": 4,
                                            "shift dist(m)": 2.1,
                                            "axle dist": 10.2
                                        },
                                        "604": {
                                            "lenght": 60,
                                            "nr of axles": 4,
                                            "shift dist(m)": 2.1,
                                            "axle dist": 14.2
                                        },
                                        "804": {
                                            "lenght": 80,
                                            "nr of axles": 4,
                                            "shift dist(m)": 2.7,
                                            "axle dist": 19.3
                                        },
                                        "806": {
                                            "lenght": 80,
                                            "nr of axles": 6,
                                            "shift dist(m)": 2.18,
                                            "axle dist": 10.395
                                        },
                                        "906": {
                                            "lenght": 90,
                                            "nr of axles": 6,
                                            "shift dist(m)": 2.18,
                                            "axle dist": 11.995
                                        },
                                        "908": {
                                            "lenght": 90,
                                            "nr of axles": 8,
                                            "shift dist(m)": 2.43,
                                            "axle dist": 11.985
                                        },
                                        "1046": {
                                            "lenght": 104,
                                            "nr of axles": 6,
                                            "shift dist(m)": 2.28,
                                            "axle dist": 14.2
                                        },
                                        "1048": {
                                            "lenght": 104,
                                            "nr of axles": 8,
                                            "shift dist(m)": 2.3,
                                            "axle dist": 13.08
                                        },
                                        "1068": {
                                            "lenght": 106,
                                            "nr of axles": 8,
                                            "shift dist(m)": 2.3,
                                            "axle dist": 13.5
                                        }
                                        }"""

        dictionairy = json.loads(dictionairy_json_string)
        return dictionairy

    def to_JSON(self):
        wagon_dict = {}
        wagon_dict["wagon_id"] = self.wagonID
        wagon_dict["weight_capacity"] = self.get_weight_capacity()
        wagon_dict["length_capacity"] = self.get_length_capacity()
        wagon_dict["position"] = self.get_position()
        wagon_dict["containers"] = []
        if not self.containers:
            return wagon_dict
        else:
            for container in self.get_containers():
                container_json = container.to_JSON()
                wagon_dict["containers"].append(container_json)
            return wagon_dict


    # CONSTRAINTS

    # The weight of the containers cannot exceed the weight capacity of the wagon
    def c_weight_capacity(self, containers, x, w_j):
        return sum(x[(c_i, w_j)] * container.get_gross_weight()
                for c_i, container in enumerate(containers)) <= self.get_weight_capacity()

    # The length of the containers cannot exceed the length capacity of the wagon
    def c_length_capacity(self, containers, x, w_j):
        return sum(x[(c_i, w_j)] * container.get_length()
                for c_i, container in enumerate(containers)) <= self.get_length_capacity()  


    # Input for this funciton is the wagon and a list with the containers. The list of containers contains the container and the spots it takes in the wagon
    def get_axle_load(self, containers):
        # Set the weight of the wagon to wagon only to add the weight of the containers later
        total_load = self.wagon_weight
        # Refining the list of containers so it contains the container and the mean of the slots it stands on ordered from left to right (not that that stil matters).
        fillrate = 0
        hinge_splittable = False
        containerList = []
        for container in containers:
            containerList.append([container, container.get_length() / 2 + fillrate]) # containers , position of container on wagon
            fillrate += container.get_length()
            total_load += container.get_gross_weight()
            if fillrate == (self.length_capacity / 2):
                hinge_splittable = True
        key = str(self.length_capacity).split('.')[0] + str(self.number_of_axles).split('.')[0]
        dictionairy = self.wagon_dictionairy
    
        axleshift = dictionairy[key]['shift dist(m)']
        axledist = dictionairy[key]['axle dist']




        # Starting with all the Wagons that have 2 bogies and so have 4 axles
        if self.number_of_axles == 4:
            left_axle_load = 0.5 * self.wagon_weight
            # Adding the containers to the load on the Right bogie
            for container in containerList:
                dist = container[1] * 0.3048 - float(axleshift)
                left_axle_load += self.container_load(container[0].gross_weight, dist, axledist)
            # calculating the left axle by taking the total and subtracting the load on the right axle
            right_axle_load = total_load - left_axle_load
            # Returning the data: left axle, right axle, total load
            return [left_axle_load / 2, right_axle_load / 2], total_load
        # Setting The right numbers for the wagons with 3 bogies
        elif self.number_of_axles == 6:
            if hinge_splittable:
                middle = axleshift + axledist
                # Setting the basic load on the axles to add the containers later, given the load is equal on all bogies
                left_axle_load = right_axle_load = self.wagon_weight / 3
                # Adding the weight of the containers
                for container in containerList: # splitting the train to calculate load on different parts
                    if container[1] < (self.length_capacity / 2):
                        dist = middle - container[1] * 0.3048
                        left_axle_load += self.container_load(container[0].gross_weight, dist, axledist)
                    else:
                        dist = container[1] * 0.3048 - middle
                        right_axle_load += self.container_load(container[0].gross_weight, dist, axledist)
                    middle_axle_load = total_load - right_axle_load - left_axle_load
                return [left_axle_load / 2, middle_axle_load / 2, right_axle_load / 2], total_load
            else:
                return [200000, 200000, 200000], 0
        elif self.number_of_axles == 8:
            if hinge_splittable:
                # define middle
                middle = axleshift + axledist
                # setting the basic load over the axles (assumption: all load is devided equally)
                right_axle_load = right_axle1_load = self.wagon_weight / 4
                for container in containerList: # splitting front and back to find relative load
                    if container[1] < self.length_capacity / 2:
                        dist = container[1] * 0.3048 - axleshift
                        right_axle_load += self.container_load(container[0].gross_weight, dist, axledist)
                    else:
                        dist = container[1] * 0.3048 - (axleshift + middle)
                        right_axle1_load += self.container_load(container[0].gross_weight, dist, axledist)
                    axle_1 = total_load / 2 - right_axle_load
                    axle_3 = total_load / 2 - right_axle1_load
                return [axle_1 / 2, right_axle_load / 2, axle_3 / 2, right_axle1_load / 2], total_load
            else:
                return [200000, 200000, 200000], 0
        else:
            print('this is a very weird wagon')
            return []

    def container_load(self, weight, dist, axledist):
        load = weight * dist / axledist
        return load         

    def get_axle_load_cp(self, containers):
        res = ""
        for container in containers:
            res += f'({container.get_containerID()})'
        print(res)
        axle_load, _ = self.get_axle_load(containers)
        for i in range(len(axle_load)):
            axle_load[i] = int(axle_load[i])
        print(axle_load)
        return axle_load
        

    # Sets the optimal axle load by reordering self.containers
    # Returns False if it does not find one. Which should not happen if
    # the constraint c_has_acceptable_axle_load is active and working correctly
    def set_optimal_axle_load(self):
        if(self.containers is None):
            print("The wagon is empty, so axile load is fine.")
            return True

        axle_load_score = math.inf
        axle_best_found_permutation = []
        
        #occupied_weight = self.wagon_weight_load()
        # occupied_length = self.wagon_length_load()
        # dummy_container1 = None
        # dummy_container2 = None
        # container_copy = self.containers
        
        # if self.length_capacity - occupied_length > 0:
        #     empty_length = self.length_capacity - occupied_length
        #     dummy_length = math.floor(empty_length/2)
        #     dummy_container1 = Container("", 0, -1, dummy_length, None, None, None, None, None)
        #     dummy_container2 = Container("", 0, -1, dummy_length, None, None, None, None, None)
        #     container_copy.append(dummy_container1)
        #     container_copy.append(dummy_container2)

        

        for i, container_list in enumerate(it.permutations(self.containers)):
            axle_load, _ = self.get_axle_load(container_list)
            # print(self.get_axle_load(combination))
            container_list = list(container_list)
            # Get score and update best_found if better
            if(max(axle_load) < axle_load_score):
                axle_best_found_permutation = container_list
                axle_load_score = max(axle_load)

        # print("Wagon:", self.wagonID, "Axle Load:", axle_load_score)
        print("Wagon", self.wagonID, "max load: ", axle_load_score)
        if axle_load_score < 22500:

            # If dummy_container1 is in there, dummy_container2 is also there
            # if dummy_container1 in axle_best_found_permutation:
            #     axle_best_found_permutation.remove(dummy_container1)
            #     axle_best_found_permutation.remove(dummy_container2)
                

            self.containers = axle_best_found_permutation
            return True
            
        return False

    def add_dummies(self):
        if(self.containers is None):
            print("The wagon is empty, so axile load is fine.")
            pass
    
        occupied_weight = self.wagon_weight_load()
        occupied_length = self.wagon_length_load()
        dummy_container1 = None
        dummy_container2 = None
        container_copy = self.containers
        
        if self.length_capacity - occupied_length > 0:
            empty_length = self.length_capacity - occupied_length
            dummy_length = round((empty_length/2), 1)
            dummy_container1 = Container("", 0, -1, dummy_length, None, None, None, None, None)
            dummy_container2 = Container("", 0, -1, dummy_length, None, None, None, None, None)
            container_copy.append(dummy_container1)
            container_copy.append(dummy_container2)

        self.containers = container_copy
        

    def wagon_weight_load(self):
        if(self.containers is None):
            return 0
        load = 0
        for container in self.containers:
            load += container.get_gross_weight()
        return load
    
    def wagon_length_load(self):
        if(self.containers is None):
            return 0
        load = 0
        for container in self.containers:
            if container.get_gross_weight() != 0:
                load += container.get_length()
        return load
    
    def wagon_travel_distance(self):
        if(self.containers is None):
            return 0
        travel_distance = 0
        for container in self.containers:
            if (len(container.get_position()) == 3) and (container.get_position()[0] <= 52) and (container.get_position()[1] <= 7):
                travel_distance += Container.get_travel_distance(container.get_position(), self.get_location())
        return travel_distance


    # Getters
    def get_position(self):
        return self.position

    def get_weight_capacity(self):
        return self.weight_capacity

    def get_length_capacity(self):
        return self.length_capacity

    def get_total_length(self):
        return self.total_length

    def get_contents(self):
        return self.contents

    def get_location(self):
        return self.location

    def get_slots(self):
        return self.slots

    def get_containers(self):
        return self.containers
    
    def get_number_of_axles(self):
        return self.number_of_axles
    
    def get_wagon_weight(self):
        return self.wagon_weight
    
    # Setters
    
    def set_length_capacity(self, length_capacity):
        self.length_capacity = length_capacity

    def set_weight_capacity(self, weight_capacity):
        self.weight_capacity = weight_capacity
    
    def set_containers(self, containers):
        self.containers = containers

    # Used to add one or multiple containers
    def add_container(self, container):
        if self.containers:
            self.containers.append(container)
        else:
            self.containers = []
            self.containers.append(container)



    # UNUSED/UNFINISHED CONSTRAINTS
    
    # # Constraint that a container has to be put on the wagon as a whole
    # # y is the variable used in TrainLoadingX.py
    # # w_j is the index of the wagon
    # # TODO If people can optimize this, go ahead. This function will be called very often
    # def c_container_is_whole(self, y, num_containers, w_j):
    #     # Create a dictionairy of all containers c_i and the slots
    #     # They occupy in the wagon
    #     containers = {}
    #     for c_i in range(num_containers):
    #         for s_k in range(len(self.slots)):
    #             if(y[(c_i, w_j, s_k)] == 1):
    #                 if(c_i in containers):
    #                     containers[c_i].append(s_k)
    #                 else:
    #                     containers[c_i] = [s_k]
    #     # Now check for each container if the slots they occupy are in order
    #     for c_i in containers:
    #         containers[c_i].sort()
    #         # Since the list is ordered, the following means the container is ordered
    #         return containers[c_i][-1] - containers[c_i][0] == len(containers[c_i]) - 1

   
    # Possible constraint for the axle load
    # The function self.calculateLoad calculcates the axle load based on a container list, we still need to make this.
    # @TODO make calculateLoad function
    # def c_axle_load(self, y, containers, w_j):
    #     containers_on_wagon = []
    #     for c_i, container in enumerate(containers):
    #         for s_k in range(len(self.slots)):
    #             if y[(c_i, w_j, s_k)] == 1:
    #                 containers_on_wagon.append((container, s_k))
    #     return self.calculateLoad(containers_on_wagon, maxLoad) 



class Train():

    
    # wagons should be a list of wagons
    def __init__(self, wagons, containers, wrong_wagons, split, isReversed, max_traveldistance):
        self.wagons = wagons # This is the list of all the wagons on the train
        self.wrong_wagons = wrong_wagons
        self.maxWeight = 100000000000
        self.containers = containers
        self.split = split
        self.max_traveldistance = max_traveldistance
        self.isReversed = isReversed

        self.set_location()
        self.placed_containers = []
        self.unplaced_containers = []        
    

    # Create some wagons, to use for testing
    def test_train(self):
        wagon1 = Wagon(0, 100, 5, None, [0,0])
        wagon2 = Wagon(1, 110, 7, None, [0,1])
        wagon3 = Wagon(2, 130, 6, None, [1,0])
        wagon4 = Wagon(3, 150, 9, None, [1,0])
        wagon5 = Wagon(4, 140, 8, None, [0,2])
        return Train([wagon1, wagon2, wagon3, wagon4, wagon5])

    # Show the basic information
    def __str__(self):
        return "Train with wagons: \n" + '\n'.join(list(map(str, self.wagons)))
    
    # Show all informatoin
    def __repr__(self):
        return "Train with wagon: \n" + '\n'.join(list(map(repr,self.wagons)))
    
    # Print the wagon values with the containers that filled them
    def print_solution(self):
        total_length_packed = self.get_total_packed_length()
        total_weight_packed = self.get_total_packed_weight()
        total_travel_distance = self.get_total_travel_distance()

        for wagon in self.wagons:
            packed_length = wagon.wagon_length_load()
            packed_weight = wagon.wagon_weight_load()
            travel_distance = wagon.wagon_travel_distance()
            print('Packed wagon weight:', Color.GREEN, packed_weight, Color.END, ' Wagon weight capacity: ', wagon.get_weight_capacity())
            print('Packed wagon length:', Color.GREEN, packed_length, Color.END, ' Wagon length capacity: ', wagon.get_length_capacity())
            print('Wagon travel distance:', travel_distance)
        
        print()
        print('Total packed weight:', total_weight_packed, '(',round(total_weight_packed / self.get_total_weight_capacity() * 100,1),'%)')
        print('Total packed length:', total_length_packed, '(',round(total_length_packed / self.get_total_length_capacity() * 100,1),'%)')
        print('Total distance travelled:', total_travel_distance)



    # Maybe check for success, but this is fine for now
    def set_optimal_axle_load(self):
        success = True
        for wagon in self.wagons:
            if(not wagon.set_optimal_axle_load()):
                #print(wagon.wagonID, "has too much axle load")
                success = False
        return success
            
    def to_JSON(self, **kwargs):
        result = {}
        result["train"] = kwargs
        for wagon in self.wagons:

            wagon_json = wagon.to_JSON()
            result["train"]["wagons"].append(wagon_json)

        with open('data/train.json', 'w') as output:
            json.dump(result, output)
        
    def to_CSV(self):
        data = []
        for wagon in self.wagons:
            if not wagon.containers:
                wagon_dict = {}
                wagon_dict["wagon_id"] = wagon.wagonID
                wagon_dict["weight_capacity"] = wagon.get_weight_capacity()
                wagon_dict["length_capacity"] = wagon.get_length_capacity()
                wagon_dict["position"] = wagon.get_position()
                wagon_dict["container_id"] = None
                wagon_dict["gross_weight"] = None
                wagon_dict["length"] = None
                wagon_dict["hazard_class"] = None
                data.append(wagon_dict)
                continue
            for container in wagon.containers:
                wagon_dict = {}
                wagon_dict["wagon_id"] = wagon.wagonID
                wagon_dict["weight_capacity"] = wagon.get_weight_capacity()
                wagon_dict["length_capacity"] = wagon.get_length_capacity()
                wagon_dict["position"] = wagon.get_position()
                wagon_dict["container_id"] = container.get_containerID()
                wagon_dict["gross_weight"] = container.get_gross_weight()
                wagon_dict["length"] = container.get_length()
                wagon_dict["hazard_class"] = container.get_hazard_class()
                data.append(wagon_dict)
        df = pd.DataFrame(data)
        df.to_excel("planning.xlsx")    
    
    def get_containers(self):
        return self.containers

    def get_split(self):
        return self.split

    def get_max_traveldistance(self):
        return self.max_traveldistance

    def get_reversed_status(self):
        return self.isReversed

    def get_total_packed_length(self):
        length_packed = 0
        for wagon in self.wagons:
            if wagon.containers is None:
                   continue
            length_packed += wagon.wagon_length_load()
        return length_packed

    def get_total_travel_distance(self):
        total_travel_distance = 0
        for wagon in self.wagons:
            total_travel_distance += wagon.wagon_travel_distance()
        return total_travel_distance

    def get_total_packed_weight(self):
        weight_packed = 0
        
        for wagon in self.wagons:
            if wagon.containers is None:
                   return 0
            weight_packed += wagon.wagon_weight_load()
        return weight_packed
    
    def get_total_weight_capacity(self):
        total_weight = 0
        for wagon in self.wagons:
            total_weight += wagon.weight_capacity
        return total_weight

    def get_total_length_capacity(self):
        total_length = 0
        for wagon in self.wagons:
            total_length += wagon.length_capacity
        return total_length
    
    # Returns the list of containers placed on a wagon
    def get_placed_containers(self):
        return self.placed_containers

    def get_unplaced_containers(self):
        return self.unplaced_containers

    def set_placed_containers(self, placed_containers):
        self.placed_containers = placed_containers

    def set_unplaced_containers(self, unplaced_containers):
        self.unplaced_containers = unplaced_containers

    # Set the weight capacities of the wagons to a value between min and max
    def set_random_weight_capacities(self, min, max):
        for wagon in self.wagons:
            wagon.set_weight_capacity(get_random_value(min, max))

    # Same as the functions above, but for setting to 1 value
    def set_weight_capacities(self, value):
        for wagon in self.wagons:
            wagon.set_weight_capacity(value)

    # Set the weight capacities of the wagons to a value between min and max
    def set_random_length_capacities(self, min, max):
        for wagon in self.wagons:
            wagon.set_length_capacity(get_random_value(min, max))

    # Same as the functions above, but for setting to 1 value
    def set_length_capacities(self, value):
        for wagon in self.wagons:
            wagon.set_weight_capacity(value)



    def get_container_plot(self, containers):
        
        #Initiliase lists for input matplotlib table
        data = []
        cellColours = []
        #axs[0].set_title('Table 1: Unplaced containers')
        
        #Set column length for table
        column_length = 3

        #Make datachunks of container list
        containerlist = [containers[x:x+column_length] for x in range(0, len(containers), column_length)]
        
        for containers in containerlist:
            datarow = []
            cellRowColour = []
            #Initialise all cell of the table
            if 0 < column_length:
                datarow.extend('' for x in range(0, column_length))
                data.append(datarow)
                cellRowColour.extend('#fefefe' for x in range(0, column_length)) 
                cellColours.append(cellRowColour)

            #Give value to the table cells
            for i, container in enumerate(containers):
                datarow[i] = 'ID: ' + str(container.get_containerID()) + ' | Type: ' + str(container.get_type()) +  ' | Position: ' + str(container.get_position()) + ' | Gross (kg): ' + str(container.get_gross_weight()) + ' | Container Lenght: ' + str(container.get_length()) 
                if container.hazard_class == 1 or container.hazard_class == 2 or container.hazard_class == 3:
                    cellRowColour[i] = '#11aae1'

        return data, cellColours

    
    # Make a table to that represents a train planning
    def get_planning_plot(self):

        # total_length = total length of containers planned on train.
        # total_weight = total weight of containers planned on tainr.
        total_length = self.get_total_packed_length()
        total_weight = self.get_total_packed_weight()
        
        # The amount of containers of the wagon with the most containers. Starts at 0.
        maxContainers = 0
        # for now, columns = rows
        columns = []
        #Sort wagons on their position
        wagons = self.wagons
        l = len(wagons)
        for i in range(0, l): 
            for j in range(0, l-i-1): 
                if (wagons[j].position > wagons[j + 1].position): 
                    tempo = wagons[j] 
                    wagons[j]= wagons[j + 1] 
                    wagons[j + 1]= tempo 

        #Set max number of containers on wagon, needed for amount of table rows 
        #print(wagons)
        for wagon in wagons:
            
            if wagon.containers is None:
                continue
            
            # If wagon contains more containers than maxContainers, set maxContainers to new amount.
            if len(wagon.containers) > maxContainers:
                maxContainers = len(wagon.containers)
                
        data = []
        cellColours = []
        # Loop through all wagons
        title = wagons[0].call
        for wagon in wagons:           
            #Add wagonID to first cell of the row
            columns.append(str(int(wagon.position))+ ". " + wagon.wagonID + " | " + str(wagon.number_of_axles))
            datarow = []
            cellRowColour = []
        
            # Initialize all cells with "empty" and basic grey color
            if 0 < maxContainers: 
                # We do maxContainers + 2, since we want to add two more columns that contain information.
                datarow.extend('' for x in range(0, maxContainers + 2))
                cellRowColour.extend('#fefefe' for x in range(0, maxContainers + 2)) 
            
            # If the wagon is empty, we set the lengts and weight to 0%
            if wagon.containers is None: 
                datarow[len(datarow) - 2] = "0/" + str(wagon.get_weight_capacity()).split(".")[0] + " (0%)"
                datarow[len(datarow) - 1] = "0/" + str(wagon.get_length_capacity()).split(".")[0] + " (0%)"  
                data.append(datarow)
                cellColours.append(cellRowColour) 
                continue

            wagon_weight = wagon.wagon_weight_load()
            wagon_length = wagon.wagon_length_load()
            # Place all containers in the cells
            for i, container in enumerate(wagon.containers):
                #wagon_weight += container.get_gross_weight()
                #wagon_length += container.get_length()
                datarow[i] = container.containerID + " (" + str(container.get_length() / 20) + ") " + str(int(container.get_gross_weight() / 1000))
                # orange #ff6153
                # dark green #498499
                if str(container.hazard_class).startswith("1") or str(container.hazard_class).startswith("2") or str(container.hazard_class).startswith("3"):
                    cellRowColour[i] = '#11aae1'

            # Calculate the packed weight and length of a wagon.
            weight_perc = round((wagon_weight/wagon.get_weight_capacity()) * 100, 1)
            length_perc = round((wagon_length/wagon.get_length_capacity()) * 100, 1)

            # Set the final two columns to the packed weight and packed length
            datarow[len(datarow) - 2] = str(wagon_weight) + "/" + str(wagon.get_weight_capacity()).split(".")[0] + " ("+str(weight_perc)+ "%)"
            datarow[len(datarow) - 1] = str(wagon_length) + "/" + str(wagon.get_length_capacity()).split(".")[0] + " ("+str(length_perc)+ "%)"

            # If 90% of the weight is used, make the column red.
            if weight_perc > 90:
                cellRowColour[maxContainers] = '#ff6153'

            # Add the row for this wagon to the list of all rows.
            cellColours.append(cellRowColour)
            data.append(datarow)
        
        # Add a final row, that is called Total, that contains the total weight and length of the train.
        datarow = []
        cellRowColour = []
        columns.append("Total")
        datarow.extend('' for x in range(0, maxContainers + 2))
        cellRowColour.extend('#fefefe' for x in range(0, maxContainers + 2)) 
        datarow[len(datarow) - 2] = str(total_weight) + "/" + str(self.get_total_weight_capacity()).split(".")[0] + " ("+str(round((total_weight/self.get_total_weight_capacity()) * 100, 1))+ " %)"
        datarow[len(datarow) - 1] = str(total_length) + "/" + str(self.get_total_length_capacity()).split(".")[0] + " ("+str(round((total_length/self.get_total_length_capacity()) * 100, 1))+ " %)"
        cellColours.append(cellRowColour)
        data.append(datarow)

        # Set the column titles to slot x, and the last two to Wagon Weight and Wagon Length
        n_rows = len(data)
        rows = ['slot %d' % (x+1) for x in range(len(data))]
        rows[maxContainers] = "Wagon Weight"
        rows[maxContainers + 1] = "Wagon Length"
        
        # Set the text to the cells
        cell_text = []
        for row in range(n_rows):
            cell_text.append(['%s' % (x) for x in data[row]])
        
        # @TODO Find out what .reverse() does.
        cell_text.reverse()
        
        #CTT Green color: #8bc53d
        #CTT Blue color: #11aae1
        rcolors = np.full(n_rows, '#8bc53d')
        ccolors = np.full(n_rows, '#8bc53d')

        return data, columns, rcolors, cellColours, ccolors, rows, title


    #Get plot with unplaced containers table and planning table
    def get_tableplot(self, unplaced_containers):
        
        fig = None
        axs = None        
        planning_table = None
        container_table = None
        title = 'planning'
        unknown_wagonlist = []
        
        #Create a list of wagons with null values to list as footnote of table
        for wagon in self.wrong_wagons:
            unknown_wagonlist.append(str(int(wagon.wagonPosition)) + ". " + wagon.wagonID)

        #Check there are unplaced containers, if yes show in table plot
        if(len(unplaced_containers) > 0): 
            #Create figure and 2 axis to stack to tables
            fig, axs = plt.subplots(2,1)
            #Create container table
            t2data, t2cellColours = self.get_container_plot(unplaced_containers)
            container_table = axs[0].table(cellText=t2data,
                    cellColours=t2cellColours,
                    loc='center')
            #Create planning table
            t1data, t1columns, t1rcolors, t1cellColours, t1ccolors, t1rows, t1title = self.get_planning_plot()
            title = t1title
            planning_table = axs[1].table(cellText=t1data,
                    rowLabels=t1columns,
                    rowColours=t1rcolors,
                    cellColours=t1cellColours,
                    colColours=t1ccolors,
                    colLabels=t1rows,
                    loc='center')
        #If there are no unplaced containers, only show the planning plot and take full space
        else:
            fig, axs = plt.subplots()
            t1data, t1columns, t1rcolors, t1cellColours, t1ccolors, t1rows, t1title = self.get_planning_plot()
            title = t1title
            planning_table = plt.table(cellText=t1data,
                    rowLabels=t1columns,
                    rowColours=t1rcolors,
                    cellColours=t1cellColours,
                    colColours=t1ccolors,
                    colLabels=t1rows,
                    loc='center')

        #Formatting container table
        if container_table is not None:
            container_table.auto_set_font_size(False)
            container_table.set_fontsize(10)
            axs[0].axis('tight')
            axs[0].axis('off')  

        #Formatting planning table
        if planning_table is not None:
            planning_table.auto_set_font_size(False)
            planning_table.set_fontsize(8)
        
        #Plot layout settings
        plt.subplots_adjust(left=0.1, bottom=0.195, right=0.986, top=0.8)
        plt.axis('off')
        
        # If no current figure exists, a new one is created using figure()
        fig = plt.gcf()
        # Figure title including date string: dd/mm/YY H:M:S
        fig.suptitle(title + " on " + datetime.now().strftime("%d/%m/%Y %H:%M:%S \n" 
        + " Reversed: " + str(self.isReversed) 
        + ", Split: " + str(self.split) 
        + ", MaxTravel: " + str(self.max_traveldistance) ), weight='bold', fontsize=12)

        # Display all unknown wagons with null values in the footnote, color: red.
        if len(unknown_wagonlist) > 0:
            plt.figtext(0.8, 0.01, "[WARNING] Missing information for the following wagon(s): \n" + str(unknown_wagonlist),
                horizontalalignment='right',
                size=7,
                weight='bold',
                color='#ff0000'
            )
        else:
            plt.figtext(0.8, 0.01, "The train is split between wagon " + str(int(self.split) - 1) + " and wagon " + str(int(self.split)) + '.',
                horizontalalignment='right',
                size=7,
                weight='light',
                color='#000'
            )
        
        #Save figure as png image
        # Month abbreviation, day and year	
        currentdate = date.today().strftime("%b-%d-%Y")
        plt.savefig(title + '-planning-' + currentdate, bbox_inches='tight', dpi=150)
        return plt
        
    # Sets the location of the wagon takes a list of all the containers in the train
    def set_location(self):
                
        xlen = 0
        y_val = 0
        result = []

        if len(self.wagons) == 0:
            raise TypeError("No wagons")

        for wagon in self.wagons:
            if self.split != None:


                if wagon.position < self.split:
                    wagon.location = [math.ceil((xlen + 0.5 * wagon.total_length)/6.1), y_val]
                    xlen += wagon.total_length
                    if wagon.location[1] == 0:
                        splitshift = wagon
                
                elif wagon.position == self.split:
                    xlen = 0
                    #self.split = 100
                    y_val = -1
                    wagon.location = [math.ceil((xlen + 0.5 * wagon.total_length)/6.1), y_val]
                    xlen += wagon.total_length
                else:
                    wagon.location = [math.ceil((xlen + 0.5 * wagon.total_length)/6.1), y_val]
                    xlen += wagon.total_length

            else:
                if (xlen + wagon.total_length) < 320:
                    wagon.location = [math.ceil((xlen + 0.5 * wagon.total_length)/6.1), y_val]
                    xlen += wagon.total_length

                else:
                    xlen = 0
                    y_val = -1
                    wagon.location = [math.ceil((xlen + 0.5 * wagon.total_length)/6.1), y_val]
                    xlen += wagon.total_length

            result.append(wagon)
    # See where the last wagon in located to calculate the shift the 2nd row of wagons hast to make

        shift_wagon = splitshift
        shift_wagon_xloc = shift_wagon.location[0]
        shift_wagon_length = shift_wagon.total_length
        x_shift = (52 - math.ceil(shift_wagon_length / 2 / 6.1)) - shift_wagon_xloc

        for wagon in self.wagons:
            if wagon.location[1] == 0:
                wagon.location[0] += x_shift

        shift_wagon = self.wagons[len(self.wagons)-1]
        shift_wagon_xloc = shift_wagon.location[0]
        shift_wagon_length = shift_wagon.total_length
        x_shift = (52 - math.ceil(shift_wagon_length / 2 / 6.1)) - shift_wagon_xloc

        for wagon in self.wagons:
            if wagon.location[1] == -1:
                wagon.location[0] += x_shift

        return result


def main(train, objective_value_limit = None):
    testing = False
    start = timer()
    containers = train.get_containers()
    # Define the cp model
    model = cp_model.CpModel()
    priority_list = []

    # Set some random containers to be in the priority list.
    if testing:
        for i in range(0, len(containers), 10):
            priority_list.append(i)
        ("These containers are in the priority list:", priority_list)
    
    # Make every nth container hazardous
    if testing:
        n = 7
        for i in range(0, len(containers), n):
            containers[i].set_hazard_class(1)
        print("These containers are hazardous:", [i for i, container in enumerate(containers) if(container.get_hazard_class() is not None and container.get_hazard_class() > 0)])


    # Split wagons that have a mid bogie
    wagon_list = []
    for wagon in train.wagons:
        if wagon.number_of_axles > 4:
            wagonA = Wagon(wagon.wagonID, wagon.weight_capacity, wagon.length_capacity * 0.5, wagon.contents, wagon.position, wagon.number_of_axles, wagon.total_length, wagon.wagon_weight, wagon.call)
            wagonB = Wagon(wagon.wagonID, wagon.weight_capacity, wagon.length_capacity * 0.5, wagon.contents, wagon.position, wagon.number_of_axles, wagon.total_length, wagon.wagon_weight, wagon.call)

            wagonA.is_copy = True
            wagonA.location = wagon.location
            wagonB.is_copy = True
            wagonB.location = wagon.location

            wagon_list.append(wagonA)
            wagon_list.append(wagonB)
            # print("A", wagonA)
            # print("B", wagonB)
        else:
            wagon_list.append(wagon)


    
    for wagon in wagon_list:
        print(wagon)
    
    train.wagons = wagon_list
    """
                VARIABLES
    """

    #region variables

    # x[c_i, w_j] = 1 if container c_i is packed in wagon w_j
    x = {}
    for c_i, _ in enumerate(containers):    
        for w_j, wagon in enumerate(train.wagons):
            x[(c_i,w_j)] = model.NewIntVar(0, 1, 'cont:%i,wagon%i' % (c_i, w_j))
    
    # This value of this is: spreadContainers == (len(containers) > len(train.wagons))
    # This is added as a constraint
    spreadContainers = model.NewBoolVar('spreadContainers')

    container_positions = {}
    for c_i, _ in enumerate(containers):
        # Assume maximum number of positions is 5
        # Might need to calculate/change this depending on the wagon
        container_positions[c_i] = model.NewIntVar(0, 5, 'container_pos(c_i:%i)' % c_i)

    # y = {}
    # for w_j, wagon in enumerate(train.wagons):
    #     y[(w_j)] = model.NewIntervalVar(0, wagon.get_total_length(), wagon.get_total_length(), 'wagon_slot_%i' % (w_j))


    # w_slot = {}
    # for w_j, wagon in enumerate(train.wagons):
    #     w_slot[(w_j)] = model.NewIntervalVar(0, int(wagon.get_total_length()), int(wagon.get_total_length()), 'wagon_%i' % w_j)

    # c_start = {}
    # for c_i, container in enumerate(containers):
    #     c_start[(c_i)] = model.NewIntVar(0, 10, 'c_start_%i' % c_i)

    #endregion 

    """
                CONSTRAINTS
    """

    #region train-wagon-constraints

    # Each container can be in at most one wagon.
    for c_i, container in enumerate(containers):
        if container not in priority_list:
            model.Add(
                sum(x[(c_i, w_j)] for w_j, _ in enumerate(train.wagons)) <= 1
                )
     # All containers in the priority list need to be loaded on the train, no matter what.
    for c_i in priority_list:
        model.Add(sum(x[(c_i,w_j)] for w_j, _ in enumerate(train.wagons)) == 1)

    # Each wagon has at least one container
    # Only enforce if there are enough containers
    model.Add( 
        spreadContainers == (len(containers) > len(train.wagons)) # Check if there are enough containers to spread them out over wagons
        )
    for w_j, _ in enumerate(train.wagons):
        model.Add(
            sum(x[(c_i, w_j)] for c_i, _ in enumerate(containers)) >= 1 # Each wagon has at least one container
        ).OnlyEnforceIf(spreadContainers)

    # The amount packed in each wagon cannot exceed its weight capacity.
    for w_j, wagon in enumerate(train.wagons):
        model.Add(
            sum(x[(c_i, w_j)] * container.get_gross_weight()
                for c_i, container in enumerate(containers))
                <=
                int(wagon.get_weight_capacity() * 0.85)
        )

    # The length of the containers cannot exceed the length of the wagon
    for w_j, wagon in enumerate(train.wagons):
            model.Add(
                sum(x[(c_i, w_j)] * container.get_length()
                    for c_i, container in enumerate(containers))
                    <=
                    int(wagon.get_length_capacity())
            )

    #Travel distance constraint for total distance.
    model.Add(sum(x[(c_i, w_j)] * int(Container.get_travel_distance(container.get_position(), wagon.get_location()))
                    for c_i, container in enumerate(containers) 
                    for w_j, wagon in enumerate(train.wagons) 
                    if (len(container.get_position()) == 3) and 
                    (container.get_position()[0] <= 52) and 
                    (container.get_position()[1] <= 7) ) <= int(train.get_max_traveldistance()) * 
                        len([container for container in train.containers 
                        if (len(container.get_position()) == 3) and 
                        (container.get_position()[0] <= 52) and 
                        (container.get_position()[1] <= 7)]))

    # A train may not surpass a maximum weight, based on the destination of the train.
    model.Add(sum(x[(c_i, w_j)] * container.get_gross_weight() 
                    for c_i, container in enumerate(containers) 
                    for w_j, wagon in enumerate(train.wagons)) <= train.maxWeight)
    
    # Two halfs of the split wagon may not surpass total weight
    for w_j, wagon1 in enumerate(train.wagons):
        for w_jj, wagon2 in enumerate(train.wagons):
            if w_j != w_jj:
                if wagon1.is_copy == True and wagon2.is_copy == True:
                    if wagon1.wagonID == wagon2.wagonID:
                        model.Add(sum(x[c_i, w_j] * container.get_gross_weight() + x[c_i, w_jj] * container.get_gross_weight() 
                        for c_i, container in enumerate(containers))
                        <= int(wagon1.get_weight_capacity() * 0.85))

    # The distance between two hazardous containers should be at least one wagon
    for c_i, container_i in enumerate(containers):
        for c_ii, container_ii in enumerate(containers):
            if(c_i == c_ii):
                continue
            if(not container_i.get_hazard_class() > 0 or not container_ii.get_hazard_class() > 0):
                continue

            if(not container_i.get_hazard_class() <= 3 or not container_ii.get_hazard_class() <= 3):
                continue

            if (container_i.get_hazard_class() == container_ii.get_hazard_class()):
                continue

            # Let OR-tools determine this value
            # The constraints force OR tools to choose the right value
            direction = model.NewBoolVar('direction_to_enforce')

            # TODO: remove position and position_2, this 
            # makes the code more messy, but probably faster for long solves
            # TODO: if there are too many hazardous goods, then the solver can't find the solution
            # So add a check somewhere to see if it is possible to uphold this constraint
            position = model.NewIntVar(0, 50, 'position_%i' % c_i)
            position_2 = model.NewIntVar(0, 50, 'position_%i' % c_ii)
            model.Add(
                position == sum(x[c_i, w_j] * int(wagon.get_position()) for w_j, wagon in enumerate(train.wagons))
                )
            model.Add(
                position_2 == sum(x[c_ii, w_j] * int(wagon.get_position()) for w_j, wagon in enumerate(train.wagons))
                )
            model.Add(
                position >= 2 + position_2
                ).OnlyEnforceIf(direction)
            model.Add(
                position  <= -2 + position_2
            ).OnlyEnforceIf(direction.Not())

    # # Bogie in middle of wagon constraint
    # for w_j, wagon in enumerate(train.wagons):
    #     if wagon.number_of_axles > 4:
    #         # get the number of 30ft containers on the wagon
    #         number_of_30ft = model.NewIntVar(0, 2, 'wagon_%i' % w_j)

    #         model.Add(number_of_30ft == sum(x[c_i, w_j] for c_i, container in enumerate(containers) if container.get_length() > 22 and container.get_length() <= 30))

    #         # model.Add(sum(x[c_i, w_j] for c_i, container in enumerate(containers) if container.get_length() == 30))
            
    #         # for c_i, container in enumerate(containers):
    #         #     model.Add(x[c_i, w_j] * container.get_length() <= int((wagon.get_length_capacity() / 2)))
    #         # model.Add(sum(x[c_i, w_j] * container.get_length() for c_i, container in enumerate(containers)))

    #endregion

    #region axle-load-constraints

    # Containers cant occupy the same position on the wagon
    # for w_j, wagon in enumerate(train.wagons):
    #     for c_i, container in enumerate(containers):
    #         model.Add(
    #             sum(x[c_i, w_j] * container_positions[c_i]) == container_positions[c_i]
    #         )
    
    #endregion

    """t
                OBJECTIVE
    """


    objective_length = model.NewIntVar(0, int(train.get_total_length_capacity()), 'length')
    model.Add(
        objective_length == sum(
            x[(c_i, w_j)] * container.get_length() 
                for c_i, container in enumerate(containers) 
                for w_j, _ in enumerate(train.wagons)
            )
        )

    objective_weight = model.NewIntVar(0, int(train.get_total_weight_capacity()), 'weight')
    model.Add(
        objective_weight == sum(
            x[(c_i, w_j)] * container.get_gross_weight() 
                for c_i, container in enumerate(containers) 
                for w_j, _ in enumerate(train.wagons)
            )
        )  


    # Add objective_value_limit if is is defined
    if(objective_value_limit):
        model.Add(objective_length < int(objective_value_limit))

    model.Maximize(objective_length)

    """"
                Solving & Printing Solution
    """

    print("Starting Solve...")
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL:
        print('Objective Value:', solver.ObjectiveValue())

        added_containers_indices = []
        placed_containers = []
        for w_j, wagon in enumerate(train.wagons):
            for c_i, container in enumerate(containers):
                if solver.Value(x[c_i,w_j]) > 0:
                    train.wagons[w_j].add_container(container)
                    added_containers_indices.append(c_i)
                    placed_containers.append(container)


        unplaced_containers = []
        for c_i, container in enumerate(containers):
            if(c_i not in added_containers_indices):
                unplaced_containers.append(container)

        train.set_placed_containers(placed_containers)
        train.set_unplaced_containers(unplaced_containers)


        for wagon in train.wagons:
            wagon.add_dummies()

        # Combine the split wagons\
        visited_list = []
        final_list = []
        for wagon in train.wagons:
            if wagon.is_copy == True:
                if wagon.wagonID not in visited_list:
                    combined_wagon = Wagon(wagon.wagonID, wagon.weight_capacity, wagon.length_capacity * 2, wagon.contents, wagon.position, wagon.number_of_axles, wagon.total_length, wagon.wagon_weight, wagon.call)
                    combined_wagon.is_copy = False
                    combined_wagon.location = wagon.location
                    combined_wagon.containers = wagon.containers
                    visited_list.append(wagon.wagonID)
                    final_list.append(combined_wagon)
                else:
                    for final_wagon in final_list:
                        if final_wagon.wagonID == wagon.wagonID:
                            try:
                                final_wagon.containers += wagon.containers
                            except:
                                continue
            else:
                final_list.append(wagon)
        
        train.wagons = final_list

        for wagon in train.wagons:
            print(wagon)
        
        axle_load_success = train.set_optimal_axle_load()

        # for wagon in train.wagons:
        #     new_containers = []
        #     container_list = wagon.containers
        #     if container_list is not None:
        #         i = 0
        #         while i < len(container_list) - 2:
        #             if container_list[i].get_gross_weight() == -1 and container_list[i+1].get_gross_weight() == -1:
        #                 merged_container = Container("", 0, -1, container_list[i].get_length() * 2, None, None, None, None, None)
        #                 new_containers.append(merged_container)
        #                 i += 2
        #             else:
        #                 new_containers.append(container_list[i])
        #                 i += 1
        #     wagon.containers = new_containers

        print("Calculation time", timer() - start)
        return train, axle_load_success, solver.ObjectiveValue()
        # print(solver.ResponseStats())
    elif status == cp_model.FEASIBLE:
        print('status == cp_model.FEASIBLE')
    else:
        print("Solution Not found. Stats: ", solver.ResponseStats())


def setup(dataset):
    containerlist = []
    wagonlist = []

    #Set parameters
    max_traveldistance = 50
    if dataset.MAXTRAVELDISTANCE[1] is not None:
        max_traveldistance = dataset.MAXTRAVELDISTANCE[1]
    max_traveldistance = 11

    split = None 
    if dataset.TRAINSPLIT[1] is not None:
        split = dataset.TRAINSPLIT[1]
    split = 14

    isReversed = False
    if dataset.TRAINREVERSED[1] is not None and dataset.TRAINREVERSED[1] == 1:
        isReversed = True

    for i, value in enumerate(dataset.WAGON):
        if pandas.notna(value):
            wagonID = value
            wagonType = dataset.WAGTYPE[i]
            wagonTare = dataset.TARE[i]
            wagonSizeft = dataset.SIZEFT[i]
            wagonNoAxes = dataset.NRAXES[i]
            wagonMaxTEU = dataset.MAXTEU[i]
            wagonLenght = dataset.LEN[i]
            wagonPosition = dataset.WPOS[i]
            wagonPayload = dataset.PAYLOAD[i]
            wagonTare = dataset.TARE[i]
            wagonTrack = dataset.TRACK[i]
            wagonCall = dataset.CALLCODE[i]
            wagonlist.append([wagonID, wagonType, wagonSizeft, wagonNoAxes, wagonMaxTEU, wagonLenght, wagonPosition, wagonPayload, wagonCall, wagonTare, wagonTrack])

    for i, value in enumerate(dataset.CONTAINERNUMBER):
        if pandas.notna(value):
            containerID = value
            containerType = dataset.UNITTYPE[i]
            unNR = dataset.UNNR[i]
            unKlasse = dataset.UNKLASSE[i]
            nettWeight = dataset.UNITWEIGHTNETT[i]
            terminalWeightNett = dataset.TERMINALWEIGHTNETT[i]
            containerTEU = dataset.TEUS[i]
            containerPosition = dataset.COMPOUNDPOS[i]
            containerTarra = dataset.CONTAINERTARRA[i]
            containerCall = dataset.CALLCODE[i]
            containerlist.append([containerID, containerType, unNR, unKlasse, nettWeight, terminalWeightNett, containerTEU, containerPosition, containerTarra, containerCall])
    #Creating dataframes from container en wagon lists
    wagondf = pandas.DataFrame(wagonlist, columns =['wagonID', 'wagonType', 'wagonSizeft', 'wagonNoAxes', 'wagonMaxTEU', 'wagonLength', 'wagonPosition', 'wagonPayload', 'wagonCall', 'wagonTare', 'wagonTrack'])
    containerdf = pandas.DataFrame(containerlist, columns =['containerID', 'containerType', 'unNR', 'unKlasse', 'nettWeight', 'terminalWeightNett', 'containerTEU', 'containerPosition', 'containerTarra', 'containerCall'])
    
    print(wagondf)
    wagondf = wagondf.sort_values(by='wagonPosition')
    
    #Reverse wagons if neccesary
    if isReversed:
        
        wagondf = wagondf[::-1]
        wagondf = wagondf.reset_index(drop=True)
        for i, wagon in wagondf.iterrows():
            wagondf.at[i, 'wagonPosition'] = i+1

    # Remove all wagons and containers that contain Null values
    wagons = []
    containers = []
    wrong_wagons = []    
    null_containers = []
    for index, wagon in wagondf.iterrows():
        if pandas.notna(wagon['wagonSizeft']) and pandas.notna(wagon['wagonLength']) and pandas.notna(wagon['wagonPosition']) and pandas.notna(wagon['wagonPayload']) and pandas.notna(wagon['wagonTare']) and pandas.notna(wagon['wagonNoAxes']): 
            wagonID = wagon['wagonID']
            weight_capacity = wagon['wagonPayload']
            length_capacity = wagon['wagonSizeft']
            total_length = wagon['wagonLength']
            position = wagon['wagonPosition'] 
            number_of_axles = wagon['wagonNoAxes']
            wagon_weight = wagon['wagonTare']
            call = wagon['wagonCall']
            wagonObj = Wagon(wagonID, weight_capacity, length_capacity, 0, position, number_of_axles, total_length, wagon_weight, call)
            wagons.append(wagonObj)
        else:
            # print("Wagon", index, "contained null values.")
            null_containers.append(index)
            wrong_wagons.append(wagon)

    print("Containers with indices: ", null_containers, " contain null values.")

    for index, container in containerdf.iterrows():
        containerID = container['containerID']
        gross_weight = int(container['nettWeight']) + int(container['containerTarra'])
        net_weight = container['nettWeight']
        foot = int(20 * container['containerTEU'])
        position = str(container['containerPosition'])
        goods = container['unKlasse']
        priority = 1
        typeid = container['containerType']
        hazard_class = container['unKlasse']
        
        containerObj = Container(containerID, gross_weight, net_weight, foot, position, goods, priority, typeid, hazard_class)
        containers.append(containerObj)
    return Train(wagons, containers, wrong_wagons, split, isReversed, max_traveldistance)

if __name__ == '__main__':
    train = setup(dataset)
    #train, axle_load_success, objective_value = TrainLoadingConstraint.main(train)
    #print("axle_load_success: ", axle_load_success, ", objective_value: ", objective_value)

    # This needs to be tested
    # while(axle_load_success is False):
    #     train, axle_load_success, objective_value = TrainLoadingConstraint.main(train, objective_value)
    #     print("axle_load_success: ", axle_load_success, ", objective_value: ", objective_value)
    

    placed_containers = train.get_placed_containers()
    containers = train.get_containers()
    unplaced_containers = train.get_unplaced_containers()
    
    #train.to_JSON(callcode=train.wagons[1].call, weight=train.get_total_packed_weight(), length=train.get_total_packed_length(), distance=train.get_total_travel_distance(), amount=len(placed_containers), wagons=[])
    train.to_CSV()
    
    train.print_solution()

    trainplanning_plot = train.get_tableplot(unplaced_containers)
    trainplanning_plot.show()




