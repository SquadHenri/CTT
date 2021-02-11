import csv as csv

def get_data():
    container_dict = {}
    with open("currentContainers.csv", encoding="utf-8-sig") as containers:
        data = csv.reader(containers, delimiter=",")
        next(data)
        for row in data:
            position = row[3]
            position = position.split(".")
            position = [int(x) for x in position]
            container_dict[row[1]] = position
    return container_dict
print(get_data())
