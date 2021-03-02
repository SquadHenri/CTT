import math

class Wagon():
    def __init__(self, wagonID, weight_capacity, length_capacity, contents, position, number_of_axles, total_length):
        self.wagonID = wagonID # number of the wagon
        self.weight_capacity = weight_capacity # Weight capacity
        self.length_capacity = length_capacity # The capacity of a wagon set in Feet
        self.total_length = total_length # The total length of the wagon
        self.slots = [[0 for i in range(int(length_capacity * 2))]] # Each slot is 0.5 TEU (for now) TODO get rid of this and work in feet
        self.contents = contents # are there dangerous goods in the wagon
        self.position = position # the placement in the train
        self.location = None # The location where the wagon in placed in the loading bay
        self.number_of_axles = number_of_axles

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

    # The weight of the containers cannot exceed the weight capacity of the wagon
    def c_weight_capacity(self, containers, y, w_j, s_k):
        return sum(y[(c_i, w_j, s_k)] * container.get_net_weight()
                for c_i, container in enumerate(containers)) <= self.get_weight_capacity()

    # The length of the containers cannot exceed the length capacity of the wagon
    def c_length_capacity(self, containers, y, w_j, s_k):
        return sum(y[(c_i, w_j, s_k)] * container.get_length()
                for c_i, container in enumerate(containers)) <= self.get_length_capacity()
    
        
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

