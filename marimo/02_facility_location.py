# /// script
# [tool.marimo.opengraph]
# title = "Facility Location"
# description = "Mixed-Integer Location Model"
# image = "__marimo__/thumbnail-facility.svg"
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
    # **Facility location problem**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    A facility location problem to select the location of parks over a set of candidate sites that are meant to serve public schools at minimum (average or maximum) distance.

    &copy; Copyright 2025-2026 Fair Isaac Corporation. The use of this example is subject to [legal and license requirements](https://github.com/fico-xpress/python-notebooks#legal-and-license-requirements).
    """)
    return


@app.cell
def _():
    # Install the necessary packages
    # '%pip install -q xpress numpy matplotlib' command supported automatically in marimo
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
    There are $n$ public schools in a region. The administration wants to create parks (or gyms, swimming pools, etc.) that can be used by these schools and has $m$ currently unused sites that could be converted for this purpose. The coordinates of both the public schools and the candidate sites are therefore known. For budget reasons, the administration can only open $p$ parks.

    We formulate and solve the problem of choosing the $p$ parks among the candidate sites in such a way as to minimize one of the following two objective functions:

    * the average (i.e. the sum divided by the number of schools) of the distances between each school and the closest (open) park;
    * the maximum, calculated on the set of schools, of the distance between the school and the closest park.

    The **binary variables $serves_{i,j}$** indicate if school $i \in SCHOOLS$ is served (=1) by the candidate site $j \in SITES$ or not (=0). The **binary variables $build_j$** indicate if a certain candidate site $j$ is selected for creating a park (=1) or not (=0).

    $$\min \frac{\sum_{i \in SCHOOLS} \sum_{j \in SITES} dist_{i,j} \cdot serves_{i,j}}{|SCHOOLS|}$$

    Subject to:

    * Every school must be served by one park:
    $$\sum_{j \in SITES} serves_{i,j} = 1, \qquad \forall i \in SCHOOLS$$

    * Exactly $p$ parks are built:
    $$\sum_{j \in SITES} build_{j} = p$$

    * Only parks that are built can serve schools:
    $$\sum_{i \in SCHOOLS} serves_{i,j} \leq |SCHOOLS| \cdot build_{j}, \qquad \forall j \in SITES$$

    To instead minimize the **maximum distance** (as opposed to the average), an auxiliary variable $z$ is introduced, with objective $\min z$ and the additional constraint $z \geq \sum_{j \in SITES} dist_{i,j} \cdot serves_{i,j}, \ \forall i \in SCHOOLS$.
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
    num_schools_slider = mo.ui.slider(5, 15, value=9, label="Number of schools", show_value=True)
    num_sites_slider = mo.ui.slider(10, 20, value=11, label="Number of candidate sites", show_value=True)
    num_parks_slider = mo.ui.slider(1, 8, value=4, label="Number of parks to build", show_value=True)
    seed_slider = mo.ui.slider(0, 99, value=10, label="Random seed (each value gives a different instance)", show_value=True)
    objective_selector = mo.ui.radio(
        options={"Minimize average distance": "avg", "Minimize maximum distance": "max"},
        value="Minimize average distance",
        label="Objective"
    )
    mo.vstack([num_schools_slider, num_sites_slider, num_parks_slider, seed_slider, objective_selector])
    return num_parks_slider, num_schools_slider, num_sites_slider, objective_selector, seed_slider


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Data preparation and analysis
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We start by importing the necessary modules, to then create random coordinates for schools and candidate sites and calculate the distances between them. For a different instance, change the value of **Random seed** above.
    """)
    return


@app.cell
def _(mo, np, num_schools_slider, num_sites_slider, seed_slider):
    num_schools = num_schools_slider.value
    num_sites = num_sites_slider.value

    rng = np.random.default_rng(seed_slider.value)

    SCHOOLS = range(num_schools)  # Set of schools
    SITES = range(num_sites)      # Set of candidate sites

    coord_schools = 10 * rng.random((num_schools, 2))  # x-y coordinates between 0 and 10 (in km)
    coord_sites = 10 * rng.random((num_sites, 2))

    # Dictionary with the distances between schools and candidate sites
    dist = {(i, j): np.linalg.norm(coord_schools[i] - coord_sites[j]) for i in SCHOOLS for j in SITES}
    mo.show_code()
    return SCHOOLS, SITES, coord_schools, coord_sites, dist, np, num_schools, num_sites


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now we plot the points for schools (blue) and candidate sites (grey).
    """)
    return


@app.cell
def _(SCHOOLS, SITES, coord_schools, coord_sites, plt):
    # Plot the schools and candidate sites before solving, with no assignment yet.
    fig_start, ax_start = plt.subplots(figsize=(7, 7))

    ax_start.scatter(coord_schools[:, 0], coord_schools[:, 1], color="#5555ff", s=80, zorder=3, label="Schools")
    ax_start.scatter(coord_sites[:, 0], coord_sites[:, 1], color="#a0a0a0", s=80, zorder=3, label="Candidate sites")

    for _i in SCHOOLS:
        ax_start.annotate(str(_i), (coord_schools[_i, 0], coord_schools[_i, 1]), textcoords="offset points", xytext=(4, 4))
    for _j in SITES:
        ax_start.annotate(str(_j), (coord_sites[_j, 0], coord_sites[_j, 1]), textcoords="offset points", xytext=(4, 4))

    ax_start.set_aspect("equal", "box")
    ax_start.set_title("Schools (blue) and candidate sites for parks (grey)")
    ax_start.legend(loc="upper center", bbox_to_anchor=(0.5, -0.05), ncol=2)
    plt.tight_layout()
    fig_start
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The plot below shows the distance range and a histogram of the distances between schools and candidate sites.
    """)
    return


@app.cell
def _(dist, mo, plt):
    # Extract all distance values.
    distance_values = list(dist.values())

    # Plot histogram of distance distribution.
    fig_hist, ax_hist = plt.subplots(figsize=(10, 5))
    ax_hist.hist(distance_values, bins=10, color="skyblue", edgecolor="black")
    ax_hist.set_title("Distribution of distances between schools and candidate sites")
    ax_hist.set_xlabel("Distance (km)")
    ax_hist.set_ylabel("Frequency")
    ax_hist.grid(True)
    plt.tight_layout()

    # Display the range.
    mo.vstack([
        mo.md(f"Minimum distance: **{min(distance_values):.2f} km** &nbsp;&nbsp; Maximum distance: **{max(distance_values):.2f} km**"),
        fig_hist,
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Model implementation and solution
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    When passing sets, lists, or range objects to [problem.addVariables](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/python/HTML/problem.addVariables.html), the result is a Python dictionary of variables, whose keys are tuples of indices. Variables `serves` and `build` are created this way.

    The objective and constraints are then created and added to the problem directly. The `name` argument of [problem.addConstraint](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/python/HTML/problem.addConstraint.html) attaches a human-readable label to each constraint, which is useful when writing the LP file or diagnosing infeasibility.

    The **Objective** control above switches between minimizing the average distance and minimizing the maximum distance (via the auxiliary variable $z$ described in the problem description).
    """)
    return


@app.cell
def _(SCHOOLS, SITES, dist, mo, num_parks_slider, num_schools, objective_selector, xp):
    num_parks = num_parks_slider.value

    # Create a problem instance.
    prob = xp.problem()

    # Decision variables: serves[i,j] = 1 if school i is served by site j; build[j] = 1 if site j is built.
    serves = prob.addVariables(SCHOOLS, SITES, vartype=xp.binary, name="serves")
    build = prob.addVariables(SITES, vartype=xp.binary, name="build")

    # Every school must be served by one park - one constraint per school, named served_0..n-1.
    for i in SCHOOLS:
        prob.addConstraint(xp.Sum(serves[i, j] for j in SITES) == 1, name=f"served_{i}")

    # Exactly p parks are built.
    prob.addConstraint(xp.Sum(build[j] for j in SITES) == num_parks, name="num_parks")

    # Only parks that are built can serve schools - one constraint per site, named capacity_0..m-1.
    for j in SITES:
        prob.addConstraint(xp.Sum(serves[i, j] for i in SCHOOLS) <= num_schools * build[j], name=f"capacity_{j}")

    # Objective function: switches between minimizing average distance and minimizing maximum distance.
    if objective_selector.value == "avg":
        prob.setObjective(xp.Sum(dist[i, j] * serves[i, j] for i in SCHOOLS for j in SITES) / num_schools)
    else:
        # Auxiliary variable z and constraints to model the maximum distance.
        z = prob.addVariable(name="z")
        prob.addConstraint(z >= xp.Sum(dist[i, j] * serves[i, j] for j in SITES) for i in SCHOOLS)
        prob.setObjective(z)  # Replaces the old objective function.

    prob.controls.outputlog = 0  # Turn off output log for cleaner output.
    prob.optimize()

    # Get the solution.
    sol_serves = prob.getSolution(serves)
    sol_build = prob.getSolution(build)
    mo.show_code()
    return num_parks, prob, sol_build, sol_serves


@app.cell
def _(SCHOOLS, SITES, dist, mo, num_schools, sol_serves):
    avg_dist = sum(dist[_i, _j] * sol_serves[_i, _j] for _i in SCHOOLS for _j in SITES) / num_schools
    max_dist = max(dist[_i, _j] for _i in SCHOOLS for _j in SITES if sol_serves[_i, _j] > 0.5)

    mo.md(f"""
    **Average distance from a school to its assigned park:** {avg_dist:.2f} km

    **Maximum distance from a school to its assigned park:** {max_dist:.2f} km
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Solution Visualization
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The plot below draws the schools (blue), all candidate sites (grey), the built parks (red), and the school-to-park assignment lines.
    """)
    return


@app.cell
def _(SCHOOLS, SITES, coord_schools, coord_sites, plt, sol_build, sol_serves):
    fig_map, ax_map = plt.subplots(figsize=(7, 7))

    for _i in SCHOOLS:
        for _j in SITES:
            if sol_serves[_i, _j] > 0.5:
                ax_map.plot(
                    [coord_schools[_i, 0], coord_sites[_j, 0]],
                    [coord_schools[_i, 1], coord_sites[_j, 1]],
                    color="#cccccc", linewidth=1, zorder=1
                )

    built_sites = [_j for _j in SITES if sol_build[_j] > 0.5]
    unbuilt_sites = [_j for _j in SITES if sol_build[_j] <= 0.5]

    ax_map.scatter(coord_schools[:, 0], coord_schools[:, 1], color="#5555ff", s=80, zorder=3, label="Schools")
    ax_map.scatter(coord_sites[unbuilt_sites, 0], coord_sites[unbuilt_sites, 1], color="#a0a0a0", s=80, zorder=3, label="Candidate sites")
    ax_map.scatter(coord_sites[built_sites, 0], coord_sites[built_sites, 1], color="#ff5555", s=120, zorder=3, label="Built parks")

    for _i in SCHOOLS:
        ax_map.annotate(str(_i), (coord_schools[_i, 0], coord_schools[_i, 1]), textcoords="offset points", xytext=(4, 4))
    for _j in SITES:
        ax_map.annotate(str(_j), (coord_sites[_j, 0], coord_sites[_j, 1]), textcoords="offset points", xytext=(4, 4))

    ax_map.set_aspect("equal", "box")
    ax_map.set_title("Schools, candidate sites, and selected parks")
    ax_map.legend(loc="upper center", bbox_to_anchor=(0.5, -0.05), ncol=3)
    plt.tight_layout()
    fig_map
    return


if __name__ == "__main__":
    app.run()
