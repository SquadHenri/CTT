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


    #Getter for container position coordinates
    def get_containerID(self):
        return self.containerID

    def get_net_weight(self):
        return self.net_weight

    def get_gross_weight(self):
        return self.gross_weight    

    def get_length(self):
        return self.foot

    def get_goods(self):
        return self.goods

    def get_position(self):
        return self.position

    def get_priority(self):
        return self.priority

    def get_type(self):
        return self.typeid
    