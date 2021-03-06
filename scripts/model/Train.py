__authors__ = "Dennis Maneschijn, Rowin Veneman, Hein Rödel, Maurits Becks"
import matplotlib.pyplot as plt

import math
import random
import numpy as np
import pandas as pd
import json
import pandas as pd
from datetime import date, datetime
from model.Container import Container
from model.Wagon import Wagon
from colors import Color
import os
from pathlib import Path

class Train():

    # wagons should be a list of wagons
    def __init__(self, wagons, containers, wrong_wagons, split, isReversed, max_traveldistance, maxTrainWeight, weightPerc, hide_unplaced, lengthPerc, callcode):
        self.wagons = wagons # This is the list of all the wagons on the train
        #Wagons with null values.
        self.wrong_wagons = wrong_wagons
        #Maximum weight for a train, default = 1600000.
        self.maxWeight = maxTrainWeight
        #Containers for a call.
        self.containers = containers
        #Split position of a train, split 11 means split between 10 and 11.
        self.split = split
        #Max traveldistance per container.
        self.max_traveldistance = max_traveldistance
        #Boolean value indicating whether the train arrived reversed.
        self.isReversed = isReversed

        #Table settings parameters
        #Conditional constraint on weight for which a cell gets a color.
        self.weightPerc = weightPerc
        #Hide or show unplaced containers table.
        self.hide_unplaced = hide_unplaced
        #Conditional constraint to give cell a color at a given threshold.
        self.lengthPerc = lengthPerc


        self.set_location()
        self.placed_containers = []
        self.unplaced_containers = []  
        self.callcode = callcode

        Path(os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop/CTT-trainplanning/' + self.callcode)).mkdir(parents=True, exist_ok=True)
        self.PATH_OUTPUT = str(os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop\CTT-trainplanning\\' + self.callcode + '\\'))      

    # Show the basic information
    def __str__(self):
        return "Train with wagons: \n" + '\n'.join(list(map(str, self.wagons)))
    
    # Show all informatoin
    def __repr__(self):
        return "Train with wagon: \n" + '\n'.join(list(map(repr,self.wagons)))
    
    # Print the wagon values with the containers that filled them
    def print_solution(self):
        total_length_packed = self.get_total_packed_length()
        total_weight_packed = self.get_total_packed_weight()
        total_travel_distance = self.get_total_travel_distance()

        for wagon in self.wagons:
            packed_length = wagon.wagon_length_load()
            packed_weight = wagon.wagon_weight_load()
            travel_distance = wagon.wagon_travel_distance()
            print('Packed wagon weight:', Color.GREEN, packed_weight, Color.END, ' Wagon weight capacity: ', wagon.get_weight_capacity())
            print('Packed wagon length:', Color.GREEN, packed_length, Color.END, ' Wagon length capacity: ', wagon.get_length_capacity())
            print('Wagon travel distance:', travel_distance)
            print('Wagon position:', wagon.get_position(), "Wagon location:", wagon.get_location())
            for container in wagon.get_containers():
                if (len(container.get_position()) == 3) and (container.get_position()[0] <= 52) and (container.get_position()[1] <= 7):
                        print(container.get_containerID())
                        print("Container_ID:", container.get_containerID(), "Location:", container.get_position(), "Distance", Container.get_travel_distance(container.get_position(), wagon.get_location()))
            print()

        print()
        print('Total packed weight:', total_weight_packed, '(',round(total_weight_packed / self.get_total_weight_capacity() * 100,1),'%)')
        print('Total packed length:', total_length_packed, '(',round(total_length_packed / self.get_total_length_capacity() * 100,1),'%)')
        print('Total distance travelled:', total_travel_distance)


    # Maybe check for success, but this is fine for now
    def set_optimal_axle_load(self):
        success = True
        for wagon in self.wagons:
            if(not wagon.set_optimal_axle_load()):
                success = False
        return success
        
    def to_JSON(self, **kwargs):
        result = {}
        result["train"] = kwargs
        for wagon in self.wagons:

            wagon_json = wagon.to_JSON()
            result["train"]["wagons"].append(wagon_json)

        filename = self.callcode + " " + str(datetime.now().strftime("%d-%m-%Y %H%M"))

        with open(self.PATH_OUTPUT + filename + ".json", 'w') as output:
            json.dump(result, output)
        
    def to_CSV(self):
        data = []
        unplaced_containers = self.containers
        for wagon in self.wagons:
            if not wagon.containers:
                wagon_dict = {}
                wagon_dict["wagon_id"] = wagon.wagonID
                wagon_dict["weight_capacity"] = wagon.get_weight_capacity()
                wagon_dict["length_capacity"] = wagon.get_length_capacity()
                wagon_dict["position"] = wagon.get_position()
                wagon_dict["container_id"] = None
                wagon_dict["gross_weight"] = None
                wagon_dict["length"] = None
                wagon_dict["hazard_class"] = None
                data.append(wagon_dict)
                continue
            for container in wagon.containers:
                for unplaced in unplaced_containers:
                    if unplaced == container:
                        unplaced_containers.remove(container)
                wagon_dict = {}
                wagon_dict["wagon_id"] = wagon.wagonID
                wagon_dict["weight_capacity"] = wagon.get_weight_capacity()
                wagon_dict["length_capacity"] = wagon.get_length_capacity()
                wagon_dict["position"] = wagon.get_position()
                wagon_dict["container_id"] = container.get_containerID()
                wagon_dict["gross_weight"] = container.get_gross_weight()
                wagon_dict["length"] = container.get_length()
                wagon_dict["hazard_class"] = container.get_hazard_class()
                data.append(wagon_dict)
        
        unplaced_dict = []
        for container in unplaced_containers:
            container_dict = {}
            container_dict["container_id"] = container.get_containerID()
            container_dict["gross_weight"] = container.get_gross_weight()
            container_dict["length"] = container.get_length()
            container_dict["hazard_class"] = container.get_hazard_class()
            unplaced_dict.append(container_dict)

        df = pd.DataFrame(data)
        unplaced_df = pd.DataFrame(unplaced_dict)

        filename = self.callcode + " " + str(datetime.now().strftime("%d-%m-%Y %H%M"))
        writer = pd.ExcelWriter(self.PATH_OUTPUT + filename + 'planning.xlsx', engine="xlsxwriter")

        df.to_excel(writer, sheet_name="Planning")    
        unplaced_df.to_excel(writer, sheet_name="Unplaced Containers")
        
        writer.save()

    #region getters

    def get_containers(self):
        return self.containers

    def get_split(self):
        return self.split

    def get_max_traveldistance(self):
        return self.max_traveldistance

    def get_reversed_status(self):
        return self.isReversed

    def get_total_packed_length(self):
        length_packed = 0
        for wagon in self.wagons:
            if wagon.containers is None:
                   continue
            length_packed += wagon.wagon_length_load()
        return length_packed

    def get_total_travel_distance(self):
        total_travel_distance = 0
        for wagon in self.wagons:
            total_travel_distance += wagon.wagon_travel_distance()
        return total_travel_distance

    def get_total_packed_weight(self):
        weight_packed = 0
        
        for wagon in self.wagons:
            if wagon.containers is None:
                   return 0
            weight_packed += wagon.wagon_weight_load()
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
    
    # Returns the list of containers placed on a wagon
    def get_placed_containers(self):
        return self.placed_containers

    def get_unplaced_containers(self):
        return self.unplaced_containers

    #endregion

    #region setters
    def set_placed_containers(self, placed_containers):
        self.placed_containers = placed_containers

    def set_unplaced_containers(self, unplaced_containers):
        self.unplaced_containers = unplaced_containers

    # Same as the functions above, but for setting to 1 value
    def set_weight_capacities(self, value):
        for wagon in self.wagons:
            wagon.set_weight_capacity(value)

    # Same as the functions above, but for setting to 1 value
    def set_length_capacities(self, value):
        for wagon in self.wagons:
            wagon.set_weight_capacity(value)

    #endregion

    #region plotters

    def get_container_plot(self, containers):
        
        #Initiliase lists for input matplotlib table
        data = []
        cellColours = []
        #axs[0].set_title('Table 1: Unplaced containers')
        
        #Set column length for table
        column_length = 3

        #Make datachunks of container list
        containerlist = [containers[x:x+column_length] for x in range(0, len(containers), column_length)]
        
        for containers in containerlist:
            datarow = []
            cellRowColour = []
            #Initialise all cell of the table
            if 0 < column_length:
                datarow.extend('' for x in range(0, column_length))
                data.append(datarow)
                cellRowColour.extend('#fefefe' for x in range(0, column_length)) 
                cellColours.append(cellRowColour)

            #Give value to the table cells
            for i, container in enumerate(containers):
                datarow[i] = 'ID: ' + str(container.get_containerID()) + ' | Type: ' + str(container.get_type()) +  ' | Position: ' + str(container.get_position()) + ' | Gross (kg): ' + str(container.get_gross_weight()) + ' | Container Lenght: ' + str(container.get_length()) 
                if container.hazard_class == 1 or container.hazard_class == 2 or container.hazard_class == 3:
                    cellRowColour[i] = '#11aae1'

        return data, cellColours

    
    # Make a table to that represents a train planning
    def get_planning_plot(self):

        # total_length = total length of containers planned on train.
        # total_weight = total weight of containers planned on tainr.
        total_length = self.get_total_packed_length()
        total_weight = self.get_total_packed_weight()
        
        # The amount of containers of the wagon with the most containers. Starts at 0.
        maxContainers = 0
        # for now, columns = rows
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
        #print(wagons)
        for wagon in wagons:
            
            if wagon.containers is None:
                continue
            
            # If wagon contains more containers than maxContainers, set maxContainers to new amount.
            if len(wagon.containers) > maxContainers:
                maxContainers = len(wagon.containers)
                
        data = []
        cellColours = []
        # Loop through all wagons
        title = wagons[0].call
        for wagon in wagons:           
            #Add wagonID to first cell of the row
            columns.append(str(int(wagon.position))+ ". " + wagon.wagonID)
            datarow = []
            cellRowColour = []
        
            # Initialize all cells with "empty" and basic grey color
            if 0 < maxContainers: 
                # We do maxContainers + 2, since we want to add two more columns that contain information.
                datarow.extend('' for x in range(0, maxContainers + 4))
                cellRowColour.extend('#fefefe' for x in range(0, maxContainers + 4)) 
            
            # If the wagon is empty, we set the lengts and weight to 0%
            if wagon.containers is None: 
                datarow[len(datarow) - 4] = "0/" + str(wagon.get_weight_capacity()).split(".")[0] + " (0%)"
                datarow[len(datarow) - 3] = "0/" + str(wagon.get_length_capacity()).split(".")[0] + " (0%)"
                datarow[len(datarow) - 2] = str(int(wagon.number_of_axles))
                datarow[len(datarow) - 1] = "0"   
                data.append(datarow)
                cellColours.append(cellRowColour) 
                continue

            wagon_weight = wagon.wagon_weight_load()
            wagon_length = wagon.wagon_length_load()
            # Place all containers in the cells
            for i, container in enumerate(wagon.containers):
                #wagon_weight += container.get_gross_weight()
                #wagon_length += container.get_length()
                datarow[i] = container.containerID + " (" + str(container.get_actual_length() / 20) + " | " + str(int(container.get_gross_weight() / 1000)) + ")"
                # orange #ff6153
                # dark green #498499
                if str(container.hazard_class).startswith("1") or str(container.hazard_class).startswith("2") or str(container.hazard_class).startswith("3"):
                    cellRowColour[i] = '#11aae1'

            # Calculate the packed weight and length of a wagon.
            weight_perc = round((wagon_weight/wagon.get_weight_capacity()) * 100, 1)
            length_perc = round((wagon_length/wagon.get_length_capacity()) * 100, 1)

            # Set the final two columns to the packed weight and packed length
            datarow[len(datarow) - 4] = str(wagon_weight) + "/" + str(wagon.get_weight_capacity()).split(".")[0] + " ("+str(weight_perc)+ "%)"
            datarow[len(datarow) - 3] = str(wagon_length) + "/" + str(wagon.get_length_capacity()).split(".")[0] + " ("+str(length_perc)+ "%)"
            datarow[len(datarow) - 2] = str(int(wagon.number_of_axles))
            datarow[len(datarow) - 1] = str(int(wagon.highest_axle_load))

            if wagon.highest_axle_load >= 22000:
                cellRowColour[maxContainers+3] = '#ff6153'

            # If 90% of the weight is used, make the column red.
            
            if weight_perc >= self.weightPerc:
                cellRowColour[maxContainers] = '#ff6153'
            
            if length_perc >= self.lengthPerc:
                cellRowColour[maxContainers+1] = '#d3f8d3'

            # Add the row for this wagon to the list of all rows.
            cellColours.append(cellRowColour)
            data.append(datarow)
        
        # Add a final row, that is called Total, that contains the total weight and length of the train.
        datarow = []
        cellRowColour = []
        columns.append("Total")
        datarow.extend('' for x in range(0, maxContainers + 4))
        cellRowColour.extend('#fefefe' for x in range(0, maxContainers + 4)) 
        datarow[len(datarow) - 4] = str(total_weight) + "/" + str(self.get_total_weight_capacity()).split(".")[0] + " ("+str(round((total_weight/self.get_total_weight_capacity()) * 100, 1))+ " %)"
        datarow[len(datarow) - 3] = str(total_length) + "/" + str(self.get_total_length_capacity()).split(".")[0] + " ("+str(round((total_length/self.get_total_length_capacity()) * 100, 1))+ " %)"
        
        #datarow[len(datarow) - 2] = ""
        #datarow[len(datarow) - 1] = "" 
        cellColours.append(cellRowColour)
        data.append(datarow)

        # Set the column titles to slot x, and the last two to Wagon Weight and Wagon Length
        n_rows = len(data)
        rows = ['slot %d' % (x+1) for x in range(len(data))]
        rows[maxContainers] = "Wagon Gross Weight"
        rows[maxContainers + 1] = "Wagon Length"
        rows[maxContainers + 2] = "Axles"
        rows[maxContainers + 3] = "Highest Axle Load"
        
        # Set the text to the cells
        cell_text = []
        for row in range(n_rows):
            cell_text.append(['%s' % (x) for x in data[row]])
        
        # @TODO Find out what .reverse() does.
        cell_text.reverse()
        
        #CTT Green color: #8bc53d
        #CTT Blue color: #11aae1
        rcolors = np.full(n_rows, '#8bc53d')
        ccolors = np.full(n_rows, '#8bc53d')
        rcolors[-1] = '#fff'

        return data, columns, rcolors, cellColours, ccolors, rows, title


    #Get plot with unplaced containers table and planning table
    def get_tableplot(self, unplaced_containers):
        
        fig = None
        axs = None        
        planning_table = None
        container_table = None
        title = 'planning'
        unknown_wagonlist = []
        
        #Create a list of wagons with null values to list as footnote of table
        for wagon in self.wrong_wagons:
            unknown_wagonlist.append(str(int(wagon.wagonPosition)) + ". " + wagon.wagonID)

        #Check there are unplaced containers, if yes show in table plot
        if(len(unplaced_containers) > 0) and self.hide_unplaced is not True: 
            #Create figure and 2 axis to stack to tables
            fig, axs = plt.subplots(2,1)
            #Create container table
            t2data, t2cellColours = self.get_container_plot(unplaced_containers)
            container_table = axs[0].table(cellText=t2data,
                    cellColours=t2cellColours,
                    loc='center',
                    cellLoc='center')
            container_table.auto_set_column_width(col=list(range(3)))
            #Create planning table
            t1data, t1columns, t1rcolors, t1cellColours, t1ccolors, t1rows, t1title = self.get_planning_plot()
            title = t1title
            planning_table = axs[1].table(cellText=t1data,
                    rowLabels=t1columns,
                    rowColours=t1rcolors,
                    cellColours=t1cellColours,
                    colColours=t1ccolors,
                    colLabels=t1rows,
                    cellLoc='center',
                    loc='center')
            planning_table.auto_set_column_width(col=list(range(len(t1rows))))
        #If there are no unplaced containers, only show the planning plot and take full space
        else:
            fig, axs = plt.subplots()
            t1data, t1columns, t1rcolors, t1cellColours, t1ccolors, t1rows, t1title = self.get_planning_plot()
            title = t1title
            planning_table = plt.table(cellText=t1data,
                    rowLabels=t1columns,
                    rowColours=t1rcolors,
                    cellColours=t1cellColours,
                    colColours=t1ccolors,
                    colLabels=t1rows,
                    cellLoc='center',
                    loc='center')

            planning_table.auto_set_column_width(col=list(range(len(t1rows))))

        #Formatting container table
        if container_table is not None:
            container_table.auto_set_font_size(False)
            container_table.set_fontsize(8)
            axs[0].axis('tight')
            axs[0].axis('off')  

        #Formatting planning table
        if planning_table is not None:
            planning_table.auto_set_font_size(False)
            planning_table.set_fontsize(8)
            
        
        #Plot layout settings
        plt.subplots_adjust(left=0, bottom=0.26, right=0.986, top=0.8)
        plt.axis('tight')
        plt.axis('off')
        
        # If no current figure exists, a new one is created using figure()
        fig = plt.gcf()
        # Figure title including date string: dd/mm/YY H:M:S
        fig.suptitle(title + " on " + datetime.now().strftime("%d/%m/%Y %H:%M:%S \n" 
        + " Reversed: " + str(self.isReversed) 
        + ", Split: " + str(self.split) 
        + ", MaxTravel: " + str(self.max_traveldistance)
        + "\nWeight Threshold: " + str(self.weightPerc)
        + ", Length Threshold: " + str(self.lengthPerc)
        + ", Hide Unplaced containertable: " + str(self.hide_unplaced)), weight='bold', fontsize=10)

        # Display all unknown wagons with null values in the footnote, color: red.
        if len(unknown_wagonlist) > 0:
            plt.figtext(0.8, 0.01, "[WARNING] Missing information for the following wagon(s): \n" + str(unknown_wagonlist),
                horizontalalignment='right',
                size=7,
                weight='bold',
                color='#ff0000'
            )
        else:
            plt.figtext(0.8, 0.01, "The train is split between wagon " + str(int(self.split) - 1) + " and wagon " + str(int(self.split)) + '.',
                horizontalalignment='right',
                size=7,
                weight='light',
                color='#000'
            )
        
        #Save figure as png image
        # Month abbreviation, day and year	
        currentdate = date.today().strftime("%b-%d-%Y")
        plt.savefig(title + '-planning-' + currentdate, bbox_inches='tight', dpi=150)
        return plt
        

    #endregion


    # Sets the location of the wagon takes a list of all the containers in the train
    def set_location(self):
                
        xlen = 0
        y_val = 0
        result = []

        if len(self.wagons) == 0:
            raise TypeError("No wagons")

        for wagon in self.wagons:
            if pd.notna(self.split) and self.split != None:
                if wagon.position < self.split:
                    wagon.location = [math.ceil((xlen + 0.5 * wagon.total_length)/6.1), y_val]
                    xlen += wagon.total_length
                    if wagon.location[1] == 0:
                        splitshift = wagon
                
                elif wagon.position == self.split:
                    xlen = 0
                    #self.split = 100
                    y_val = -1
                    wagon.location = [math.ceil((xlen + 0.5 * wagon.total_length)/6.1), y_val]
                    xlen += wagon.total_length
                else:
                    wagon.location = [math.ceil((xlen + 0.5 * wagon.total_length)/6.1), y_val]
                    xlen += wagon.total_length
            else:
                if (xlen + wagon.total_length) < 320:
                    wagon.location = [math.ceil((xlen + 0.5 * wagon.total_length)/6.1), y_val]
                    xlen += wagon.total_length
                    if wagon.location[1] == 0:
                        splitshift = wagon

                else:
                    xlen = 0
                    y_val = -1
                    wagon.location = [math.ceil((xlen + 0.5 * wagon.total_length)/6.1), y_val]
                    xlen += wagon.total_length

            result.append(wagon)
        # See where the last wagon in located to calculate the shift the 2nd row of wagons hast to make

        shift_wagon = splitshift
        shift_wagon_xloc = shift_wagon.location[0]
        shift_wagon_length = shift_wagon.total_length
        x_shift = (52 - math.ceil(shift_wagon_length / 2 / 6.1)) - shift_wagon_xloc

        for wagon in self.wagons:
            if wagon.location[1] == 0:
                wagon.location[0] += x_shift

        shift_wagon = self.wagons[len(self.wagons)-1]
        shift_wagon_xloc = shift_wagon.location[0]
        shift_wagon_length = shift_wagon.total_length
        x_shift = (52 - math.ceil(shift_wagon_length / 2 / 6.1)) - shift_wagon_xloc

        for wagon in self.wagons:
            if wagon.location[1] == -1:
                wagon.location[0] += x_shift

        return result
