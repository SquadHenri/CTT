    for w_j, wagon in enumerate(train.wagons):
        for c_i, container in enumerate(containers):
            for c_ii, containerii in enumerate(containers):
                if c_i == c_ii:
                    continue
                direction = model.NewBoolVar('direction_to_enforce_distance')
                model.Add(
                    x[c_i, w_j, p_k] * x[c_ii, w_j, p_kk] * (p_k - p_kk) 
                    >=
                    x[c_i, w_j, p_k] * x[c_ii, w_j, p_kk] * int(0.5 * container.get_length() + containerii.get_length())
                    for p_k in range(int(wagon.get_length_capacity()))
                    for p_kk in range (int(wagon.get_length_capacity()))
                ).OnlyEnforceIf(direction)

                model.Add(
                    x[c_i, w_j, p_k] * x[c_ii, w_j, p_kk] * (p_kk - p_k) 
                    >=
                    x[c_i, w_j, p_k] * x[c_ii, w_j, p_kk] * int(0.5 * container.get_length() + containerii.get_length())
                    for p_k in range(int(wagon.get_length_capacity()))
                    for p_kk in range (int(wagon.get_length_capacity()))
                ).OnlyEnforceIf(direction.Not())

    for w_j, wagon in enumerate(train.wagons):
        for c_i, container in enumerate(containers):
            for c_ii, containerii in enumerate(containers):
                if c_i == c_ii:
                    continue
                for p_k in range (int(wagon.get_length_capacity())):
                    for p_kk in range (int(wagon.get_length_capacity())):
                        if p_k == p_kk:
                            continue

                        direction = model.NewBoolVar('direction_to_enforce_distance')
                        model.Add(
                            x[c_i, w_j, p_k] * x[c_ii, w_j, p_kk] * (p_k - p_kk) 
                            >=
                            x[c_i, w_j, p_k] * x[c_ii, w_j, p_kk] * int(0.5 * container.get_length() + containerii.get_length())
                        ).OnlyEnforceIf(direction)

                        model.Add(
                            x[c_i, w_j, p_k] * x[c_ii, w_j, p_kk] * (p_kk - p_k) 
                            >=
                            x[c_i, w_j, p_k] * x[c_ii, w_j, p_kk] * int(0.5 * container.get_length() + containerii.get_length())
                        ).OnlyEnforceIf(direction.Not())

positions = range(0,10)
item_loads = [model.NewIntVar(0, max_load, f"load for item {idx}")
    for idx, p in enumerate(positions)]
is_loaded = []
for idx in data['all_items']:
    item_is_loaded = model.NewIntVar(0, 1, f"item {idx} is loaded somewhere")
    model.Add(item_is_loaded == sum(x[idx, b] for b in data['all_bins']))
    is_loaded.append(item_is_loaded)
    model.Add(item_loads[idx] == compute_item_load(data["weights"][idx], positions[idx])).OnlyEnforceIf(item_is_loaded)
    model.Add(item_loads[idx] == 0).OnlyEnforceIf(item_is_loaded.Not()) 

for b in data['all_bins']:
# for bin capacities
    model.Add(
    sum(x[(i, b)] * data['weights'][i]
    for i in data['all_items']) <= data['bin_capacities'][b])
# limit each bin's pseudo axle loads
    loaded_weights = []
    for i in data['all_items']:
        loaded_weight = model.NewIntVar(0, 10000, f"item {i} weight in bin {b}")
        model.Add(loaded_weight == item_loads[i]).OnlyEnforceIf(x[(i, b)])
        model.Add(loaded_weight == 0).OnlyEnforceIf(x[(i, b)].Not())
        loaded_weights.append(loaded_weight)
        model.Add(sum(loaded_weights) <= data['max_pseudoaxle_load'])

    # TODO: REMOVE HARDCODE RANGE LIMIT!
    # The distance between the p_k of two containers on the same wagon needs
    # to be at least: 
    # p_k - p_kk >= 0.5 * (container.get_length() + containerii.get_length())
    # OR depending on the direction boolean variable
    # p_kk - p_k >= 0.5 * (container.get_length() + containerii.get_length())
    stop_point = math.ceil(len(containers) / 2) # Cache stop_point
    for w_j, wagon in enumerate(train.wagons):
        position_range = int(wagon.get_length_capacity() - 10) # Watch out with hardcoded range-limit
        for c_i, container in enumerate(containers):
            if(c_i == stop_point):
                break
            for c_ii, containerii in enumerate(containers):
                if c_i == c_ii:
                    continue
                for p_k in range (10, position_range):
                    for p_kk in range (10, position_range):
                        if p_k == p_kk:
                            continue

                        direction = model.NewBoolVar('')
                        model.Add(
                        p_k - p_kk
                        >=
                        int(0.5 * container.get_length() + containerii.get_length())
                        ).OnlyEnforceIf(model.AddBoolAnd([direction, x[c_i, w_j,p_k], x[c_ii, w_j, p_kk]]))

                        model.Add(
                         p_kk - p_k
                        >=
                        int(0.5 * container.get_length() + containerii.get_length())
                        ).OnlyEnforceIf(model.AddBoolAnd([direction.Not(), x[c_i, w_j,p_k], x[c_ii, w_j, p_kk]]))