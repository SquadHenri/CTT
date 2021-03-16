# OR-TOOLS
from ortools.sat.python import cp_model
import collections
import math as math

# Required modules
import pandas as pd
import numpy as np
# Our files
from colors import Color
from model import *
from data import getContainersFromCSV
import functions

def main(containers, train):

    # Define the cp model
    model = cp_model.CpModel()
    priority_list = []
    # Set some random containers to be in the priority list.
    for i in range(0, len(containers), 10):
        print("Container ", i, "Must be loaded")
        priority_list.append(i)

    """
                VARIABLES
    """

    # x[c_i, w_j] = 1 if container c_i is packed in wagon w_j
    x = {}
    for c_i, _ in enumerate(containers):    
        for w_j, wagon in enumerate(train.wagons):
            x[(c_i,w_j)] = model.NewIntVar(0, 1, 'cont:%i,wagon%i' % (c_i, w_j))


    """
                CONSTRAINTS
    """

    # Each container can be in at most one wagon.
    for c_i, container in enumerate(containers):
        if container not in priority_list:
            model.Add(sum(x[(c_i, w_j)] for w_j, _ in enumerate(train.wagons)) <= 1)

    # All containers in the priority list need to be loaded on the train, no matter what.
    for c_i in priority_list:
        model.Add(sum(x[(c_i,w_j)] for w_j, _ in enumerate(train.wagons)) == 1)

    # The amount packed in each wagon cannot exceed its weight capacity.
    for w_j, wagon in enumerate(train.wagons):
        model.Add(
            sum(x[(c_i, w_j)] * container.get_gross_weight()
                for c_i, container in enumerate(containers))
                <=
                int(wagon.get_weight_capacity())
        )

    # The length of the containers cannot exceed the length of the wagon
    for w_j, wagon in enumerate(train.wagons):
        model.Add(
            sum(x[(c_i, w_j)] * container.get_length()
                for c_i, container in enumerate(containers))
                <=
                int(wagon.get_length_capacity())
        )

    #Travel distance constraint for total distance.
    model.Add(sum(x[(c_i, w_j)] * int(functions.getTravelDistance(container.get_position(), wagon.get_location()))
                    for c_i, container in enumerate(containers) 
                    for w_j, wagon in enumerate(train.wagons) 
                    if (len(container.get_position()) == 3) and 
                    (container.get_position()[0] <= 52) and 
                    (container.get_position()[1] <= 7) ) <= 300)

    # A train may not surpass a maximum weight, based on the destination of the train.
    model.Add(sum(x[(c_i, w_j)] * container.get_gross_weight() 
                    for c_i, container in enumerate(containers) 
                    for w_j, wagon in enumerate(train.wagons)) <= train.maxWeight)


    """
                OBJECTIVE
    """

    # objective_terms = []

    # for w_j, wagon in enumerate(train.wagons):
    #     for c_i, container in enumerate(containers):
    #         objective_terms.append(x[c_i,w_j] * container.get_length())
    
    # for w_j, wagon in enumerate(train.wagons):
    #     for c_i, container in enumerate(containers):
    #         objective_terms.append(x[c_i,w_j] * container.get_gross_weight())

    # model.Maximize(sum(objective_terms))

    objective_length = model.NewIntVar(0, int(train.get_total_length_capacity()), 'length')
    model.Add(
        objective_length == sum(
            x[(c_i, w_j)] * container.get_length() 
                for c_i, container in enumerate(containers) 
                for w_j, _ in enumerate(train.wagons)
            )
        )
    # model.Maximize(objective_length)

    objective_weight = model.NewIntVar(0, int(train.get_total_weight_capacity()), 'weight')
    model.Add(
        objective_weight == sum(
            x[(c_i, w_j)] * container.get_gross_weight() 
                for c_i, container in enumerate(containers) 
                for w_j, _ in enumerate(train.wagons)
            )
        )  
    #model.Maximize(objective_weight)

    model.Maximize(objective_length)

    """"
                Solving & Printing Solution
    """

    print("Validation: " + model.Validate())

    print("Starting Solve...")
    solver = cp_model.CpSolver()
    #solution_printer = SolutionPrinter(x)
    status = solver.Solve(model)

    #status = solver.SearchForAllSolutions(model, solution_printer)
    #print("Solution Count: ", solution_printer.SolutionCount())

    if status == cp_model.OPTIMAL:
        print('Objective Value:', solver.ObjectiveValue())
        total_weight = 0
        total_length = 0
        total_distance = 0
        container_count = 0
        unplaced = [(c_i, container) for c_i, container in enumerate(containers)]
        placed_containers = []
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
                if solver.Value(x[c_i,w_j]) > 0:
                    filled_wagons[w_j].append((c_i, container))
                    unplaced.remove((c_i, container))
                    train.wagons[w_j].add_container(container)
                    if container in containers_:
                        pass # The container is already in the solution
                    else:
                        containers_.append(container)
                        placed_containers.append(c_i)
                        print(Color.GREEN, "\tc_i:", c_i, Color.END, " \t", container)
                        wagon_weight += container.get_gross_weight()
                        wagon_length += container.get_length()
                        if (len(container.get_position()) == 3) and (container.get_position()[0] <= 52) and (container.get_position()[1] <= 7):
                            wagon_distance += functions.getTravelDistance(container.get_position(), wagon.get_location())
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
        placed_containers = sorted(placed_containers)
        print()
        print("Placed", placed_containers)
        print("Not placed", [x[0] for x in unplaced])

        # Only get the container objects of unplaced, this will be used for plotting.
        unplaced_container = [x[1] for x in unplaced]
    
class SolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Prints intermediate solutions"""

    def __init__(self, variables):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__variables = variables
        self.__solution_count = 0
    
    def OnSolutionCallback(self):
        self.__solution_count += 1
        for v in self.__variables:
            print('%s = %i' % (v, self.Value(v)), end = ' ')
        print()
    
    def SolutionCount(self):
        return self.__solution_count
