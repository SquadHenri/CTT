import csv as csv
import math
import pandas as pd

def get_wagons(fileloc):
    dicts = {}

    # open file
    with open(fileloc, encoding="utf-8-sig") as wagontypes:
        data = csv.reader(wagontypes, delimiter=";")
        w_idList = []
        values = []
        for row in data:
            w_id = row[0]
            wlen = row[1]
            axles = row[2]
            axleshift = row[3]
            axledist = row[4]
            w_idList.append(w_id)
            values.append([wlen, axles, axleshift, axledist])
        for i, wid in enumerate(w_idList):
            dicts[wid] = values[i]        
    return dicts

# if __name__ == '__main__':
#    dicts = get_wagons()
#    print(dicts)