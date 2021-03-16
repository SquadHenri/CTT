# OR-TOOLS
from ortools.sat.python import cp_model
import collections

# Required modules
import pandas as pd
import numpy as np
# Our files
from colors import Color
from model import *
from data import getContainersFromCSV
import functions

def main(containers, train):

    # Define the cp model
    model = cp_model.CpModel()

    """
                VARIABLES
    """

    # x[c_i, w_j] = 1 if container c_i is packed in wagon w_j
    x = {}
    for c_i, _ in enumerate(containers):    
        for w_j, wagon in enumerate(train.wagons):
            x[(c_i,w_j)] = model.NewIntVar(0, 1, 'cont:%i,wagon%i' % (c_i, w_j))


    """
                CONSTRAINTS
    """

    # The amount packed in each wagon cannot exceed its weight capacity.
    # for w_j, wagon in enumerate(train.wagons):
    #     model.AddLinearConstraint(
    #         sum(x[(c_i, w_j)] * container.get_gross_weight()
    #             for c_i, container in enumerate(containers)),
    #             0,
    #             int(wagon.get_weight_capacity())
    #     )

    for w_j, wagon in enumerate(train.wagons):
        model.Add(
            sum(x[(c_i, w_j)] * container.get_gross_weight()
                for c_i, container in enumerate(containers))
                <=
                int(wagon.get_weight_capacity())
        )

    for w_j, wagon in enumerate(train.wagons):
        model.Add(
            sum(x[(c_i, w_j)] * container.get_length()
                for c_i, container in enumerate(containers))
                <=
                int(wagon.get_length_capacity())
                # wagon.get_length_capacity()
        )

    # The length of the containers cannot exceed the length of the wagon
    # for w_j, wagon in enumerate(train.wagons):
    #     model.AddLinearConstraint(
    #         sum(x[(c_i, w_j)] * container.get_length()
    #             for c_i, container in enumerate(containers)),
    #             0,
    #             int(wagon.get_length_capacity())
    #     )

    """
                OBJECTIVE
    """

    print(train.get_total_weight_capacity())
    # objective = model.NewIntVar(0, int(train.get_total_weight_capacity()), 'weight')
    # model.Add(
    #     objective == sum(
    #         x[(c_i, w_j)] * container.gross_weight 
    #             for c_i, container in enumerate(containers) 
    #             for w_j, _ in enumerate(train.wagons)
    #         )
    #     ) 
    model.Maximize(sum(
            x[(c_i, w_j)] * container.gross_weight 
                for c_i, container in enumerate(containers) 
                for w_j, _ in enumerate(train.wagons)
            ))

    """"
                Solving & Printing Solution
    """

    print("Validating...")
    print(model.Validate())

    print("Starting Solve...")
    solver = cp_model.CpSolver()
    solution_printer = SolutionPrinter(x)
    # status = solver.SearchForAllSolutions(model, solution_printer)
    
    status = solver.Solve(model)

    print("Solved?")
    print(solution_printer.SolutionCount())

    print(status)
    if(status == cp_model.OPTIMAL):
        print(f'Optimal weight: {solver.ObjectiveValue()}')
    else:
        print('No optimal solution found')
    
class SolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Prints intermediate solutions"""

    def __init__(self, variables):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__variables = variables
        self.__solution_count = 0
    
    def OnSolutionCallback(self):
        self.__solution_count += 1
        for v in self.__variables:
            print('%s = %i' % (v, self.Value(v)), end = ' ')
        print()
    
    def SolutionCount(self):
        return self.__solution_count
