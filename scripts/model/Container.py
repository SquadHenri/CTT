class Container():
    def __init__(self, containerID, weight, length, contents, position):
        self.containerID = containerID
        self.weight = weight
        self.length = length
        self.contents = contents
        self.position = position


#Getter for container position coordinates
    def get_position(self):
        return self.position

