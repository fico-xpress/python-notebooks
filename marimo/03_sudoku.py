# /// script
# [tool.marimo.opengraph]
# title = "Sudoku Solving"
# description = "Feasibility Problem"
# image = "__marimo__/thumbnail-sudoku.svg"
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
    import matplotlib.ticker as ticker
    import math
    return math, mo, np, plt, ticker, xp


@app.cell(hide_code=True)
def _(mo):
    def license_error_callout(error):
        # Render a clear, copyable error message as normal cell output instead
        # of letting the SolverError surface as marimo's generic "see console"
        # error popup, which is unhelpful (and there may be no visible console
        # at all when running locally with `marimo run`).
        return mo.callout(mo.md(f"""
        **This instance could not be solved:**

        ```
        {error}
        ```

        This is due to the Community license's combined rows-plus-columns limit of 5000 being exceeded - the 16x16 grid alone requires 5120. Try the 4x4 or 9x9 grid size instead, or use a full Xpress license to solve the 16x16 variant.
        """), kind="danger")

    return (license_error_callout,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # **Solving a Sudoku problem**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Sudoku: place numbers from 1 to $n$ into a $n \times n$ grid such that no number repeats in any row, column, or $q \times q$ sub-grid.

    &copy; Copyright 2025-2026 Fair Isaac Corporation. The use of this example is subject to [legal and license requirements](https://github.com/fico-xpress/python-notebooks#legal-and-license-requirements).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Problem description and formulation

    In classic sudoku, the objective is to fill a $n \times n$ grid with digits so that each column, each row, and each of the $q \times q$ subgrids that compose the grid (also called "boxes", "blocks", or "regions") contains all of the digits from 1 to $n$. The puzzle setter provides a partially completed grid, which for a well-posed puzzle has a single solution.

    Several formulations exist for this problem, where choosing the right variables is a fundamental step. Although all cells must contain integer numbers, using integer decision variables would make it hard to guarantee that they are different within a given block (row/column) with a mathematical programming formulation.

    In this example, we use binary variables $assign_{i,j,k}$ that indicate whether a value $k \in \{1,..,n\}$ is assigned to a given cell $i,j \in \mathcal{N}$ of the grid (=1) or not (=0). Also, no objective function is needed: this is a **feasibility** problem not an **optimization** problem, subject to the following constraints:

    * Each cell can only have one value:
    $$\sum_{k \in \mathcal{N}} assign_{i,j,k} = 1, \qquad \forall i,j \in \mathcal{N}$$

    * Assign values already in grid ($g_{i,j}$ has a positive value):
    $$assign_{i,j,k} = 1, \qquad \forall i,j \in \mathcal{N}, k = g_{i,j}, g_{i,j} > 0$$

    * Every number must appear once on every row:
    $$\sum_{j \in \mathcal{N}} assign_{i,j,k} = 1, \qquad \forall i,k \in \mathcal{N}$$

    * Every number must appear once on every column:
    $$\sum_{i \in \mathcal{N}} assign_{i,j,k} = 1, \qquad \forall j,k \in \mathcal{N}$$

    * Every number must appear once in every $q \times q$ block:
    $$\sum_{i,j \in \mathcal{Q}: n = i+q.h, m = j+q.l} assign_{n,m,k} = 1, \qquad \forall h,l \in \mathcal{Q}, \forall k \in \mathcal{N}$$
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Data preparation

    The input is a starting grid where the unknown numbers are replaced by zero. You can adjust the parameter below to switch between the $4 \times 4$, $9 \times 9$ (classic), and $16 \times 16$ variants. The $16 \times 16$ variant creates a much larger model and **requires a full Xpress license** - it will not solve under a Community license. The starting grid is shown below.
    """)
    return


@app.cell
def _(mo):
    grid_selector = mo.ui.radio(
        options={"4x4 (small)": "4x4", "9x9 (classic)": "9x9", "16x16 (variant, requires full Xpress license)": "16x16"},
        value="9x9 (classic)",
        label="Grid size"
    )
    grid_selector
    return (grid_selector,)


@app.cell
def _(grid_selector, mo):
    grid2x2 = [
        [1, 0, 0, 4],
        [0, 4, 1, 0],
        [0, 1, 4, 0],
        [4, 0, 0, 1]
    ]
    grid3x3 = [
        [8, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 3, 6, 0, 0, 0, 0, 0],
        [0, 7, 0, 0, 9, 0, 2, 0, 0],
        [0, 5, 0, 0, 0, 7, 0, 0, 0],
        [0, 0, 0, 0, 4, 5, 7, 0, 0],
        [0, 0, 0, 1, 0, 0, 0, 3, 0],
        [0, 0, 1, 0, 0, 0, 0, 6, 8],
        [0, 0, 8, 5, 0, 0, 0, 1, 0],
        [0, 9, 0, 0, 0, 0, 4, 0, 0]
    ]
    grid4x4 = [
        [0, 0, 12, 0, 0, 2, 0, 0, 0, 7, 3, 0, 13, 15, 0, 0],
        [15, 0, 0, 0, 0, 3, 0, 0, 9, 0, 0, 0, 12, 0, 0, 10],
        [0, 0, 0, 0, 9, 0, 6, 0, 0, 0, 12, 0, 0, 0, 2, 5],
        [6, 11, 1, 0, 0, 10, 5, 0, 0, 2, 0, 15, 0, 0, 0, 0],
        [4, 6, 3, 0, 0, 0, 13, 14, 0, 0, 0, 0, 0, 7, 0, 0],
        [0, 15, 11, 0, 7, 0, 9, 0, 0, 0, 0, 0, 0, 0, 1, 0],
        [0, 1, 0, 10, 15, 0, 0, 0, 11, 3, 14, 0, 6, 0, 0, 0],
        [13, 0, 8, 7, 0, 5, 0, 0, 0, 1, 9, 12, 0, 0, 0, 0],
        [0, 0, 0, 6, 3, 7, 15, 4, 0, 0, 0, 0, 0, 14, 0, 0],
        [0, 8, 0, 0, 0, 0, 0, 0, 0, 11, 7, 0, 4, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 13, 0, 0, 6, 9, 0, 3, 0],
        [0, 0, 0, 0, 2, 8, 14, 0, 3, 0, 0, 10, 0, 0, 13, 7],
        [0, 0, 0, 8, 0, 0, 0, 7, 10, 0, 0, 0, 0, 0, 5, 1],
        [0, 4, 10, 1, 6, 0, 0, 0, 0, 12, 0, 14, 7, 3, 9, 15],
        [3, 0, 15, 0, 0, 0, 0, 8, 0, 0, 1, 0, 14, 12, 0, 0],
        [2, 0, 0, 9, 12, 0, 0, 1, 0, 0, 0, 0, 0, 6, 8, 0]
    ]
    if grid_selector.value == "4x4":
        grid = grid2x2
        q = 2
    elif grid_selector.value == "9x9":
        grid = grid3x3
        q = 3
    else:
        grid = grid4x4
        q = 4
    mo.show_code()
    return grid, q


@app.cell
def _(grid, np, plt, q, ticker):
    encode_start = {1: '1', 2: '2', 3: '3', 4: '4', 5: '5',
                     6: '6', 7: '7', 8: '8', 9: '9', 10: 'A',
                     11: 'B', 12: 'C', 13: 'D', 14: 'E', 15: 'F', 16: 'G'}
    n_start = q**2
    fig_start, ax_start = plt.subplots(figsize=(max(6, n_start // 2), max(6, n_start // 2)))
    min_val_start, max_val_start, diff_start = 0, n_start, 1
    for i_start in range(n_start):
        for j_start in range(n_start):
            value = grid[i_start][j_start]
            if value > 0:
                ax_start.text(j_start, n_start - 1 - i_start, encode_start[value], va='center', ha='center')
    ax_start.set_aspect('equal', 'box')
    ax_start.set_xlim(min_val_start - diff_start / 2, max_val_start - diff_start / 2)
    ax_start.set_ylim(min_val_start - diff_start / 2, max_val_start - diff_start / 2)
    ax_start.set_xticklabels([])
    ax_start.set_yticklabels([])
    ax_start.yaxis.set_minor_locator(ticker.FixedLocator(np.arange(-0.5, q * q, 1)))
    ax_start.xaxis.set_minor_locator(ticker.FixedLocator(np.arange(-0.5, q * q, 1)))
    ax_start.xaxis.set_major_locator(ticker.FixedLocator(np.arange(-0.5, q * q, q)))
    ax_start.yaxis.set_major_locator(ticker.FixedLocator(np.arange(-0.5, q * q, q)))
    ax_start.grid(which='minor')
    ax_start.grid(which='major', color='black')
    fig_start
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Model implementation and results

    When passing sets, lists, or range objects to [prob.addVariables()](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/python/HTML/problem.addVariables.html), the result is a Python dictionary of variables, whose keys are tuples of indices. Variables $assign$ are created this way.

    The constraints are then created and added to the problem directly by passing the corresponding expression as a list comprehension. Note that no objective is set as this is a feasibility problem.
    """)
    return


@app.cell
def _(grid, license_error_callout, mo, q, xp):
    # Main dimensions of the problem: q is the size of the qxq block (3x3 in the classic Sudoku game).

    n = q**2       # the size must be the square of the size of the subgrids
    N = range(n)   # set of numbers from 0 to n-1
    Q = range(q)   # set of numbers from 0 to q-1

    # Create a model
    prob = xp.problem()

    assign = prob.addVariables(N, N, N, vartype=xp.binary)

    # Constraint 1: each cell can only have one value
    prob.addConstraint(xp.Sum(assign[i,j,k] for k in N) == 1 for i in N for j in N)

    # Constraint 2: fix the cells in the starting grid
    prob.addConstraint(assign[i,j,grid[i][j] - 1] == 1 for i in N for j in N if grid[i][j] > 0)

    # Constraint 3a: Every number must appear once on every row
    prob.addConstraint(xp.Sum(assign[i,j,k] for j in N) == 1 for i in N for k in N)

    # Constraint 3b: ... and on every column
    prob.addConstraint(xp.Sum(assign[i,j,k] for i in N) == 1 for j in N for k in N)

    # Constraint 3c: Every number must appear once in every qxq block
    prob.addConstraint(xp.Sum(assign[i+q*h,j+q*l,k] for i in Q for j in Q) == 1 for h in Q for l in Q for k in N)

    prob.controls.outputlog = 0  # Suppress solver logging for cleaner output

    # Catches a Community-license size limit so it renders as a clear message
    # below, instead of marimo's generic "see console" error popup. Only the
    # 16x16 grid can hit this.
    try:
        prob.optimize()
        solve_error = None
    except xp.SolverError as e:
        solve_error = e

    mo.show_code(license_error_callout(solve_error) if solve_error else None, position="above")
    return N, Q, assign, n, prob, solve_error


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Visualization

    Now we use *matplotlib* to visualize the solution in a $n\times n$ grid.
    """)
    return


@app.cell
def _(N, Q, assign, math, mo, n, np, plt, prob, q, solve_error, ticker):
    if solve_error is not None:
        fig = None
    else:
        # Visualize solution
        fig, ax = plt.subplots(figsize=(max(6, n//2), max(6, n//2)))
        min_val, max_val, diff = 0, n, 1

        # This is used to visualize the Sudoku solution with the 16x16 grid too
        encode = {1: '1', 2: '2', 3: '3', 4: '4', 5: '5',
                  6: '6', 7: '7', 8: '8', 9: '9', 10: 'A',
                  11: 'B', 12: 'C', 13: 'D', 14: 'E', 15: 'F', 16: 'G'}

        xsol = prob.getSolution(assign)

        for i1 in Q:
            for i2 in Q:
                for j1 in Q:
                    for j2 in Q:
                        c = encode[math.floor(1 + sum(xsol[i1*q + i2, j1*q + j2, k]*k for k in N) + 0.5)]
                        ax.text(j1*q + j2, n - 1 - (i1*q + i2), c, va='center', ha='center')

        # Set up the plot dimensions
        ax.set_aspect('equal', 'box')
        ax.set_xlim(min_val-diff/2, max_val-diff/2)
        ax.set_ylim(min_val-diff/2, max_val-diff/2)

        # Hide the axis labels
        ax.set_xticklabels([])
        ax.set_yticklabels([])

        # Draw the sudoku grid
        ax.yaxis.set_minor_locator(ticker.FixedLocator(np.arange(-0.5, q*q, 1)))
        ax.xaxis.set_minor_locator(ticker.FixedLocator(np.arange(-0.5, q*q, 1)))
        ax.xaxis.set_major_locator(ticker.FixedLocator(np.arange(-0.5, q*q, q)))
        ax.yaxis.set_major_locator(ticker.FixedLocator(np.arange(-0.5, q*q, q)))
        ax.grid(which='minor')
        ax.grid(which='major', color='black')

    fig
    return (fig,)


if __name__ == "__main__":
    app.run()