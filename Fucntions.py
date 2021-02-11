import math

def main():
    print('test')



def get_distance(container_lcoation, wagon_location):
    Xdist = 3
    Ydist = 7

    xContainer = container_lcoation[1]
    yContainer = container_lcoation[2]

    xWagon = wagon_location[1]
    yWagon = wagon_location[2]

    xdiff = xContainer - xWagon
    ydiff = yContainer - yWagon

    x = math.sqrt(math.pow(xdiff, 2) + math.pow(ydiff, 2))

    return x

