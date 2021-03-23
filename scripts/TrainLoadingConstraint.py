# OR-TOOLS
from ortools.sat.python import cp_model
import collections
import math as math
from timeit import default_timer as timer

# Required modules
import pandas as pd
import numpy as np
# Our files
from colors import Color
from model import *
from data import getContainersFromCSV
import functions




def main(train, objective_value_limit = None):
    testing = True
    start = timer()
    containers = train.get_containers_for_call()
    # Define the cp model
    model = cp_model.CpModel()
    priority_list = []

    # Set some random containers to be in the priority list.
    for i in range(0, len(containers), 10):
        priority_list.append(i)
    print("These containers are in the priority list:", priority_list)
    
    # Make every nth container hazardous
    if testing:
        n = 7
        for i in range(0, len(containers), n):
            containers[i].set_hazard_class(1)
        print("These containers are hazardous:", [i for i, container in enumerate(containers) if(container.get_hazard_class() is not None and container.get_hazard_class() > 0)])

    

    """
                VARIABLES
    """

    # x[c_i, w_j] = 1 if container c_i is packed in wagon w_j
    x = {}
    for c_i, _ in enumerate(containers):    
        for w_j, wagon in enumerate(train.wagons):
            x[(c_i,w_j)] = model.NewIntVar(0, 1, 'cont:%i,wagon%i' % (c_i, w_j))
    
    # This value of this is: spreadContainers == (len(containers) > len(train.wagons))
    # This is added as a constraint
    spreadContainers = model.NewBoolVar('spreadContainers')

    # y = {}
    # for w_j, wagon in enumerate(train.wagons):
    #     y[(w_j)] = model.NewIntervalVar(0, wagon.get_total_length(), wagon.get_total_length(), 'wagon_slot_%i' % (w_j))


    # w_slot = {}
    # for w_j, wagon in enumerate(train.wagons):
    #     w_slot[(w_j)] = model.NewIntervalVar(0, int(wagon.get_total_length()), int(wagon.get_total_length()), 'wagon_%i' % w_j)

    # c_start = {}
    # for c_i, container in enumerate(containers):
    #     c_start[(c_i)] = model.NewIntVar(0, 10, 'c_start_%i' % c_i)

    """
                CONSTRAINTS
    """


    # Each container can be in at most one wagon.
    for c_i, container in enumerate(containers):
        if container not in priority_list:
            model.Add(
                sum(x[(c_i, w_j)] for w_j, _ in enumerate(train.wagons)) <= 1
                )

    # Each wagon has at least one container
    # Only enforce if there are enough containers
    model.Add( 
        spreadContainers == (len(containers) > len(train.wagons)) # Check if there are enough containers to spread them out over wagons
        )
    for w_j, _ in enumerate(train.wagons):
        model.Add(
            sum(x[(c_i, w_j)] for c_i, _ in enumerate(containers)) >= 1 # Each wagon has at least one container
        ).OnlyEnforceIf(spreadContainers)

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
                    (container.get_position()[1] <= 7) ) <= int(train.get_max_traveldistance()))

    # A train may not surpass a maximum weight, based on the destination of the train.
    model.Add(sum(x[(c_i, w_j)] * container.get_gross_weight() 
                    for c_i, container in enumerate(containers) 
                    for w_j, wagon in enumerate(train.wagons)) <= train.maxWeight)

    # The distance between two hazardous containers should be at least one wagon
    for c_i, container_i in enumerate(containers):
        for c_ii, container_ii in enumerate(containers):
            if(c_i == c_ii):
                continue
            if(not container_i.get_hazard_class() > 0 or not container_ii.get_hazard_class() > 0):
                continue

            if(not container_i.get_hazard_class() <= 3 or not container_ii.get_hazard_class() <= 3):
                continue

            if (container_i.get_hazard_class() == container_ii.get_hazard_class()):
                continue

            # Let OR-tools determine this value
            # The constraints force OR tools to choose the right value
            direction = model.NewBoolVar('direction_to_enforce')

            # TODO: remove position and position_2, this 
            # makes the code more messy, but probably faster for long solves
            # TODO: if there are too many hazardous goods, then the solver can't find the solution
            # So add a check somewhere to see if it is possible to uphold this constraint
            position = model.NewIntVar(0, 50, 'position_%i' % c_i)
            position_2 = model.NewIntVar(0, 50, 'position_%i' % c_ii)
            model.Add(
                position == sum(x[c_i, w_j] * int(wagon.get_position()) for w_j, wagon in enumerate(train.wagons))
                )
            model.Add(
                position_2 == sum(x[c_ii, w_j] * int(wagon.get_position()) for w_j, wagon in enumerate(train.wagons))
                )
            model.Add(
                position >= 2 + position_2
                ).OnlyEnforceIf(direction)
            model.Add(
                position  <= -2 + position_2
            ).OnlyEnforceIf(direction.Not())
    

    # Axle load constraint
    # print("Axle Load")
    # for w_j, wagon in enumerate(train.wagons):
        # number_of_axles = wagon.get_number_of_axles()
        # total_load = int(wagon.get_wagon_weight())
        # total_load += sum(x[c_i, w_j] * int(container.get_gross_weight()) for c_i, container in enumerate(containers))
        # axle_load = model.NewIntVar(0, total_load, 'axle_load(w_j:%i)' % w_j)
        
        # if(number_of_axles == 4):
        #     model.AddMaxEquality(
        #         axle_load,
        #         [sum(x[c_i,w_j] * container.get_gross_weight()),2]
        #     )
        # axle_load = model.NewIntVar(0, 100000, 'axle_load(wagon %i)' %w_j)

    # # Axle load constraint
    # for w_j, wagon in enumerate(train.wagons):
    #     print("c_IIIS:fjjso ", [c_i for c_i, container in enumerate(containers) if(x[(c_i, w_j)] == 1)])
    #     c_list = []
    #     for c_ii, container_i in enumerate(containers):
    #         if(x[(c_ii, w_j)] == 1):
    #             c_list.append(c_ii)
    #     print("c_list: ", c_list)
    #     axle_load = model.NewIntVar(0, 1000000, 'axle_load')
    #     model.AddMaxEquality(
    #         axle_load,
    #         wagon.get_axle_load_cp([container for c_i, container in enumerate(containers) if x[(c_i, w_j)] == 1])
    #     )
    #     model.Add(
    #         axle_load <= 22500
    #         )
    #     model.Add(
    #         max(wagon.get_axle_load_cp([container for c_i, container in enumerate(containers) if x[(c_i, w_j)] == 1])) 
    #         <= 22500
    #     )
    #     max_axle_load = model.NewIntVar(0, 100000, 'axle_load(wagon %i)' %w_j)
    #     model.AddMaxEquality(
    #         max_axle_load, 
    #         wagon.get_axle_load_cp([container for c_i, container in enumerate(containers) if(x[c_i, w_j] == 1)])
    #     )
    #     model.Add(
    #         max_axle_load < 66879180
    #         )
    # print("added axle load constraint")

    #model.AddMaxEquality(wagon.set_optimal_axle_load() <= 22500, wagon for wagon in train.wagons)

    """t
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

    # Add objective_value_limit if is is defined
    if(objective_value_limit):
        model.Add(objective_length < int(objective_value_limit))

    model.Maximize(objective_length)

    """"
                Solving & Printing Solution
    """

    print("Starting Solve...")
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL:
        print('Objective Value:', solver.ObjectiveValue())
        for w_j, wagon in enumerate(train.wagons):
            for c_i, container in enumerate(containers):
                if solver.Value(x[c_i,w_j]) > 0:
                    train.wagons[w_j].add_container(container)

        axle_load_success = train.set_optimal_axle_load()
        print("Calculation time", timer() - start)
        return train, axle_load_success, solver.ObjectiveValue()
        # print(solver.ResponseStats())
    elif status == cp_model.FEASIBLE:
        print('hoi, status == cp_model.FEASIBLE')
    else:
        print("Solution Not found. Stats: ", solver.ResponseStats())
    
class SolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Prints intermediate solutions"""

    def __init__(self, variables):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__variables = variables
        self.__solution_count = 0
    
    def OnSolutionCallback(self):
        self.__solution_count += 1
        print('SOlutuin cakkbaafos')
        for v in self.__variables:
            print('%s = %i' % (v, self.Value(v)), end = ' ')
        print()
    
    def SolutionCount(self):
        return self.__solution_count
