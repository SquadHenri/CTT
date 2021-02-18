from ortools.linear_solver import pywraplp

from model.Wagon import Wagon
from model.Train import Train
from getContainersFromCSV import *

# This TrainLoading variant will switch from the dictionairy data model to using classes

def create_train_and_containers():
    train = create_train()

    train.set_random_weight_capacities(300000, 5000000)
    train.set_random_length_capacities(100, 150)
    #print(train)
    containers = list(get_containers_1())
    print(train)
    print(containers[0])
    print(containers[1])
    print(containers[2])
    return train, containers

def main():
    # data = create_data_model()
    train, containers = create_train_and_containers()

    # Create the mip solver with the SCIP backend.
    solver = pywraplp.Solver.CreateSolver('SCIP')

    # Variables

    # y[c_i,w_j,s_k] = 1 if container c_i is packed in slot s_k of wagon w_j
    y = {}
    for c_i, _ in enumerate(containers):
        for w_j, wagon in enumerate(train.wagons):
            for s_k, _ in enumerate(wagon.get_slots()):
                y[(c_i,w_j,s_k)] = solver.IntVar(0, 1, 'cont:%i,wagon:%i,slot:%i' % (c_i,w_j,s_k))

    # Constraints

    # Each slot can only have one container?
    # This constraint might still be necessary
    

    # Each container can be in at most one wagon.
    for c_i, _ in enumerate(containers):
        solver.Add(train.c_container_on_wagon(y,c_i))

    # A container has to be put on a wagon as a whole
    for w_j, wagon in enumerate(train.wagons):
        solver.Add(wagon.c_container_is_whole(y, len(containers), w_j))

    # The amount packed in each wagon cannot exceed its weight capacity.
    for w_j, wagon in enumerate(train.wagons):
        solver.Add(wagon.c_weight_capacity(y, containers, w_j))
    
    # The length of the containers cannot exceed the length of the wagon
    for w_j, wagon in enumerate(train.wagons):
        solver.Add(wagon.c_length_capacity(y, containers, w_j))

        

    # Objectives

    # This objective tries to maximize the weight of the containers
    # For now this objective works, but we possibly need to change this later
    objective = solver.Objective()
    for c_i, container in enumerate(containers):
        for w_j, wagon in enumerate(train.wagons):
            for s_k, _ in enumerate(wagon.get_slots()):
                objective.SetCoefficient(
                    y[(c_i,w_j,s_k)], (container.get_priority() * 0.1 - container.get_length() * 0.9)
                )
    objective.SetMaximization()

    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        print('Total space used:', objective.Value())
        total_weight = 0
        total_length = 0
        container_count = 0
        for w_j, wagon in enumerate(train.wagons):
            wagon_weight = 0
            wagon_length = 0
            print(wagon)
            for c_i, container in enumerate(containers):
                # Used to keep track of the containers in the wagon
                # so we print information for each container and not for each slot
                containers_ = []
                for slot_index, _ in enumerate(wagon.get_slots()):
                    if y[c_i,w_j,slot_index].solution_value() > 0:
                        if container in containers_:
                            pass # The container is already in the solution
                        else:
                            containers_.append(container)
                            print(container)
                            wagon_weight += container.get_net_weight()
                            wagon_length += container.get_length()
                            container_count += 1 
            print('Packed wagon weight:', wagon_weight, ' Wagon weight capacity: ', wagon.get_weight_capacity())
            print('Packed wagon length:', wagon_length, ' Wagon length capacity: ', wagon.get_length_capacity())
            total_length += wagon_length
            total_weight += wagon_weight
            print()
        print()
        print('Total packed weight:', total_weight, '(',round(total_weight / train.get_total_weight_capacity() * 100,1),'%)')
        print('Total packed length:', total_length, '(',round(total_length / train.get_total_length_capacity() * 100,1),'%)')
        print('Containers packed: ', container_count,"/",len(containers))
    elif status == pywraplp.Solver.FEASIBLE:
        print('The problem does have a feasible solution')
    else:
        print('The problem does not have an optimal solution.')



if __name__ == '__main__':
    main()
