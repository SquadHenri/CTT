import math

class Wagon():
    def __init__(self, wagonID, weight, length, contents, position):
        self.wagonID = wagonID
        self.weight = weight
        self.length = length
        self.contents = contents
        self.position = position
        self.location = [-2, -2]

    # TODO call: "set the locations"  at appropriate time

    # Getter for container position coordinates

    def get_position(self):
        return self.position

    def get_weight(self):
        return self.weight

    def get_length(self):
        return self.length

    def get_contents(self):
        return self.contents

    def get_location(self):
        return self.location

