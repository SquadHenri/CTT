import math as math

containers = [[1,1,3], [1,2,2], [5,2,4], [3,2,1]]
wagons = [[1,0], [2,0], [3,0], [4,0]]

def getAllDistances():
    dist_dict = {}
    for i, container in enumerate(containers):
        for j, wagon in enumerate(wagons):
            dist = getTravelDistance(container, wagon)
            dist_dict[(i, j)] = dist
    return dist_dict


def getTravelDistance(c_cord, w_cord):
    x_dist = c_cord[0] - w_cord[0]
    y_dist = c_cord[1] - w_cord[1]

    dist = math.sqrt(math.pow(x_dist, 2) + math.pow(y_dist, 2))

    return dist


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

def main1():

    result = getAllDistances()

    for key in result.keys():
        print(key, result[key])


def main2():
    dist = get_distance(containers[0], wagons[0])
    print(dist)


if __name__ == '__main__':
    main1()
    main2()
