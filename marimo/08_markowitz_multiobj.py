# /// script
# [tool.marimo.opengraph]
# title = "Markowitz Portfolio Optimization"
# description = "Multi-Objective Quadratic Programming"
# image = "__marimo__/thumbnail-markowitz.svg"
# ///

import marimo

__generated_with = "0.23.13"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import xpress as xp
    import numpy as np
    import matplotlib.pyplot as plt

    return mo, np, plt, xp


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # **Markowitz portfolio multi-objective optimization**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Markowitz portfolio optimization. A multi-objective quadratic programming example.

    In Markowitz portfolio optimization there are two objectives: to maximize reward while minimizing risk (i.e. variance). This example plots several points on the optimal frontier using a blended multi-objective approach, and shows that a point computed using a lexicographic approach also lies on this frontier.

    &copy; Copyright 2025-2026 Fair Isaac Corporation. The use of this example is subject to [legal and license requirements](https://github.com/fico-xpress/python-notebooks#legal-and-license-requirements).
    """)
    return


@app.cell
def _():
    # Install the necessary packages
    # '%pip install -q xpress matplotlib' command supported automatically in marimo
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Problem description
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Markowitz portfolio optimization focuses on making a selection on the fraction of a budget to allocate to $S$ possible stocks to form a portfolio with two key objectives:

    * Maximize expected returns: $\max \sum_{i \in \mathcal{S}} RET_i \cdot frac_i$
    * Minimize the portfolio variance: $\min \sum_{i,j \in \mathcal{S}} frac_i \cdot frac_j \cdot COV_{i,j}$

    where:

    * $frac$ is the vector of portfolio stock allocations.
    * $COV$ is the covariance matrix of asset returns.
    * $RET$ is the returns vector.

    The sum of the portfolio stock allocations should be equal to 1 (fully invested portfolio): $\sum_{i \in \mathcal{S}} frac_i = 1$

    In this example, we work with $S$ = 5 stocks, where the matrix of co-variance between each pair of stocks is given by:

    |   | Stock 1 | Stock 2 | Stock 3 | Stock 4 | Stock 5 |
    |---|---|---|---|---|---|
    | **Stock 1** | 0.32 | 0.70 | 0.19 | 0.52 | 0.16 |
    | **Stock 2** | 0.70 | 4.35 | -0.48 | -0.06 | -0.03 |
    | **Stock 3** | 0.19 | -0.48 | 0.98 | 1.10 | 0.10 |
    | **Stock 4** | 0.52 | -0.60 | 1.10 | 2.48 | 0.37 |
    | **Stock 5** | 0.16 | -0.30 | 0.10 | 0.37 | 0.31 |

    The returns of each stock are given as:

    |   | Returns |
    |---|---|
    | **Stock 1** | 0.31 |
    | **Stock 2** | 0.87 |
    | **Stock 3** | 0.31 |
    | **Stock 4** | 0.66 |
    | **Stock 5** | 0.24 |
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Model parameters

    **You can adjust the parameters below to change the number of frontier points computed, select a specific blended weight on the 'Return' objective to mark on the frontier, and control the lexicographic trade-off tolerance.**
    """)
    return


@app.cell
def _(mo):
    num_points_slider = mo.ui.slider(5, 100, value=50, step=5, label="Number of efficient-frontier points", show_value=True)
    selected_weight_slider = mo.ui.slider(0.05, 0.98, value=0.5, step=0.05, label="Blended: weight on 'Return' objective", show_value=True)
    reltol_slider = mo.ui.slider(0.0, 0.3, value=0.1, step=0.01, label="Lexicographic: max. relative loss in return", show_value=True)
    mo.vstack([num_points_slider, selected_weight_slider, reltol_slider])
    return num_points_slider, reltol_slider, selected_weight_slider


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Data preparation
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The necessary packages are imported, and returns and covariance data is created as NumPy arrays to allow the use of the [xpress.Dot()](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/python/HTML/xpress.Dot.html) operator.
    """)
    return


@app.cell
def _(mo, np):
    # The historical mean return on investment for five stocks
    RET = np.array([0.31, 0.87, 0.31, 0.66, 0.24])

    # The historical covariances of the five stocks
    COV = np.array([
        [0.32,  0.70,  0.19,  0.52,  0.16],
        [0.70,  4.35, -0.48, -0.06, -0.03],
        [0.19, -0.48,  0.98,  1.10,  0.10],
        [0.52, -0.6,   1.10,  2.48,  0.37],
        [0.16, -0.3,   0.10,  0.37,  0.31]
    ])
    mo.show_code()
    return COV, RET


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Model implementation and visualization of efficient frontier
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Non-negative variables represent percentage of capital to invest in each stock. In order to use Xpress' built in multi-objective handling functionality, all objectives must be linear, so we define a free variable *variance* to serve as transfer variable.

    A list of constraints is created and passed as an argument to [problem.addConstraint()](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/python/HTML/problem.addConstraint.html).
    """)
    return


@app.cell
def _(COV, RET, mo, xp):
    p = xp.problem()

    # Non-negative variables represent percentage of capital to invest in each stock
    frac = p.addVariables(len(RET))

    # All objectives must be linear, so we define a free variable for the variance
    variance = p.addVariable(lb=-xp.infinity)

    ctrs = [
        xp.Sum(frac) == 1,                        # Must invest 100% of capital
        xp.Dot(frac, COV, frac) - variance <= 0    # Set up transfer variable for variance
    ]

    p.addConstraint(ctrs)
    p.controls.outputlog = 0  # Turn off output log for cleaner output
    mo.show_code()
    return frac, p, variance


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Next we define the two objectives. First, we call [problem.setObjective()](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/python/HTML/problem.setObjective.html) to define the first objective, and the second objective is added using the [problem.addObjective()](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/python/HTML/problem.addObjective.html) method, which is designed for the formulation of multi-objective optimization problems by adding a new objective to an optimization problem.

    Alternatively, the [problem.setObjective()](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/python/HTML/problem.setObjective.html) method can be used to add a new objective to a problem, as long as an *objidx* argument is defined for each objective, as consecutive integers starting from zero.
    """)
    return


@app.cell
def _(RET, frac, mo, p, variance, xp):
    p.setObjective(xp.Dot(frac, RET))     # Maximize mean return
    p.addObjective(variance)              # Minimize variance

    # or alternatively
    # p.setObjective(xp.Dot(frac, RET), objidx=0)
    # p.setObjective(variance, objidx=1)
    mo.show_code()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Vary the objective weights to explore the optimal frontier, with the first objective having a weight ranging from 0.05 up to 0.98 (using the **Number of efficient-frontier points** control above to set the number of weights tried), with the second objective (weight) being the complement for each instance. Weight 1.0 is deliberately excluded: with a weight of exactly 0 on the variance objective, its value becomes arbitrary among the (many) equally-optimal-return solutions, producing a spurious jump at the very end of the curve. Stopping at 0.98 keeps the frontier smooth while still reaching essentially the same maximum return the lexicographic approach below can achieve.

    A loop allows iterating through each weight case, optimizing and saving the two objective values in each instance (coordinates).

    When using either [problem.setObjective()](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/python/HTML/problem.setObjective.html) or [problem.addObjective()](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/python/HTML/problem.addObjective.html), if **objectives have equal priority, a Blended (or Archimedean) approach is applied**, setting as objective function of the problem the linear combination of the added objectives and their weights.
    """)
    return


@app.cell
def _(RET, frac, mo, np, num_points_slider, p, variance, xp):
    # Vary the objective weights to explore the optimal frontier
    weights = np.linspace(0.05, 0.98, num_points_slider.value)
    means = []
    variances = []

    for w in weights:
        # priority=0 on both objectives keeps this a blended (not lexicographic) solve,
        # regardless of what priority a previous solve on this same problem may have set.
        p.setObjective(objidx=0, weight=w, priority=0, sense=xp.ObjSense.MAXIMIZE)  # First objective defines the sense of the problem
        p.setObjective(objidx=1, weight=w - 1, priority=0)                          # Reverse the sense by assigning a negative weight because we minimize variance
        p.optimize()
        means.append(xp.Dot(p.getSolution(frac), RET).item())
        variances.append(p.getSolution(variance))
    mo.show_code()
    return means, variances, weights


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The **Blended: weight on 'Return' objective** control above picks a single, arbitrary weight for the 'Return' objective (not necessarily one of the points from the sweep above) and re-solves the model once for that value, so the resulting point can be marked on the frontier below.
    """)
    return


@app.cell
def _(RET, frac, mo, p, selected_weight_slider, variance, xp):
    selected_weight = selected_weight_slider.value  # Weight on the 'Return' objective
    # priority=0 on both objectives keeps this a blended (not lexicographic) solve,
    # regardless of what priority a previous solve on this same problem may have set.
    p.setObjective(objidx=0, weight=selected_weight, priority=0, sense=xp.ObjSense.MAXIMIZE)
    p.setObjective(objidx=1, weight=selected_weight - 1, priority=0)
    p.optimize()
    selected_mean = xp.Dot(p.getSolution(frac), RET).item()
    selected_variance = p.getSolution(variance)
    mo.show_code()
    return selected_mean, selected_variance, selected_weight


@app.cell
def _(mo, selected_mean, selected_variance, selected_weight):
    mo.md(f"""
    **Selected weight on 'Return': {selected_weight:.2f}** &nbsp;&nbsp; **Expected return:** {selected_mean:.4f} &nbsp;&nbsp; **Variance:** {selected_variance:.4f}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Draw the efficient frontier with *matplotlib*, marking the point for the selected 'Return' weight in red.
    """)
    return


@app.cell
def _(means, plt, selected_mean, selected_variance, variances):
    fig_frontier, ax_frontier = plt.subplots()
    ax_frontier.plot(means, variances, label="Efficient frontier")
    ax_frontier.scatter([selected_mean], [selected_variance], c="tab:red", zorder=3, label="Selected weight on 'Return'")
    ax_frontier.set_title("Return on investment vs variance")
    ax_frontier.set_xlabel("Expected return")
    ax_frontier.set_ylabel("Variance")
    ax_frontier.legend()
    fig_frontier
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Applying a lexicographic approach
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now we will maximize profit alone, and then minimize variance while not sacrificing more than the **Lexicographic: max. relative loss in return** control's percentage of the maximum profit possible.

    When **objectives have a different priority but the same weight, a Lexicographic approach is applied**. Xpress will solve the problem once for each distinct objective priority that is defined. All objectives from previous iterations are fixed to their optimal values within the tolerances:

    * For minimization objectives: `objective <= optimal_value * (1 + reltol) + abstol`
    * For maximization objectives: `objective <= optimal_value * (1 - reltol) - abstol`

    with the parameter `reltol` being the relative tolerance and `abstol` the absolute tolerance for the objective in subsequent runs.

    Further calls to [problem.setObjective()](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/python/HTML/problem.setObjective.html) allow users to configure each objective via the `objidx` argument, which receives the `id` of each objective, a counter starting with 0 in the order objectives are created.

    By running the code cell below, we can observe that the final solution from the lexicographic method falls within the efficient frontier previously generated.
    """)
    return


@app.cell
def _(RET, frac, mo, p, reltol_slider, variance, xp):
    # Now we will maximize profit alone, and then minimize variance while not
    # sacrificing more than reltol_slider.value of the maximum profit
    p.setObjective(objidx=0, priority=1, weight=1, reltol=reltol_slider.value, sense=xp.ObjSense.MAXIMIZE)
    p.setObjective(objidx=1, priority=0, weight=-1)
    p.optimize()
    lex_mean = xp.Dot(p.getSolution(frac), RET).item()
    lex_variance = p.getSolution(variance)
    mo.show_code()
    return lex_mean, lex_variance


@app.cell
def _(lex_mean, lex_variance, mo):
    mo.md(f"""
    **Expected return:** {lex_mean:.4f} &nbsp;&nbsp; **Variance:** {lex_variance:.4f}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Plot the lexicographic solution (red) against the efficient frontier (blue) to confirm it lies on the frontier.
    """)
    return


@app.cell
def _(lex_mean, lex_variance, means, plt, variances):
    fig_lex, ax_lex = plt.subplots()
    ax_lex.plot(means, variances)
    ax_lex.scatter([lex_mean], [lex_variance], c="tab:red", zorder=3, label="Lexicographic solution")
    ax_lex.set_title("Return on investment vs variance")
    ax_lex.set_xlabel("Expected return")
    ax_lex.set_ylabel("Variance")
    ax_lex.legend()
    fig_lex
    return


if __name__ == "__main__":
    app.run()
