# /// script
# [tool.marimo.opengraph]
# title = "Circle Packing"
# description = "Uses Xpress Global (Nonlinear)"
# image = "__marimo__/thumbnail-circlepacking.svg"
# ///

import marimo

__generated_with = "0.23.13"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Place $N$ disjoint circles in the unit square to maximize the sum of their radii. Circle packing problems of this kind have recently gained renewed visibility as a benchmark for AI-driven algorithm design, for example in Google DeepMind's AlphaEvolve project - see this [FICO blog post](https://marketplace.fico.com/blogs/best-global-optimization-solver) for how FICO Xpress compares against AlphaEvolve on this very problem.

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
    ## Problem description and formulation
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    In this example, we aim at packing $N$ circles inside the unit square to maximize the sum of their radii. The circles must not overlap with each other and must be fully contained inside the unit square. Let $CIRCLES$ be the set $\{1,...,N\}$.

    The continuous decision variables $x_i$ and $y_i$ represent the vector of $(x,y)$ coordinates of the center point of each circle $i \in CIRCLES$, and variables $r_i$ the corresponding radius.

    The goal is to maximize the area inside the unit square occupied by circles, that is, the sum of the radii of all circles:

    $$\max \sum_{i \in CIRCLES} r_{i}$$

    The circles must not overlap, that is, the Euclidean distance between the center of any two circles must not be shorter than the sum of their radii. This can be represented by the following set of quadratic constraints:

    $$ (x_i - x_j)^2 + (y_i - y_j)^2  \geq (r_i + r_j)^2, \qquad \forall i \in CIRCLES, \forall j \in i+1,...,N$$

    Moreover, we need each circle to be fully contained within the unit square. Therefore, both the $x_i$ and $y_i$ coordinates of each circle must not be lower than its radius (similarly, they must not be greater than (1 - $r_i$)). This can be represented by the following linking constraints:

    $$
    \begin{array}{llll}
    & \qquad  x_i \geq r_i, \qquad \forall i \in CIRCLES \\
    & \qquad  x_i \leq 1 - r_i, \qquad \forall i \in CIRCLES \\
    & \qquad  y_i \geq r_i, \qquad \forall i \in CIRCLES \\
    & \qquad  y_i \leq 1 - r_i, \qquad \forall i \in CIRCLES \\
    \end{array}
    $$

    Additionally, the radius of each circle has a trivial upper bound equal to 0.5, since the diameter of any circle can never be greater than 1:

    $$0 \leq r_i \leq 0.5, \qquad \forall i \in 1..N $$
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Model implementation
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The model described above is implemented below with the Xpress Python API. Note that the upper bound is defined on variable creation with [p.addVariables](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/python/HTML/problem.addVariables.html), which creates a *NumPy* array of $N$ variables when an integer is passed as the first argument.

    Use the slider below to change the number of circles $N$ and re-run the model.
    """)
    return


@app.cell
def _():
    import xpress as xp
    import matplotlib.pyplot as plt

    return plt, xp


@app.cell
def _(mo):
    n_slider = mo.ui.slider(2, 14, value=6, label="Number of circles N", show_value=True)
    n_slider
    return (n_slider,)


@app.cell
def _(mo, n_slider, xp):
    N = n_slider.value   # Number of circles to place.
    CIRCLES = range(N)

    # Create a problem instance.
    p = xp.problem()

    # Decision variables.
    x = p.addVariables(N, name="x")         # x-coordinate of center points.
    y = p.addVariables(N, name="y")         # y-coordinate of center points.
    r = p.addVariables(N, name="r", ub=0.5) # Radii of circles, upper bound is 0.5 to fit in unit square.

    # Non-overlap constraints.
    p.addConstraint((x[i] - x[j])**2 + (y[i] - y[j])**2 >= (r[i] + r[j])**2 for i in CIRCLES for j in range(i + 1, N))

    # Ensure that each circle is contained in the unit square.
    p.addConstraint(x[i] >= r[i] for i in CIRCLES)
    p.addConstraint(x[i] <= 1 - r[i] for i in CIRCLES)
    p.addConstraint(y[i] >= r[i] for i in CIRCLES)
    p.addConstraint(y[i] <= 1 - r[i] for i in CIRCLES)

    # Objective function.
    p.setObjective(xp.Sum(r), sense=xp.ObjSense.MAXIMIZE)
    mo.show_code()
    return CIRCLES, N, p, r, x, y


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Before triggering the optimization, a number of optimizer controls are set. For exact arithmetic, the feasibility tolerance is lowered to a very small value with [FEASTOL](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/HTML/FEASTOL.html).

    Moreover, we set a time limit of 3 seconds before defining the global solver (default) to solve the problem.

    The code below defines these control parameters and optimizes the problem before printing the solution and objective values.
    """)
    return


@app.cell
def _(CIRCLES, N, mo, p, r, x, xp, y):
    # Control parameters.
    p.controls.feastol = 1e-9               # Set the feasibility tolerance to a very small value.
    p.controls.timelimit = 3                # Set a time limit in seconds.
    p.controls.nlpsolver = xp.constants.NLPSOLVER_GLOBAL        # Set the NLP solver to global.

    # Solve the problem.
    p.optimize()

    # Print a solution summary.
    xsol = p.getSolution(x)
    ysol = p.getSolution(y)
    rsol = p.getSolution(r)
    with mo.capture_stdout() as _buffer:
        print(f"Sum of radii for N = {N} is {p.attributes.objval}")
        for i in CIRCLES:
            print(f"{i}: x = {xsol[i]}, y = {ysol[i]}, r = {rsol[i]}")
    mo.show_code(mo.plain_text(_buffer.getvalue()), position="above")
    return rsol, xsol, ysol


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Visualization
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The plot below shows the circles defined by the solution inside the unit square, with a blue line and label indicating the radius of each circle.
    """)
    return


@app.cell
def _(plt, rsol, xsol, ysol):
    # Create a plot
    fig, ax = plt.subplots()

    # Plot each circle
    for (_x, _y, _r) in zip(xsol, ysol, rsol):
        # Draw the circle with red edge
        circle = plt.Circle((_x, _y), _r, edgecolor='red', facecolor='none')
        ax.add_patch(circle)

        # Draw the radius line in blue
        ax.plot([_x, _x + _r], [_y, _y], color='blue')

        # Add the radius length as label
        ax.text(_x + _r / 2, _y, f'R={_r:.2f}', color='blue', fontsize=8, ha='center', va='bottom')

    # Set the limits and aspect ratio
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal', 'box')
    ax.grid(True)
    fig
    return


if __name__ == "__main__":
    app.run()
