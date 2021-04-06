import math
import pandas as pd

class Container():
    def __init__(self, containerID, gross_weight, net_weight, foot, position, goods, priority, typeid, hazard_class, actual_length):
        self.containerID = containerID # name of the container
        self.gross_weight = gross_weight # weight of the container and the goods in kg
        self.foot = foot # length of the contianer in Foot (This length is adjusted to make sure it's either 20, 30, 40 or 45)
        self.position = self.calc_pos(position) # position of the container (on the dock or train)
        self.goods = goods # What is in the container (used for dangerous goods)
        self.priority = priority # ctt does not set a priority so this might be left unused
        self.net_weight = net_weight # Weight of the goods without the container (do not use this)
        self.typeid = typeid # Type of the container (len in feet and a letter combo)
        self.hazard_class = hazard_class # None means it is not hazardous, 1,2,3 means it is
        self.actual_length = actual_length # The actual length of the wagon (since foot is normalized to a calculating length)


    def __str__(self):
        return f'Container {self.containerID},'\
             f' priority: {self.priority}, gross_weight: {self.gross_weight}, foot: {self.foot}, position: {self.position}'

    def __repr__(self):
        return f'Container {self.containerID}, '\
                f'priority: {self.priority}, gross_weight: {self.gross_weight}, '\
                f'foot: {self.foot}, position: {self.position}, goods: {self.goods},'\
                f'net_weight: {self.net_weight}, typeid: {self.typeid}'

    def __eq__(self, other):
        return self.containerID == other.containerID

    def to_JSON(self):
        container_dict = {}
        container_dict["container_id"] = self.get_containerID()
        container_dict["gross_weight"] = self.get_gross_weight()
        container_dict["length"] = self.get_length()
        if not pd.isna(self.get_hazard_class()):
            container_dict["hazard_class"] = self.get_hazard_class()
        else:
            container_dict["hazard_class"] = None
        return container_dict

    # Transform the position of the container into a list with coordinates.
    def calc_pos(self, position):
        if position is None:
            return []
        position = position.split(" ")
        position = position[0].split(".")

        try:
            return [int(x) for x in position]
        except ValueError:
            return position

    def get_travel_distance(c_cord, w_cord):

        # factorize the difference in length of x and y
        x_fact = 6.5
        y_fact = 3

        # calculate the distance over the x-axis between a container and a wagon
        x_dist = (c_cord[0] - w_cord[0]) * x_fact
        # calculate the distance over the y-axis between a container and a wagon
        y_dist = (c_cord[1] - w_cord[1]) * y_fact

        # calculate the distance using Pythagoras
        dist = math.sqrt(math.pow(x_dist, 2) + math.pow(y_dist, 2))

        return dist

    # Getter for container position coordinates
    # Container ID used to identify the container at hand
    def get_containerID(self):
        return self.containerID

    # The weight of the container excluding the container itself
    def get_net_weight(self):
        return self.net_weight

    # The weight of the container including the container itself
    def get_gross_weight(self):
        return self.gross_weight    

    # The Length of the container in Foot,
    # This is done in foot since some containers have a length that is different from 1 or 1,5
    def get_length(self):
        return self.foot

    # The type of goods that is in the container
    def get_goods(self):
        return self.goods

    # The Position of the container 
    def get_position(self):
        return self.position

    # if the priority of a container is higher than normal this will differ from 1
    def get_priority(self):
        return self.priority

    # The type of the container
    def get_type(self):
        return self.typeid

    # The hazard class of this container, an int that is of value
    # 1,2,3 for the hazard classes, or None if is not hazardous
    def get_hazard_class(self):
        return self.hazard_class

    def set_hazard_class(self, value):
        self.hazard_class = value
    
    def get_actual_length(self):
        return self.actual_length
