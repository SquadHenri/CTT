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




def main(train):
    testing = False
    start = timer()
    containers = train.get_containers_for_call()
    # Define the cp model
    model = cp_model.CpModel()
    priority_list = []

    # Set some random containers to be in the priority list.
    if testing:
        for i in range(0, len(containers), 10):
            print("Container ", i, "Must be loaded")
            priority_list.append(i)
    
    # Make every nth container hazardous
    if testing:
        n = 7
        for i in range(0, len(containers), n):
            print("Container ", i, "is hazardous")
            containers[i].set_hazard_class(1)
    
    for c in containers:
        print(c.containerID, c.hazard_class)

    

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

    print("amount of containers on terminal with right coordinates")
    print(len([container for container in train.containers 
                        if (len(container.get_position()) == 3) and 
                        (container.get_position()[0] <= 52) and 
                        (container.get_position()[1] <= 7)]))

    #Travel distance constraint for total distance.
    model.Add(sum(x[(c_i, w_j)] * int(functions.getTravelDistance(container.get_position(), wagon.get_location()))
                    for c_i, container in enumerate(containers) 
                    for w_j, wagon in enumerate(train.wagons) 
                    if (len(container.get_position()) == 3) and 
                    (container.get_position()[0] <= 52) and 
                    (container.get_position()[1] <= 7) ) <= int(train.get_max_traveldistance()) * 
                        len([container for container in train.containers 
                        if (len(container.get_position()) == 3) and 
                        (container.get_position()[0] <= 52) and 
                        (container.get_position()[1] <= 7)]))

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
            position = model.NewIntVar(0, 40, 'position_%i' % c_i)
            position_2 = model.NewIntVar(0, 40, 'position_%i' % c_ii)
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

    # Bogie in middle of wagon constraint
    for w_j, wagon in enumerate(train.wagons):
        if wagon.number_of_axles > 4:
            # get the number of 30ft containers on the wagon
            number_of_30ft = model.NewIntVar(0, 2, 'wagon_%i' % w_j)

            model.Add(number_of_30ft == sum(x[c_i, w_j] for c_i, container in enumerate(containers) if container.get_length() == 30))

            #model.Add(sum(x[c_i, w_j] for c_i, container in enumerate(containers) if container.get_length() == 30))
            
            # for c_i, container in enumerate(containers):
            #     model.Add(x[c_i, w_j] * container.get_length() <= int((wagon.get_length_capacity() / 2)))
            #model.Add(sum(x[c_i, w_j] * container.get_length() for c_i, container in enumerate(containers)))
    
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
    model.Maximize(objective_weight)

    #model.Maximize(objective_length)

    """"
                Solving & Printing Solution
    """

    #print("Validation: " + model.Validate())

    print("Starting Solve...")
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    # solution_printer = SolutionPrinter(x)
    # status = solver.SolveWithSolutionCallback(model, solution_printer)

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
        unplaced_containers = [x[1] for x in unplaced]

        # trainplanning_plot = train.get_tableplot(total_length, total_weight, unplaced_containers)
        # trainplanning_plot.show()

        axle_load_success = train.set_optimal_axle_load()
        # print("Axle load success: ", axle_load_success)

        print("Calculation time", timer() - start)

        train.to_JSON(callcode=train.wagons[1].call, weight=total_weight, length=total_length, distance=total_distance, amount=container_count, wagons=[])
        train.to_CSV(total_weight, total_length)
    
        trainplanning_plot = train.get_tableplot(unplaced_containers)
        trainplanning_plot.show()

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
