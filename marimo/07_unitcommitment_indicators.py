# /// script
# [tool.marimo.opengraph]
# title = "Unit Commitment"
# description = "Indicator Constraints"
# image = "__marimo__/thumbnail-unitcommitment.svg"
# ///

import marimo

__generated_with = "0.23.13"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import xpress as xp
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    return mo, np, pd, plt, xp


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # **Solving an electricity generation problem using indicator constraints**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    This example shows how to model and solve an electricity generation problem typically found in power markets (see [Garver (1963)](https://ieeexplore.ieee.org/document/4501405)), showcasing the use of indicator constraints to model change state constraints when generators are turned on/off.

    &copy; Copyright 2025-2026 Fair Isaac Corporation. The use of this example is subject to [legal and license requirements](https://github.com/fico-xpress/python-notebooks#legal-and-license-requirements).
    """)
    return


@app.cell
def _():
    # Install the necessary packages
    # '%pip install -q xpress numpy pandas matplotlib' command supported automatically in marimo
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Problem description

    Four types of power generators are available to meet daily electricity demand and a security reserve above the estimated demand. Each type of generator has a set minimum and maximum power output, a start-up cost, an hourly cost at minimum output, and a cost per MW above minimum output. A generator can only be started or stopped at the beginning of a time period.

    We first solve the **basic model**, where generators can freely switch ON/OFF between consecutive periods. We then add the requirement that once a generator is switched ON/OFF it must remain in that state for at least a minimum number of periods, modeled with **indicator constraints**, and compare the extra cost this introduces against the basic model.

    Use the **Demand scale factor** control below to scale the whole demand curve up or down.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Model formulation

    Binary variables $work_{u,t}$, $start_{u,t}$, $stop_{u,t}$ track whether unit $u$ is working, starting, or stopping in period $t$; continuous variable $padd_{u,t}$ is the output above the unit's minimum.

    $$\min \sum_{u,t} COST^{start}_u \cdot start_{u,t} + LEN_t \cdot (COST^{min}_u \cdot work_{u,t} + COST^{add}_u \cdot padd_{u,t}) + PEN \sum_{u,t} stop_{u,t}$$

    Subject to, for every unit $u$ and period $t$ (with $n$ the previous period):

    * Start/stop tracking: $start_{u,t} \geq work_{u,t} - work_{u,n}$, $start_{u,t} \leq work_{u,t}$, $stop_{u,t} \geq work_{u,n} - work_{u,t}$, $stop_{u,t} \leq 1 - work_{u,t}$
    * Output above minimum limited by capacity: $padd_{u,t} \leq (P^{max}_u - P^{min}_u) \cdot work_{u,t}$
    * Demand satisfied: $\sum_u P^{min}_u \cdot work_{u,t} + padd_{u,t} \geq DEM_t$
    * Security reserve: $\sum_u P^{max}_u \cdot work_{u,t} \geq (1 + reserve) \cdot DEM_t$
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Model parameters

    **You can adjust the parameters below to change the problem instance and re-solve the model automatically.**
    """)
    return


@app.cell
def _(mo):
    demand_scale_slider = mo.ui.slider(0.7, 1.3, value=1.0, step=0.05, label="Demand scale factor", show_value=True)
    reserve_slider = mo.ui.slider(0.0, 0.4, value=0.2, step=0.05, label="Security reserve (fraction above demand)", show_value=True)
    penalty_slider = mo.ui.slider(0.0, 5.0, value=0.1, step=0.1, label="Stop penalty", show_value=True)
    mo.vstack([demand_scale_slider, reserve_slider, penalty_slider])
    return demand_scale_slider, penalty_slider, reserve_slider


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Data preparation and analysis

    We define the time periods, demand, and generator characteristics. The **Demand scale factor** control above rescales the whole demand curve to explore how the optimal schedule adapts.
    """)
    return


@app.cell
def _(demand_scale_slider, np):
    # Time periods
    LEN = [6, 3, 3, 2, 4, 4, 2]
    DEM = list(np.array([12000, 32000, 25000, 36000, 25000, 30000, 18000]) * demand_scale_slider.value)

    # Power plants
    PMIN = [750, 1000, 1200, 1800]      # minimum output (MW) per generator type
    PMAX = [1750, 1500, 2000, 3500]     # maximum output (MW) per generator type
    CSTART = [5000, 1600, 2400, 1200]   # start-up cost per generator type
    CMIN = [2250, 1800, 3750, 4800]     # hourly cost of operating generator type at minimum output (see PMIN)
    CADD = [2.7, 2.2, 1.8, 3.8]         # cost/hour/MW of prod. above min. level per generator type
    AVAIL = [10, 4, 8, 3]               # number of units per type

    NT = 7                              # number of time periods
    PERIODS = range(NT)                 # set of time periods
    TYPES = range(4)                    # power generator types
    UNITS = range(sum(AVAIL))           # power generation units
    TYPE = [i for i in TYPES for p in range(AVAIL[i])]      # associating units with types
    return AVAIL, CADD, CMIN, CSTART, DEM, LEN, NT, PERIODS, PMAX, PMIN, TYPE, TYPES, UNITS


@app.cell
def _(DEM, LEN, NT, mo, pd):
    # Build a display table with the period boundaries, length and demand
    ct = 0
    rows = []
    for period in range(NT):
        rows.append({"Period": f"{ct}h-{ct+LEN[period]}h", "Length (h)": LEN[period], "Demand (MW)": round(DEM[period])})
        ct += LEN[period]

    mo.ui.table(pd.DataFrame(rows), selection=None)
    return


@app.cell
def _(NT, PMAX, PMIN, TYPE, TYPES, UNITS, np, plt):
    def compute_outputs(p, work, padd):
        # Get the total power output per generator type per planning period
        outputs = [[0.0 for _ in range(NT)] for _ in TYPES]
        reserve_series = [0.0 for _ in range(NT)]
        for i in TYPES:
            for t in range(NT):
                for u in UNITS:
                    if TYPE[u] == i and p.getSolution(work[u, t]) > 0.5:
                        power_output = p.getSolution(PMIN[TYPE[u]] * work[u, t] + padd[u, t])
                        outputs[i][t] += power_output
                        reserve_series[t] += PMAX[TYPE[u]] - power_output
        return outputs, reserve_series

    def plot_outputs(outputs, reserve_series, DEM, title):
        # Labels for the unit types
        labels = [f"Unit type {i + 1}" for i in TYPES]

        # Create a stacked bar chart
        fig, ax = plt.subplots(figsize=(9, 5))

        # Plot output for each unit type per planning period
        for i in range(len(outputs)):
            ax.bar(range(1, NT + 1), outputs[i], label=labels[i], bottom=np.sum(outputs[:i], axis=0))

        # Plot the total reserve per planning period
        ax.bar(range(1, NT + 1), reserve_series, label="Total reserve",
               bottom=np.sum(outputs, axis=0), fill=False, edgecolor="black", linestyle="--")

        # Plot the demand data as a line
        ax.plot(range(1, NT + 1), DEM, color="black", marker="o", label="Demand (MW)")

        # Label and size the axes
        ax.set_xlabel("Planning period", fontsize=12)
        ax.set_ylabel("Total output (MW)", fontsize=12)
        ax.set_title(title, fontsize=13)

        # Add a legend
        ax.legend(loc="upper left", bbox_to_anchor=(1, 1), fontsize=10)
        plt.tight_layout()
        return fig

    return compute_outputs, plot_outputs


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Model implementation and solution

    Constraints are added directly to the problem using generator expressions over `(unit, period)` pairs. The daily cost and stop penalty are tracked as separate expressions so they can be reported individually alongside the total objective value. We start with the **basic model**, without minimum up/down time constraints.
    """)
    return


@app.cell
def _(
    CADD,
    CMIN,
    CSTART,
    DEM,
    LEN,
    NT,
    PERIODS,
    PMAX,
    PMIN,
    TYPE,
    UNITS,
    mo,
    penalty_slider,
    reserve_slider,
    xp,
):
    PEN = penalty_slider.value            # penalty associated with stopping units
    RESERVE = 1.0 + reserve_slider.value

    # Create problem
    p = xp.problem("Unit commitment")

    # Create decision variables
    start = p.addVariables(UNITS, PERIODS, vartype=xp.binary, name="start")
    stop = p.addVariables(UNITS, PERIODS, vartype=xp.binary, name="stop")
    work = p.addVariables(UNITS, PERIODS, vartype=xp.binary, name="work")
    padd = p.addVariables(UNITS, PERIODS, name="padd")

    # If generator starts in period
    p.addConstraint(start[u, t] >= work[u, t] - work[u, (NT + t - 1) % NT] for u in UNITS for t in PERIODS)
    p.addConstraint(start[u, t] <= work[u, t] for u in UNITS for t in PERIODS)

    # If generator stops before period
    p.addConstraint(stop[u, t] >= work[u, (NT + t - 1) % NT] - work[u, t] for u in UNITS for t in PERIODS)
    p.addConstraint(stop[u, t] <= 1 - work[u, t] for u in UNITS for t in PERIODS)

    # Limit on power production above minimum level
    p.addConstraint(padd[u, t] <= (PMAX[TYPE[u]] - PMIN[TYPE[u]]) * work[u, t] for u in UNITS for t in PERIODS)

    # Satisfy demands
    p.addConstraint(xp.Sum(PMIN[TYPE[u]] * work[u, t] + padd[u, t] for u in UNITS) >= DEM[t] for t in PERIODS)

    # Security reserve
    p.addConstraint(xp.Sum(PMAX[TYPE[u]] * work[u, t] for u in UNITS) >= RESERVE * DEM[t] for t in PERIODS)

    # Create and add the objective function of the problem (compute 'daily cost' and 'penalty' separately)
    Cost = xp.Sum(CSTART[TYPE[u]] * start[u, t] +
                   LEN[t] * (CMIN[TYPE[u]] * work[u, t] + CADD[TYPE[u]] * padd[u, t]) for u in UNITS for t in PERIODS)
    Penalty = PEN * xp.Sum(stop[u, t] for u in UNITS for t in PERIODS)
    p.setObjective(Cost + Penalty)

    # Optimize the problem and print the daily cost, penalty and total objective value
    p.controls.outputlog = 0
    p.optimize()

    basic_cost = p.getSolution(Cost)
    basic_penalty = p.getSolution(Penalty)
    basic_objval = p.attributes.objval
    mo.show_code()
    return Cost, PEN, Penalty, p, padd, start, stop, work, basic_cost, basic_objval, basic_penalty


@app.cell
def _(basic_cost, basic_objval, basic_penalty, mo):
    mo.md(f"""
    **Daily cost:** {basic_cost:,.2f}

    **Stop penalty:** {basic_penalty:,.2f}

    **Objective value:** {basic_objval:,.2f}
    """)
    return


@app.cell
def _(DEM, compute_outputs, p, padd, plot_outputs, work):
    _outputs, _reserve = compute_outputs(p, work, padd)
    plot_outputs(_outputs, _reserve, DEM, "Basic model (no minimum up/down time)")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Adding indicator constraints

    In real-world applications, generators must often remain for some time in a certain state after they have been switched to that state, i.e. if a generator is turned ON/OFF, it must remain in that state for at least $ON^{min}_s$/$OFF^{min}_s$ periods, respectively. Such state-change constraints can be formulated with the help of so-called **indicator constraints**, whose enforcement depends on the value of a binary "indicator" variable.

    $$
    \begin{align*}
    & \hbox{Can only switch OFF at least $ON^{min}_s$ periods after it has been turned ON:} \\
    & \qquad \sum_{j=t+1}^{t+ON^{min}_s-1} stop_{u,(j \bmod NT)} \leq 0, \qquad \forall u, \forall t: start_{u,t} = 1 \\
    & \hbox{Can only switch ON at least $OFF^{min}_s$ periods after it has been turned OFF:} \\
    & \qquad \sum_{j=t+1}^{t+OFF^{min}_s-1} start_{u,(j \bmod NT)} \leq 0, \qquad \forall u, \forall t: stop_{u,t} = 1 \\
    \end{align*}
    $$

    Indicator constraints are added with [problem.addIndicator()](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/python/HTML/chModeling.html?scroll=secModelingIndicator) to the **same problem** used for the basic model above. Comparing the outcome with the basic model, there is usually an extra cost from introducing these constraints, since units are no longer allowed to flip ON/OFF within a short window. The indicators also make the problem harder (and slower) to solve.
    """)
    return


@app.cell
def _(NT, PERIODS, TYPE, UNITS, mo, p, start, stop, xp):
    # Minimum time
    ONMIN = [3, 3, 3, 3]                # minimum time intervals a generator type must be ON once switched to that state
    DWMIN = [3, 3, 3, 3]                # minimum time intervals a generator type must be OFF once switched to that state

    # Indicator constraints
    for u in UNITS:
        for t in PERIODS:
            # Can only switch off at least ONMIN periods later
            p.addIndicator(start[u, t] == 1, xp.Sum(stop[u, j % NT] for j in range(t + 1, t + ONMIN[TYPE[u]])) <= 0)
            # Can only switch on at least DWMIN periods later
            p.addIndicator(stop[u, t] == 1, xp.Sum(start[u, j % NT] for j in range(t + 1, t + DWMIN[TYPE[u]])) <= 0)

    # Re-optimize the problem and print the daily cost, penalty and total objective value
    p.controls.outputlog = 0
    p.optimize()
    mo.show_code()
    return


@app.cell
def _(Cost, Penalty, basic_objval, mo, p):
    ind_cost = p.getSolution(Cost)
    ind_penalty = p.getSolution(Penalty)
    ind_objval = p.attributes.objval
    delta = ind_objval - basic_objval
    pct = 100 * delta / basic_objval if basic_objval else 0.0
    mo.md(f"""
    **Daily cost:** {ind_cost:,.2f}

    **Stop penalty:** {ind_penalty:,.2f}

    **Objective value:** {ind_objval:,.2f}

    **Extra cost from enforcing minimum up/down time:** {delta:,.2f} ({pct:.2f}% higher than the basic model)
    """)
    return


@app.cell
def _(DEM, compute_outputs, p, padd, plot_outputs, work):
    _outputs, _reserve = compute_outputs(p, work, padd)
    plot_outputs(_outputs, _reserve, DEM, "With minimum up/down time (indicator constraints)")
    return


if __name__ == "__main__":
    app.run()
