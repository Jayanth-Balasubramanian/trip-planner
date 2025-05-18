import gurobipy as gp
import matplotlib.pyplot as plt
from gurobipy import GRB

from consts import (
    Locations,
    end,
    max_leg,
    max_stops,
    mock_distances,
    num_days,
    root,
    stay_cost,
)

model = gp.Model("KeralaTrip")

V = list(Locations)
D = range(num_days)
V_stay = [v for v, c in stay_cost.items() if c < 1e8]

n = len(V)
dist = {(i, j): mock_distances[i.value - 1][j.value - 1] for i in V for j in V}

# chatgpt suggested trick to avoid subtours, MTZ constraints
A = [(i, j, d) for d in D for i in V for j in V if i != j and dist[i, j] <= max_leg]
x = model.addVars(A, vtype=GRB.BINARY, name="x")
y = model.addVars([(i, d) for i in V for d in D], vtype=GRB.BINARY, name="y")

# leave from start
model.addConstr(
    gp.quicksum(x[root, j, 0] for j in V if (root, j, 0) in x) == 1, name="start_out"
)
# end at sink
last = num_days - 1
model.addConstr(
    gp.quicksum(x[i, end, last] for i in V if (i, end, last) in x) == 1, name="end_in"
)
model.addConstr(
    gp.quicksum(x[end, j, last] for j in V if (end, j, last) in x) == 0, name="end_out"
)

# start from prev day's stay vertex
for d in range(num_days - 1):
    for j in V_stay:
        model.addConstr(
            gp.quicksum(x[i, j, d] for i in V if (i, j, d) in x)
            == gp.quicksum(x[j, k, d + 1] for k in V if (j, k, d + 1) in x),
            name=f"overnight_{j.name}_{d}",
        )

# incoming = outgoing for continuity
for d in D:
    for i in V:
        if i not in (root, end):
            model.addConstr(
                gp.quicksum(x[i, j, d] for j in V if (i, j, d) in x) == y[i, d],
                name=f"out_{i.name}_{d}",
            )
            model.addConstr(
                gp.quicksum(x[j, i, d] for j in V if (j, i, d) in x) == y[i, d],
                name=f"in_{i.name}_{d}",
            )

# max stops/day
NON_STAY = [v for v in V if v not in V_stay and v not in (root, end)]
for d in D:
    model.addConstr(
        gp.quicksum(y[i, d] for i in NON_STAY) <= max_stops, name=f"daily_cap_{d}"
    )

# no repeats except if we're staying there
for i in NON_STAY:
    model.addConstr(gp.quicksum(y[i, d] for d in D) <= 1, name=f"no_repeat_{i.name}")

# visit some place every day
for d in D:
    model.addConstr(
        gp.quicksum(y[i, d] for i in NON_STAY) >= 1, name=f"min_visit_per_day_{d}"
    )

n = len(V)
u = model.addVars(V, lb=1, ub=n, vtype=GRB.CONTINUOUS, name="u")

# MTZ constraints for subtour elimination
model.addConstr(u[root] == 1, name="u_root")

# MTZ inequalities
for i, j, d in A:  # A is the arc-day index triple list
    if i != root and j != root:  # skip rows whose tail is PRK (already fixed)
        model.addConstr(
            u[i] - u[j] + n * x[i, j, d] <= n - 1, name=f"mtz_{i.name}_{j.name}_{d}"
        )

model.update()
print(f"Model has {model.NumConstrs} constraints and {model.NumVars} variables.")

RUPEES_PER_KM = 100 / 10
MAX_COST = 6 * 10**4
MAX_LOCS = n

alphas = range(11)
alphas = [a / 10 for a in alphas]

results = []
for alph in alphas:
    visit_term = gp.quicksum(
        y[i, d] for (i, d) in y.keys() if i not in V_stay + [root, end]
    )
    drive_cost = gp.quicksum(dist[i, j] * RUPEES_PER_KM * x[i, j, d] for (i, j, d) in A)
    stay_costsum = gp.quicksum(stay_cost[i] * y[i, d] for i in V_stay for d in D)

    model.setObjective(
        alph * visit_term / MAX_LOCS
        - (1 - alph) * (drive_cost + stay_costsum) / MAX_COST,
        GRB.MAXIMIZE,
    )

    model.optimize()

    if model.status == GRB.OPTIMAL:
        num_visited = sum(
            int(y[i, d].X > 0.5) for (i, d) in y.keys() if i not in (root, end)
        )

        net_travel = sum(dist[i, j] * RUPEES_PER_KM * x[i, j, d].X for (i, j, d) in A)
        net_stay = sum(stay_cost[i] * y[i, d].X for i in V_stay for d in D)
        net_cost = net_travel + net_stay

        results.append((net_cost, num_visited))
    else:
        # infeasible or time-lim limit
        results.append((None, None))

# unpack for plotting, drop any Nones
print(results)
costs, visits = zip(*[r for r in results if r[0] is not None])

plt.figure()
plt.plot(costs, visits, marker="o")
plt.xlabel("Net cost (₹)")
plt.ylabel("Number of places visited")
plt.title("Pareto frontier: cost vs visits")
plt.grid(True)
plt.show()
