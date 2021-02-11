import math

def main():
    dist = get_distance(containers[0], wagon[0])
    print(dist)

containers = [[1, 1, 1], [2, 1, 1], [6, 2, 1]]
wagon = [[0, 2], [0, 3], [0, 1]]



def get_distance(container_lcoation, wagon_location):
    Xdist = 7
    Ydist = 3

    xContainer = container_lcoation[0]
    yContainer = container_lcoation[1]

    xWagon = wagon_location[0]
    yWagon = wagon_location[1]

    xdiff = (xContainer - xWagon) * Xdist
    ydiff = (yContainer - yWagon) * Ydist

    x = math.sqrt(math.pow(xdiff, 2) + math.pow(ydiff, 2))

    return x

if __name__ == '__main__':
    main()