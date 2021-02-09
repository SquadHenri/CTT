from ortools.linear_solver import pywraplp


# Declare the solver
solver = pywraplp.Solver.CreateSolver('GLOP')


# Create variables
x = solver.NumVar(0, 1, 'x')
y = solver.NumVar(0, 2, 'y')

print('Number of variables = ', solver.NumVariables())

# Define constraints
ct = solver.Constraint(0, 2, 'ct')
ct.SetCoefficient(x, 1)
ct.SetCoefficient(y, 1)

print('Number of constraints = ', solver.NumConstraints())

# Define the objective function
objective  = solver.Objective()
objective.SetCoefficient(x, 3)
objective.SetCoefficient(y, 1)
objective.SetMaximization()

# Invoke solver and display results
solver.Solve()
print('Solution: ')
print('Objective value = ', objective.Value())
print('x = ', x.solution_value())
print('y = ', y.solution_value())
