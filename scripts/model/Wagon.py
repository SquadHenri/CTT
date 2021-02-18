import math

class Wagon():
    def __init__(self, wagonID, weight_capacity, length_capacity, contents, position):
        self.wagonID = wagonID
        self.weight_capacity = weight_capacity # Weight capacity
        self.length_capacity = length_capacity # Length capacity in TEU (for now)
        self.slots = [[0 for i in range(int(length_capacity * 2))]] # Each slot is 0.5 TEU (for now)
        self.contents = contents
        self.position = position
        self.location = [-2, -2]

    # Convert Wagon to string
    # Print relevant information only, __repr__ is used to print every detail
    def __str__(self):
        return f'Wagon {self.wagonID}, weight capacity: {self.weight_capacity}, '\
             f'length capacity: {self.length_capacity}'

    def __repr__(self):
        return f'Wagon {self.wagonID}, weight capacity: {self.weight_capacity}, '\
             f'length_capacity: {self.length_capacity}, contents: {self.contents}, '\
             f'position: {self.position}, location: {self.location}'

    # TODO call: "set the locations"  at appropriate time

    # CONSTRAINTS

    # Constraint that a container has to be put on the wagon as a whole
    # y is the variable used in TrainLoadingX.py
    def c_container_is_whole(self, y, num_containers):
        for s_k, _ in enumerate(self.slots):
            if s_k == 0:
                return True # The first one is always fine
            
            
        
    # Getter for container position coordinates
    def get_position(self):
        return self.position

    def get_weight_capacity(self):
        return self.weight_capacity

    def get_length_capacity(self):
        return self.length_capacity

    def get_contents(self):
        return self.contents

    def get_location(self):
        return self.location

    def get_slots(self):
        return self.slots

