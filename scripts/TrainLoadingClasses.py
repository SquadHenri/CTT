from ortools.linear_solver import pywraplp

from model.Wagon import Wagon
from model.Train import Train
from getContainersFromCSV import *

# This TrainLoading variant will switch from the dictionairy data model to using classes

def create_data_model():
    """Create the data for the example."""
    data = {}
    container_distances = [48, 30, 42, 36, 36, 48, 42, 42, 36, 24, 30, 30, 42, 36, 36]
    container_distances *= 10
    container_weights = [48, 30, 42, 36, 36, 48, 42, 42, 36, 24, 30, 30, 42, 36, 36]
    container_lengths = [1.0, 3.0, 2.5, 5.0, 3.5, 3.0, 1.5, 4.0, 3.0, 3.5, 4.5, 1.0, 2.0, 3.0, 2.5] # In TEU's
    data['container_weights'] = container_weights
    data['container_lengths'] = container_lengths
    data['container_distances'] = container_distances
    data['containers'] = list(range(len(container_weights)))
    data['num_containers'] = len(container_weights)
    num_wagons = 7
    data['wagons'] = list(range(num_wagons))
    data['wagon_weight_capacities'] = [150, 90, 130, 110, 115, 110, 140]
    data['wagon_length_capacities'] = [4, 4.5, 6, 2, 8, 6, 8] # in TEU's

    data['wagon_slots'] = []    # each slot represents 0.5 TEU's. The slot is occupied if it is non-zero
                                # the number in the slot is the index of the container
    data['wagon_slots'].append([0 for i in range(8)])
    data['wagon_slots'].append([0 for i in range(9)])
    data['wagon_slots'].append([0 for i in range(12)])
    data['wagon_slots'].append([0 for i in range(4)])
    data['wagon_slots'].append([0 for i in range(16)])
    data['wagon_slots'].append([0 for i in range(6)])
    data['wagon_slots'].append([0 for i in range(16)])
    return data

def create_train_and_containers():
    train = create_train()
    train.set_random_weight_capacities(30, 50)
    #print(train)
    containers = list(get_containers_1())

    return train, containers

def main():
    # data = create_data_model()
    train, containers = create_train_and_containers()
    # 1 means there is a container, 0 means there is none
    # Possibly add classes of the containers here so we can get more information
    # Note: this 
    # container_grid = np.asarray(
    #     [
    #     [[1,1],[1,0]],
    #     [[1,0],[0,0]],
    #     [[0,1],[0,0]]
    #     ]) 
    

    # Create the mip solver with the SCIP backend.
    solver = pywraplp.Solver.CreateSolver('SCIP')

    # Variables

    # y[c_i,w_j,s_k] = 1 if container c_i is packed in slot s_k of wagon w_j
    y = {}
    for c_i, _ in enumerate(containers):
        for w_j, wagon in enumerate(train.wagons):
            for index, s_k in enumerate(wagon.get_slots()):
                y[(c_i,w_j,index)] = solver.IntVar(0, 1, 'cont:%i,wagon:%i,slot:%i' % (c_i,w_j,index))

    # Constraints

    # Each container can be in at most one wagon.
    for c_i, _ in enumerate(containers):
        solver.Add(train.c_container_on_wagon(y,c_i))

    # A container has to be put on a wagon as a whole
    for wagon in train.wagons:
        for index, s_k in enumerate(wagon.get_slots()):
            # If s_k has been found before, but s_k is not the one before that, then there is a gap
            # Or s_k has not occured yet, then there is no gap 
            solver.Add(index == 0 or (s_k in wagon.get_slots()[0:index] and index - 1 >= 0 and wagon.get_slots()[index-1] == s_k) or s_k not in wagon.get_slots()[0:index])
            # It might be cleaner to move these tests to a function of the wagon class.

    # The amount packed in each wagon cannot exceed its capacity.
    for w_j, wagon in enumerate(train.wagons):
        solver.Add(
            sum(y[(c_i, w_j, s_k)] * containers[c_i].get_net_weight() # Net weight or gross weight?
                for c_i, _ in enumerate(containers)) <= wagon.get_weight_capacity()
                )
    # The length of the containers cannot exceed the length of the wagon
    for w_j, wagon in enumerate(train.wagons):
        solver.Add(
            sum(y[(c_i,w_j,s_k)] * container.get_length()
            for c_i, container in enumerate(containers)) <= wagon.get_length_capacity()
        )

    # Objectives

    # Objective minimize left over space on wagons
    # Maximize container_lengths, this is possible because there is a contraint that
    # length cant be exceeded
    # objective = solver.Objective()
    # for c_i in data['containers']:
    #     for w_j in data['wagons']:
    #         for index, s_k in enumerate(data['wagon_slots'][w_j]):
    #             # Test if s_k is the first occurance of s_k in the wagon_slots
    #             if s_k not in data['wagon_slots'][0:index]:
    #                 objective.SetCoefficient(
    #                     y[(c_i,w_j,s_k)], 1 #data['container_lengths'][c_i]
    #                 )

    # objective.SetMaximization()

    # This objective tries to maximize the weight of the containers
    # For now this objective works, but we possibly need to change this later
    objective = solver.Objective()
    for c_i, container in enumerate(containers):
        for w_j, wagon in train.wagons:
            for index, s_k in enumerate(wagon.get_slots()):
                objective.SetCoefficient(
                    y[(c_i,w_j,s_k)], container.get_net_weight()
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
