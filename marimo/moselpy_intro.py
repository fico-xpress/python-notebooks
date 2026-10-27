# /// script
# [tool.marimo.opengraph]
# title = "MoselPy: Introduction"
# description = "LP, MIP, knapsack and price breaks"
# image = "__marimo__/thumbnail-moselpy-intro.svg"
# ///

import marimo

__generated_with = "0.25.2"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # **FICO&reg; Xpress MoselPy: Introduction**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ***moselpy_intro.py*** - Getting started with MoselPy using introductory Xpress application book examples.

    &copy; Copyright 2026 Fair Isaac Corporation. The use of this example is subject to [legal and license requirements](https://github.com/fico-xpress/xpress-community#legal-and-license-requirements).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Getting started with MoselPy
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    [MoselPy](https://pypi.org/project/moselpy/) lets you compile and run FICO&reg; Xpress Mosel models from Python, and exchange data bidirectionally. It enables you to combine Mosel's algebraic modeling language with Python's data and visualization ecosystem.

    > **Requirements:** `pip install moselpy mosellibs xpresslibs` - `mosellibs` provides the Mosel runtime and `xpresslibs` the Xpress solver libraries. No local Xpress installation is needed to run these notebooks, as long as the packages with libraries have been installed.

    > A local FICO&reg; Xpress installation is recommended if you want access to the full set of examples, user guides and documentation, solver libraries, and Xpress Workbench. Obtain one via the [FICO&reg; Xpress community license](https://www.fico.com/en/fico-xpress-community-license) page. If a local installation is present, set `XPRESSDIR` before starting marimo to use it instead of the `mosellibs` and `xpresslibs` packages.

    > **MoselPy documentation:** [MoselPy User Guide and Reference Manual](https://www.fico.com/fico-xpress-optimization/docs/latest/mosel/MoselPy/dhtml)

    > **Mosel examples on the web:** [examples.xpress.fico.com](https://examples.xpress.fico.com/example.pl?id=mosel_app_intro)

    ### When to use MoselPy

    | Scenario | Use |
    |----------|-----|
    | You have existing Mosel models and want to execute them from Python | **MoselPy** |
    | You prefer Mosel's algebraic syntax for building models | **MoselPy** |
    | You want to distribute compiled `.bim` files for IP protection | **MoselPy** |
    | You are building a new model directly in Python | [Xpress Python API](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/python/HTML/GUID-616C323F-05D8-3460-B0D7-80F77DA7D046.html) |

    ### Running Mosel models from Python

    MoselPy offers two workflows for running a Mosel model:

    **One-step:** compile and run in a single call; returns `(model, output_dict)`:

    ```python
    model, output = mp.execute_model("model.mos", exec_params={"OUTFILE": "moselpy:"})
    ```

    **Three-step:** compile once, load the binary, then run as many times as needed:

    ```python
    # 1. Compile: Mosel source (.mos) -> binary model (.bim)
    mp.compile_model("model.mos", "model.bim")

    # 2. Load the compiled model
    model = mp.load_model("model.bim")

    # 3. Run with optional parameters; results come back as a dict
    output = model.run(exec_params={"OUTFILE": "moselpy:"})
    ```

    In both cases, results exported via `initializations to "moselpy:"` are returned in `output`. The three-step workflow is preferred when the same model needs to run multiple times with different data (load once, run many times), and produces a distributable `.bim` binary. Note that `execute_model` does not write a `.bim` file to disk.

    ### Adapting a Mosel model for MoselPy

    The models in this notebook are adapted versions of the original [Xpress application book examples](https://examples.xpress.fico.com/example.pl?id=mosel_app_intro). The four standard adaptations are:

    1. **Add `DATASOURCE` for data file models:** Replace hardcoded filenames in `initializations from` with a `DATASOURCE` parameter. Override it with `exec_params={"DATASOURCE": "moselpy:"}` to inject data from Python via `input_data={...}`.

    2. **Replace `writeln` output with `initializations to OUTFILE`:** Original models use `writeln()` to print results. Adapted models add `OUTFILE = "\"` to a `parameters` block and write results with `initializations to OUTFILE`. Empty string writes to stdout when run standalone; `"moselpy:"` returns data to Python as a dict via `exec_params={"OUTFILE": "moselpy:"}`.

    3. **Use `evaluation of` for scalar results:** Scalar expressions such as `getobjval` or `getsol(xs)` can be exported without an intermediate variable: `evaluation of getobjval as 'obj_val'`.

    4. **Array results require a helper variable:** For arrays of decision variables, declare a `real` array (e.g., `sol_x: array(ITEMS) of real`), populate it after the solve with `forall(i in ITEMS) sol_x(i) := getsol(x(i))`, then include `sol_x` in the `initializations to` block.

    ### Models and data files

    The Mosel source files (`.mos`) and compiled binary model files (`.bim`) for this notebook live in [`models/intro/`](https://github.com/fico-xpress/python-notebooks/tree/main/marimo/public/moselpy/models/intro). Data files used by some models are in [`data/intro/`](https://github.com/fico-xpress/python-notebooks/tree/main/marimo/public/moselpy/data/intro). The `.bim` files are generated by the first `compile_model()` call; they are platform-independent and can be distributed without the source.

    ### About this notebook

    This notebook groups models that explain the basics of LP and MIP model development with Mosel, including data input/output patterns. The examples progress from a simple LP (chess sets) through integer programming and knapsack variants, to special ordered sets (SOS1/SOS2) and piecewise linear functions.

    ### Suppressing solver output

    The setup cell below calls `mp.config.set_default_stream(mp.StreamType.OUTPUT, "null:")` before any model is loaded, silencing solver output globally for this notebook. This must be done before the first `load_model()` call; per-model `model.set_default_stream()` is available as an alternative for finer control. To retrieve solver logging output, enable it by setting the `XPRS_VERBOSE` control. The error stream (`mp.StreamType.ERROR`) should not be silenced - redirect it to Python if you need to capture runtime errors.

    ### MoselPy features demonstrated in this notebook

    - **Single execution command vs compile-load-run sequence**: the Chess sets LP demonstrates both workflows side by side - `mp.execute_model()` for a one-shot run and the three-step sequence for reuse.
    - **`exec_params` for output routing**: all models return results via `OUTFILE="moselpy:"` in `exec_params`; knapsack models also set `DATASOURCE="moselpy:"` to inject input data.
    - **`input_data` with 1-indexed dicts**: the Knapsack with external data file passes item values and weights as Python dicts directly to `input_data`, replacing the `.dat` file for the notebook run.
    - **`pd.DataFrame` as `input_data`**: the Knapsack with DataFrame input passes item data as a `pd.DataFrame`; MoselPy maps the index to the Mosel array index automatically.
    - **`model.find_identifier(use_pandas=True)`**: the Function approximation (SOS2/piecewise linear) example retrieves the solution array as a pandas Series after the solve.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Setup

    The cell below imports MoselPy, matplotlib, NumPy, and pandas, and to set `MODELS` and `DATA`, the path variables pointing to the Mosel source files and data files used throughout this notebook. Other notebooks in this series place an equivalent setup cell right after the package installation cell; here it appears alongside the workflow description above.
    """)
    return


@app.cell
def _(mo):
    # On Linux, preload the Xpress solver library so the Mosel optimizer module
    # (mmxprs) can resolve it at runtime.
    import sys, os, glob, ctypes, xpresslibs
    if sys.platform == "linux":
        for _lib in glob.glob(os.path.join(xpresslibs.solver_libs_dir, "libxprs.so*")):
            ctypes.CDLL(_lib, mode=ctypes.RTLD_GLOBAL)

    import moselpy as mp
    from moselpy import ExecStatus
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import numpy as np
    import pandas as pd

    _root = mo.notebook_dir() / "public" / "moselpy"
    MODELS = str(_root / "models" / "intro")
    DATA   = str(_root / "data" / "intro")

    print(f"MoselPy {mp.version}  |  Mosel {mp.mosel_version}  |  Xpress {mp.xpress_version}")
    mp.config.set_default_stream(mp.StreamType.OUTPUT, "null:")
    return ExecStatus, MODELS, mp, mpatches, np, pd, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Chess sets (LP)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    *Introductory example: Chapter 1 - Linear Programming*

    > **Mosel model:** [`chess2_p.mos`](https://github.com/fico-xpress/python-notebooks/blob/main/marimo/public/moselpy/models/intro/chess2_p.mos)

    A company makes two chess set sizes. Each **small set** requires 3 lathe-hours and 1 kg boxwood; each **large set** requires 2 lathe-hours and 3 kg boxwood. Available per week: 160 lathe-hours and 200 kg boxwood. Profit: \$5 per small set, \$20 per large set.

    **Decision variables:** $x_s, x_l \geq 0$ (sets produced per week).

    $$
    \begin{align*}
    \text{maximize}   \quad & 5\,x_s + 20\,x_l \\
    \text{subject to} \quad & x_s + 3\,x_l \leq 200 \quad \text{(boxwood, kg)} \\
                              & 3\,x_s + 2\,x_l \leq 160 \quad \text{(lathe-hours)} \\
                              & x_s,\, x_l \geq 0
    \end{align*}
    $$

    Beyond the optimal solution, post-solution LP queries reveal constraint and variable information:

    - **Constraint activity** (`getact`): how much of each resource is actually used at the optimal solution
    - **Dual value / shadow price** (`getdual`): how much the objective would improve if the right-hand side of a binding constraint were relaxed by one unit, e.g. a lathe shadow price of 6.67 means one extra lathe-hour is worth \$6.67 of profit
    - **Reduced cost** (`getrcost`): how much the objective function coefficient of a non-basic variable must change before that variable enters the basis; zero for basic variables

    **Adaptation from original:** `chess2.mos` uses `writeln()` for all output. In `chess2_p.mos`, every `writeln` call is replaced by an `evaluation of` expression inside `initializations to OUTFILE`, one line per result. This is the simplest adaptation: no helper variables needed when all outputs are scalars.

    The cell below uses `mp.execute_model()`, which compiles and runs in a single call and returns a `(model, output)` tuple: `model` is the `Model` object (useful for inspecting `model.prob_status`, accessing identifiers, etc.) and `output` is a dict containing everything exported via `initializations to "moselpy:"`. This is the one-step alternative to the compile/load/run three-step workflow - convenient for a single run when no `.bim` file needs to be written to disk.
    """)
    return


@app.cell
def _(MODELS, mp):
    model, output = mp.execute_model(f"{MODELS}/chess2_p.mos", exec_params={"OUTFILE": "moselpy:"})

    if model.prob_status.is_solution_available:
        print(f"Optimal profit: ${output['obj_val']:.2f}")
        print(f"Small sets: {output['sol_xs']:.0f}   Large sets: {output['sol_xl']:.0f}")
        print()
        print(f"{'Constraint':<12} {'Activity':>10} {'Shadow price':>14}")
        print(f"{'Lathe':<12} {output['act_lathe']:>10.2f} {output['dual_lathe']:>14.4f}")
        print(f"{'Boxwood':<12} {output['act_boxwood']:>10.2f} {output['dual_boxwood']:>14.4f}")
        print()
        print(f"{'Variable':<12} {'Reduced cost':>14}")
        print(f"{'xs':<12} {output['rc_xs']:>14.4f}")
        print(f"{'xl':<12} {output['rc_xl']:>14.4f}")
        print()
        print(f"Model name : {model.name}")
        print(f"Exec status: {model.exec_status}")
        print(f"Optimal    : {model.prob_status.is_solution_optimal}")
    else:
        print(f"No solution found ({model.prob_status})")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The knapsack problem (Burglar)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    *Introductory examples: Chapters 2-3 - Integer Programming*

    > **Mosel model:** [`burglari_p.mos`](https://github.com/fico-xpress/python-notebooks/blob/main/marimo/public/moselpy/models/intro/burglari_p.mos)

    A burglar can carry at most $\text{WTMAX} = 102$ kg. Eight items have values $\text{VALUE}_i$ and weights $\text{WEIGHT}_i$. Which items to take?

    | Item | camera | necklace | vase | picture | tv | video | chest | brick |
    |------|--------|----------|------|---------|----|----|------|-------|
    | VALUE | 15 | 100 | 90 | 60 | 40 | 15 | 10 | 1 |
    | WEIGHT | 2 | 20 | 20 | 30 | 40 | 30 | 60 | 10 |

    **Decision variables:** $\mathit{take}_i \in \{0,1\}$ (1 if item $i$ is taken, 0 otherwise).

    $$
    \begin{align*}
    \text{maximize}   \quad & \sum_i \text{VALUE}_i\,\mathit{take}_i \\
    \text{subject to} \quad & \sum_i \text{WEIGHT}_i\,\mathit{take}_i \leq \text{WTMAX} \\
                              & \mathit{take}_i \in \{0,1\} \quad \forall\, i
    \end{align*}
    $$

    `burglari_p.mos` uses named string indices - a common pattern in real-world Mosel models.

    **Workflow:** This section uses the three-step workflow (`compile_model` -> `load_model` -> `run`) to demonstrate the pattern explicitly. The compiled `.bim` file is reused by subsequent cells (the pandas data exchange and sensitivity analysis below), so loading once and running multiple times is the natural fit here.
    """)
    return


@app.cell
def _(MODELS, mp):
    mp.compile_model(f'{MODELS}/burglari_p.mos', f'{MODELS}/burglari_p.bim')
    model_1 = mp.load_model(f'{MODELS}/burglari_p.bim')
    model_1.set_default_stream(mp.StreamType.OUTPUT, 'null:')
    output_1 = model_1.run(exec_params={'OUTFILE': 'moselpy:'})
    print(f'Total value: ${output_1['obj_val']:.0f}')
    taken = {item: v for item, v in output_1['sol_take'].items() if v > 0.5}
    print(f'Items taken: {sorted(taken.keys())}')
    return model_1, output_1, taken


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Checking solution status

    After any `model.run()` call, check two properties before using results:

    - **`model.exec_status`** (`ExecStatus.OK` / `ExecStatus.ERROR`): whether Mosel itself ran successfully (compiled, loaded, no runtime error). Check this first.
    - **`model.prob_status`**: the optimizer's verdict on the mathematical problem. Key boolean flags: `is_solution_optimal`, `is_solution_feasible`, `is_problem_infeasible`, `is_problem_unbounded`.
    - **`model.objective_value`**: the objective function value at the best solution found.
    """)
    return


@app.cell
def _(ExecStatus, model_1):
    # Check the solution status (good practice after any solve)
    if model_1.exec_status == ExecStatus.OK:
        ps = model_1.prob_status
        if ps.is_solution_optimal:
            status = 'optimal'
        elif ps.is_solution_feasible:
            status = 'feasible (possibly not optimal)'
        elif ps.is_problem_infeasible:
            status = 'infeasible'
        elif ps.is_problem_unbounded:
            status = 'unbounded'
        else:
            status = 'unknown'
        print(f'exec_status  : {model_1.exec_status}')
        print(f'prob_status  : {status}')
        print(f'objective    : {model_1.objective_value:.0f}')
    else:
        print(f'Execution error: {model_1.exec_status}')
    return


@app.cell
def _(mo, mpatches, output_1, plt, taken):
    _items = ['camera', 'necklace', 'vase', 'picture', 'tv', 'video', 'chest', 'brick']
    values = [15, 100, 90, 60, 40, 15, 10, 1]
    _weights = [2, 20, 20, 30, 40, 30, 60, 10]
    selected = set(taken.keys())
    colors_v = ['#2196F3' if it in selected else '#BBDEFB' for it in _items]
    colors_w = ['#FF5722' if it in selected else '#FFCCBC' for it in _items]
    _fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    y = range(len(_items))
    ax1.barh(list(y), values, color=colors_v)
    ax1.set_yticks(list(y))
    ax1.set_yticklabels(_items)
    ax1.set_xlabel('Value ($)')
    ax1.set_title('Item values')
    ax1.invert_yaxis()
    ax2.barh(list(y), _weights, color=colors_w)
    ax2.set_yticks(list(y))
    ax2.set_yticklabels(_items)
    ax2.set_xlabel('Weight (kg)')
    ax2.set_title(f'Item weights  (capacity: 102 kg)')
    ax2.invert_yaxis()
    legend = [mpatches.Patch(color='#2196F3', label='Selected'), mpatches.Patch(color='#BBDEFB', label='Not taken')]
    ax1.legend(handles=legend, loc='lower right')
    legend2 = [mpatches.Patch(color='#FF5722', label='Selected'), mpatches.Patch(color='#FFCCBC', label='Not taken')]
    ax2.legend(handles=legend2, loc='lower right')
    plt.suptitle(f'Knapsack solution -total value ${output_1['obj_val']:.0f}', fontweight='bold')
    plt.tight_layout()
    mo.output.append(plt.gcf())
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Two ways to read results from Python
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    `burglari_p.mos` has both `public` declarations and an `initializations to OUTFILE` block, making it a good place to compare the two standard approaches to reading results in MoselPy:

    **Approach 1 - `initializations to OUTFILE`** (shown above; used in all subsequent examples)
    The model exports results via `initializations to OUTFILE`; Python receives them as the dict returned by `model.run(exec_params={"OUTFILE": "moselpy:"})`. The model also runs correctly standalone, writing results to a file by default.

    **Approach 2 - `public` + `find_identifier()`**
    Declarations marked `public` in the model remain accessible from Python after the model runs. Retrieve them with `model.find_identifier(name)`, optionally as a pandas `Series` by passing `use_pandas=True`.

    All subsequent examples use **Approach 1 only**. It is preferred because the model produces output when run standalone, without any Python wrapper.
    """)
    return


@app.cell
def _(model_1):
    # Approach 2: find_identifier() accesses 'public' declarations directly from Python.
    # use_pandas=True returns a pandas Series, convenient for further analysis.
    sol_take_pd = model_1.find_identifier('sol_take', use_pandas=True)
    print('Item selection (pandas Series):')
    print(sol_take_pd.sort_values(ascending=False).rename('selected').to_frame().to_string())
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Knapsack with an external data file
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    > **Mosel model:** [`burglar2_p.mos`](https://github.com/fico-xpress/python-notebooks/blob/main/marimo/public/moselpy/models/intro/burglar2_p.mos)

    `burglar2_p.mos` reads item data using `initializations from DATASOURCE`. Here the item data is defined directly in Python and injected at runtime via `input_data`. The `.dat` file (`burglar_p.dat`) is kept alongside the model for standalone execution.

    `exec_params` overrides Mosel `parameters` block values before the model starts; use it for scalars such as file paths or mode flags. `input_data` is passed via `initializations from "moselpy:"` at runtime and can transfer scalars, arrays, sets, and pandas objects. Setting `DATASOURCE="moselpy:"` in `exec_params` redirects the `initializations from` block to read from Python instead of a file.
    """)
    return


@app.cell
def _():
    VALUE  = {"camera": 15, "necklace": 100, "vase": 90, "picture": 60,
              "tv": 40, "video": 15, "chest": 10, "brick": 1}
    WEIGHT = {"camera": 2, "necklace": 20, "vase": 20, "picture": 30,
              "tv": 40, "video": 30, "chest": 60, "brick": 10}
    return VALUE, WEIGHT


@app.cell
def _(MODELS, VALUE, WEIGHT, mp):
    mp.compile_model(f'{MODELS}/burglar2_p.mos', f'{MODELS}/burglar2_p.bim')
    model_2 = mp.load_model(f'{MODELS}/burglar2_p.bim')
    model_2.set_default_stream(mp.StreamType.OUTPUT, 'null:')
    output_2 = model_2.run(exec_params={'DATASOURCE': 'moselpy:', 'OUTFILE': 'moselpy:'}, input_data={'VALUE': VALUE, 'WEIGHT': WEIGHT})
    if model_2.prob_status.is_solution_available:
        print(f'Total value: ${output_2['obj_val']:.0f}')
        taken_1 = {item: v for item, v in output_2['sol_take'].items() if v > 0.5}
        print(f'Items taken: {sorted(taken_1.keys())}')
    else:
        print(f'No solution found ({model_2.prob_status})')
    return (model_2,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Injecting data from Python with `exec_params`
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Setting `exec_params={"DATASOURCE": "moselpy:"}` (used for scalars such as file paths) redirects the `initializations from` block to read data from Python instead of a file. Combined with `input_data`, this lets you pass any Python dict or pandas object directly to the model.

    A key advantage: the model is loaded once and can be run as many times as needed with different data; no recompile or reload between runs.
    """)
    return


@app.cell
def _(model_2):
    _items = {'camera': 15, 'necklace': 100, 'vase': 90, 'picture': 60, 'tv': 40, 'video': 15, 'chest': 10, 'brick': 1}
    _weights = {'camera': 2, 'necklace': 20, 'vase': 20, 'picture': 30, 'tv': 40, 'video': 30, 'chest': 60, 'brick': 10}
    print(f'{'vase (kg)':>9}   {'value':>6}   items taken')
    for vase_weight in [20, 40, 60, 80]:
        _out = model_2.run(exec_params={'DATASOURCE': 'moselpy:', 'OUTFILE': 'moselpy:'}, input_data={'VALUE': _items, 'WEIGHT': dict(_weights, vase=vase_weight)})
        taken_2 = sorted((k for k, v in _out['sol_take'].items() if v > 0.5))
        print(f'{vase_weight:>6} kg   {_out['obj_val']:>6.0f}   {taken_2}')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Knapsack with DataFrame input
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    > **Mosel model:** [`burglar_df_p.mos`](https://github.com/fico-xpress/python-notebooks/blob/main/marimo/public/moselpy/models/intro/burglar_df_p.mos)

    `burglar_df_p.mos` stores item data in a 2D Mosel array `I(FIELDS, ITEMS)` where `FIELDS = {'value', 'weight'}` and `ITEMS` is the set of item names. This layout maps directly to a `pd.DataFrame` -- rows are fields, columns are items. Passing the DataFrame via `input_data` is the most natural way to inject tabular item data from Python into Mosel.

    Both `FIELDS` and `ITEMS` are `set of string` in the model and auto-populate from the DataFrame row and column labels when the data is passed.
    """)
    return


@app.cell
def _(pd):
    item_df = pd.DataFrame(
        {"camera":    [15,  2],
         "necklace":  [100, 20],
         "vase":      [90,  20],
         "picture":   [60,  30],
         "tv":        [40,  40],
         "video":     [15,  30],
         "chest":     [10,  60],
         "brick":     [1,   10]},
        index=["value", "weight"],
    )
    print(item_df.to_string())
    return (item_df,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Pass the `pd.DataFrame` via `input_data`. MoselPy maps rows to `FIELDS` and columns to `ITEMS` automatically.
    """)
    return


@app.cell
def _(MODELS, item_df, mp):
    mp.compile_model(f'{MODELS}/burglar_df_p.mos', f'{MODELS}/burglar_df_p.bim')
    model_3 = mp.load_model(f'{MODELS}/burglar_df_p.bim')
    model_3.set_default_stream(mp.StreamType.OUTPUT, 'null:')
    output_3 = model_3.run(exec_params={'DATASOURCE': 'moselpy:', 'OUTFILE': 'moselpy:'}, input_data={'I': item_df})
    if model_3.prob_status.is_solution_available:
        print(f'Total value: ${output_3['obj_val']:.0f}')
        taken_3 = {item: v for item, v in output_3['sol_take'].items() if v > 0.5}
        print(f'Items taken: {sorted(taken_3.keys())}')
    else:
        print(f'No solution found ({model_3.prob_status})')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Price breaks: all-item discount
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    *Introductory example: Chapter 4 - Special Ordered Sets*

    > **Mosel models:** [`pricebrai_p.mos`](https://github.com/fico-xpress/python-notebooks/blob/main/marimo/public/moselpy/models/intro/pricebrai_p.mos), [`pricebrai2_p.mos`](https://github.com/fico-xpress/python-notebooks/blob/main/marimo/public/moselpy/models/intro/pricebrai2_p.mos)

    We fix the purchased quantity to `DEM`=150 units to make the code runnable. Unit price depends on the total quantity purchased:

    | Band | Quantity range | Unit cost |
    |------|---------------|-----------|
    | 1 | 0-50 | 1.00 |
    | 2 | 50-120 | 0.70 |
    | 3 | 120-200 | 0.50 |

    All units are charged at whichever band rate applies to the total quantity bought.

    **Decision variables:** $x_i \geq 0$ (quantity bought at price $\text{COST}_i$), $b_i \in \{0,1\}$ (active price band).

    $$
    \begin{align*}
    \text{minimize}   \quad & \sum_{i=1}^{3} \text{COST}_i\,x_i \\
    \text{subject to} \quad & \sum_{i=1}^{3} x_i = \text{DEM} \\
                              & B_{i-1}\,b_i \leq x_i \leq B_i\,b_i \quad \forall\,i \\
                              & \sum_{i=1}^{3} b_i = 1, \quad b_i \in \{0,1\}
    \end{align*}
    $$

    Data (`DEM`, `B`, `COST`) is read via a `DATASOURCE` parameter, which lets us pass Python values directly to Mosel using `input_data`. Mosel arrays are 1-indexed by default, but `B` is declared as `array(0..NB)` so its keys run from 0 to 3 - the dict passed for `B` must match that range.
    """)
    return


@app.cell
def _(MODELS, mp):
    B = [0, 50, 120, 200]
    COST = [1.0, 0.7, 0.5]
    DEM = 150
    mp.compile_model(f'{MODELS}/pricebrai_p.mos', f'{MODELS}/pricebrai_p.bim')
    model_4 = mp.load_model(f'{MODELS}/pricebrai_p.bim')
    model_4.set_default_stream(mp.StreamType.OUTPUT, 'null:')
    output_4 = model_4.run(exec_params={'DATASOURCE': 'moselpy:', 'OUTFILE': 'moselpy:'}, input_data={'DEM': DEM, 'B': {i: B[i] for i in range(len(B))}, 'COST': {i + 1: COST[i] for i in range(len(COST))}})
    if model_4.prob_status.is_solution_available:
        print(f'Total cost: {output_4['obj_val']:.2f}  (avg per unit: {output_4['obj_val'] / DEM:.4f})')
        print(f'{'Band':<6} {'Quantity':>10} {'Unit cost':>10}')
        for _i in range(1, 4):
            print(f'{_i:<6} {output_4['sol_x'][_i]:>10.2f} {COST[_i - 1]:>10.2f}')
    else:
        print(f'No solution found ({model_4.prob_status})')
    return B, COST, DEM


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### All-item discount via `pwlin` (pricebrai2_p.mos)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    `pricebrai2_p.mos` reformulates the same problem using a `pwlin` piecewise-linear expression (requires `mmxnlp`). The model reduces to a single continuous variable $x$ with a piecewise cost function.

    As with `chess2_p.mos`, we use `execute_model` for a one-step run.
    """)
    return


@app.cell
def _(DEM, MODELS, mp):
    model_5, output_5 = mp.execute_model(f'{MODELS}/pricebrai2_p.mos', exec_params={'OUTFILE': 'moselpy:'})
    if model_5.prob_status.is_solution_available:
        print(f'Total cost: {output_5['obj_val']:.2f}  (avg per unit: {output_5['obj_val'] / DEM:.4f})')
        print(f'Quantity bought: {output_5['sol_x']:.0f}')
    else:
        print(f'No solution found ({model_5.prob_status})')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Price breaks: incremental discount
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    *Introductory example: Chapter 4 - Special Ordered Sets*

    > **Mosel models:** [`pricebrinc_p.mos`](https://github.com/fico-xpress/python-notebooks/blob/main/marimo/public/moselpy/models/intro/pricebrinc_p.mos), [`pricebrinc2_p.mos`](https://github.com/fico-xpress/python-notebooks/blob/main/marimo/public/moselpy/models/intro/pricebrinc2_p.mos), [`pricebrinc3_p.mos`](https://github.com/fico-xpress/python-notebooks/blob/main/marimo/public/moselpy/models/intro/pricebrinc3_p.mos)

    Same quantity bands as above, but pricing is now **incremental**: the first 50 units cost 0.80 each, the next 70 (up to 120) cost 0.50 each, and anything beyond 120 costs 0.30 each.

    `pricebrinc_p.mos` models this with an SOS2 (Special Ordered Set of Type 2). At each of the four breakpoints $B_0, B_1, B_2, B_3$, a weight variable $w_i \geq 0$ is introduced; $\text{CBP}_i$ is the total cost of buying exactly $B_i$ units. The SOS2 constraint allows **at most two adjacent** $w_i$ to be non-zero -this forces the solution onto one linear segment of the piecewise cost function.

    **Decision variables:** $x \geq 0$ (total quantity), $w_i \geq 0$, $i = 0..3$ (SOS2 interpolation weights).

    $$
    \begin{align*}
    \text{minimize}   \quad & \sum_{i=0}^{3} \text{CBP}_i\, w_i \\
    \text{subject to} \quad & x = \text{DEM} \\
                              & x = \sum_{i=0}^{3} B_i\, w_i \\
                              & \sum_{i=0}^{3} w_i = 1, \quad w \in \text{SOS2}
    \end{align*}
    $$

    A key subtlety: `makesos2` is used instead of `is_sos2` because the reference row contains a zero-valued coefficient ($B_0 = 0$), which `is_sos2` cannot handle correctly.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Injecting data from Python

    `pricebrinc_p.mos` accepts its data via a `DATASOURCE` parameter (defaulting to a `.dat` file when run standalone). Passing `exec_params={"DATASOURCE": "moselpy:"}` redirects the `initializations from DATASOURCE` block to read from Python instead. The `input_data` dict then maps Python values directly to Mosel identifiers by name.

    This is the standard MoselPy pattern for pushing data into a model at runtime - no `.dat` file needed. The three-step workflow is used here because the loaded `model` is reused in the parametric run in the next cell.
    """)
    return


@app.cell
def _(B, DEM, MODELS, mp):
    # Three-step workflow: model is loaded once here and reused in the parametric loop below
    COST_INC = [0.8, 0.5, 0.3]  # unit cost per band (reused in viz below)
    mp.compile_model(f'{MODELS}/pricebrinc_p.mos', f'{MODELS}/pricebrinc_p.bim')
    model_6 = mp.load_model(f'{MODELS}/pricebrinc_p.bim')
    output_6 = model_6.run(exec_params={'DATASOURCE': 'moselpy:', 'OUTFILE': 'moselpy:'}, input_data={'DEM': DEM, 'B': {i: b for i, b in enumerate(B)}, 'COST': {i + 1: c for i, c in enumerate(COST_INC)}})
    if model_6.prob_status.is_solution_available:
    # exec_params={"DATASOURCE": "moselpy:"} redirects 'initializations from DATASOURCE'
    # to read from Python; input_data maps Python values to Mosel identifiers
        print(f'Total cost: {output_6['obj_val']:.2f}  (avg per unit: {output_6['obj_val'] / DEM:.4f})')
        print(f'Quantity bought: {output_6['sol_x']:.0f}')
        print(f'SOS2 weights: { {i: f'{v:.4f}' for i, v in output_6['sol_w'].items()}}')
    else:
        print(f'No solution found ({model_6.prob_status})')
    return COST_INC, model_6


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Varying demand

    When the same model runs many times with different data, the three-step workflow pays off: compile and load once, then call `run()` in a loop. `run()` resets the model automatically before each execution - no manual `reset()` needed.
    """)
    return


@app.cell
def _(B, COST_INC, model_6, pd):
    demands = [50, 80, 120, 150, 180, 200]
    rows = []
    for dem in demands:
        _out = model_6.run(exec_params={'DATASOURCE': 'moselpy:', 'OUTFILE': 'moselpy:'}, input_data={'DEM': dem, 'B': {i: b for i, b in enumerate(B)}, 'COST': {i + 1: c for i, c in enumerate(COST_INC)}})
        rows.append({'demand': dem, 'total_cost': _out['obj_val'], 'avg_unit_cost': _out['obj_val'] / dem})
    df = pd.DataFrame(rows).set_index('demand')
    print(df.to_string(float_format='{:.4f}'.format))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Incremental discount with binary variables (pricebrinc2_p.mos)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    An alternative formulation of the same incremental problem using explicit binary variables $b_i$ instead of SOS2.
    """)
    return


@app.cell
def _(COST_INC, DEM, MODELS, mp):
    model_7, output_7 = mp.execute_model(f'{MODELS}/pricebrinc2_p.mos', exec_params={'OUTFILE': 'moselpy:'})
    if model_7.prob_status.is_solution_available:
        print(f'Total cost: {output_7['obj_val']:.2f}  (avg per unit: {output_7['obj_val'] / DEM:.4f})')
        print(f'{'Band':<6} {'Quantity':>10} {'Unit cost':>10}')
        for _i in range(1, 4):
            print(f'{_i:<6} {output_7['sol_x'][_i]:>10.2f} {COST_INC[_i - 1]:>10.2f}')
    else:
        print(f'No solution found ({model_7.prob_status})')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Incremental discount via `pwlin` (pricebrinc3_p.mos)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    A third formulation using a `pwlin` piecewise-linear expression (requires `mmxnlp`). The cost function is specified directly as a piecewise linear function of the total quantity $x$.
    """)
    return


@app.cell
def _(DEM, MODELS, mp):
    model_8, output_8 = mp.execute_model(f'{MODELS}/pricebrinc3_p.mos', exec_params={'OUTFILE': 'moselpy:'})
    if model_8.prob_status.is_solution_available:
        print(f'Total cost: {output_8['obj_val']:.2f}  (avg per unit: {output_8['obj_val'] / DEM:.4f})')
        print(f'Quantity bought: {output_8['sol_x']:.0f}')
    else:
        print(f'No solution found ({model_8.prob_status})')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Visualizing the two pricing models
    """)
    return


@app.cell
def _(B, COST, COST_INC, mo, np, plt):
    # B, COST defined in the all-item section; COST_INC defined in the SOS2 section
    cbp = [0]
    for _i in range(3):
        cbp.append(cbp[-1] + COST_INC[_i] * (B[_i + 1] - B[_i]))

    def allitem_cost(q):
        for i in range(2, -1, -1):
            if q >= B[i]:
                return COST[i] * q
        return COST[0] * q

    def incremental_cost(q):
        for i in range(3):
            if q <= B[i + 1]:
                return cbp[i] + COST_INC[i] * (q - B[i])
        return cbp[3]
    qty = np.linspace(1, 200, 400)
    ai = [allitem_cost(q) for q in qty]
    inc = [incremental_cost(q) for q in qty]
    _fig, _ax = plt.subplots(figsize=(8, 4))
    _ax.plot(qty, ai, label='All-item discount (pricebrai)', color='steelblue')
    _ax.plot(qty, inc, label='Incremental discount (pricebrinc)', color='darkorange')
    for b in B[1:-1]:
        _ax.axvline(b, color='grey', linestyle='--', linewidth=0.8)
    _ax.axvline(150, color='red', linestyle=':', linewidth=1.2, label='Demand = 150')
    _ax.set_xlabel('Quantity')
    _ax.set_ylabel('Total cost ($)')
    _ax.set_title('All-item vs incremental price breaks')
    _ax.legend()
    plt.tight_layout()
    mo.output.append(plt.gcf())
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Function approximation with SOS2
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    *Introductory example: Chapter 5 - Piecewise Linear Programming*

    > **Mosel models:** [`approx_p.mos`](https://github.com/fico-xpress/python-notebooks/blob/main/marimo/public/moselpy/models/intro/approx_p.mos), [`approx2_p.mos`](https://github.com/fico-xpress/python-notebooks/blob/main/marimo/public/moselpy/models/intro/approx2_p.mos)

    Minimize a piecewise linear function $f(x)$ defined by five breakpoints:

    | $i$ | $\text{R}_i$ | $\text{F}_i$ |
    |-----|-------|-------|
    | 1 | 1.0 | 2.0 |
    | 2 | 2.2 | 3.2 |
    | 3 | 3.4 | 1.4 |
    | 4 | 4.8 | 2.5 |
    | 5 | 6.5 | 0.8 |

    **Decision variables:** $x, f \geq 0$ (position and function value), $y_i \geq 0$ (SOS2 interpolation weights at each breakpoint).

    $$
    \begin{align*}
    \text{minimize}   \quad & f \\
    \text{subject to} \quad & f = \sum_{i=1}^{5} \text{F}_i\,y_i \\
                              & x = \sum_{i=1}^{5} \text{R}_i\,y_i, \quad \sum_{i=1}^{5} y_i = 1 \\
                              & R_1 \leq x \leq R_5, \quad y \in \text{SOS2}
    \end{align*}
    $$

    The breakpoint coordinates ($R_i$, $F_i$) are defined in Python as plain lists and injected into the model via `input_data`. The model receives them through an `initializations from DATASOURCE` block, with `DATASOURCE` overridden to `"moselpy:"` at runtime - the same pattern used throughout these examples. This makes it trivial to experiment with different breakpoint configurations without editing the Mosel source. The model also ships with `approx_p.dat` and can run standalone with `mosel exec approx_p.mos`.
    """)
    return


@app.cell
def _(MODELS, mo, mp, plt):
    mp.compile_model(f'{MODELS}/approx_p.mos', f'{MODELS}/approx_p.bim')
    model_9 = mp.load_model(f'{MODELS}/approx_p.bim')
    model_9.set_default_stream(mp.StreamType.OUTPUT, 'null:')
    R = [1.0, 2.2, 3.4, 4.8, 6.5]
    F = [2.0, 3.2, 1.4, 2.5, 0.8]
    output_9 = model_9.run(exec_params={'DATASOURCE': 'moselpy:', 'OUTFILE': 'moselpy:'}, input_data={'R': {i + 1: v for i, v in enumerate(R)}, 'F': {i + 1: v for i, v in enumerate(F)}})
    if model_9.prob_status.is_solution_available:
        print(f'Optimal f: {output_9['sol_f']:.4f}  at x = {output_9['sol_x']:.4f}')
    else:
        print(f'No solution found ({model_9.prob_status})')
    _fig, _ax = plt.subplots(figsize=(6, 3))
    _ax.plot(R, F, 'b-o', label='f(x)')
    _ax.plot(output_9['sol_x'], output_9['sol_f'], 'r*', markersize=14, label=f'minimum: ({output_9['sol_x']:.2f}, {output_9['sol_f']:.2f})')
    _ax.set_xlabel('x')
    _ax.set_ylabel('f(x)')
    _ax.set_title('Piecewise linear function - minimum via SOS2')
    _ax.legend()
    plt.tight_layout()
    mo.output.append(plt.gcf())
    return F, R


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Piecewise linear approximation via `pwlin` (approx2_p.mos)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    `approx2_p.mos` uses a `pwlin` expression (requires `mmxnlp`) to state the same piecewise linear constraint - a more compact formulation handled natively by the MIP solver. The same breakpoint data from the cell above (`R` and `F`) is reused and passed under the model's variable names `X` and `FX`.
    """)
    return


@app.cell
def _(F, MODELS, R, mp):
    # Reuse the same breakpoint data from above, passed as X and FX
    model_10, output_10 = mp.execute_model(f'{MODELS}/approx2_p.mos', exec_params={'DATASOURCE': 'moselpy:', 'OUTFILE': 'moselpy:'}, input_data={'X': {i + 1: v for i, v in enumerate(R)}, 'FX': {i + 1: v for i, v in enumerate(F)}})
    if model_10.prob_status.is_solution_available:
        print(f'Optimal f: {output_10['sol_f']:.4f}  at x = {output_10['sol_x']:.4f}')
    else:
        print(f'No solution found ({model_10.prob_status})')
    return


if __name__ == "__main__":
    app.run()
