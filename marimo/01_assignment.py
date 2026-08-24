# /// script
# [tool.marimo.opengraph]
# title = "Project Assignment"
# description = "Binary Assignment Model"
# image = "__marimo__/thumbnail-assignment.svg"
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
    import pandas as pd
    return mo, np, pd, plt, xp


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # **Project Assignment Problem**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    One-to-one assignment of $n$ persons to $n$ projects to maximize total preference.

    &copy; Copyright 2025-2026 Fair Isaac Corporation. The use of this example is subject to [legal and license requirements](https://github.com/fico-xpress/python-notebooks#legal-and-license-requirements).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Problem description and formulation

    There are $n$ persons and $n$ projects. Each person $i \in \mathcal{I}$ ranks every project $j \in \mathcal{J}$ with a non-negative integer preference score $p_{i,j}$. The goal is to find a one-to-one matching between persons and projects that maximizes the total satisfaction across all assignments.

    Let $x_{i,j}$ be the set of **binary decision variables** indicating if person $i$ is assigned to project $j$ (=1), or not (=0). The objective function aims to maximize the total satisfaction:

    $$\max \sum_{i\in \mathcal{I}}\sum_{j\in \mathcal{J}} p_{i,j}\,x_{i,j}.$$

    Subject to the following constraints:

    * One project per person:
    $$\sum_{j\in \mathcal{J}} x_{i,j} = 1, \quad\forall\,i\in \mathcal{I}.$$

    * One person per project:
    $$\sum_{i\in \mathcal{I}} x_{i,j} = 1, \quad\forall\,j\in \mathcal{J}.$$
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Data preparation

    We first define the preference matrix `PREF`, where each entry `PREF[i, j]` captures how much person $i$ values project $j$. From this matrix, we infer the number of persons and projects, and establish simple Python ranges (`people` and `projects`) to list them.

    **You can adjust the parameters below to change the problem instance and re-solve the model automatically.**
    """)
    return


@app.cell
def _(mo):
    n_slider = mo.ui.slider(2, 8, value=5, label="Problem size n (persons = projects = n)", show_value=True)
    seed_slider = mo.ui.slider(0, 99, value=42, label="Random seed (each value gives a different instance)", show_value=True)
    mo.vstack([n_slider, seed_slider])
    return n_slider, seed_slider


@app.cell
def _(mo, n_slider, np, seed_slider):
    n = n_slider.value                              # problem size (persons = projects)
    rng = np.random.default_rng(seed_slider.value)  # random generator seeded from the Random seed control

    # Preference matrix: PREF[i, j] is how much person i values project j
    PREF = rng.integers(1, 9, size=(n, n))

    people = range(n)     # set of persons
    projects = range(n)   # set of projects

    mo.show_code()
    return PREF, n, people, projects


@app.cell(hide_code=True)
def _(mo):
    mo.md("## Preference matrix")
    return


@app.cell
def _(PREF, mo, n, pd):
    df_pref = pd.DataFrame(
        PREF,
        index=[f"Person {i+1}" for i in range(n)],
        columns=[f"Project {j+1}" for j in range(n)]
    )
    mo.ui.table(df_pref, selection=None)
    return (df_pref,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Model implementation

    We instantiate an Xpress model named **Assignment**, and create the set of binary decision variables. By passing integer arguments to [p.addVariables()](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/python/HTML/problem.addVariables.html), a *NumPy* array of variables (`assign`) is created.

    The objective and constraints are then created and added to the problem by passing the corresponding expressions, using list comprehension, to [p.setObjective()](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/python/HTML/problem.setObjective.html) and [p.addConstraint()](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/python/HTML/problem.addConstraint.html), respectively.

    After building the model, we turn off solver logging using the `OUTPUTLOG` control and call [p.optimize()](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/python/HTML/problem.optimize.html) to solve the problem, then extract and display the total satisfaction as well as each individual assignment.
    """)
    return


@app.cell
def _(PREF, mo, n, people, projects, xp):
    # Create a problem instance and the binary assignment variables
    p = xp.problem(name='Assignment')
    assign = p.addVariables(n, n, vartype=xp.binary, name='x')

    # Objective: maximize total preference across all assignments
    p.setObjective(
        xp.Sum(PREF[i, j] * assign[i, j] for i in people for j in projects),
        sense=xp.ObjSense.MAXIMIZE
    )

    # One project per person, and one person per project
    p.addConstraint(xp.Sum(assign[i, j] for j in projects) == 1 for i in people)
    p.addConstraint(xp.Sum(assign[i, j] for i in people) == 1 for j in projects)

    # Solve the problem
    p.controls.outputlog = 0  # Turn off solver logging for cleaner output
    p.optimize()

    # Get the solution
    sol = p.getSolution(assign)
    total_satisfaction = p.attributes.objval
    mo.show_code()
    return assign, p, sol, total_satisfaction


@app.cell
def _(mo, np, people, sol, total_satisfaction):
    rows = [{"Person": f"Person {i+1}", "Assigned to": f"Project {int(np.argmax(sol[i]))+1}"} for i in people]
    mo.vstack([
        mo.md(f"**Total satisfaction score: {int(total_satisfaction)}**"),
        mo.ui.table(rows, selection=None),
    ])
    return (rows,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Visualization

    After running the code cell below, we can visualize the assignment as a bipartite graph with persons on the left, projects on the right, and lines whose **thickness reflects preference connecting each matched pair** connecting both sides.
    """)
    return


@app.cell
def _(PREF, n, np, people, plt, projects, sol):
    fig, ax = plt.subplots(figsize=(6, max(4, n)))
    left_x, right_x = 0, 2
    y = np.arange(1, n + 1)

    # Plot the persons (left) and projects (right) as two columns of points
    ax.scatter([left_x] * n, y, s=100, zorder=5, label='Persons')
    ax.scatter([right_x] * n, y, s=100, zorder=5, label='Projects')

    # Label each point
    for i in people:
        ax.text(left_x - 0.1, i + 1, f"Person {i+1}", ha='right', va='center')
    for j in projects:
        ax.text(right_x + 0.1, j + 1, f"Project {j+1}", ha='left', va='center')

    # Draw a line for each assigned pair, with thickness proportional to preference
    for i in people:
        j = int(np.argmax(sol[i]))
        ax.plot([left_x, right_x], [i + 1, j + 1], linewidth=PREF[i, j])

    ax.axis('off')
    ax.set_title('Assignment (line thickness = preference score)')
    ax.legend(loc='upper center')
    plt.tight_layout()
    fig
    return (fig,)


if __name__ == "__main__":
    app.run()