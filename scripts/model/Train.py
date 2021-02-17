import random

from model.Wagon import Wagon



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


    # Set the weight capacities of the wagons to a value between min and max
    def set_random_weight_capacities(self, min, max):
        for wagon in self.wagons:
            wagon.weight_capacity = get_random_value(min, max)

def get_random_value(min, max):
    if min == max:
        return min
    elif min > max:
        return random.randint(max * 2, min * 2) / 2
    elif max > min:
        return random.randint(min * 2, max * 2) / 2 


    