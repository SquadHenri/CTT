from ortools.linear_solver import pywraplp
from colors import Color
from model import *
from data import getContainersFromCSV
import functions

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
        print("Container ", i, "is hazardous.")
        containers[i].set_hazard_class(1)

    print(train)
    return train, containers

def main():
    # data = create_data_model()
    train, containers = create_train_and_containers()

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


    # Each container can be in at most one wagon.
    for c_i, _ in enumerate(containers):
            solver.Add(sum(x[(c_i, w_j)] for w_j, _ in enumerate(train.wagons)) <= 1)

    # A container has to be put on a wagon as a whole
    # for w_j, wagon in enumerate(train.wagons):
    #     solver.Add(
    #         wagon.c_container_is_whole(y, len(containers), w_j)
    #         )

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

    #Contents constraint
    # Example of GitHub Jobshop might not work since his locations of the machines are somewhat predefined
    # We only know the starting positions of the containers, but we need to know the positions of the containers on the train.

    # make list of pairs of containers that are allready added to the constraint.
    added = []
    for c1_i, container1 in enumerate(containers):
        for c2_i, container2 in enumerate(containers):
            # Check we are not working with the same containers
            if c1_i != c2_i:
                # If the pair of containers has not yet been added, we continue
                if (c1_i, c2_i) not in added and (c2_i, c1_i) not in added:
                    # If both containers are in a hazard class, add the constraint
                    if container1.hazard_class != None and container2.hazard_class != None:
                        # The difference in position >= 2.
                        # We need to fix something for -2.
                        solver.Add(
                           sum(x[(c1_i, w_j)] * wagon.get_position() - x[(c2_i, w_j)] * wagon.get_position() for w_j, wagon in enumerate(train.wagons)) >= 2
                           )

                        # if sum(x[(c1_i, w_j)] * wagon.get_position() - x[(c2_i, w_j)] * wagon.get_position() for w_j, wagon in enumerate(train.wagons)) >= 0:
                        #     solver.Add(sum(x[(c1_i, w_j)] * wagon.get_position() - x[(c2_i, w_j)] * wagon.get_position() for w_j, wagon in enumerate(train.wagons)) >= 2)
                        # else:
                        #     solver.Add(sum(x[(c1_i, w_j)] * wagon.get_position() - x[(c2_i, w_j)] * wagon.get_position() for w_j, wagon in enumerate(train.wagons)) <= -2)
                        
                        # Add the pair of containers to the added list
                        added.append((c1_i, c2_i))
                        added.append((c2_i, c1_i))

                    
    

    # Travel distance constraint per container
    #
    #     # Travel distance constraint
    # for c_i, container in enumerate(containers):
    #     # For every container add the travel distance constraint.
    #     c_location = container.get_position()
    #     if (len(c_location) == 3) and (c_location[0] <= 52) and (c_location[1] <= 7):
    #         solver.Add( sum(x[(c_i, w_j)] * functions.getTravelDistance(c_location, wagon.get_location()) for w_j, wagon in enumerate(train.wagons)) <= 100)
    
    # Travel distance constraint for total distance.
    # The total travel distance may not be higher than the specified value.
    solver.Add(sum(x[(c_i, w_j)] * functions.getTravelDistance(container.get_position(), wagon.get_location()) for c_i, container in enumerate(containers) for w_j, wagon in enumerate(train.wagons) if (len(container.get_position()) == 3) and (container.get_position()[0] <= 52) and (container.get_position()[1] <= 7) ) <= 1000)

    # A train may not surpass a maximum weight, based on the destination of the train.
    solver.Add(sum(x[(c_i, w_j)] * container.get_gross_weight() for c_i, container in enumerate(containers) for w_j, wagon in enumerate(train.wagons)) <= train.maxWeight)

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
                            wagon_distance += functions.getTravelDistance(container.get_position(), wagon.get_location())
                        container_count += 1 
                          
            print('Packed wagon weight:', Color.GREEN, wagon_weight, Color.END, ' Wagon weight capacity: ', wagon.get_weight_capacity())
            print('Packed wagon length:', Color.GREEN, wagon_length, Color.END, ' Wagon length capacity: ', wagon.get_length_capacity())
            total_length += wagon_length
            total_weight += wagon_weight
            total_distance += wagon_distance
            print()
        #print(filled_wagons)
        print()
        print('Total packed weight:', total_weight, '(',round(total_weight / train.get_total_weight_capacity() * 100,1),'%)')
        print('Total packed length:', total_length, '(',round(total_length / train.get_total_length_capacity() * 100,1),'%)')
        print('Total distance travelled:', total_distance)
        print('Containers packed: ', container_count,"/",len(containers))

        # This is another way of printing solution values
        # train.print_solution()
    elif status == pywraplp.Solver.FEASIBLE:
        print('The problem does have a feasible solution')
    else:
        print('The problem does not have an optimal solution.')

if __name__ == '__main__':
    main()
