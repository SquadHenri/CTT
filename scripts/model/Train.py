import random
from model.Wagon import Wagon
import functions
import numpy as np
import matplotlib.pyplot as plt
import json
from datetime import date, datetime


class Train():

    
    # wagons should be a list of wagons
    def __init__(self, wagons):
        self.wagons = wagons # This is the list of all the wagons on the train
        self.maxWeight = 1000000000
    
    # Create some wagons, to use for testing
    def test_train(self):
        wagon1 = Wagon(0, 100, 5, None, [0,0])
        wagon2 = Wagon(1, 110, 7, None, [0,1])
        wagon3 = Wagon(2, 130, 6, None, [1,0])
        wagon4 = Wagon(3, 150, 9, None, [1,0])
        wagon5 = Wagon(4, 140, 8, None, [0,2])
        return Train([wagon1, wagon2, wagon3, wagon4, wagon5])

    # Show the basic information
    def __str__(self):
        return "Train with wagons: \n" + '\n'.join(list(map(str, self.wagons)))
    
    # Show all informatoin
    def __repr__(self):
        return "Train with wagon: \n" + '\n'.join(list(map(repr,self.wagons)))
    
    # Print the wagon values with the containers that filled them
    def print_solution(self):
        for wagon in self.wagons:
            wagon.print_solution()

    # Maybe check for success, but this is fine for now
    def set_optimal_axle_load(self):
        for wagon in self.wagons:
            wagon.set_optimal_axle_load()
            
    def to_JSON(self, **kwargs):
        result = {}
        result["train"] = kwargs
        for wagon in self.wagons:

            wagon_json = wagon.to_JSON()
            result["train"]["wagons"].append(wagon_json)

            # wagon_dict = {}
            # wagon_dict["wagon_id"] = wagon.wagonID
            # wagon_dict["weight_capacity"] = wagon.get_weight_capacity()
            # wagon_dict["length_capacity"] = wagon.get_length_capacity()
            # wagon_dict["position"] = wagon.get_position()
            # wagon_dict["containers"] = []
            # if not wagon.containers:
            #     continue
            # for container in wagon.get_containers():
            #     container_dict = {}
            #     container_dict["container_id"] = container.get_containerID()
            #     container_dict["gross_weight"] = container.get_gross_weight()
            #     container_dict["length"] = container.get_length()
            #     container_dict["hazard_class"] = container.get_hazard_class()
            #     wagon_dict["containers"].append(container_dict)

            # result["train"]["wagons"].append(wagon_dict)

        with open('train.json', 'w') as output:
            json.dump(result, output)



    # Maybe split this up, but for now this is fine
    def get_total_capacity(self):
        total_length = 0
        total_weight = 0
        for wagon in self.wagons:
            total_length += wagon.length_capacity
            total_weight += wagon.weight_capacity
        return total_length, total_weight

    def get_total_packed_weight(self):
        weight_packed = 0
        
        
        for wagon in self.wagons:
            if wagon.containers is None:
                   return 0
            for i, container in enumerate(wagon.containers):
                    weight_packed += container.gross_weight
        return weight_packed
    
    def get_total_weight_capacity(self):
        total_weight = 0
        for wagon in self.wagons:
            total_weight += wagon.weight_capacity
        return total_weight

    def get_total_length_capacity(self):
        total_length = 0
        for wagon in self.wagons:
            total_length += wagon.length_capacity
        return total_length
        
    # Set the weight capacities of the wagons to a value between min and max
    def set_random_weight_capacities(self, min, max):
        for wagon in self.wagons:
            wagon.set_weight_capacity(get_random_value(min, max))

    # Same as the functions above, but for setting to 1 value
    def set_weight_capacities(self, value):
        for wagon in self.wagons:
            wagon.set_weight_capacity(value)

    # Set the weight capacities of the wagons to a value between min and max
    def set_random_length_capacities(self, min, max):
        for wagon in self.wagons:
            wagon.set_length_capacity(get_random_value(min, max))

    # Same as the functions above, but for setting to 1 value
    def set_length_capacities(self, value):
        for wagon in self.wagons:
            wagon.set_weight_capacity(value)

    # Make a table to that represents a train planning
    def get_tableplot(self):
            
        maxContainers = 0
        columns = []
        #Sort wagons on their position
        wagons = self.wagons
        l = len(wagons)
        for i in range(0, l): 
            for j in range(0, l-i-1): 
                if (wagons[j].position > wagons[j + 1].position): 
                    tempo = wagons[j] 
                    wagons[j]= wagons[j + 1] 
                    wagons[j + 1]= tempo 

        #Set max number of containers on wagon, needed for amount of table rows 
        for wagon in wagons:
            if wagon.containers is None:
                raise TypeError("No containers selected")
            
            if len(wagon.containers) > maxContainers:
                maxContainers = len(wagon.containers)
        title = ''
        data = []
        cellColours = []
        for wagon in wagons:
            #Add wagonID to column list
            columns.append(str(int(wagon.position))+ ". " + wagon.wagonID)
            datarow = []
            cellRowColour = []
            #Title of table
            title = wagon.call
            if 0 < maxContainers: 
                datarow.extend('empty' for x in range(0, maxContainers))
                cellRowColour.extend('#fefefe' for x in range(0, maxContainers)) 
                #datarow.append(maxContainers) 

            for i, container in enumerate(wagon.containers):
                datarow[i] = container.containerID
                if container.gross_weight > 30000:
                    cellRowColour[i] = '#cc244b'
                # orange #ff6153
                # dark green #498499
                print(container.typeid)
                if container.goods == 1 or container.goods == 2 or container.goods == 3:
                    cellRowColour[i] = '#11aae1'

            cellColours.append(cellRowColour)
            data.append(datarow)
        print(data)
        n_rows = len(data)
        rows = ['slot %d' % (x+1) for x in range(len(data))]
        print(rows)
        
        cell_text = []
        for row in range(n_rows):
            cell_text.append(['%s' % (x) for x in data[row]])
        
        cell_text.reverse()
        #CTT Green color: #8bc53d
        #CTT Blue color: #11aae1
        rcolors = np.full(n_rows, '#8bc53d')
        ccolors = np.full(n_rows, '#8bc53d')
        

        the_table = plt.table(cellText=data,
                    rowLabels=columns,
                    rowColours=rcolors,
                    cellColours=cellColours,
                    colColours=ccolors,
                    colLabels=rows,
                    loc='center')
        plt.subplots_adjust(left=0.230, bottom=0, right=0.965, top=0.938)
        plt.axis('off')
        #plt.title(title, fontsize=8, pad=None, )
   
        # Month abbreviation, day and year	
        currentdate = date.today().strftime("%b-%d-%Y")
        

        now = datetime.now()
 
        print("now =", now)

        # dd/mm/YY H:M:S
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

        fig = plt.gcf()
        
        train_weight = str(self.get_total_packed_weight())
        plt.figtext(0.95, 0.05, "Total weight: " + train_weight,
            horizontalalignment='right',
            size=6,
            weight='light',
            color='#000'
           )


        fig.suptitle(title + " on " + datetime.now().strftime("%d/%m/%Y %H:%M:%S"), fontsize=10)
        plt.savefig(title + '-planning-' + currentdate, bbox_inches='tight', dpi=150)
        return plt
        


    # CONSTRAINTS

    # UNUSED/UNFINISHED CONSTRAINTS

    # Travel distance constraint
    # def c_container_travel_distance(self, y, c_i, container):
    #     for w_j, wagon in enumerate(self.wagons):
    #         for s_k, _ in enumerate(wagon.get_slots()):
    #             # If the container is on the wagon, add the constraint.
    #             if y[(c_i, w_j, s_k)] == 1:
    #                 # The difference in position between the container and the wagon may not be larger than 50 metres.
    #                 return functions.getTravelDistance(container.get_position(), wagon.get_location()) < 50



    #Total weight of train may not surpass the maximum allowed weight on the track.
    #Later on we need to replace 100000000 with the max weight of the location of the train.
    # def c_max_train_weight(self, y, containers):
    #     slot_found = False
    #     total_weight = 0
    #     for c_i, container in enumerate(containers):
    #         for w_j, wagon in enumerate(self.wagons):
    #             for s_k, _ in enumerate(wagon.get_slots()):
    #                 if y[(c_i, w_j, s_k)] == 1:
    #                     print(container.get_gross_weight())
    #                     total_weight += container.get_gross_weight()
    #                     slot_found = True
    #                     break
    #         if slot_found:
    #             break
    #     print(total_weight)
    #     return total_weight < self.maxWeight

    # Contents constraint
    # def c_container_location_valid(self, x, c1_i, c2_i, container_1, container_2):
    #     c1_pos = 0
    #     c2_pos = 0
    #     #print(c1_i)
    #     #print(c2_i)
    #     for w_j, wagon in enumerate(self.wagons):
    #             # get the positions of both wagons
    #             if(x[(c1_i, w_j)] == 1):
    #                 c1_pos = wagon.get_position()
    #                 print(c1_pos)
    #             elif(x[(c2_i, w_j)] == 1):
    #                 c2_pos = wagon.get_position()
    #                 print(c2_pos)
    #     # make sure that the wagon positions >= 2, so that there is 1 wagon in between.
    #     return abs(c1_pos - c2_pos) >= 2


def get_random_value(min, max):
    if min == max:
        return min
    elif min > max:
        return random.randint(max * 2, min * 2) / 2
    elif max > min:
        return random.randint(min * 2, max * 2) / 2



    