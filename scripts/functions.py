import math as math

containers = [[1,1,3], [1,2,2], [5,2,4], [3,2,1]]
wagons = [[1,0], [2,0], [3,0], [4,0]]

def getAllDistances():
    dist_dict = {}

    # loop through all containers and wagons, and store the distances in a dictionary
    for i, container in enumerate(containers):
        for j, wagon in enumerate(wagons):
            dist = getTravelDistance(container, wagon)
            dist_dict[(i, j)] = dist
    return dist_dict


def getTravelDistance(c_cord, w_cord):

    # factorize the difference in length of x and y
    x_fact = 7
    y_fact = 3

    # calculate the distance over the x-axis between a container and a wagon
    x_dist = (c_cord[0] - w_cord[0]) * x_fact
    # calculate the distance over the y-axis between a container and a wagon
    y_dist = (c_cord[1] - w_cord[1]) * y_fact

    # calculate the distance using Pythagoras
    dist = math.sqrt(math.pow(x_dist, 2) + math.pow(y_dist, 2))

    return dist

def main():

    result = getAllDistances()

    for key in result.keys():
        print(key, result[key])

if __name__ == '__main__':
    main()
