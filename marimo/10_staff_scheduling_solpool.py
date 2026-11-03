# /// script
# [tool.marimo.opengraph]
# title = "Staff Scheduling"
# description = "Solution Pool and Enumeration"
# image = "__marimo__/thumbnail-staffscheduling.svg"
# ///

import marimo

__generated_with = "0.23.13"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import xpress as xp
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap
    from matplotlib.patches import Patch
    return ListedColormap, Patch, mo, plt, xp


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # **Staff shift scheduling with the solution pool and enumeration**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    This example shows how to use the Xpress solution pool and solution enumeration on a weekly staff scheduling problem: collecting several good schedules in a single solve, warm-starting a re-solve from the pool, enumerating the cheapest distinct schedules, and restricting the enumeration to the part of the schedule you care about.

    &copy; Copyright 2026 Fair Isaac Corporation. The use of this example is subject to [legal and license requirements](https://github.com/fico-xpress/python-notebooks#legal-and-license-requirements).
    """)
    return


@app.cell
def _():
    # Install the necessary packages
    # '%pip install -q xpress matplotlib' command supported automatically in marimo
    # This notebook requires Xpress 10 or later (solution enumeration controls)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Problem description

    A staffing manager rarely wants just *the* cheapest weekly roster. In practice there are many equally cheap (or nearly as cheap) rosters, and the manager picks between them using preferences the model does not capture: who likes to work together, who dislikes a shift, fairness across the team. The solution pool gives the decision maker a menu of good alternatives instead of a single answer.

    The personnel-planning demo "Julian's Problem" (Colombani & Heipcke, PACT98 1998 / ORInsight 1999) had the same need: persons to plan prefer variety of work assignments from one week to the next. Its objective was not a real cost function at all, but a sum of *randomly generated* coefficients, used purely to force a different feasible schedule on every run. The solution pool and enumeration controls below ask for the best distinct alternatives directly, instead of re-solving with random weights and hoping for variety.

    We schedule 8 employees over 7 days (Mon-Sun) with 2 shifts per day (Early, Late):

    * each employee works at most one shift per day, and at most 5 shifts per week;
    * a Late shift may not be followed by an Early shift the next day (rest);
    * each (day, shift) needs a minimum headcount, with weekdays needing more cover than weekends;
    * a few recorded personality **clashes** mean certain pairs of employees may never share a shift;
    * employees have different hourly wages, and weekend shifts pay a **premium**.

    The objective is to minimize the total wage cost.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Model formulation

    Let $E$ be the employees, $D$ the days and $S = \{\text{Early}, \text{Late}\}$ the shifts. The binary variable $x_{e,d,s}$ is 1 if and only if employee $e$ works shift $s$ on day $d$. The cost $c_{e,d}$ is the wage of $e$, multiplied by the weekend premium if $d$ is a Saturday or Sunday.

    $$\min \sum_{e,d,s} c_{e,d} \cdot x_{e,d,s}$$

    Subject to:

    * One shift per day: $\sum_s x_{e,d,s} \leq 1$ for all $e, d$
    * Coverage: $\sum_e x_{e,d,s} \geq REQ_{d,s}$ for all $d, s$
    * Rest: $x_{e,d,\text{Late}} + x_{e,d+1,\text{Early}} \leq 1$ for all $e$ and $d < |D|-1$
    * Weekly cap: $\sum_{d,s} x_{e,d,s} \leq MAXSHIFTS$ for all $e$
    * Clashes: $x_{e_1,d,s} + x_{e_2,d,s} \leq 1$ for all clashing pairs $(e_1, e_2)$ and all $d, s$
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Model parameters

    **You can adjust the parameters below to change the problem instance and re-solve the model automatically.** The default values reproduce the numbers quoted in the text.
    """)
    return


@app.cell
def _(mo):
    premium_slider = mo.ui.slider(1.0, 2.0, value=1.5, step=0.1, label="Weekend pay premium", show_value=True)
    poollimit_slider = mo.ui.slider(2, 15, value=10, step=1, label="Solutions to collect in a normal solve", show_value=True)
    mo.vstack([premium_slider, poollimit_slider])
    return poollimit_slider, premium_slider


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Data preparation

    Wages are deliberately not sorted by employee index, so that no subset of employees looks special for a reason other than cost. Employee 0 clashes with employees 1, 3 and 5.
    """)
    return


@app.cell
def _(premium_slider):
    N_EMP = 8
    N_DAYS = 7
    N_SHIFTS = 2                      # 0 = Early, 1 = Late
    WEEKEND_DAYS = (5, 6)             # Sat, Sun
    MAX_SHIFTS = 5                    # max shifts per employee per week
    WEEKEND_PREMIUM = premium_slider.value

    DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    SHIFT_NAMES = ["Early", "Late"]

    WAGES = [23, 20, 26, 22, 27, 21, 24, 25]

    # Minimum headcount per (day, shift): weekdays need more cover than weekends
    REQ = [[3, 2] if d < 5 else [2, 2] for d in range(N_DAYS)]

    # Recorded personality clashes: these employee pairs may never share a shift
    CLASHES = [(0, 1), (0, 3), (0, 5)]

    def cost(e, d):
        # Cost of one shift worked by employee e on day d, including the weekend premium
        return WAGES[e] * (WEEKEND_PREMIUM if d in WEEKEND_DAYS else 1.0)
    return (
        CLASHES,
        DAY_NAMES,
        MAX_SHIFTS,
        N_DAYS,
        N_EMP,
        N_SHIFTS,
        REQ,
        SHIFT_NAMES,
        WAGES,
        WEEKEND_DAYS,
        cost,
    )


@app.cell
def _(
    CLASHES,
    MAX_SHIFTS,
    N_DAYS,
    N_EMP,
    N_SHIFTS,
    REQ,
    cost,
    xp,
):
    def build_model():
        # Builds a fresh staff scheduling problem and returns it with its variables
        prob = xp.problem(name="StaffScheduling")
        prob.controls.outputlog = 0

        x = prob.addVariables(N_EMP, N_DAYS, N_SHIFTS, vartype=xp.binary, name="x")

        prob.setObjective(
            xp.Sum(cost(e, d) * x[e, d, s]
                   for e in range(N_EMP) for d in range(N_DAYS) for s in range(N_SHIFTS)),
            sense=xp.ObjSense.MINIMIZE,
        )

        # (1) At most one shift per day per employee
        prob.addConstraint(
            xp.Sum(x[e, d, s] for s in range(N_SHIFTS)) <= 1
            for e in range(N_EMP) for d in range(N_DAYS)
        )

        # (2) Coverage: minimum headcount per day/shift
        prob.addConstraint(
            xp.Sum(x[e, d, s] for e in range(N_EMP)) >= REQ[d][s]
            for d in range(N_DAYS) for s in range(N_SHIFTS)
        )

        # (3) Rest: no Late shift immediately followed by an Early shift
        prob.addConstraint(
            x[e, d, 1] + x[e, d + 1, 0] <= 1
            for e in range(N_EMP) for d in range(N_DAYS - 1)
        )

        # (4) Weekly cap on shifts per employee
        prob.addConstraint(
            xp.Sum(x[e, d, s] for d in range(N_DAYS) for s in range(N_SHIFTS)) <= MAX_SHIFTS
            for e in range(N_EMP)
        )

        # (5) Clashes: these employee pairs may never share a shift
        prob.addConstraint(
            x[e1, d, s] + x[e2, d, s] <= 1
            for (e1, e2) in CLASHES for d in range(N_DAYS) for s in range(N_SHIFTS)
        )

        return prob, x
    return (build_model,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Helper functions

    The helpers below read the solutions held in the pool and draw them as employee-by-day heatmaps (off, Early, Late). A pool solution is retrieved with [problem.getPoolSolution()](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/python/HTML/problem.getPoolSolution.html) and its objective value with `problem.getPoolSolObjVal()`; index 0 always holds the best solution.
    """)
    return


@app.cell
def _(
    DAY_NAMES,
    ListedColormap,
    N_DAYS,
    N_EMP,
    N_SHIFTS,
    Patch,
    SHIFT_NAMES,
    WAGES,
    WEEKEND_DAYS,
    plt,
):
    # Off, Early, Late. Orange/blue is the Okabe-Ito colorblind-safe pair
    SHIFT_COLORS = ["#f0f0f0", "#e69f00", "#0072b2"]
    SHIFT_CMAP = ListedColormap(SHIFT_COLORS)

    def pool_solutions(prob, x):
        # Returns a list of (objective value, shift matrix) for every solution in the pool.
        # The matrix is employees x days: 0 = off, 1 = Early, 2 = Late
        result = []
        for k in range(prob.attributes.poolsize):
            obj = prob.getPoolSolObjVal(k)
            sol = prob.getPoolSolution(k)
            matrix = [[2 if round(sol[x[e, d, 1].index]) else
                       1 if round(sol[x[e, d, 0].index]) else 0
                       for d in range(N_DAYS)]
                      for e in range(N_EMP)]
            result.append((obj, matrix))
        return result

    def weekend_roster(matrix):
        # For each weekend day and shift, the tuple of employees working it
        return {(DAY_NAMES[d], SHIFT_NAMES[s]): tuple(e for e in range(N_EMP) if matrix[e][d] == s + 1)
                for d in WEEKEND_DAYS for s in range(N_SHIFTS)}

    def solutions_table(sols):
        # Markdown table of cost, employees used and weekend shifts for each pooled solution
        lines = ["| Sol# | Cost | Employees used | Weekend shifts |", "|---:|---:|---:|---:|"]
        for k, (obj, matrix) in enumerate(sols):
            used = sum(1 for row in matrix if any(row))
            weekend = sum(1 for row in matrix for d in WEEKEND_DAYS if row[d])
            lines.append(f"| {k} | {obj:.1f} | {used} | {weekend} |")
        return "\n".join(lines)

    def plot_schedule(matrix, title):
        # A single employee x day heatmap, annotated with Early/Late
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.imshow(matrix, cmap=SHIFT_CMAP, vmin=0, vmax=2, aspect="auto")
        ax.set_xticks(range(N_DAYS))
        ax.set_xticklabels(DAY_NAMES)
        ax.set_yticks(range(N_EMP))
        ax.set_yticklabels([f"Emp {e} (${WAGES[e]}/hr)" for e in range(N_EMP)])
        for i, row in enumerate(matrix):
            for j, val in enumerate(row):
                if val:
                    ax.text(j, i, SHIFT_NAMES[val - 1], ha="center", va="center", fontsize=8)
        ax.set_xticks([v - 0.5 for v in range(1, N_DAYS)], minor=True)
        ax.set_yticks([v - 0.5 for v in range(1, N_EMP)], minor=True)
        ax.grid(which="minor", color="white", linewidth=1.5)
        ax.set_title(title)
        fig.tight_layout()
        return fig

    def plot_pool_grid(sols, suptitle):
        # One small heatmap per pooled solution covering the whole Mon-Sun week. A black line
        # marks the weekday/weekend boundary, since that is the dimension being compared
        n = len(sols)
        fig, axes = plt.subplots(1, n, figsize=(2.6 * n, 4), squeeze=False)
        for k, (_, matrix) in enumerate(sols):
            ax = axes[0][k]
            ax.imshow(matrix, cmap=SHIFT_CMAP, vmin=0, vmax=2, aspect="auto")
            ax.axvline(WEEKEND_DAYS[0] - 0.5, color="black", linewidth=1.5)
            ax.set_xticks(range(N_DAYS))
            ax.set_xticklabels(DAY_NAMES, fontsize=7)
            ax.set_yticks(range(N_EMP))
            ax.set_yticklabels([f"E{e}" for e in range(N_EMP)] if k == 0 else [])
            ax.set_title(f"Sol#{k}", fontsize=9)
        handles = [Patch(facecolor=SHIFT_COLORS[1], label="Early"),
                   Patch(facecolor=SHIFT_COLORS[2], label="Late"),
                   Patch(facecolor=SHIFT_COLORS[0], edgecolor="gray", label="Off")]
        fig.legend(handles=handles, loc="lower center", ncol=3, fontsize=8, bbox_to_anchor=(0.5, -0.02))
        fig.suptitle(f"{suptitle}\n(black line marks the weekday/weekend boundary)")
        fig.tight_layout(rect=(0, 0.08, 1, 1))
        return fig
    return plot_pool_grid, plot_schedule, pool_solutions, solutions_table, weekend_roster


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. Collecting solutions during a normal solve

    Setting the `poollimit` control makes the solver store the distinct integer solutions it happens to find on the way to proving optimality, at no extra search effort. They are kept from best to worst.
    """)
    return


@app.cell
def _(build_model, mo, poollimit_slider, plot_schedule, pool_solutions, solutions_table, xp):
    prob, x = build_model()

    # Collect up to poollimit solutions during the MIP search
    prob.controls.poollimit = poollimit_slider.value
    prob.optimize()
    assert prob.attributes.solstatus == xp.SolStatus.OPTIMAL

    collected = pool_solutions(prob, x)
    best_obj, best_matrix = collected[0]
    mo.show_code()
    return best_matrix, best_obj, collected, prob, x


@app.cell
def _(best_matrix, best_obj, collected, mo, plot_schedule, solutions_table):
    mo.vstack([
        mo.md(f"Collected **{len(collected)}** solution(s); the best one costs **{best_obj:.1f}**.\n\n{solutions_table(collected)}"),
        plot_schedule(best_matrix, f"Best weekly schedule (cost={best_obj:.1f})"),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Warm-starting a re-solve from the pool

    An employee requests a specific day off, which we model by fixing both of their shift variables on that day to 0. Any modification of the problem invalidates the collected solutions, so we first set `poolkeepsols = -1`: the existing pool is then transferred to the warm-start pool and used by the next solve. The problem must be in its original state, so we call `problem.postSolve()` first.

    Weekend shifts pay a premium, so losing a cheap employee on a weekend day forces a costlier substitute. Without the premium, almost any single day-off request is absorbed for free by shuffling who works which day.
    """)
    return


@app.cell
def _(DAY_NAMES, N_EMP, mo):
    emp_dropdown = mo.ui.dropdown(options={f"Employee {e}": e for e in range(N_EMP)}, value="Employee 1", label="Employee requesting a day off")
    day_dropdown = mo.ui.dropdown(options={name: d for d, name in enumerate(DAY_NAMES)}, value="Sun", label="Day off")
    mo.hstack([emp_dropdown, day_dropdown], justify="start")
    return day_dropdown, emp_dropdown


@app.cell
def _(DAY_NAMES, best_obj, day_dropdown, emp_dropdown, mo, prob, pool_solutions, solutions_table, x, xp):
    # Make sure the problem is in its original state before changing it
    prob.postSolve()

    # Transfer the existing pool to the warm-start pool before modifying the problem
    prob.controls.poolkeepsols = -1

    # Fix both shift variables of the chosen employee on the chosen day to 0
    _emp, _day = emp_dropdown.value, day_dropdown.value
    _dayoff = [x[_emp, _day, 0], x[_emp, _day, 1]]
    prob.chgBounds(_dayoff, ['B', 'B'], [0.0, 0.0])
    prob.optimize()
    assert prob.attributes.solstatus == xp.SolStatus.OPTIMAL

    warm = pool_solutions(prob, x)
    warm_obj = warm[0][0]

    # Reset the control first, then undo the fix (only the upper bound moved)
    prob.setDefaultControl('poolkeepsols')
    prob.chgBounds(_dayoff, ['U', 'U'], [1.0, 1.0])
    mo.show_code()

    mo.md(f"""
    With employee {_emp} off on {DAY_NAMES[_day]}, the best cost is **{warm_obj:.1f}**, compared with {best_obj:.1f} before: an extra **{warm_obj - best_obj:.1f}**.

    {solutions_table(warm)}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Full enumeration of the cheapest schedules

    Solution enumeration goes further than collecting what the search happens to find: with `poolenumstrategy = FULL` the solver keeps searching after the optimum to fill the pool with the best *distinct* solutions. By default two solutions are distinct if they differ in any binary variable, i.e. any shift of any employee on any day. The control `poolrelgap` restricts collection to solutions within a relative gap of the best cost, which speeds up the search.
    """)
    return


@app.cell
def _(mo):
    enum_slider = mo.ui.slider(2, 8, value=5, step=1, label="Schedules to enumerate", show_value=True)
    gap_slider = mo.ui.slider(0.0, 0.2, value=0.1, step=0.01, label="Relative gap to the best cost", show_value=True)
    mo.vstack([enum_slider, gap_slider])
    return enum_slider, gap_slider


@app.cell
def _(build_model, enum_slider, gap_slider, mo, plot_pool_grid, pool_solutions, solutions_table, weekend_roster, xp):
    prob_full, x_full = build_model()
    prob_full.controls.poollimit = enum_slider.value
    prob_full.controls.poolenumstrategy = xp.PoolEnumStrategy.FULL
    prob_full.controls.poolrelgap = gap_slider.value
    prob_full.optimize()
    assert prob_full.attributes.solstatus == xp.SolStatus.OPTIMAL

    full = pool_solutions(prob_full, x_full)
    full_weekends = {tuple(sorted(weekend_roster(m).items())) for _, m in full}
    mo.show_code()

    mo.vstack([
        mo.md(f"Found **{len(full)}** schedules, with **{len(full_weekends)}** distinct weekend roster(s).\n\n{solutions_table(full)}"),
        plot_pool_grid(full, "Full enumeration"),
    ])
    return full, full_weekends


@app.cell(hide_code=True)
def _(full, full_weekends, mo, weekend_roster):
    _teams = {tuple(sorted({e for w in weekend_roster(m).values() for e in w})) for _, m in full}
    mo.md(f"""
    Here the {len(full)} schedules have **{len(full_weekends)}** distinct weekend roster(s), drawn from only **{len(_teams)}** distinct weekend team(s) (the set of employees working at least one weekend shift). Because all of these schedules cost the same, full enumeration ranks them arbitrarily: it returns the N best schedules overall, and does not try to make them differ in the part you care about most. Compare the right-hand side of the black line across panels with what we get in section 4.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Restricted enumeration with branching directives

    Suppose we want the cheapest distinct **weekend rosters**, with the weekday assignment simply optimal for each. We pass the Saturday/Sunday shift variables to `problem.loadBranchDirs()`. Variables without a directive are not enumerated, so two solutions with the same weekend roster are treated as duplicates and only the cheaper one is kept.
    """)
    return


@app.cell
def _(WEEKEND_DAYS, N_EMP, N_SHIFTS, build_model, enum_slider, gap_slider, mo, plot_pool_grid, pool_solutions, solutions_table, weekend_roster, xp):
    prob_res, x_res = build_model()
    prob_res.controls.poollimit = enum_slider.value
    prob_res.controls.poolenumstrategy = xp.PoolEnumStrategy.FULL
    prob_res.controls.poolrelgap = gap_slider.value

    # Enumerate the weekend shift variables only
    weekend_vars = [x_res[e, d, s] for e in range(N_EMP) for d in WEEKEND_DAYS for s in range(N_SHIFTS)]
    prob_res.loadBranchDirs(weekend_vars, [1] * len(weekend_vars))
    prob_res.optimize()
    assert prob_res.attributes.solstatus == xp.SolStatus.OPTIMAL

    restricted = pool_solutions(prob_res, x_res)
    mo.show_code()

    _rosters = "\n".join(
        f"* Sol#{k}: " + "; ".join(f"{d} {s}: {list(w)}" for (d, s), w in weekend_roster(m).items())
        for k, (_, m) in enumerate(restricted)
    )
    mo.vstack([
        mo.md(f"Found **{len(restricted)}** schedules.\n\n{solutions_table(restricted)}\n\nWeekend rosters:\n\n{_rosters}"),
        plot_pool_grid(restricted, "Restricted enumeration (weekend variables only)"),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    This time the schedules differ visibly to the right of the line: the pool holds genuinely different weekend teams at the same cost, while the weekday side is near-identical. Compared with section 3, instead of N schedules that differ in a part you do not care about, you get N schedules that differ specifically in the part you do. Pick between them with the preferences the model does not capture.
    """)
    return


if __name__ == "__main__":
    app.run()
