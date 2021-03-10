from ortools.linear_solver import pywraplp
from colors import Color
from model import *
from data import getContainersFromCSV
import functions
import json

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
        print("Container ", i, "is hazardous")
        containers[i].set_hazard_class(1)

    print(train)
    return train, containers

def main(containers, train):
    # data = create_data_model()
    #train, containers = create_train_and_containers()

    priority_list = []

    # Set some random containers to be in the priority list.
    for i in range(0, len(containers), 10):
        print("Container ", i, "Must be loaded")
        priority_list.append(i)

    # # Make every sixth container hazardous
    # for i in range(0, len(containers), 10):
    #     print("Container ", i, "is hazardous")
    #     containers[i].set_hazard_class(1)

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

    # All containers in the priority list need to be loaded on the train, no matter what.
    for c_i in priority_list:
        solver.Add(sum(x[(c_i,w_j)] for w_j, _ in enumerate(train.wagons)) == 1)

    # Each container can be in at most one wagon.
    for c_i, container in enumerate(containers):
        if container not in priority_list:
            solver.Add(sum(x[(c_i, w_j)] for w_j, _ in enumerate(train.wagons)) <= 1)

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
    
    #Travel distance constraint for total distance.
    solver.Add(sum(x[(c_i, w_j)] * functions.getTravelDistance(container.get_position(), wagon.get_location()) 
        for c_i, container in enumerate(containers) 
        for w_j, wagon in enumerate(train.wagons) 
        if (len(container.get_position()) == 3) and 
        (container.get_position()[0] <= 52) and 
        (container.get_position()[1] <= 7) ) <= 500)

    # #Travel distance constraint per container
    # for c_i, container in enumerate(containers):
    #     # For every container add the travel distance constraint.
    #     c_location = container.get_position()
    #     if (len(c_location) == 3) and (c_location[0] <= 52) and (c_location[1] <= 7):
    #         solver.Add( sum(x[(c_i, w_j)] * functions.getTravelDistance(c_location, wagon.get_location()) for w_j, wagon in enumerate(train.wagons)) <= 10000)


    # A train may not surpass a maximum weight, based on the destination of the train.
    solver.Add(sum(x[(c_i, w_j)] * container.get_gross_weight() 
    for c_i, container in enumerate(containers) 
    for w_j, wagon in enumerate(train.wagons)) <= train.maxWeight)


    # UNUSED/UNFINISHED CONSTRAINTS

    # Loop through the container list of the wagon
    # find all possible order (shuffles) of the list
    # Make sure that there is at least one shuffle that does not exceed the axle load



    # A container has to be put on a wagon as a whole
    # for w_j, wagon in enumerate(train.wagons):
    #     solver.Add(
    #         wagon.c_container_is_whole(y, len(containers), w_j)
    #         )


    #Contents constraint
    # Example of GitHub Jobshop might not work since his locations of the machines are somewhat predefined
    # We only know the starting positions of the containers, but we need to know the positions of the containers on the train.

    # make list of pairs of containers that are allready added to the constraint.
    # added = []
    # for c1_i, container1 in enumerate(containers):
    #     for c2_i, container2 in enumerate(containers):
    #         # Check we are not working with the same containers
    #         if c1_i != c2_i:
    #             # If the pair of containers has not yet been added, we continue
    #             if (c1_i, c2_i) not in added and (c2_i, c1_i) not in added:
    #                 # If both containers are in a hazard class, add the constraint
    #                 if container1.hazard_class != None and container2.hazard_class != None:
    #                     print("Adding", c1_i, c2_i)
    #                     solver.Add(train.c_container_location_valid(x, c1_i, c2_i, container1, container2))

    #                     # ======================================
    #                     # Try something with a seperate function.
    #                     # ======================================


    #                     # The difference in position >= 2.
    #                     # We need to fix something for -2.
    #                     # solver.Add(
    #                     #     sum((x[(c1_i, w_j)] * wagon.get_position()) - (x[(c2_i, w_j)] * wagon.get_position()) for w_j, wagon in enumerate(train.wagons)) >= 2
    #                     #     )
    #                     # if sum(x[(c1_i, w_j)] * wagon.get_position() - x[(c2_i, w_j)] * wagon.get_position() for w_j, wagon in enumerate(train.wagons)) >= 0:
    #                     #     solver.Add(sum(x[(c1_i, w_j)] * wagon.get_position() - x[(c2_i, w_j)] * wagon.get_position() for w_j, wagon in enumerate(train.wagons)) >= 2)
    #                     # else:
    #                     #     solver.Add(sum(x[(c1_i, w_j)] * wagon.get_position() - x[(c2_i, w_j)] * wagon.get_position() for w_j, wagon in enumerate(train.wagons)) <= -2)
                        
    #                     # Add the pair of containers to the added list
    #                     added.append((c1_i, c2_i))
    #                     added.append((c2_i, c1_i))


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

    import numpy as np
    import matplotlib.pyplot as plt

    def get_tableplot(train):
            
            maxContainers = 0
            columns = []

            wagons = train.wagons
            #Sort wagons on their position
            l = len(wagons)
            for i in range(0, l): 
                for j in range(0, l-i-1): 
                    if (wagons[j].position > wagons[j + 1].position): 
                        tempo = wagons[j] 
                        wagons[j]= wagons[j + 1] 
                        wagons[j + 1]= tempo 
            
        
            #Set max number of containers on wagon, needed for amount of table rows 
            for wagon in wagons:
                if len(wagon.containers) > maxContainers:
                    maxContainers = len(wagon.containers)
            title = ''
            data = []
            for wagon in wagons:
                #Add wagonID to column list
                columns.append(str(int(wagon.position))+ ". " + wagon.wagonID)
                datarow = [] 
                #Title of table
                title = wagon.call
                if 0 < maxContainers: 
                    datarow.extend('empty' for x in range(0, maxContainers)) 
                    #datarow.append(maxContainers) 

                for i, container in enumerate(wagon.containers):
                    datarow[i] = container.containerID

                data.append(datarow)
            print(data)
            n_rows = len(data)
            rows = ['slot %d' % (x+1) for x in range(len(data))]
            print(rows)
            colors = plt.cm.BuPu(np.linspace(0, 0.5, len(rows)))

            cell_text = []
            for row in range(n_rows):
                cell_text.append(['%s' % (x) for x in data[row]])
            # Reverse colors and text labels to display the last value at the top.
            colors = colors[::-1]
            cell_text.reverse()
            
            the_table = plt.table(cellText=data,
                      rowLabels=columns,
                      rowColours=colors,
                      colLabels=rows,
                      loc='center')
            plt.subplots_adjust(left=0.230, bottom=0, right=0.965, top=0.938)
            plt.axis('off')
            #plt.title(title, fontsize=8, pad=None, )

            fig = plt.gcf()
            fig.suptitle(title, fontsize=10)
            plt.savefig(title + '-planning', bbox_inches='tight', dpi=150)
            plt.show()
            



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
            
        #print(filled_wagons)
        print()
        print('Total packed weight:', total_weight, '(',round(total_weight / train.get_total_weight_capacity() * 100,1),'%)')
        print('Total packed length:', total_length, '(',round(total_length / train.get_total_length_capacity() * 100,1),'%)')
        print('Total distance travelled:', total_distance)
        print('Containers packed: ', container_count,"/",len(containers))

        # for container in containers:
        #     if container not in filled_wagons.values():
        #         print("unplanned", container)

        # This is another way of printing solution values
        #train.print_solution()
        train.to_JSON(callcode="BASEL12345", weight=total_weight, length=total_length, distance=total_distance, amount=container_count, wagons=[])

        with open('result.json', 'w') as fp:
            json.dump(filled_wagons, fp)

        get_tableplot(train)

    elif status == pywraplp.Solver.FEASIBLE:
        print('The problem does have a feasible solution')
    else:
        print('The problem does not have an optimal solution.')

       

        
    
    
    
   



# if __name__ == '__main__':
#     main()
