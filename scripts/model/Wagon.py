import math

class Wagon():
    def __init__(self, wagonID, weight_capacity, length_capacity, contents, position):
        self.wagonID = wagonID # number of the wagon
        self.weight_capacity = weight_capacity # Weight capacity
        self.length_capacity = length_capacity # Length capacity in TEU (for now)
        self.slots = [[0 for i in range(int(length_capacity * 2))]] # Each slot is 0.5 TEU (for now)
        self.contents = contents # are there dangerous goods in the wagon
        self.position = position # the placement in the train
        self.location = None # The location where the wagon in placed in the loading bay

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

    def c_weight_capacity(self, y, containers, w_j):
        # Create dictionairy of all containers c_i and their respective slots
        containers = {}
        for c_i in range(len(containers)):
            for s_k in range(len(self.slots)):
                if(y[(c_i, w_j, s_k)] == 1):
                    if(c_i in containers):
                        containers[c_i].append(s_k)
                    else:
                        containers[c_i] = [s_k]
        # Sum the weights of all containers
        packed_weight = 0
        for container in containers:
            packed_weight += container.get_net_weight()
        return packed_weight < self.get_weight_capacity()
    
    def c_length_capacity(self, y, containers, w_j):
        # Create dictionairy of all containers c_i and their respective slots
        containers = {}
        for c_i in range(len(containers)):
            for s_k in range(len(self.slots)):
                if(y[(c_i, w_j, s_k)] == 1):
                    if(c_i in containers):
                        containers[c_i].append(s_k)
                    else:
                        containers[c_i] = [s_k]
        # count
        packed_length = 0
        for container in containers:
            packed_length += container.get_length()
        return packed_length < self.get_length_capacity()
    
    # Possible constraint for the axle load
    # The function self.calculateLoad calculcates the axle load based on a container list, we still need to make this.
    # @TODO make calculateLoad function
    # def c_axle_load(self, y, containers, w_j):
    #     containers_on_wagon = []
    #     for c_i, container in enumerate(containers):
    #         for s_k in range(len(self.slots)):
    #             if y[(c_i, w_j, s_k)] == 1:
    #                 containers_on_wagon.append((container, s_k))
    #     return self.calculateLoad(containers_on_wagon) < maxLoad



                

            
            
            
        
    # Getter for container position coordinates
    def get_position(self):
        return self.position

    def get_weight_capacity(self):
        return self.weight_capacity
        
def set_weight_capacity(self, weight_capacity):
        self.weight_capacity = weight_capacity

    def get_length_capacity(self):
        return self.length_capacity

    def set_length_capacity(self, length_capacity):
        self.length_capacity = length_capacity

    def get_contents(self):
        return self.contents

    def get_location(self):
        return self.location

    def get_slots(self):
        return self.slots

