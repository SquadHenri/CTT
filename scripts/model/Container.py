class Container():
    def __init__(self, containerID, gross_weight, net_weight, foot, position, goods, priority, typeid, hazard_class):
        self.containerID = containerID # name of the container
        self.gross_weight = gross_weight # weight of the container and the goods in kg
        self.foot = foot # length of the contianer in Foot
        self.position = self.calc_pos(position) # position of the container (on the dock or train)
        self.goods = goods # What is in the container (used for dangerous goods)
        self.priority = priority # ctt does not set a priority so this might be left unused
        self.net_weight = net_weight # Weight of the goods without the container (do not use this)
        self.typeid = typeid # Type of the container (len in feet and a letter combo)
        self.hazard_class = hazard_class # None means it is not hazardous, 1,2,3 means it is


    def __str__(self):
        return f'Container {self.containerID},'\
             f' priority: {self.priority}, gross_weight: {self.gross_weight}, foot: {self.foot}, position: {self.position}'

    def __repr__(self):
        return f'Container {self.containerID}, '\
                f'priority: {self.priority}, gross_weight: {self.gross_weight}, '\
                f'foot: {self.foot}, position: {self.position}, goods: {self.goods},'\
                f'net_weight: {self.net_weight}, typeid: {self.typeid}'

    def to_JSON(self):
        container_dict = {}
        container_dict["container_id"] = self.get_containerID()
        container_dict["gross_weight"] = self.get_gross_weight()
        container_dict["length"] = self.get_length()
        container_dict["hazard_class"] = self.get_hazard_class()
        return container_dict

    # Transform the position of the container into a list with coordinates.
    def calc_pos(self, position):
        if position is None:
            return -1
        position = position.split(" ")
        position = position[0].split(".")

        try:
            return [int(x) for x in position]
        except ValueError:
            return position

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
