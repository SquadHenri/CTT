import math
from statistics import mean
from model import container

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
        
    """

    def __init__(self, wagonID, weight_capacity, length_capacity, contents, position, number_of_axles, total_length):
        self.wagonID = wagonID 
        self.weight_capacity = weight_capacity 
        self.length_capacity = total_length * 20 
        self.total_length = total_length 
        self.slots = [[0 for i in range(0,int(total_length * 20))]] 
        #self.slots = [[0 for i in range(int(length_capacity * 2))]]
        self.contents = contents 
        self.position = position 
        self.location = None 
        self.number_of_axles = number_of_axles
        self.wagon_weight = wagon_weight

    # Convert Wagon to string
    # Print relevant information only, __repr__ is used to print every detail
    def __str__(self):
        return f'Wagon {self.wagonID}, weight capacity: {self.weight_capacity}, '\
             f'length capacity: {self.length_capacity}'

    # prints all values from the wagon
    def __repr__(self):
        return f'Wagon {self.wagonID}, weight capacity: {self.weight_capacity}, '\
             f'length_capacity: {self.length_capacity}, contents: {self.contents}, '\
             f'position: {self.position}, location: {self.location}'


    # CONSTRAINTS

    # Constraint that a container has to be put on the wagon as a whole
    # y is the variable used in TrainLoadingX.py
    # w_j is the index of the wagon
    # TODO If people can optimize this, go ahead. This function will be called very often
    def c_container_is_whole(self, y, num_containers, w_j):
        # Create a dictionairy of all containers c_i and the slots
        # They occupy in the wagon
        containers = {}
        for c_i in range(num_containers):
            for s_k in range(len(self.slots)):
                if(y[(c_i, w_j, s_k)] == 1):
                    if(c_i in containers):
                        containers[c_i].append(s_k)
                    else:
                        containers[c_i] = [s_k]
        # Now check for each container if the slots they occupy are in order
        for c_i in containers:
            containers[c_i].sort()
            # Since the list is ordered, the following means the container is ordered
            return containers[c_i][-1] - containers[c_i][0] == len(containers[c_i]) - 1

   
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


    # Input for this funciton is the wagon and a list with the containers. The list of containers contains the container and the spots it takes in the wagon
    def get_axle_load(self, containers):
        #firstly give all the right numbers to the respective wagons (due to minor differences the numbers may vary but they are likely very close to each other)
        # 40 feet 4 axles
        axle_shift_40 = 2.15 # The length between the middle of the bogie en the end of the loading platform
        axle_dist_40 = 8.07 # The length between 2 bogies of the wagon
        # 47 feet 4 axles
        axle_shift_47 = 2.1
        axle_dist_47 = 10.2
        # 60 feet (4 axles)
        axle_shift_60 = 2.10 
        axle_dist_60 = 14.200 
        # 80 feet 4 axles
        axle_shift_80_2 = 2.70 
        axle_dist_80_2 = 19.300 
        # 80 feet 6 axles
        axle_shift_80_3 = 2.18
        axle_dist_80_3 = 10.395
        # 90 feet 6 axles
        axle_shift_90 = 2.18
        axle_dist_90 = 11.995
        # 104 feet 6 axles
        axle_shift_104 = 2.28
        axle_dist_104 = 14.2
        # Set the weight of the wagon to wagon only to add the weight of the containers later
        total_load = self.wagon_weight
        # Refining the list of containers so it contains the container and the mean of the slots it stands on ordered from left to right (not that that stil matters).
        for container in containers:
            container[1] = mean(container[1])
            total_load += container[0].gross_weight
        containers = sorted(containers, key=lambda container: containers[1])
        # Starting with all the Wagons that have 2 bogies and so have 4 axles
        if self.number_of_axles == 4:
            # Setting the right data in the 'distances' varable to work with in the calculation to prevent repeating code
            if self.length_capacity == 40:
                distances = [axle_shift_40, axle_dist_40]
            elif self.length_capacity == 47:
                distances = [axle_shift_47, axle_dist_47]
            elif self.length_capacity == 60:
                distances = [axle_shift_60, axle_dist_60]
            elif self.length_capacity == 80:
                distances = [axle_shift_80_2, axle_dist_80_2]
            # Setting half the load of the wagon on one bogie
            right_axle_load = 0.5 * self.wagon_weight
            # Adding the containers to the load on the Right bogie
            for container in containers:
                dist = container[1] * 0.3048 - distances[0]
                right_axle_load += self.container_load(container[0].gross_weight, dist, distances[1])
            # calculating the left axle by taking the total and subtracting the load on the right axle
            left_axle_load = total_load - right_axle_load
            # Returning the data: left axle, right axle, total load
            return [left_axle_load, right_axle_load, total_load]
        # Setting The right numbers for the wagons with 3 bogies
        elif self.number_of_axles == 6:
            if self.length_capacity == 80:
                distances = [axle_shift_80_3, axle_dist_80_3]
            elif self.length_capacity == 90:
                distances = [axle_shift_90, axle_dist_90]
            elif self.length_capacity == 104:
                distances = [axle_shift_104, axle_dist_104]
            middle = distances[0] + distances[1]
            # Setting the basic load on the axles to add the containers later, given the load is equal on all bogies
            left_axle_load = right_axle_load = self.wagon_weight / 3
            # Adding the weight of the containers
            for container in containers:
                if container[1] < self.length_capacity / 2:
                    dist = middle - containers[1] * 0.3048
                    left_axle_load += self.container_load(container[0].gross_weigth, dist, distances[1])
                else:
                    dist = container[1] * 0.3048 - middle
                    right_axle_load += self.container_load(container[0].gross_weight, dist, distances[1])
                middle_axle_load = total_load - right_axle_load - left_axle_load
                return [left_axle_load, middle_axle_load, right_axle_load, total_load]
        else:
            print('the 4 bogies wagons have not been configured yet')


    # The weight of the containers cannot exceed the weight capacity of the wagon
    def c_weight_capacity(self, containers, y, w_j, s_k):
        return sum(y[(c_i, w_j, s_k)] * container.get_net_weight()
                for c_i, container in enumerate(containers)) <= self.get_weight_capacity()

    # The length of the containers cannot exceed the length capacity of the wagon
    def c_length_capacity(self, containers, y, w_j, s_k):
        return sum(y[(c_i, w_j, s_k)] * container.get_length()
                for c_i, container in enumerate(containers)) <= self.get_length_capacity()       

    def container_load(self, weight, dist, axledist):
        load = weight * dist / axledist
        return load            
        
    # Getter for container position coordinates
    def get_position(self):
        return self.position

    def get_weight_capacity(self):
        return self.weight_capacity
        
    def set_weight_capacity(self, weight_capacity):
        self.weight_capacity = weight_capacity

    def get_length_capacity(self):
        return self.length_capacity

    def get_total_length(self):
        return self.total_length

    def set_length_capacity(self, length_capacity):
        self.length_capacity = length_capacity

    def get_contents(self):
        return self.contents

    def get_location(self):
        return self.location

    def get_slots(self):
        return self.slots

