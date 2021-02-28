class Container():
    def __init__(self, containerID, gross_weight, net_weight, foot, position, goods, priority, typeid):
        self.containerID = containerID
        self.gross_weight = gross_weight
        self.foot = foot
        self.position = position
        self.goods = goods
        self.priority = priority
        self.net_weight = net_weight
        self.typeid = typeid
        self.hazard_class = None # None means it is not hazardous, 1,2,3 means it is


    def __str__(self):
        return f'Container {self.containerID},'\
             f' priority: {self.priority}, gross_weight: {self.gross_weight}, foot: {self.foot}'

    def __repr__(self):
        return f'Container {self.containerID}, '\
                f'priority: {self.priority}, gross_weight: {self.gross_weight}, '\
                f'foot: {self.foot}, position: {self.position}, goods: {self.goods},'\
                f'net_weight: {self.net_weight}, typeid: {self.typeid}'


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
