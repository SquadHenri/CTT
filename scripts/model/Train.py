import random
from model.Wagon import Wagon
import functions



class Train():

    
    # wagons should be a list of wagons
    def __init__(self, wagons):
        self.wagons = wagons # This is the list of all the wagons on the train
        self.maxWeight = 1000000000
    
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


    # CONSTRAINTS

    # Each container can be in at most one wagon
    # y is the variable used in TrainLoadingX.py
    # c_i is the key of the container in the dictionairy: y[(c_i, , )]
    def c_container_on_wagon(self, y, c_i, s_k):
        return sum(y[(c_i, w_j, s_k)] for w_j, _ in enumerate(self.wagons)) <= 16


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

    # Travel distance constraint
    def c_container_travel_distance(self, y, c_i, container):
        for w_j, wagon in enumerate(self.wagons):
            for s_k, _ in enumerate(wagon.get_slots()):
                # If the container is on the wagon, add the constraint.
                if y[(c_i, w_j, s_k)] == 1:
                    # The difference in position between the container and the wagon may not be larger than 50 metres.
                    return functions.getTravelDistance(container.get_position(), wagon.get_location()) < 50



    # Total weight of train may not surpass the maximum allowed weight on the track.
    # Later on we need to replace 100000000 with the max weight of the location of the train.
    # def c_max_train_weight(self, y, containers):
    #     total_weight = 0
    #     for c_i, container in enumerate(containers):
    #         for w_j, wagon in enumerate(self.wagons):
    #             for s_k, _ in enumerate(wagon.get_slots()):
    #                 if y[(c_i, w_j, s_k)] == 1:
    #                     total_weight += container.get_gross_weight()
    #     return total_weight < self.maxWeight


def get_random_value(min, max):
    if min == max:
        return min
    elif min > max:
        return random.randint(max * 2, min * 2) / 2
    elif max > min:
        return random.randint(min * 2, max * 2) / 2



    