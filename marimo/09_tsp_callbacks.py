# /// script
# [tool.marimo.opengraph]
# title = "TSP with Callbacks"
# description = "Solver Callbacks and Cut Generation"
# image = "__marimo__/thumbnail-tsp.svg"
# ///

import marimo

__generated_with = "0.23.13"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import xpress as xp
    import numpy as np
    import networkx as nx
    import matplotlib.pyplot as plt
    import itertools
    import time

    return itertools, mo, np, nx, plt, time, xp


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # **Solving a TSP problem using callbacks**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Solve an instance of the [Traveling Salesperson Problem (TSP)](https://en.wikipedia.org/wiki/Travelling_salesman_problem) with Xpress using callbacks and *NumPy* arrays.

    We compare three ways of eliminating subtours from the standard TSP formulation: adding every subtour elimination constraint upfront, the Miller-Tucker-Zemlin (MTZ) formulation, and a solver **callback** that adds only the subtour elimination cuts that are actually needed while the branch-and-bound runs.

    *This example requires a full license of the FICO&reg; Xpress Optimizer to run the larger instances below. Click on [this link](https://www.fico.com/en/fico-xpress-trial-and-licensing-options) for more information about trial and licensing options.*

    &copy; Copyright 2025-2026 Fair Isaac Corporation. The use of this example is subject to [legal and license requirements](https://github.com/fico-xpress/python-notebooks#legal-and-license-requirements).
    """)
    return


@app.cell
def _():
    # Install the necessary packages
    # '%pip install -q xpress networkx matplotlib' command supported automatically in marimo
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
    Binary variables $use_{ij} \in \{0,1\}, \forall i,j \in \mathcal{N}$ represent the decision of whether the tour uses the arc $(i,j)$ (i.e. if we go from city $i$ to $j$) or not. An optimal tour can be found by solving:
    $$
    \min \sum_{i,j \in \mathcal{N}} dist_{ij} \cdot use_{ij}
    $$

    subject to:

    * We have to enter and leave every city, and a city cannot be its own destination:
    $$
    \sum_{j \in \mathcal{N}} use_{ij} = 1, \quad \forall i \in \mathcal{N} \\
    \sum_{j \in \mathcal{N}} use_{ji} = 1, \quad \forall i \in \mathcal{N} \\
    use_{ii} = 0, \quad \forall i \in \mathcal{N}
    $$

    where $dist_{ij}, \forall i,j \in \mathcal{N}$ represents the distance (or cost) associated with traveling on an arc $(i,j)$. These constraints alone allow **subtours**: several disjoint short cycles that together visit every city, instead of one single tour. We look at three ways of ruling subtours out below.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Model parameters

    **You can adjust the parameters below to change the problem instance and re-solve each formulation automatically.**

    **Values of 13 cities or more require a full Xpress license: the naive (upfront constraints) formulation below already exceeds the Community license's combined rows-plus-columns limit of 5000 at that size. Further down, we provide separate sliders for the formulations that scale well under a Community license.**
    """)
    return


@app.cell
def _(mo):
    small_n_slider = mo.ui.slider(10, 15, value=12, label="Number of cities", show_value=True)
    seed_slider = mo.ui.slider(0, 99, value=0, label="Random seed (each value gives a different instance)", show_value=True)
    time_limit_slider = mo.ui.slider(5, 60, value=20, step=5, label="Solver time limit in seconds", show_value=True)
    mo.vstack([small_n_slider, seed_slider, time_limit_slider])
    return seed_slider, small_n_slider, time_limit_slider


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Data preparation and visualization
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We generate random city coordinates and the resulting distance matrix for the naive/MTZ instance size chosen above (**Number of cities**). The callback demo further down generates its own, larger instance using the same seed.
    """)
    return


@app.cell
def _(mo, np, seed_slider, small_n_slider):
    n_small = small_n_slider.value
    CITIES_small = range(n_small)

    np.random.seed(seed_slider.value)
    X_small = 100 * np.random.rand(n_small)
    Y_small = 100 * np.random.rand(n_small)

    # Compute distance matrix
    dist_small = np.ceil(np.sqrt((X_small.reshape(n_small, 1) - X_small.reshape(1, n_small)) ** 2 +
                                  (Y_small.reshape(n_small, 1) - Y_small.reshape(1, n_small)) ** 2))
    mo.show_code()
    return CITIES_small, X_small, Y_small, dist_small, n_small


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    A small helper function draws a set of cities and, if given, the arcs used by a tour (highlighted in red if it contains a subtour, dictated by the `subtour` flag).
    """)
    return


@app.cell(hide_code=True)
def _(nx, plt):
    def plot_tour(X, Y, edges, title, subtour=False):
        fig, ax = plt.subplots(figsize=(8, 6), dpi=100)

        xy = {i: (X[i], Y[i]) for i in range(len(X))}

        graph = nx.Graph()
        graph.add_nodes_from(range(len(X)))
        graph.add_edges_from(edges)

        edge_color = "#cc3333" if subtour else "#5555ff"
        nx.draw(graph, pos=xy, node_size=250, with_labels=True, node_color="lightblue",
                edge_color=edge_color, ax=ax)
        ax.set_title(title)
        plt.tight_layout()
        return fig

    return (plot_tour,)


@app.cell(hide_code=True)
def _(mo, time, xp):
    def optimize_safe(p):
        """Call p.optimize(), returning (error, solve_time). error is None on success.

        Catching xp.SolverError here means a Community-license size limit shows up
        as a clear, copyable message in the cell output below, instead of marimo's
        generic "see console" error popup - which is unhelpful, and there may be no
        visible console at all when running locally with `marimo run`.
        """
        try:
            start = time.time()
            p.optimize()
            return None, time.time() - start
        except xp.SolverError as e:
            return e, None

    def license_error_callout(error, max_safe_n):
        return mo.callout(mo.md(f"""
        **This instance could not be solved:**

        ```
        {error}
        ```

        This is due to the Community license's combined rows-plus-columns limit of 5000 being exceeded - see the license note next to the relevant slider above. Try a smaller **Number of cities** value (up to {max_safe_n}), or use a full Xpress license to avoid this limit.
        """), kind="danger")

    return license_error_callout, optimize_safe


@app.cell(hide_code=True)
def _(X_small, Y_small, plot_tour):
    plot_tour(X_small, Y_small, [], "Cities (no tour yet)")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Standard formulation (subtours possible)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We first solve the standard formulation above with no subtour elimination at all. Note the use of [problem.addVariables](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/python/HTML/problem.addVariables.html) to create a square matrix of binary variables, which lets NumPy operations like `.flatten()` and slicing (`use[i,:]`) work directly on the Xpress variables.
    """)
    return


@app.cell
def _(CITIES_small, dist_small, mo, n_small, xp):
    # Create problem
    p_naive = xp.problem()

    # Create variables as a square matrix of binary variables.
    use_naive = p_naive.addVariables(n_small, n_small, vartype=xp.binary, name="x")

    # Degree constraints
    p_naive.addConstraint(xp.Sum(use_naive[i, :]) == 1 for i in CITIES_small)
    p_naive.addConstraint(xp.Sum(use_naive[:, i]) == 1 for i in CITIES_small)

    # Fix diagonals (i.e. city X -> city X) to zero
    p_naive.addConstraint(use_naive[i, i] == 0 for i in CITIES_small)

    # Objective function
    p_naive.setObjective(xp.Sum((dist_small * use_naive).flatten()))

    p_naive.controls.outputlog = 0
    p_naive.optimize()

    sol_naive = p_naive.getSolution(use_naive)
    edges_naive = [(i, j) for i in CITIES_small for j in CITIES_small if i != j and sol_naive[i, j] > 0.5]
    mo.show_code()
    return edges_naive, p_naive


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The plot below shows the resulting tour. As you can see, the solution contains subtours: it is not yet a valid solution for the problem, since a valid tour must visit every city exactly once in a single loop.
    """)
    return


@app.cell(hide_code=True)
def _(X_small, Y_small, edges_naive, plot_tour):
    plot_tour(X_small, Y_small, edges_naive, "Standard formulation: subtours present", subtour=True)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Adding subtour elimination constraints upfront
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    A straightforward way to rule out subtours is to add a constraint for every possible subset $\mathcal{S} \subsetneq \mathcal{N}$ of size $\geq 2$:

    $$
    \sum_{i,j \in \mathcal{S}} use_{ij} \leq |\mathcal{S}| - 1 \quad \forall \mathcal{S} \subsetneq \mathcal{N},\ |\mathcal{S}| \geq 2
    $$

    The number of such constraints grows exponentially with the number of cities, so this only scales to a handful of cities - which is why the **Number of cities** control above is capped at 15 for this comparison (see the license note next to that control).
    """)
    return


@app.cell
def _(CITIES_small, itertools, license_error_callout, mo, optimize_safe, p_naive, time_limit_slider, use_naive, xp):
    # Add every subtour elimination constraint, then re-solve.
    p_naive.addConstraint(
        xp.Sum(use_naive[i, j] for i in subset for j in subset) <= len(subset) - 1
        for L in range(2, len(CITIES_small))
        for subset in itertools.combinations(CITIES_small, L)
    )

    p_naive.controls.timelimit = time_limit_slider.value
    # optimize_safe() re-solves p_naive, catching a Community-license size
    # error so it renders as a clear message instead of crashing.
    naive_error, naive_solve_time = optimize_safe(p_naive)

    if naive_error is None:
        sol_naive_full = p_naive.getSolution(use_naive)
        edges_naive_full = [(i, j) for i in CITIES_small for j in CITIES_small if i != j and sol_naive_full[i, j] > 0.5]
        naive_obj = p_naive.attributes.objval
        naive_callout = None
    else:
        edges_naive_full = None
        naive_obj = None
        naive_callout = license_error_callout(naive_error, 12)

    mo.show_code(naive_callout, position="above")
    return edges_naive_full, naive_error, naive_obj, naive_solve_time


@app.cell(hide_code=True)
def _(mo, naive_error, naive_obj, naive_solve_time):
    if naive_error is None:
        naive_result_md = mo.md(f"""
        **Objective value with all subtour elimination constraints added upfront:** {naive_obj:.1f} &nbsp;&nbsp; **Solve time:** {naive_solve_time:.2f}s (if the limit was hit, this may only be the best solution found so far, not a proven optimum).
        """)
    else:
        naive_result_md = None
    naive_result_md
    return


@app.cell(hide_code=True)
def _(X_small, Y_small, edges_naive_full, plot_tour):
    naive_full_fig = plot_tour(X_small, Y_small, edges_naive_full, "All subtour elimination constraints added upfront") if edges_naive_full is not None else None
    naive_full_fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Miller-Tucker-Zemlin (MTZ) formulation
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The Miller, Tucker, Zemlin subtour elimination constraints instead introduce a new set of continuous variables $step_i$ = the step at which node $i$ is visited, $\forall i \in \{2,...,|\mathcal{N}|\}$, and use them to forbid subtours with only $(|\mathcal{N}|-1)^2$ extra constraints - a polynomial number, instead of an exponential one:

    $$
    step_j \geq step_i + 1 - (n-1) \cdot (1 - use_{ij}), \quad \forall i,j \in \{2,..,n\}
    $$

    with $n = |\mathcal{N}|$. This scales much better than the previous approach, at the cost of a slightly less tight LP relaxation.
    """)
    return


@app.cell
def _(CITIES_small, dist_small, mo, n_small, time, time_limit_slider, xp):
    # Create problem
    p_mtz = xp.problem()

    use_mtz = p_mtz.addVariables(n_small, n_small, vartype=xp.binary, name="x")
    step_mtz = p_mtz.addVariables(n_small, name="t")

    # Degree constraints
    p_mtz.addConstraint(xp.Sum(use_mtz[i, :]) == 1 for i in CITIES_small)
    p_mtz.addConstraint(xp.Sum(use_mtz[:, i]) == 1 for i in CITIES_small)

    # Fix diagonals (i.e. city X -> city X) to zero
    p_mtz.addConstraint(use_mtz[i, i] == 0 for i in CITIES_small)

    # Miller, Tucker, Zemlin subtour elimination constraints
    p_mtz.addConstraint(
        step_mtz[j] >= step_mtz[i] + 1 - (n_small - 1) * (1 - use_mtz[i, j])
        for i in range(1, n_small) for j in range(1, n_small)
    )

    # Objective function
    p_mtz.setObjective(xp.Sum((dist_small * use_mtz).flatten()))

    p_mtz.controls.outputlog = 0
    p_mtz.controls.timelimit = time_limit_slider.value
    mtz_start = time.time()
    p_mtz.optimize()
    mtz_solve_time = time.time() - mtz_start

    sol_mtz = p_mtz.getSolution(use_mtz)
    edges_mtz = [(i, j) for i in CITIES_small for j in CITIES_small if i != j and sol_mtz[i, j] > 0.5]
    mtz_obj = p_mtz.attributes.objval
    mo.show_code()
    return edges_mtz, mtz_obj, mtz_solve_time


@app.cell(hide_code=True)
def _(mo, mtz_obj, mtz_solve_time, naive_error, naive_obj, naive_solve_time):
    if naive_error is None:
        mtz_comparison_md = mo.md(f"""
        **Objective value with the MTZ formulation:** {mtz_obj:.1f} &nbsp;&nbsp; **Solve time:** {mtz_solve_time:.2f}s (compare with **{naive_obj:.1f}** in **{naive_solve_time:.2f}s** from the upfront subtour elimination above - both formulations solve the same instance and should agree once neither one is cut short by the solver time limit).
        """)
    else:
        mtz_comparison_md = mo.md(f"""
        **Objective value with the MTZ formulation:** {mtz_obj:.1f} &nbsp;&nbsp; **Solve time:** {mtz_solve_time:.2f}s (no comparison available since the upfront subtour elimination above could not be solved - see the error above).
        """)
    mtz_comparison_md
    return


@app.cell(hide_code=True)
def _(X_small, Y_small, edges_mtz, plot_tour):
    plot_tour(X_small, Y_small, edges_mtz, "Miller-Tucker-Zemlin formulation")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## MTZ at a larger scale

    Because MTZ only adds a polynomial number of constraints, it comfortably outgrows the **Number of cities** control above. The slider below lets you push the MTZ formulation on its own, independently of the naive comparison, using a fresh instance of the same size.

    **Values of 50 cities or more require a full Xpress license: at that point the model's rows plus columns exceeds the Community license's combined limit of 5000.**
    """)
    return


@app.cell
def _(mo):
    mtz_scale_n_slider = mo.ui.slider(15, 100, value=30, step=1, label="Number of cities (MTZ formulation)", show_value=True)
    mtz_scale_n_slider
    return (mtz_scale_n_slider,)


@app.cell
def _(license_error_callout, mo, mtz_scale_n_slider, np, optimize_safe, seed_slider, xp):
    n_mtz_scale = mtz_scale_n_slider.value
    CITIES_mtz_scale = range(n_mtz_scale)

    np.random.seed(seed_slider.value)
    X_mtz_scale = 100 * np.random.rand(n_mtz_scale)
    Y_mtz_scale = 100 * np.random.rand(n_mtz_scale)

    dist_mtz_scale = np.ceil(np.sqrt((X_mtz_scale.reshape(n_mtz_scale, 1) - X_mtz_scale.reshape(1, n_mtz_scale)) ** 2 +
                                      (Y_mtz_scale.reshape(n_mtz_scale, 1) - Y_mtz_scale.reshape(1, n_mtz_scale)) ** 2))

    # Create problem
    p_mtz_scale = xp.problem()

    use_mtz_scale = p_mtz_scale.addVariables(n_mtz_scale, n_mtz_scale, vartype=xp.binary, name="x")
    step_mtz_scale = p_mtz_scale.addVariables(n_mtz_scale, name="t")

    # Degree constraints
    p_mtz_scale.addConstraint(xp.Sum(use_mtz_scale[i, :]) == 1 for i in CITIES_mtz_scale)
    p_mtz_scale.addConstraint(xp.Sum(use_mtz_scale[:, i]) == 1 for i in CITIES_mtz_scale)

    # Fix diagonals (i.e. city X -> city X) to zero
    p_mtz_scale.addConstraint(use_mtz_scale[i, i] == 0 for i in CITIES_mtz_scale)

    # Miller, Tucker, Zemlin subtour elimination constraints
    p_mtz_scale.addConstraint(
        step_mtz_scale[j] >= step_mtz_scale[i] + 1 - (n_mtz_scale - 1) * (1 - use_mtz_scale[i, j])
        for i in range(1, n_mtz_scale) for j in range(1, n_mtz_scale)
    )

    # Objective function
    p_mtz_scale.setObjective(xp.Sum((dist_mtz_scale * use_mtz_scale).flatten()))

    p_mtz_scale.controls.outputlog = 0
    # optimize_safe() re-solves p_mtz_scale, catching a Community-license size
    # error so it renders as a clear message instead of crashing.
    mtz_scale_error, mtz_scale_solve_time = optimize_safe(p_mtz_scale)

    if mtz_scale_error is None:
        sol_mtz_scale = p_mtz_scale.getSolution(use_mtz_scale)
        edges_mtz_scale = [(i, j) for i in CITIES_mtz_scale for j in CITIES_mtz_scale if i != j and sol_mtz_scale[i, j] > 0.5]
        mtz_scale_obj = p_mtz_scale.attributes.objval
        mtz_scale_callout = None
    else:
        edges_mtz_scale = None
        mtz_scale_obj = None
        mtz_scale_callout = license_error_callout(mtz_scale_error, 49)

    mo.show_code(mtz_scale_callout, position="above")
    return X_mtz_scale, Y_mtz_scale, edges_mtz_scale, mtz_scale_obj, mtz_scale_solve_time, n_mtz_scale


@app.cell(hide_code=True)
def _(mo, mtz_scale_obj, mtz_scale_solve_time, n_mtz_scale):
    if mtz_scale_obj is not None:
        mtz_scale_result_md = mo.md(f"""
        **Objective value with the MTZ formulation ({n_mtz_scale} cities):** {mtz_scale_obj:.1f} &nbsp;&nbsp; **Solve time:** {mtz_scale_solve_time:.2f}s.
        """)
    else:
        mtz_scale_result_md = None
    mtz_scale_result_md
    return


@app.cell(hide_code=True)
def _(X_mtz_scale, Y_mtz_scale, edges_mtz_scale, n_mtz_scale, plot_tour):
    mtz_scale_fig = plot_tour(X_mtz_scale, Y_mtz_scale, edges_mtz_scale, f"MTZ formulation: valid tour over {n_mtz_scale} cities") if edges_mtz_scale is not None else None
    mtz_scale_fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Using callbacks
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Neither of the two formulations above scales well: the first one because of the exponential number of constraints, the second because a dense set of MTZ constraints slows down the LP relaxation as the number of cities grows.

    [Solver callbacks](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/python/HTML/chCallbacks.html) let us do much better: we drop subtour elimination entirely from the model and instead register a **pre-intsol callback** with [problem.addPreIntsolCallback](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/python/HTML/problem.addPreIntsolCallback.html). The Optimizer calls this function every time the branch-and-bound finds a new integer-feasible solution, *before* accepting it. Our callback:

    * reconstructs the tour from the current solution using [problem.getCallbackSolution](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/python/HTML/problem.getCallbackSolution.html),
    * checks whether it is a single tour or contains subtours,
    * if it contains subtours, either rejects the solution outright (if it came from a heuristic) or adds a cut for each subtour found via [problem.presolveRow](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/python/HTML/problem.presolveRow.html) and [problem.addCuts](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/python/HTML/problem.addCuts.html) (if it came from the LP relaxation at the current node).

    By default the Xpress Optimizer serializes calls into this callback across its B&B worker threads (the `MUTEXCALLBACKS` control, on by default), so the callback code below does not need to worry about being called concurrently from multiple threads - it always runs one call at a time, even though `problem.optimize()` itself uses several threads internally.

    The callback function is defined fresh inside the solve cell below, so a new instance of the callback is created (closing over the current `use` variable array) every time this cell re-runs - e.g. when the **Number of cities** control below changes.

    **Because the callback formulation scales much further than the naive and MTZ formulations above, it gets its own, wider-range control here rather than sharing the one at the top of the notebook.**

    **Values of 70 cities or more require a full Xpress license: at that point the model's rows plus columns exceeds the Community license's combined limit of 5000.**
    """)
    return


@app.cell
def _(mo):
    callback_n_slider = mo.ui.slider(10, 150, value=60, step=1, label="Number of cities (callback formulation)", show_value=True)
    callback_n_slider
    return (callback_n_slider,)


@app.cell
def _(itertools, license_error_callout, mo, np, optimize_safe, seed_slider, callback_n_slider, xp):
    n_cb = callback_n_slider.value
    CITIES_cb = range(n_cb)

    np.random.seed(seed_slider.value)
    X_cb = 100 * np.random.rand(n_cb)
    Y_cb = 100 * np.random.rand(n_cb)

    dist_cb = np.ceil(np.sqrt((X_cb.reshape(n_cb, 1) - X_cb.reshape(1, n_cb)) ** 2 +
                              (Y_cb.reshape(n_cb, 1) - Y_cb.reshape(1, n_cb)) ** 2))

    # Create problem
    p_cb = xp.problem()

    use_cb = p_cb.addVariables(n_cb, n_cb, vartype=xp.binary, name="x")

    # Degree constraints (no subtour elimination at all - the callback below handles that)
    p_cb.addConstraint(xp.Sum(use_cb[i, :]) == 1 for i in CITIES_cb)
    p_cb.addConstraint(xp.Sum(use_cb[:, i]) == 1 for i in CITIES_cb)
    p_cb.addConstraint(use_cb[i, i] == 0 for i in CITIES_cb)

    p_cb.setObjective(xp.Sum((dist_cb * use_cb).flatten()))

    def cb_preintsol(prob, data, soltype, cutoff):
        """Callback for checking if a MIP solution is acceptable.

        prob: Xpress problem object
        data: data object = number of cities
        soltype: type of MIP solution found. 0 - LP relaxation is integer
            feasible, 1 - MIP solution found by a heuristic, 2 - MIP solution
            provided by the user.
        """
        n = data
        xsol = np.array(prob.getCallbackSolution(use_cb)).reshape(n, n)
        tour = np.argmax(xsol, axis=1)  # index of the max (non-zero) element in each row = next city in the tour

        i = 0
        ncities = 1
        while tour[i] != 0 and ncities < n:
            ncities += 1
            i = tour[i]

        reject = False
        if ncities < n:
            # The tour does not pass through all the cities: it contains subtours.
            if soltype != 0:
                # Solution came from a heuristic or the user: reject outright, no cut needed.
                reject = True
            else:
                # Solution came from the LP relaxation at the current node: add a cut per subtour instead.
                unchecked = np.zeros(n)
                nsubtour = 0

                cut_mstart = [0]
                cut_ind = []
                cut_coe = []
                cut_rhs = []
                nnz = 0
                ncuts = 0

                while np.min(unchecked) == 0:
                    nsubtour += 1
                    firstcity = np.argmin(unchecked)
                    i = firstcity
                    while True:
                        unchecked[i] = nsubtour
                        i = tour[i]
                        if i == firstcity:
                            break

                    # S = cities in this subtour, compS = every other city
                    S = np.where(unchecked == nsubtour)[0].tolist()
                    compS = np.where(unchecked != nsubtour)[0].tolist()
                    indices = [i * n + j for i in S for j in compS]

                    mcolsp, dvalp, drhsp, p_status = prob.presolveRow(
                        rowtype="G", origcolind=indices, origrowcoef=np.ones(len(indices)), origrhs=1
                    )

                    nnz += len(mcolsp)
                    ncuts += 1
                    cut_ind.extend(mcolsp)
                    cut_coe.extend(dvalp)
                    cut_rhs.append(drhsp)
                    cut_mstart.append(nnz)

                if ncuts > 0:
                    prob.addCuts(cuttype=[0] * ncuts, rowtype=["G"] * ncuts, rhs=cut_rhs,
                                 start=cut_mstart, colind=cut_ind, cutcoef=cut_coe)

        return (reject, None)

    p_cb.addPreIntsolCallback(cb_preintsol, n_cb)

    p_cb.controls.outputlog = 0
    # optimize_safe() re-solves p_cb, catching a Community-license size
    # error so it renders as a clear message instead of crashing.
    cb_error, cb_solve_time = optimize_safe(p_cb)

    if cb_error is None:
        sol_cb = p_cb.getSolution(use_cb)
        edges_cb = [(i, j) for i in CITIES_cb for j in CITIES_cb if i != j and sol_cb[i, j] > 0.5]
        cb_obj = p_cb.attributes.objval
        cb_callout = None
    else:
        edges_cb = None
        cb_obj = None
        cb_callout = license_error_callout(cb_error, 69)

    mo.show_code(cb_callout, position="above")
    return X_cb, Y_cb, cb_obj, cb_solve_time, edges_cb, n_cb


@app.cell(hide_code=True)
def _(cb_obj, cb_solve_time, mo, n_cb):
    if cb_obj is not None:
        cb_result_md = mo.md(f"""
        **Objective value with the callback formulation ({n_cb} cities):** {cb_obj:.1f} &nbsp;&nbsp; **Solve time:** {cb_solve_time:.2f}s. Note this instance is typically larger than the ones the naive and MTZ demos above can handle in reasonable time, showing how much further relaxing subtour elimination into a callback lets the model scale.
        """)
    else:
        cb_result_md = None
    cb_result_md
    return


@app.cell(hide_code=True)
def _(X_cb, Y_cb, edges_cb, n_cb, plot_tour):
    cb_fig = plot_tour(X_cb, Y_cb, edges_cb, f"Callback formulation: valid tour over {n_cb} cities") if edges_cb is not None else None
    cb_fig
    return


if __name__ == "__main__":
    app.run()
