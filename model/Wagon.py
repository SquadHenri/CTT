class Wagon():
    def __init__(self, wagonID, weight, length, contents, position):
        self.wagonID = wagonID
        self.weight = weight
        self.length = length
        self.contents = contents
        self.position = position


#Getter for container position coordinates
    def get_position(self):
        return self.position