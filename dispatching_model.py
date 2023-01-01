from pulp import *

# Data
# The time slot demand
T = {0: 5000,
     1: 20000,
     2: 23000,
     3: 50000,
     4: 20000}

# The number of hours in each slot
H = {0: 6,
     1: 3,
     2: 6,
     3: 3,
     4: 6}

# The number of generators
G = [0,1,2]

# Minimum and maximum output levels of generator
minimum = {0:850, 1:1250, 2:1500}
maximum = {0:2000, 1:1750, 2:4000}

# Costs per hour at minimum
E = {0:1000, 1:2600, 2:3000}

# Costs per hour per MW above minimum
C = {0:2, 1:1.3, 2:3}

# Starting cost of generator
F = {0:2000, 1:1000, 2:500}

# Previous slots
P = {0:4, 1:0, 2:1, 3:2, 4:3}

# Generator avalability
G_a = {0:12, 1:10, 2:5}

# Creating the model
prob = LpProblem("Dispatch_problem",LpMinimize)

# Declaring the decision variables
n = {}
s = {}
x = {}
for i in G:
    for j in T.keys():
        n[(i,j)] = LpVariable(f'Number of Generators_{i}_slot_{j}', lowBound=0, cat=LpInteger)
        s[(i,j)] = LpVariable(f'Number of Generator_{i}_slot_{j} started', lowBound=0, cat=LpInteger)
        x[(i,j)] = LpVariable(f'Total output Generator_{i}_slot_{j}', lowBound=0, cat=LpInteger)

# Defining the objective function
prob += lpSum(C[i]*H[j]*(x[(i,j)]-(minimum[i]*n[(i,j)])) for i in G for j in T.keys()) 
+ lpSum(E[i]*H[j]*n[(i,j)] for i in G for j in T.keys())
+ lpSum(F[i]*s[(i,j)] for i in G for j in T.keys()), "objective function"

# Defining the constraints
# Demand constraint
for j in T.keys():
    prob += lpSum(x[(i,j)] * H[j] for i in G) >= T[j] * H[j]

# Working limits for generators
for i in G:
    for j in T.keys():
        prob += x[(i,j)] >= minimum[i]*n[(i,j)]
        prob += x[(i,j)] <= maximum[i]*n[(i,j)]

# 15% Extra load guarantee
for j in T.keys():
    prob += lpSum(maximum[i]*n[(i,j)]*H[j] for i in G) >= (115/100) * T[j] * H[j]

# Balancing the total number of generators started in period j and the total number
# of generators running
for i in G:
    for j in T.keys():
        if j == 0:
            prob += s[(i,j)] >= n[(i,j)]
        else:
            prob += s[(i,j)] >= n[(i,j)] - n[(i,P[j])]

# Upper bounds on the number of generators per slot
for i in G:
    for j in T.keys():
        prob += n[(i,j)] <= G_a[i]

# Solving the problem
prob.solve()


# Printing the solution
for j in T.keys():
    for i in G:
        print(f'number of generators of type {i+1} running in slot {j} = ',n[(i,j)].varValue)

for j in T.keys():
    for i in G:
        print(f'number of generators of type {i+1} started in slot {j} = ',s[(i,j)].varValue)

for j in T.keys():
    for i in G:
        print(f'Units generated per hour by generators of type {i+1} in slot {j} = ',x[(i,j)].varValue)