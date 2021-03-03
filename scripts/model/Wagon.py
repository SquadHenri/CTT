import math

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

