class Container():
    def __init__(self, containerID, weight, teu, position, goods, priority):
        self.containerID = containerID
        self.weight = weight
        self.teu = teu
        self.position = position
        self.goods = goods
        self.priority = priority

    #Getter for container position coordinates
    def get_containerID(self):
        return self.containerID

    def get_weight(self):
        return self.weight

    def get_teu(self):
        return self.teu

    def get_goods(self):
        return self.goods

    def get_position(self):
        return self.goods

    def get_priority(self):
        return self.priority