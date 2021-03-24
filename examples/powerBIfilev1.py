# Original Script. Please update your script content here and once completed copy below section back to the original editing window #
# The following code to create a dataframe and remove duplicated rows is always executed and acts as a preamble for your script: 

# dataset = pandas.DataFrame(NRAXES, MAXTEU, CALLCODE, WAGTYPE, WPOS, WAGON, UNNR, UNKLASSE, UNITWEIGHTNETT, UNITTYPE, UNITSEQUENCE, TRACK, TEUS, TERMINALWEIGHTNETT, TARE, SIZEFT, STARTPOSITION, SEQ, PAYLOAD, MOVETYPE, LOCATION, LEN, CONTAINERTARRA, CONTAINERNUMBER, COMPOUNDPOS, PRIOCONTAINER, PRIORITY, MAXTRAVEL, TravelDistance)
# dataset = dataset.drop_duplicates()

# Paste or type your script code here:
import math
from statistics import mean
import random
import math as math
#import matplotlib as plt
#plt.show()

def get_wagons():
    return {"a": [10,0], "b": [20,0], "c": [30,0], "d": [40,0]}

def set_location(wagons):
    xlen = 0
    y_val = 0
    result = []
    for wagon in wagons:

        if (xlen + wagon.total_length) < 320:
            wagon.location = [math.ceil((xlen + 0.5 * wagon.total_length)/6.1), y_val]
            xlen += wagon.total_length

        else:
            xlen = 0
            y_val = -1
            wagon.location = [math.ceil((xlen + 0.5 * wagon.total_length)/6/1), y_val]
            xlen += wagon.total_length

        result.append(wagon)
    # See where the last wagon in located to calculate the shift the 2nd row of wagons hast to make
    shift_wagon = wagons[len(wagons)-1]
    shift_wagon_xloc = shift_wagon.location[0]
    shift_wagon_length = shift_wagon.total_length
    x_shift = (52 - math.ceil(shift_wagon_length / 2 / 6.1)) - shift_wagon_xloc

    for wagon in wagons:
        if wagon.location[1] == -1:
            wagon.location[0] += x_shift


    return result
def getAllDistances():
    dist_dict = {}

    # loop through all containers and wagons, and store the distances in a dictionary
    for i, container in enumerate(containers):
        for j, wagon in enumerate(wagons):
            dist = getTravelDistance(container, wagon)
            dist_dict[(i, j)] = dist
    return dist_dict
def getTravelDistance(c_cord, w_cord):

    # factorize the difference in length of x and y
    x_fact = 6.5
    y_fact = 3

    # calculate the distance over the x-axis between a container and a wagon
    x_dist = (c_cord[0] - w_cord[0]) * x_fact
    # calculate the distance over the y-axis between a container and a wagon
    y_dist = (c_cord[1] - w_cord[1]) * y_fact

    # calculate the distance using Pythagoras
    dist = math.sqrt(math.pow(x_dist, 2) + math.pow(y_dist, 2))

    return dist
class Color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'
class Container():
    def __init__(self, containerID, gross_weight, net_weight, foot, position, goods, priority, typeid):
        self.containerID = containerID # name of the container
        self.gross_weight = gross_weight # weight of the container and the goods in kg
        self.foot = foot # length of the contianer in Foot
        self.position = self.calc_pos(position) # position of the container (on the dock or train)
        self.goods = goods # What is in the container (used for dangerous goods)
        self.priority = priority # ctt does not set a priority so this might be left unused
        self.net_weight = net_weight # Weight of the goods without the container (do not use this)
        self.typeid = typeid # Type of the container (len in feet and a letter combo)
        self.hazard_class = None # None means it is not hazardous, 1,2,3 means it is


    def __str__(self):
        return f'Container {self.containerID},'\
             f' priority: {self.priority}, gross_weight: {self.gross_weight}, foot: {self.foot}, position: {self.position}'

    def __repr__(self):
        return f'Container {self.containerID}, '\
                f'priority: {self.priority}, gross_weight: {self.gross_weight}, '\
                f'foot: {self.foot}, position: {self.position}, goods: {self.goods},'\
                f'net_weight: {self.net_weight}, typeid: {self.typeid}'


    # Transform the position of the container into a list with coordinates.
    def calc_pos(self, position):
        position = position.split(" ")
        position = position[0].split(".")

        try:
            return [int(x) for x in position]
        except ValueError:
            return position

    # Getter for container position coordinates
    # Container ID used to identify the container at hand
    def get_containerID(self):
        return self.containerID

    # The weight of the container excluding the container itself
    def get_net_weight(self):
        return self.net_weight

    # The weight of the container including the container itself
    def get_gross_weight(self):
        return self.gross_weight    

    # The Length of the container in Foot,
    # This is done in foot since some containers have a length that is different from 1 or 1,5
    def get_length(self):
        return self.foot

    # The type of goods that is in the container
    def get_goods(self):
        return self.goods

    # The Position of the container 
    def get_position(self):
        return self.position

    # if the priority of a container is higher than normal this will differ from 1
    def get_priority(self):
        return self.priority

    # The type of the container
    def get_type(self):
        return self.typeid

    # The hazard class of this container, an int that is of value
    # 0,1,2,3
    def get_hazard_class(self):
        return self.hazard_class

    def set_hazard_class(self, value):
        self.hazard_class = value
class Train():

    
    # wagons should be a list of wagons
    def __init__(self, wagons):
        self.wagons = wagons # This is the list of all the wagons on the train
        self.maxWeight = 1600000
    
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
    
    # Print the wagon values with the containers that filled them
    def print_solution(self):
        for wagon in self.wagons:
            wagon.print_solution()

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

    # UNUSED/UNFINISHED CONSTRAINTS

    # Travel distance constraint
    # def c_container_travel_distance(self, y, c_i, container):
    #     for w_j, wagon in enumerate(self.wagons):
    #         for s_k, _ in enumerate(wagon.get_slots()):
    #             # If the container is on the wagon, add the constraint.
    #             if y[(c_i, w_j, s_k)] == 1:
    #                 # The difference in position between the container and the wagon may not be larger than 50 metres.
    #                 return functions.getTravelDistance(container.get_position(), wagon.get_location()) < 50



    #Total weight of train may not surpass the maximum allowed weight on the track.
    #Later on we need to replace 100000000 with the max weight of the location of the train.
    # def c_max_train_weight(self, y, containers):
    #     slot_found = False
    #     total_weight = 0
    #     for c_i, container in enumerate(containers):
    #         for w_j, wagon in enumerate(self.wagons):
    #             for s_k, _ in enumerate(wagon.get_slots()):
    #                 if y[(c_i, w_j, s_k)] == 1:
    #                     print(container.get_gross_weight())
    #                     total_weight += container.get_gross_weight()
    #                     slot_found = True
    #                     break
    #         if slot_found:
    #             break
    #     print(total_weight)
    #     return total_weight < self.maxWeight

    # # Contents constraint
    # def c_container_location_valid(self, x, c1_i, c2_i, container_1, container_2):
    #     c1_pos = 0
    #     c2_pos = 0
    #     #print(c1_i)
    #     #print(c2_i)
    #     for w_j, wagon in enumerate(self.wagons):
    #             # get the positions of both wagons
    #             if(x[(c1_i, w_j)] == 1):
    #                 c1_pos = wagon.get_position()
    #                 #print(c1_pos)
    #             if(x[(c2_i, w_j)] == 1):
    #                 c2_pos = wagon.get_position()
    #                 #print(c2_pos)
    #     # make sure that the wagon positions >= 2, so that there is 1 wagon in between.
    #     return abs(c1_pos - c2_pos) >= 2
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

    def __init__(self, wagonID, weight_capacity, length_capacity, contents, position, number_of_axles, total_length, wagon_weight, call, containers = None):
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

        # Can be None
        self.containers = containers

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

    # Prints relevant wagon information for the solution, expects self.containers to be filled
    def print_solution(self):
        if not self.containers:
            print("There is no list of containers. Cannot print relevant information.")
            return
        # Print information on the wagon
        print(self)
        offset = 0
        for container in self.containers:
            print(offset, '-', offset+container.get_length(),':\t', container)
            offset += container.get_length()




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

    def container_load(self, weight, dist, axledist):
        load = weight * dist / axledist
        return load            
        
    
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

from ortools.linear_solver import pywraplp
import json

# This TrainLoading variant will switch from the dictionairy data model to using classes

def create_train_and_containers():
    train = getContainersFromCSV.create_train()
    train.set_random_weight_capacities(30000, 50000) 
    train.set_random_length_capacities(100, 150)

    containers = list(getContainersFromCSV.get_containers_1())

    for container in containers:
        print(container.position)

    # Make every sixth container hazardous
    for i in range(0, len(containers), 10):
        print("Container ", i, "is hazardous")
        containers[i].set_hazard_class(1)

    print(train)
    return train, containers

def main(containers, train):
    # data = create_data_model()
    #train, containers = create_train_and_containers()

    priority_list = []

    # Set some random containers to be in the priority list.
    for i in range(0, len(containers), 10):
        print("Container ", i, "Must be loaded")
        priority_list.append(i)

    # Create the mip solver with the SCIP backend.
    solver = pywraplp.Solver.CreateSolver('SCIP')

    # VARIABLES

    # y[c_i,w_j,s_k] = 1 if container c_i is packed in slot s_k of wagon w_j
    y = {}
    for c_i, _ in enumerate(containers):
        for w_j, wagon in enumerate(train.wagons):
            for s_k, _ in enumerate(wagon.get_slots()):
                y[(c_i,w_j,s_k)] = solver.IntVar(0, 1, 'cont:%i,wagon:%i,slot:%i' % (c_i,w_j,s_k))
    
    # x[c_i, w_j] = 1 if container c_i is packed in wagon w_j
    x = {}
    for c_i, _ in enumerate(containers):
        for w_j, wagon in enumerate(train.wagons):
            x[(c_i,w_j)] = solver.IntVar(0, 1, 'cont:%i,wagon%i' % (c_i, w_j))
    #x[(c_i,w_j)] = solver.IntVar(0, 1, 'cont:%i,wagon%i' % (c_i, w_j))

    
    # CONSTRAINTS

    # All containers in the priority list need to be loaded on the train, no matter what.
    for c_i in priority_list:
        solver.Add(sum(x[(c_i,w_j)] for w_j, _ in enumerate(train.wagons)) == 1)

    # Each container can be in at most one wagon.
    for c_i, container in enumerate(containers):
        if container not in priority_list:
            solver.Add(sum(x[(c_i, w_j)] for w_j, _ in enumerate(train.wagons)) <= 1)

    # The amount packed in each wagon cannot exceed its weight capacity.
    for w_j, wagon in enumerate(train.wagons):
        solver.Add(
            wagon.c_weight_capacity(containers, x, w_j)
        )

    # The length of the containers cannot exceed the length of the wagon
    for w_j, wagon in enumerate(train.wagons):
        solver.Add(
            wagon.c_length_capacity(containers, x, w_j)
        )
    
    # Travel distance constraint for total distance.
    # solver.Add(sum(x[(c_i, w_j)] * functions.getTravelDistance(container.get_position(), wagon.get_location()) 
    #     for c_i, container in enumerate(containers) 
    #     for w_j, wagon in enumerate(train.wagons) 
    #     if (len(container.get_position()) == 3) and 
    #     (container.get_position()[0] <= 52) and 
    #     (container.get_position()[1] <= 7) ) <= 500)

    #Travel distance constraint per container
    for c_i, container in enumerate(containers):
        # For every container add the travel distance constraint.
        c_location = container.get_position()
        if (len(c_location) == 3) and (c_location[0] <= 52) and (c_location[1] <= 7):
            solver.Add( sum(x[(c_i, w_j)] * getTravelDistance(c_location, wagon.get_location()) for w_j, wagon in enumerate(train.wagons)) <= 10000)


    # A train may not surpass a maximum weight, based on the destination of the train.
    solver.Add(sum(x[(c_i, w_j)] * container.get_gross_weight() 
    for c_i, container in enumerate(containers) 
    for w_j, wagon in enumerate(train.wagons)) <= train.maxWeight)


    # UNUSED/UNFINISHED CONSTRAINTS

    # A container has to be put on a wagon as a whole
    # for w_j, wagon in enumerate(train.wagons):
    #     solver.Add(
    #         wagon.c_container_is_whole(y, len(containers), w_j)
    #         )


    #Contents constraint
    # Example of GitHub Jobshop might not work since his locations of the machines are somewhat predefined
    # We only know the starting positions of the containers, but we need to know the positions of the containers on the train.

    # make list of pairs of containers that are allready added to the constraint.
    # added = []
    # for c1_i, container1 in enumerate(containers):
    #     for c2_i, container2 in enumerate(containers):
    #         # Check we are not working with the same containers
    #         if c1_i != c2_i:
    #             # If the pair of containers has not yet been added, we continue
    #             if (c1_i, c2_i) not in added and (c2_i, c1_i) not in added:
    #                 # If both containers are in a hazard class, add the constraint
    #                 if container1.hazard_class != None and container2.hazard_class != None:
    #                     print("Adding", c1_i, c2_i)
    #                     solver.Add(train.c_container_location_valid(x, c1_i, c2_i, container1, container2))

    #                     # ======================================
    #                     # Try something with a seperate function.
    #                     # ======================================


    #                     # The difference in position >= 2.
    #                     # We need to fix something for -2.
    #                     solver.Add(
    #                         sum(x[(c1_i, w_j)] * wagon.get_position() - x[(c2_i, w_j)] * wagon.get_position() for w_j, wagon in enumerate(train.wagons)) >= 2
    #                         )
    #                     # if sum(x[(c1_i, w_j)] * wagon.get_position() - x[(c2_i, w_j)] * wagon.get_position() for w_j, wagon in enumerate(train.wagons)) >= 0:
    #                     #     solver.Add(sum(x[(c1_i, w_j)] * wagon.get_position() - x[(c2_i, w_j)] * wagon.get_position() for w_j, wagon in enumerate(train.wagons)) >= 2)
    #                     # else:
    #                     #     solver.Add(sum(x[(c1_i, w_j)] * wagon.get_position() - x[(c2_i, w_j)] * wagon.get_position() for w_j, wagon in enumerate(train.wagons)) <= -2)
                        
    #                     # Add the pair of containers to the added list
    #                     added.append((c1_i, c2_i))
    #                     added.append((c2_i, c1_i))


    # Test constraint for the axle load
    # Loop through wagons of the train
    #for w_j, wagon in enumerate(train.wagons):
    #   solver.Add(wagon.c_axle_load(y, containers)


    # OBJECTIVE

    # This objective tries to maximize the weight of the containers
    # For now this objective works, but we possibly need to change this later
    objective = solver.Objective()
    for c_i, container in enumerate(containers):
        for w_j, wagon in enumerate(train.wagons):
                objective.SetCoefficient(
                    x[(c_i,w_j)], container.get_length() 
                    #y[(c_i,w_j,s_k)], (container.get_priority() * 3 + container.get_length() * 4) # - container.traveldistance ofzo
                    #x[(c_i, w_j)], container.get_gross_weight()
                )
    objective.SetMaximization()

    print('Starting solve...')
    status = solver.Solve()

    import numpy as np
    import matplotlib.pyplot as plt
    from datetime import date, datetime
    def get_tableplot(self):
            
        maxContainers = 0
        columns = []
        #Sort wagons on their position
        wagons = self.wagons
        l = len(wagons)
        for i in range(0, l): 
            for j in range(0, l-i-1): 
                if (wagons[j].position > wagons[j + 1].position): 
                    tempo = wagons[j] 
                    wagons[j]= wagons[j + 1] 
                    wagons[j + 1]= tempo 

        #Set max number of containers on wagon, needed for amount of table rows 
        for wagon in wagons:
            if wagon.containers is None:
                raise TypeError("No containers selected")
            
            if len(wagon.containers) > maxContainers:
                maxContainers = len(wagon.containers)
        title = ''
        data = []
        cellColours = []
        for wagon in wagons:
            #Add wagonID to column list
            columns.append(str(int(wagon.position))+ ". " + wagon.wagonID)
            datarow = []
            cellRowColour = []
            #Title of table
            title = wagon.call
            if 0 < maxContainers: 
                datarow.extend('empty' for x in range(0, maxContainers))
                cellRowColour.extend('#fefefe' for x in range(0, maxContainers)) 
                #datarow.append(maxContainers) 

            for i, container in enumerate(wagon.containers):
                datarow[i] = container.containerID
                #if container.gross_weight > 30000:
                #    cellRowColour[i] = '#cc244b'
                # orange #ff6153
                # dark green #498499
              
                if container.goods == 1 or container.goods == 2 or container.goods == 3:
                    cellRowColour[i] = '#11aae1'

            cellColours.append(cellRowColour)
            data.append(datarow)

        n_rows = len(data)
        rows = ['slot %d' % (x+1) for x in range(len(data))]

        
        cell_text = []
        for row in range(n_rows):
            cell_text.append(['%s' % (x) for x in data[row]])
        
        cell_text.reverse()
        #CTT Green color: #8bc53d
        #CTT Blue color: #11aae1
        rcolors = np.full(n_rows, '#8bc53d')
        ccolors = np.full(n_rows, '#8bc53d')
        

        the_table = plt.table(cellText=data,
                    rowLabels=columns,
                    rowColours=rcolors,
                    cellColours=cellColours,
                    colColours=ccolors,
                    colLabels=rows,
                    loc='center')
        plt.subplots_adjust(left=0.230, bottom=0, right=0.965, top=0.938)
        plt.axis('off')
        #plt.title(title, fontsize=8, pad=None, )
   
        # Month abbreviation, day and year	
        currentdate = date.today().strftime("%b-%d-%Y")
        

        now = datetime.now()
 
        print("now =", now)

        # dd/mm/YY H:M:S
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

        fig = plt.gcf()
        
        plt.figtext(0.95, 0.05, "CTT Rotterdam" + dt_string ,
            horizontalalignment='right',
            size=6,
            weight='light',
            color='#000'
           )


        fig.suptitle(title + " on " + datetime.now().strftime("%d/%m/%Y %H:%M:%S"), fontsize=10)
        plt.savefig(title + '-planning-' + currentdate, bbox_inches='tight', dpi=150)
        plt.show()
            



    # TODO: Cleanup the solution printing, move this functionality to the Container, Wagon and Train class
    # See train.print_solution() and Wagon.print_solution()
    if status == pywraplp.Solver.OPTIMAL:
        print('Objective Value:', objective.Value())
        total_weight = 0
        total_length = 0
        total_distance = 0
        container_count = 0
        filled_wagons = {}
        for w_j, wagon in enumerate(train.wagons):
            wagon_weight = 0
            wagon_length = 0
            wagon_distance = 0
            print(wagon)
            filled_wagons[w_j] = []
            for c_i, container in enumerate(containers):
                # Used to keep track of the containers in the wagon
                # so we print information for each container and not for each slot
                containers_ = []
                #for s_k, _ in enumerate(wagon.get_slots()):
                if x[c_i,w_j].solution_value() > 0:
                    filled_wagons[w_j].append(c_i)
                    train.wagons[w_j].add_container(container)
                    if container in containers_:
                        pass # The container is already in the solution
                    else:
                        containers_.append(container)
                        print(Color.GREEN, "\tc_i:", c_i, Color.END, " \t", container)
                        wagon_weight += container.get_gross_weight()
                        wagon_length += container.get_length()
                        if (len(container.get_position()) == 3) and (container.get_position()[0] <= 52) and (container.get_position()[1] <= 7):
                            wagon_distance += getTravelDistance(container.get_position(), wagon.get_location())
                        container_count += 1

                          
            print('Packed wagon weight:', Color.GREEN, wagon_weight, Color.END, ' Wagon weight capacity: ', wagon.get_weight_capacity())
            print('Packed wagon length:', Color.GREEN, wagon_length, Color.END, ' Wagon length capacity: ', wagon.get_length_capacity())
            total_length += wagon_length
            total_weight += wagon_weight
            total_distance += wagon_distance
            
        #print(filled_wagons)
        print()
        print('Total packed weight:', total_weight, '(',round(total_weight / train.get_total_weight_capacity() * 100,1),'%)')
        print('Total packed length:', total_length, '(',round(total_length / train.get_total_length_capacity() * 100,1),'%)')
        print('Total distance travelled:', total_distance)
        print('Containers packed: ', container_count,"/",len(containers))

        # for container in containers:
        #     if container not in filled_wagons.values():
        #         print("unplanned", container)

        # This is another way of printing solution values
        #train.print_solution()

        with open('result.json', 'w') as fp:
            json.dump(filled_wagons, fp)

        get_tableplot(train)

    elif status == pywraplp.Solver.FEASIBLE:
        print('The problem does have a feasible solution')
    else:
        print('The problem does not have an optimal solution.')


import pandas

def setup(dataset):
    containerlist = []
    wagonlist = []

    for i, value in enumerate(dataset.WAGON):
        if pandas.notna(value):
            wagonID = value
            wagonType = dataset.WAGTYPE[i]
            wagonTare = dataset.TARE[i]
            wagonSizeft = dataset.SIZEFT[i]
            wagonNoAxes = dataset.NRAXES[i]
            wagonMaxTEU = dataset.MAXTEU[i]
            wagonLenght = dataset.LEN[i]
            wagonPosition = dataset.WPOS[i]
            wagonPayload = dataset.PAYLOAD[i]
            wagonTare = dataset.TARE[i]
            wagonTrack = dataset.TRACK[i]
            wagonCall = dataset.CALLCODE[i]
            wagonlist.append([wagonID, wagonType, wagonSizeft, wagonNoAxes, wagonMaxTEU, wagonLenght, wagonPosition, wagonPayload, wagonCall, wagonTare, wagonTrack])

    for i, value in enumerate(dataset.CONTAINERNUMBER):
        if pandas.notna(value):
            containerID = value
            containerType = dataset.UNITTYPE[i]
            unNR = dataset.UNNR[i]
            unKlasse = dataset.UNKLASSE[i]
            nettWeight = dataset.UNITWEIGHTNETT[i]
            terminalWeightNett = dataset.TERMINALWEIGHTNETT[i]
            containerTEU = dataset.TEUS[i]
            containerPosition = dataset.COMPOUNDPOS[i]
            containerTarra = dataset.CONTAINERTARRA[i]
            containerCall = dataset.CALLCODE[i]
            containerlist.append([containerID, containerType, unNR, unKlasse, nettWeight, terminalWeightNett, containerTEU, containerPosition, containerTarra, containerCall])
    #Creating dataframes from container en wagon lists
    wagondf = pandas.DataFrame(wagonlist, columns =['wagonID', 'wagonType', 'wagonSizeft', 'wagonNoAxes', 'wagonMaxTEU', 'wagonLength', 'wagonPosition', 'wagonPayload', 'wagonCall', 'wagonTare', 'wagonTrack'])
    containerdf = pandas.DataFrame(containerlist, columns =['containerID', 'containerType', 'unNR', 'unKlasse', 'nettWeight', 'terminalWeightNett', 'containerTEU', 'containerPosition', 'containerTarra', 'containerCall'])

    # Remove all wagons and containers that contain Null values
    wagons = []
    containers = []

    for index, wagon in wagondf.iterrows():
        if pandas.notna(wagon['wagonSizeft']) and pandas.notna(wagon['wagonLength']) and pandas.notna(wagon['wagonPosition']) and pandas.notna(wagon['wagonPayload']) and pandas.notna(wagon['wagonTare']): 
            wagonID = wagon['wagonID']
            weight_capacity = wagon['wagonPayload']
            length_capacity = wagon['wagonSizeft']
            total_length = wagon['wagonLength']
            position = wagon['wagonPosition'] 
            number_of_axles = wagon['wagonPosition']
            wagon_weight = wagon['wagonTare']
            call = wagon['wagonCall']
            wagonObj = Wagon(wagonID, weight_capacity, length_capacity, 0, position, number_of_axles, total_length, wagon_weight, call)
            wagons.append(wagonObj)
        else:
            print("Wagon", index, "contained null values.")

    for index, container in containerdf.iterrows():
        containerID = container['containerID']
        gross_weight = int(container['nettWeight']) + int(container['containerTarra'])
        net_weight = container['nettWeight']
        foot = 20 * int(container['containerTEU'])
        position = str(container['containerPosition'])
        goods = container['unKlasse']
        priority = 1
        typeid = container['containerType']
        
        containerObj = Container(containerID, gross_weight, net_weight, foot, position, goods, priority, typeid)
        containers.append(containerObj)

    return containers, wagons

#dataset = pandas.read_csv('input_df_026798a1-811d-446d-a3d3-5a655d6fa538.csv')

#if __name__ == '__main__':
containers, wagons = setup(dataset)
wagons = set_location(wagons)

for i, container in enumerate(containers):
    print("Container", i, container)

for i, wagon in enumerate(wagons):
    print("Wagon", i, wagon)

train = Train(wagons)
main(containers, train)


