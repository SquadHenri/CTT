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
    # x[i, j] = 1 if item i is packed in wagon j.
    x = {}
    for i in data['containers']:
        for j in data['wagons']:
            x[(i, j)] = solver.IntVar(0, 1, 'x_%i_%i' % (i, j))

    # Constraints
    # Each container can be in at most one wagon.
    for i in data['containers']:
        solver.Add(sum(x[(i, j)] for j in data['wagons']) <= 1)
    # The amount packed in each wagon cannot exceed its capacity.
    for j in data['wagons']:
        solver.Add(
            sum(x[(i, j)] * data['container_weights'][i]
                for i in data['containers']) <= data['wagon_weight_capacities'][j]
                )
    # The length of the containers cannot exceed the length of the wagon
    for j in data['wagons']:
        solver.Add(
            sum(x[(i,j)] * data['container_lengths'][i]
            for i in data['containers']) <= data['wagon_length_capacities'][j]
        )

    # Objectives

    # Objective minimize left over space on wagons
    # Maximize container_lengths, this is possible because there is a contraint that
    # length cant be exceeded
    objective = solver.Objective()
    for i in data['containers']:
        for j in data['wagons']:
            objective.SetCoefficient(
                x[(i,j)], data['container_lengths'][j]
        )
    objective.SetMaximization()


    # Objective2: minimize movement for cranes
    # To test whether two objectives work, this will try to minimize weight
    # objective = solver.Objective()
    # for i in data['containers']:
    #      for j in data['wagons']:
    #          objective.SetCoefficient(x[(i, j)], data['container_distances'][i])
    # objective.SetMinimization()


    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        print('Total space used:', objective.Value())
        total_weight = 0
        total_length = 0
        container_count = 0
        for j in data['wagons']:
            wagon_weight = 0
            wagon_length = 0
            print('Wagon ', j, '\n')
            for i in data['containers']:
                if x[i, j].solution_value() > 0:
                    print('Container', i, '- weight:', data['container_weights'][i],' - length: ', data['container_lengths'][i])
                    wagon_weight += data['container_weights'][i]
                    wagon_length += data['container_lengths'][i]
                    container_count += 1
            print('Packed wagon weight:', wagon_weight)
            print('Packed wagon length:', wagon_length)
            total_length += wagon_length
            total_weight += wagon_weight
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