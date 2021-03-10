import math
from statistics import mean
import model.Container
from data.getWagonsFromCSV import get_wagons
from data.getContainersFromCSV import get_wagons, get_containers

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

    def __init__(self, wagonID, weight_capacity, length_capacity, contents, position, number_of_axles, total_length, wagon_weight):
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
             f'length capacity: {self.length_capacity}, position: {self.position}, location: {self.location}'

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
       
        # Set the weight of the wagon to wagon only to add the weight of the containers later
        total_load = self.wagon_weight
        # Refining the list of containers so it contains the container and the mean of the slots it stands on ordered from left to right (not that that stil matters).
        for container in containers:
            container[1] = mean(container[1])
            total_load += container[0].gross_weight
        containers = sorted(containers, key=lambda container: containers[1])
        key = str(self.length_capacity) + str(self.number_of_axles)
        dictionairy = get_wagons("data/Wagons.csv")
        # Starting with all the Wagons that have 2 bogies and so have 4 axles
        if self.number_of_axles == 4:
            key = str(self.length_capacity) + str(self.number_of_axles)
            right_axle_load = 0.5 * self.wagon_weight
            # Adding the containers to the load on the Right bogie
            for container in containers:
                dist = container[1] * 0.3048 - dictionairy[key][2]
                right_axle_load += self.container_load(container[0].gross_weight, dist, dictionairy[key][3])
            # calculating the left axle by taking the total and subtracting the load on the right axle
            left_axle_load = total_load - right_axle_load
            # Returning the data: left axle, right axle, total load
            return [left_axle_load, right_axle_load, total_load]
        # Setting The right numbers for the wagons with 3 bogies
        elif self.number_of_axles == 6:
            middle = dictionairy[key][2] + dictionairy[key][3]
            # Setting the basic load on the axles to add the containers later, given the load is equal on all bogies
            left_axle_load = right_axle_load = self.wagon_weight / 3
            # Adding the weight of the containers
            for container in containers: # splitting the train to calculate load on different parts
                if container[1] < self.length_capacity / 2:
                    dist = middle - containers[1] * 0.3048
                    left_axle_load += self.container_load(container[0].gross_weigth, dist, dictionairy[key][3])
                else:
                    dist = container[1] * 0.3048 - middle
                    right_axle_load += self.container_load(container[0].gross_weight, dist, dictionairy[key][3])
                middle_axle_load = total_load - right_axle_load - left_axle_load
                return [left_axle_load, middle_axle_load, right_axle_load, total_load]
        elif self.number_of_axles == 8:
            # define middle
            middle = dictionairy[key][2] + dictionairy[key][3]
            # setting the basic load over the axles (assumption: all load is devided equally)
            right_axle_load = right_axle1_load = self.wagon_weight / 4
            for container in containers: # splitting front and back to find relative load
                if container[1] < self.length_capacity / 2:
                    dist = container[1] * 0.3048 - dictionairy[key][2]
                    right_axle_load += self.container_load(container[0].gross_weight, dist, dictionairy[key][3])
                else:
                    dist = container[1] * 0.3048 - (dictionairy[key][2] + middle)
                    right_axle1_load += self.container_load(container[0].gross_weight, dist, dictionairy[key][3])
                axle_1 = total_load / 2 - right_axle_load
                axle_3 = total_load / 2 - right_axle1_load
                return [axle_1, right_axle_load, axle_3, right_axle1_load, total_load]
        else:
            print('the 4 bogies wagons have not been configured yet')


    # The weight of the containers cannot exceed the weight capacity of the wagon
    def c_weight_capacity(self, containers, x, w_j):
        return sum(x[(c_i, w_j)] * container.get_net_weight()
                for c_i, container in enumerate(containers)) <= self.get_weight_capacity()

    # The length of the containers cannot exceed the length capacity of the wagon
    def c_length_capacity(self, containers, x, w_j):
        return sum(x[(c_i, w_j)] * container.get_length()
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

if __name__ == '__main__':
    containers = get_containers()
    wagon1 = Wagon(0, 100, 5, None, [0,0],0,0,0)
    wagon2 = Wagon(1, 110, 7, None, [0,1],0,0,0)
    wagon3 = Wagon(2, 130, 6, None, [1,0],0,0,0)
    wagon4 = Wagon(3, 150, 9, None, [1,0],0,0,0)
    wagon5 = Wagon(4, 140, 8, None, [0,2],0,0,0)
    load = wagon1.get_axle_load(containers[1])
    print(load)