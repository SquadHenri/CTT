from numpy.lib.function_base import place
import pandas

from model.Wagon import Wagon
from model.Train import Train
from model.Container import Container
import TrainLoadingConstraint



dataset = pandas.read_csv('data\input_df_4c150a83-346f-4719-89b0-c691242fe383.csv')

def setup(dataset):
    containerlist = []
    wagonlist = []

    #Set parameters
    max_traveldistance = 50
    if dataset.MAXTRAVELDISTANCE[1] is not None:
        max_traveldistance = dataset.MAXTRAVELDISTANCE[1]
    max_traveldistance = 15

    split = None 
    if dataset.TRAINSPLIT[1] is not None:
        split = dataset.TRAINSPLIT[1]
    split = 11

    isReversed = False
    if dataset.TRAINREVERSED[1] is not None and dataset.TRAINREVERSED[1] == 1:
        isReversed = True
    
    maxTrainWeight = 1600
    if dataset.MaxTrainWeight[1] is not None:
        maxTrainWeight = dataset.MaxTrainWeight[1]

    weightPerc = 90
    if dataset.WeightPerc[1] is not None:
        maxTrainWeight = dataset.WeightPerc[1]
    
    hide_unplaced = False
    if dataset.HideUnplacedContainers[1] is not None and dataset.HideUnplacedContainers[1] == True:
        hide_unplaced = True
    
    lengthPerc = 100
    if dataset.LengthPerc[1] is not None:
        lengthPerc = dataset.LengthPerc[1]

    for i, value in enumerate(dataset.WAGON):
        if pandas.notna(value):
            wagonID = value
            wagonType = dataset.WAGTYPE[i]
            wagonTare = dataset.TARE[i]
            wagonSizeft = dataset.SIZEFT[i]
            wagonNoAxes = dataset.NRAXES[i]
            wagonMaxTEU = dataset.MAXTEU[i]
            wagonLenght = dataset.LEN[i]
            wagonPosition = dataset.WPOS[i]
            wagonPayload = dataset.PAYLOAD[i]
            wagonTare = dataset.TARE[i]
            wagonTrack = dataset.TRACK[i]
            wagonCall = dataset.CALLCODE[i]
            wagonlist.append([wagonID, wagonType, wagonSizeft, wagonNoAxes, wagonMaxTEU, wagonLenght, wagonPosition, wagonPayload, wagonCall, wagonTare, wagonTrack])

    for i, value in enumerate(dataset.CONTAINERNUMBER):
        if pandas.notna(value):
            containerID = value
            containerType = dataset.UNITTYPE[i]
            unNR = dataset.UNNR[i]
            unKlasse = dataset.UNKLASSE[i]
            nettWeight = dataset.UNITWEIGHTNETT[i]
            terminalWeightNett = dataset.TERMINALWEIGHTNETT[i]
            containerTEU = dataset.TEUS[i]
            containerPosition = dataset.COMPOUNDPOS[i]
            containerTarra = dataset.CONTAINERTARRA[i]
            containerCall = dataset.CALLCODE[i]
            containerlist.append([containerID, containerType, unNR, unKlasse, nettWeight, terminalWeightNett, containerTEU, containerPosition, containerTarra, containerCall])
    #Creating dataframes from container en wagon lists
    wagondf = pandas.DataFrame(wagonlist, columns =['wagonID', 'wagonType', 'wagonSizeft', 'wagonNoAxes', 'wagonMaxTEU', 'wagonLength', 'wagonPosition', 'wagonPayload', 'wagonCall', 'wagonTare', 'wagonTrack'])
    containerdf = pandas.DataFrame(containerlist, columns =['containerID', 'containerType', 'unNR', 'unKlasse', 'nettWeight', 'terminalWeightNett', 'containerTEU', 'containerPosition', 'containerTarra', 'containerCall'])
    
    #print(wagondf)
    wagondf = wagondf.sort_values(by='wagonPosition')
    
    #Reverse wagons if neccesary
    if isReversed:
        wagondf = wagondf[::-1]
        wagondf = wagondf.reset_index(drop=True)
        for i, wagon in wagondf.iterrows():
            wagondf.at[i, 'wagonPosition'] = i+1

    # Remove all wagons and containers that contain Null values
    wagons = []
    containers = []
    wrong_wagons = []    
    null_containers = []
    for index, wagon in wagondf.iterrows():
        if pandas.notna(wagon['wagonSizeft']) and pandas.notna(wagon['wagonLength']) and pandas.notna(wagon['wagonPosition']) and pandas.notna(wagon['wagonPayload']) and pandas.notna(wagon['wagonTare']) and pandas.notna(wagon['wagonNoAxes']): 
            wagonID = wagon['wagonID']
            weight_capacity = wagon['wagonPayload']
            length_capacity = wagon['wagonSizeft']
            total_length = wagon['wagonLength']
            position = wagon['wagonPosition'] 
            number_of_axles = wagon['wagonNoAxes']
            wagon_weight = wagon['wagonTare']
            call = wagon['wagonCall']
            wagonObj = Wagon(wagonID, weight_capacity, length_capacity, 0, position, number_of_axles, total_length, wagon_weight, call)
            wagons.append(wagonObj)
        else:
            # print("Wagon", index, "contained null values.")
            null_containers.append(index)
            wrong_wagons.append(wagon)

    print("Containers with indices: ", null_containers, " contain null values.")

    for index, container in containerdf.iterrows():
        containerID = container['containerID']
        gross_weight = int(container['nettWeight']) + int(container['containerTarra'])
        net_weight = container['nettWeight']
        foot = int(20 * container['containerTEU'])
        actual_length = foot
        if foot > 20 and foot < 30:
            foot = 30
        position = str(container['containerPosition'])
        goods = container['unKlasse']
        priority = 1
        typeid = container['containerType']
        hazard_class = container['unKlasse']
        
        containerObj = Container(containerID, gross_weight, net_weight, foot, position, goods, priority, typeid, hazard_class, actual_length)
        containers.append(containerObj)
    return Train(wagons, containers, wrong_wagons, split, isReversed, max_traveldistance, maxTrainWeight, weightPerc, hide_unplaced, lengthPerc)

if __name__ == '__main__':
    # train = setup(dataset)
    # train, axle_load_success, objective_value = TrainLoadingConstraint.main(train)
    # print("axle_load_success: ", axle_load_success, ", objective_value: ", objective_value)

    x = 15

    max_objective = 0
    travel_solutions = []
    while x >= 10:
        train = setup(dataset)
        train.max_traveldistance = x
        _, axle_load_success, objective_value = TrainLoadingConstraint.main(train, max_objective)

        if axle_load_success and objective_value >= max_objective:
            travel_solutions.append(x)
            max_objective = objective_value
        print(travel_solutions)
        x -= 1
    
    weight_solutions = []
    if len(travel_solutions) == 0:
        print("In the weight reduction loop")
        y = 0.05
        while y <= 0.15:
            train = setup(dataset)
            for wagon in train.wagons:
                wagon.weight_capacity = wagon.weight_capacity * (1 - y)
            
            _, axle_load_success, objective_value = TrainLoadingConstraint.main(train, max_objective)

            if axle_load_success and objective_value >= max_objective:
                weight_solutions.append(y)
                max_objective = objective_value
            print(weight_solutions)
            y += 0.05
    



    train = setup(dataset)
    
    if len(travel_solutions) > 0:
        train.max_traveldistance = min(travel_solutions) 

    if len(weight_solutions) > 0:
        for wagon in train.wagons:
            wagon.weight_capacity = min(weight_solutions)

    train, axle_load_success, objective_value = TrainLoadingConstraint.main(train, max_objective)
    print("axle_load_success: ", axle_load_success, ", objective_value: ", objective_value)

    # This needs to be tested
    # while(axle_load_success is False):
    #     train, axle_load_success, objective_value = TrainLoadingConstraint.main(train, objective_value)
    #     print("axle_load_success: ", axle_load_success, ", objective_value: ", objective_value)
    

    placed_containers = train.get_placed_containers()
    containers = train.get_containers()
    unplaced_containers = train.get_unplaced_containers()
    
    train.to_JSON(callcode=train.wagons[1].call, weight=train.get_total_packed_weight(), length=train.get_total_packed_length(), distance=train.get_total_travel_distance(), amount=len(placed_containers), wagons=[])
    train.to_CSV()
    
    train.print_solution()

    trainplanning_plot = train.get_tableplot(unplaced_containers)
    trainplanning_plot.show()



