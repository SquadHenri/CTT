import math as math

def main():

    result = getAllDistances()

    for key in result.keys():
        print(key, result[key])


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


main()