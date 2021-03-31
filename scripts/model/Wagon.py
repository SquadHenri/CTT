import itertools as it
import math
import json
from statistics import mean
from model.Container import Container


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
        self.highest_axle_load = 0

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
        self.max_axle_load = axle_load_score
        if axle_load_score < 22000:

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
            dummy_container1 = Container("", 0, -1, dummy_length, None, None, None, None, None, dummy_length)
            dummy_container2 = Container("", 0, -1, dummy_length, None, None, None, None, None, dummy_length)
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