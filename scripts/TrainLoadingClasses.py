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
    print(containers[0])

    return train, containers

def main():
    data = create_data_model()
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

    # y[i,j,k] = 1 if container is packed in slot k of wagon j
    y = {}
    for i in data['containers']:
        for j in data['wagons']:
            for k in data['wagon_slots'][j]:
                y[(i,j,k)] = solver.IntVar(0, 1, 'cont:%i,wagon:%i,slot:%i' % (i,j,k))

    # Constraints

    # Each container can be in at most one wagon.
    for i in data['containers']:
        solver.Add(sum(y[(i, j, k)] for j in data['wagons']) <= 1)

    # Each TEU of a container is in a single wagon
    # for i in data['containers']:
    #     for j in data['wagons']:
    #         solver.Add(sum(y[(i, j, k)] for k in data['wagon_slots'][j]) <= data['container_lengths'][i] * 2)

    # A container has to be put on a wagon as a whole
    for j in data['wagons']:
        for index, k in enumerate(data['wagon_slots'][j]):
            # If k has been found before, but k is not the one before that, then there is a gap
            # Or k has not occured yet, then there is no gap 
            solver.Add(index == 0 or (k in data['wagon_slots'][j][0:index] and index - 1 >= 0 and data['wagon_slots'][j][index-1] == k) or k not in data['wagon_slots'][j][0:index])
            # It might be cleaner to move these tests to a function of the wagon class. 
            

    # The amount packed in each wagon cannot exceed its capacity.
    for j in data['wagons']:
        solver.Add(
            sum(y[(i, j, k)] * data['container_weights'][i]
                for i in data['containers']) <= data['wagon_weight_capacities'][j]
                )
    # The length of the containers cannot exceed the length of the wagon
    for j in data['wagons']:
        solver.Add(
            sum(y[(i,j,k)] * data['container_lengths'][i]
            for i in data['containers']) <= data['wagon_length_capacities'][j]
        )

    # Objectives

    # Objective minimize left over space on wagons
    # Maximize container_lengths, this is possible because there is a contraint that
    # length cant be exceeded
    # objective = solver.Objective()
    # for i in data['containers']:
    #     for j in data['wagons']:
    #         for index, k in enumerate(data['wagon_slots'][j]):
    #             # Test if k is the first occurance of k in the wagon_slots
    #             if k not in data['wagon_slots'][0:index]:
    #                 objective.SetCoefficient(
    #                     y[(i,j,k)], 1 #data['container_lengths'][i]
    #                 )

    # objective.SetMaximization()

    # This objective tries to maximize the weight of the containers
    # For now this objective works, but we possibly need to change this later
    objective = solver.Objective()
    for i in data['containers']:
        for j in data['wagons']:
            for index, k in enumerate(data['wagon_slots'][j]):
                objective.SetCoefficient(
                    y[(i,j,k)], data['container_weights'][i]
                )
    objective.SetMaximization()

    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        print('Total space used:', objective.Value())
        total_weight = 0
        total_length = 0
        container_count = 0
        for j in data['wagons']:
            wagon_weight = 0
            wagon_length = 0
            print('Wagon ', j)
            for i in data['containers']:
                # Used to keep track of the containers in the wagon
                # so we print information for each container and not for each slot
                containers_ = []
                for k in data['wagon_slots'][j]:
                    if y[i,j,k].solution_value() > 0:
                        if i in containers_:
                            pass # The container is already in the solution
                        else:
                            containers_.append(i)
                            print('Container', i, '- weight:', data['container_weights'][i],' - length: ', data['container_lengths'][i])
                            wagon_weight += data['container_weights'][i]
                            wagon_length += data['container_lengths'][i]
                            container_count += 1 
            print('Packed wagon weight:', wagon_weight, ' Wagon weight capacity: ', data['wagon_weight_capacities'][j])
            print('Packed wagon length:', wagon_length, ' Wagon length capacity: ', data['wagon_length_capacities'][j])
            total_length += wagon_length
            total_weight += wagon_weight
            print()
        print()
        print('Total packed weight:', total_weight, '(',round(total_weight / sum(data['wagon_weight_capacities']) * 100,1),'%)')
        print('Total packed length:', total_length, '(',round(total_length / sum(data['wagon_length_capacities']) * 100,1),'%)')
        print('Containers packed: ', container_count,"/",len(data['containers']))
    elif status == pywraplp.Solver.FEASIBLE:
        print('The problem does have a feasible solution')
    else:
        print('The problem does not have an optimal solution.')



if __name__ == '__main__':
    main()
