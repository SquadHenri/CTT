from ortools.linear_solver import pywraplp
import numpy as np

# useful links for trying multiple objectives:
# https://stackoverflow.com/questions/65515182/are-multiple-objectives-possible-or-tools-constraint-programming

def create_data_model():
    """Create the data for the example."""
    data = {}
    container_distances = [48, 30, 42, 36, 36, 48, 42, 42, 36, 24, 30, 30, 42, 36, 36]
    container_distances *= 10
    container_weights = [48, 30, 42, 36, 36, 48, 42, 42, 36, 24, 30, 30, 42, 36, 36]
    container_lengths = [10, 30, 25, 50, 35, 30, 15, 40, 30, 35, 45, 10, 20, 30, 25]
    data['container_weights'] = container_weights
    data['container_lengths'] = container_lengths
    data['container_distances'] = container_distances
    data['containers'] = list(range(len(container_weights)))
    data['num_containers'] = len(container_weights)
    num_wagons = 5
    data['wagons'] = list(range(num_wagons))
    data['wagon_weight_capacities'] = [100, 70, 110, 90, 100]
    data['wagon_length_capacities'] = [100,110,90,120,50]
    return data



def main():
    data = create_data_model()

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
    # x[i, j] = 1 if item i is packed in bin j.
    x = {}
    for i in data['containers']:
        for j in data['wagons']:
            x[(i, j)] = solver.IntVar(0, 1, 'x_%i_%i' % (i, j))

    # Constraints
    # Each container can be in at most one wagon.
    for i in data['containers']:
        solver.Add(sum(x[i, j] for j in data['wagons']) <= 1)
    # The amount packed in each wagon cannot exceed its capacity.
    for j in data['wagons']:
        solver.Add(
            sum(x[(i, j)] * data['container_weights'][i]
                for i in data['containers']) <= data['wagon_weight_capacities'][j]
                )
    # The length of the containers cannot exceed the length of the wagon
    for j in data['wagons']:
        solver.Add(
            sum(x[i,j] * data['container_lengths'][i]
            for i in data['containers']) <= data['wagon_length_capacities'][j]
        )

    # Objectives

    # Objective minimize left over space on wagons
    # Maximize container_lengths, this is possible because there is a contraint that
    # length cant be exceeded
    objective = solver.Objective()
    for j in data['wagons']:
        objective.SetCoefficient(
            x[(i,j)], data['container_lengths'][j]
        )
    objective.SetMaximization()

    # Objective2: minimize movement for cranes
    # To test whether two objectives work, this will try to minimize weight
    # objective2 = solver.Objective()
    # for i in data['containers']:
    #     for j in data['wagons']:
    #         objective2.SetCoefficient(x[(i, j)], data['container_distances'][i])
    # objective2.SetMinimization()


    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        print('Total space used:', objective.Value())
        #print('Total packed weight:', objective2.Value())
        total_weight = 0
        total_length = 0
        for j in data['wagons']:
            wagon_weight = 0
            wagon_length = 0
            print('Wagon ', j, '\n')
            for i in data['containers']:
                if x[i, j].solution_value() > 0:
                    print('Item', i, '- weight:', data['container_weights'][i])
                    wagon_weight += data['container_weights'][i]
                    print('Item', i, '- length:', data['container_lengths'][i])
                    wagon_length += data['container_lengths'][i]
            print('Packed wagon weight:', wagon_weight)
            print()
            total_length += wagon_length
            total_weight += wagon_weight
        print('Total packed weight:', total_weight)
        print('Total packed length:', total_length)
    else:
        print('The problem does not have an optimal solution.')


if __name__ == '__main__':
    main()
