from numpy.lib.function_base import place
import pandas

from model.Wagon import Wagon
from model.Train import Train
from model.Container import Container
import TrainLoadingConstraint



dataset = pandas.read_csv('data\input_df_9ed65200-f569-4862-bd87-702562af2377.csv')

def setup(dataset):
    containerlist = []
    wagonlist = []

    #Set parameters
    max_traveldistance = 50
    if dataset.MAXTRAVELDISTANCE[1] is not None:
        max_traveldistance = dataset.MAXTRAVELDISTANCE[1]

    split = None 
    if dataset.TRAINSPLIT[1] is not None:
        split = dataset.TRAINSPLIT[1]


    isReversed = False
    if dataset.TRAINREVERSED[1] is not None and dataset.TRAINREVERSED[1] == 1:
        isReversed = True

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
    
    print(wagondf)
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
        position = str(container['containerPosition'])
        goods = container['unKlasse']
        priority = 1
        typeid = container['containerType']
        hazard_class = container['unKlasse']
        
        containerObj = Container(containerID, gross_weight, net_weight, foot, position, goods, priority, typeid, hazard_class)
        containers.append(containerObj)
    return Train(wagons, containers, wrong_wagons, split, isReversed, max_traveldistance)

if __name__ == '__main__':
    train = setup(dataset)
    train, axle_load_success, objective_value = TrainLoadingConstraint.main(train)
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



