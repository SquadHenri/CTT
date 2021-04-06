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
from model.Container import Container
from model.Train import Train
from model.Wagon import Wagon
from data import getContainersFromCSV




def main(train, max_objective, final_run, objective_value_limit = None):
    testing = False
    start = timer()
    containers = train.get_containers()
    # Define the cp model
    model = cp_model.CpModel()
    priority_list = []

    # Set some random containers to be in the priority list.
    if testing:
        for i in range(0, len(containers), 10):
            priority_list.append(i)
        ("These containers are in the priority list:", priority_list)
    
    # Make every nth container hazardous
    if testing:
        n = 7
        for i in range(0, len(containers), n):
            containers[i].set_hazard_class(1)
        print("These containers are hazardous:", [i for i, container in enumerate(containers) if(container.get_hazard_class() is not None and container.get_hazard_class() > 0)])


    #region Split wagons that have a mid bogie
    # this prevents the model to plan a container over the hinge of the wagon
    # creates 2 dummie wagons with both halve the length, the same positions and a boolean that tells it is a copy
    wagon_list = []
    for wagon in train.wagons:
        if wagon.number_of_axles > 4:
            wagonA = Wagon(wagon.wagonID, wagon.weight_capacity, wagon.length_capacity * 0.5, wagon.contents, wagon.position, wagon.number_of_axles, wagon.total_length, wagon.wagon_weight, wagon.call)
            wagonB = Wagon(wagon.wagonID, wagon.weight_capacity, wagon.length_capacity * 0.5, wagon.contents, wagon.position, wagon.number_of_axles, wagon.total_length, wagon.wagon_weight, wagon.call)

            wagonA.is_copy = True
            wagonA.location = wagon.location
            wagonB.is_copy = True
            wagonB.location = wagon.location

            wagon_list.append(wagonA)
            wagon_list.append(wagonB)
            # print("A", wagonA)
            # print("B", wagonB)
        else:
            wagon_list.append(wagon)

    #endregion
    
    # for wagon in wagon_list:
    #     print(wagon)
    
    train.wagons = wagon_list
    """
                VARIABLES
    """

    #region variables

    positions = list(range(5))

    # x[c_i, w_j] = 1 if container c_i is packed in wagon w_j
    x = {}
    for c_i, _ in enumerate(containers):    
        for w_j, wagon in enumerate(train.wagons):
            x[(c_i,w_j)] = model.NewIntVar(0, 1, 'cont:%i,wagon%i' % (c_i, w_j))
    
    # c_pos = {}
    # for w_j, wagon in enumerate(train.wagons):
    #     for position in range(5):
    #         c_pos[w_j, position] = model.NewIntVar(0, len(containers), 'c_pos:(%i,%i)' % (w_j, position))


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

    #endregion 

    """
                CONSTRAINTS
    """

    #region train-wagon-constraints

    # Each container can be in at most one wagon.
    for c_i, container in enumerate(containers):
        if container not in priority_list:
            model.Add(
                sum(x[(c_i, w_j)] for w_j, _ in enumerate(train.wagons)) <= 1
                )
     # All containers in the priority list need to be loaded on the train, no matter what.
    for c_i in priority_list:
        model.Add(sum(x[(c_i,w_j)] for w_j, _ in enumerate(train.wagons)) == 1)

    # Each wagon has at least one container
    # Only enforce if there are enough containers
    # TODO: If the max weight of the train is lower than the weight of the minimum amount of containers, we get an error.
    model.Add( 
        spreadContainers == (len(containers) > len(train.wagons)) # Check if there are enough containers to spread them out over wagons
        )
    for w_j, _ in enumerate(train.wagons):
        model.Add(
            sum(x[(c_i, w_j)] for c_i, _ in enumerate(containers)) >= 1 # Each wagon has at least one container
        ).OnlyEnforceIf(spreadContainers)

    # The amount packed in each wagon cannot exceed its weight capacity.
    for w_j, wagon in enumerate(train.wagons):
        model.Add(
            sum(x[(c_i, w_j)] * container.get_gross_weight()
                for c_i, container in enumerate(containers))
                <=
                int(wagon.get_weight_capacity() * 1)
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
    model.Add(sum(x[(c_i, w_j)] * int(Container.get_travel_distance(container.get_position(), wagon.get_location()))
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
    
    # Two halfs of the split wagon may not surpass total weight
    for w_j, wagon1 in enumerate(train.wagons):
        for w_jj, wagon2 in enumerate(train.wagons):
            if w_j != w_jj:
                if wagon1.is_copy == True and wagon2.is_copy == True:
                    if wagon1.wagonID == wagon2.wagonID:
                        model.Add(sum(x[c_i, w_j] * container.get_gross_weight() + x[c_i, w_jj] * container.get_gross_weight() 
                        for c_i, container in enumerate(containers))
                        <= int(wagon1.get_weight_capacity() * 1))

    # Containers that are between 20 and 30 foot, may not be placed on an 80 foot wagon
    for w_j, wagon in enumerate(train.wagons):
        #print(wagon.get_length_capacity())
        if wagon.get_length_capacity() == 40 and wagon.is_copy == True:
            print("Adding constraint for wagon", wagon.wagonID)
            model.Add(sum(x[c_i, w_j] for c_i, container in enumerate(containers) if container.get_actual_length() != container.get_length()) < 1)

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

    # # Bogie in middle of wagon constraint
    # for w_j, wagon in enumerate(train.wagons):
    #     if wagon.number_of_axles > 4:
    #         # get the number of 30ft containers on the wagon
    #         number_of_30ft = model.NewIntVar(0, 2, 'wagon_%i' % w_j)

    #         model.Add(number_of_30ft == sum(x[c_i, w_j] for c_i, container in enumerate(containers) if container.get_length() > 22 and container.get_length() <= 30))

    #         # model.Add(sum(x[c_i, w_j] for c_i, container in enumerate(containers) if container.get_length() == 30))
            
    #         # for c_i, container in enumerate(containers):
    #         #     model.Add(x[c_i, w_j] * container.get_length() <= int((wagon.get_length_capacity() / 2)))
    #         # model.Add(sum(x[c_i, w_j] * container.get_length() for c_i, container in enumerate(containers)))

    #endregion

    #region axle-load-constraints

    # If a container is in a wagon, then the container has a position on that wagon too
    # for c_i, _ in enumerate(containers):
    #     for w_j, _ in enumerate(train.wagons):
    #         model.AddImplication(
    #             x[c_i,w_j] == 1,
    #             sum(c_pos[w_j, position] == c_i for position in positions) == 1
    #         )

    # # Each container can only have one position
    # for w_j, _ in enumerate(train.wagons):
    #     model.AddAllDifferent(
    #         c_pos[w_j, position] for position in positions
    #     )

    #endregion

    """
                OBJECTIVE
    """
    #region objectives

    objective_length = model.NewIntVar(0, int(train.get_total_length_capacity()), 'length')
    model.Add(
        objective_length == sum(
            x[(c_i, w_j)] * container.get_length() 
                for c_i, container in enumerate(containers) 
                for w_j, _ in enumerate(train.wagons)
            )
        )

    objective_weight = model.NewIntVar(0, int(train.get_total_weight_capacity()), 'weight')
    model.Add(
        objective_weight == sum(
            x[(c_i, w_j)] * container.get_gross_weight() 
                for c_i, container in enumerate(containers) 
                for w_j, _ in enumerate(train.wagons)
            )
        )  


    #Add objective_value_limit if is is defined
    if(objective_value_limit):
        model.Add(objective_length < int(objective_value_limit))

    model.Maximize(objective_length)

    #endregion
    """"
                Solving & Printing Solution
    """

    print("Starting Solve...")
    solver = cp_model.CpSolver()    # setting solver
    solver.parameters.max_time_in_seconds = 10  # setting max timout for solver in seconds
    status = solver.Solve(model)    # solve the model

    if status == cp_model.OPTIMAL:
        print('Objective Value:', solver.ObjectiveValue())  # printing the objective value for testing purpose

        if solver.ObjectiveValue() < max_objective: # if the objective is lower the case is not considered
            return train, False, solver.ObjectiveValue(), 0

        #region creating lists that show what containers are placed and which are unplaced
        added_containers_indices = []
        placed_containers = []
        for w_j, wagon in enumerate(train.wagons):
            for c_i, container in enumerate(containers):
                if solver.Value(x[c_i,w_j]) > 0:
                    train.wagons[w_j].add_container(container)
                    added_containers_indices.append(c_i)
                    placed_containers.append(container)


        unplaced_containers = []
        for c_i, container in enumerate(containers):
            if(c_i not in added_containers_indices):
                unplaced_containers.append(container)

        train.set_placed_containers(placed_containers)
        train.set_unplaced_containers(unplaced_containers)
        #endregion

        for wagon in train.wagons:
            wagon.add_dummies()

        # Combine the split wagons\
        # once all the containers have been placed the split containers are put together so axle load can be determined
        #region
        visited_list = []
        final_list = []
        for wagon in train.wagons:
            if wagon.is_copy == True: # if copy combine and add to final list
                if wagon.wagonID not in visited_list:
                    combined_wagon = Wagon(wagon.wagonID, wagon.weight_capacity, wagon.length_capacity * 2, wagon.contents, wagon.position, wagon.number_of_axles, wagon.total_length, wagon.wagon_weight, wagon.call)
                    combined_wagon.is_copy = False
                    combined_wagon.location = wagon.location
                    combined_wagon.containers = wagon.containers
                    visited_list.append(wagon.wagonID)
                    final_list.append(combined_wagon)
                else:
                    for final_wagon in final_list:
                        if final_wagon.wagonID == wagon.wagonID:
                            try:
                                final_wagon.containers += wagon.containers
                            except:
                                continue
            else:
                final_list.append(wagon) # if not a copy, but an original, add to the final list
        
        train.wagons = final_list
        #endregion
        # for wagon in train.wagons:
        #     print(wagon)
        
        axle_load_success = train.set_optimal_axle_load() # returns a boolean that tells if axle load is not to high

        # The amount of wagons that exeeds the max weight
        wrong_wagons = len([wagon.max_axle_load for wagon in train.wagons if wagon.max_axle_load > 22000]) 
        
        #region
        # for wagon in train.wagons:
        #     new_containers = []
        #     container_list = wagon.containers
        #     if container_list is not None:
        #         i = 0
        #         while i < len(container_list) - 2:
        #             if container_list[i].get_gross_weight() == -1 and container_list[i+1].get_gross_weight() == -1:
        #                 merged_container = Container("", 0, -1, container_list[i].get_length() * 2, None, None, None, None, None)
        #                 new_containers.append(merged_container)
        #                 i += 2
        #             else:
        #                 new_containers.append(container_list[i])
        #                 i += 1
        #     wagon.containers = new_containers
        #endregion

        print("Calculation time", timer() - start)
        return train, axle_load_success, solver.ObjectiveValue(), wrong_wagons
        # print(solver.ResponseStats())
    elif status == cp_model.FEASIBLE:
        print('status == cp_model.FEASIBLE, no optimal solution found')
    else:
        print("Solution Not found. Stats: ", solver.ResponseStats())

#Temporary place, this code might still be useful
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



# Axle load try 2:
    # for c_i, container in enumerate(containers):
    #     for w_j, wagon in enumerate(train.wagons):
    #         c = model.NewBoolVar("")
    #         model.Add(
    #             (x[c_i, w_j] == 1)
    #         ).OnlyEnforceIf(c)
    #         model.Add(
    #             x[c_i,w_j] == 0
    #             ).OnlyEnforceIf(c.Not())
    #         model.Add(
    #             c_position[c_i,w_j] > 0
    #         ).OnlyEnforceIf(c)
    #         model.Add(
    #             c_position[c_i, w_j] == 0
    #         ).OnlyEnforceIf(c.Not())

   
    # # Each position can only be occupied by one container
    # for w_j, wagon in enumerate(train.wagons):
    #     c=model.NewBoolVar("")

    #     model.AddAllDifferent(
    #         c_position[c_i, w_j] for c_i, _ in enumerate(containers)
    #     )