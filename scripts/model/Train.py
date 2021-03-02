import random
from Wagon import Wagon



class Train():

    
    # wagons should be a list of wagons
    def __init__(self, wagons):
        self.wagons = wagons
    
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

    # Maybe split this up, but for now this is fine
    def get_total_capacity(self):
        total_length = 0
        total_weight = 0
        for wagon in self.wagons:
            total_length += wagon.length_capacity
            total_weight += wagon.weight_capacity
        return total_length, total_weight
    
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

        
    # Set the weight capacities of the wagons to a value between min and max
    def set_random_weight_capacities(self, min, max):
        for wagon in self.wagons:
            wagon.set_weight_capacity(get_random_value(min, max))

    # Set the weight capacities of the wagons to a value between min and max
    def set_random_length_capacities(self, min, max):
        for wagon in self.wagons:
            wagon.set_length_capacity(get_random_value(min, max))

    # CONSTRAINTS

    # Each container can be in at most one wagon
    # y is the variable used in TrainLoadingX.py
    # c_i is the key of the container in the dictionairy: y[(c_i, , )]
    def c_container_on_wagon(self, y, c_i):
        counter = 0
        for w_j, wagon in enumerate(self.wagons):
            for s_k, _ in enumerate(wagon.get_slots()): # check all slots
                if(y[(c_i, w_j,s_k)] == 1): # container c_i is on wagon w_j
                    counter+=1 
                    break
            continue
        return counter <= 1
    
    # Contents constraint
    def c_container_location_valid(self, y, c1_i, c2_i, container_1, container_2):
        for w_j, wagon in enumerate(self.wagons):
            for s_k, _ in enumerate(wagon.get_slots()):
                # get the positions of both wagons
                if(y[(c1_i, w_j, s_k)] == 1):
                    c1_pos = wagon.get_position()
                if(y[(c2_i, w_j, s_k)] == 1):
                    c2_pos = wagon.get_position()
        # make sure that the wagon positions >= 2, so that there is 1 wagon in between.
        return abs(c1_pos - c2_pos) >= 2



def get_random_value(min, max):
    if min == max:
        return min
    elif min > max:
        return random.randint(max * 2, min * 2) / 2
    elif max > min:
        return random.randint(min * 2, max * 2) / 2



    