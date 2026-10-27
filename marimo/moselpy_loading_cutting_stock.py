# /// script
# [tool.marimo.opengraph]
# title = "MoselPy: Loading and Cutting"
# description = "Wagon, ship, tanks, bin packing, cutting"
# image = "__marimo__/thumbnail-moselpy-loadingcutting.svg"
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
    # **FICO&reg; Xpress MoselPy - Chapter D: Loading and Cutting Stock**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ***moselpy_loading_cutting_stock.py*** - Loading and cutting stock problems from the Xpress Applications Book - wagon load balancing, ship loading, tank filling, bin packing, and cutting stock, solved with MoselPy.

    &copy; Copyright 2026 Fair Isaac Corporation. The use of this example is subject to [legal and license requirements](https://github.com/fico-xpress/xpress-community#legal-and-license-requirements).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The cell below imports the necessary libraries and set `MODELS` and `DATA`, the path variables pointing to the Mosel model files and data files used in this notebook.
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
    MODELS = str(_root / "models" / "loading_cutting_stock")
    DATA   = str(_root / "data" / "loading_cutting_stock")

    print(f"MoselPy {mp.version}  |  Mosel {mp.mosel_version}  |  Xpress {mp.xpress_version}")
    mp.config.set_default_stream(mp.StreamType.OUTPUT, "null:")
    return DATA, MODELS, mp, np, pd, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Loading and cutting stock problems
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    This notebook covers six MIP examples from Chapter D of the Xpress Applications Book, solved via [MoselPy](https://pypi.org/project/moselpy/). Examples range from bin-packing and assignment problems (wagon loading, tank filling, file backup) to cutting-stock problems (sheet metal, steel bars).

    > **Mosel source files:** [`models/loading_cutting_stock/`](https://github.com/fico-xpress/python-notebooks/tree/main/marimo/public/moselpy/models/loading_cutting_stock) &nbsp;|&nbsp; **Data files:** [`data/loading_cutting_stock/`](https://github.com/fico-xpress/python-notebooks/tree/main/marimo/public/moselpy/data/loading_cutting_stock)

    > **Requirements:** `pip install moselpy mosellibs xpresslibs` - `mosellibs` provides the Mosel runtime and `xpresslibs` the Xpress solver libraries. No local Xpress installation is needed to run these notebooks, as long as the packages with libraries have been installed.

    > A local FICO&reg; Xpress installation is recommended if you want access to the full set of examples, user guides and documentation, solver libraries, and Xpress Workbench. Obtain one via the [FICO&reg; Xpress community license](https://www.fico.com/en/fico-xpress-community-license) page. If a local installation is present, set `XPRESSDIR` before starting marimo to use it instead of the `mosellibs` and `xpresslibs` packages.

    > **MoselPy documentation:** [MoselPy User Guide and Reference Manual](https://www.fico.com/fico-xpress-optimization/docs/latest/mosel/MoselPy/dhtml)

    > **Mosel examples on the web:** [examples.xpress.fico.com](https://examples.xpress.fico.com/example.pl?id=mosel_app_4)

    ### MoselPy features demonstrated in this chapter

    - **LP/MIP file export**: D-1 calls `model.export_problem(file_name=...)` after solving to write a human-readable LP file for inspection or re-use.
    - **Warm-start via `addmipsol`**: D-1 (variant 2) feeds a Python-computed LPT heuristic solution into the MIP solver as an initial integer solution via `addmipsol`.
    - **Parametric variant selection**: D-2 accepts a `VARIANT` parameter selecting one of three progressively constrained LP/MIP formulations; all three run from Python in the compile-load-run sequence.
    - **`pd.DataFrame` for 2D input**: D-5 receives the 4x16 cutting matrix as a DataFrame; MoselPy maps row and column indices to the Mosel 2D array.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## D-1 Wagon load balancing (MIP)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    *Applications Book Chapter D, Example 1*

    > **Mosel models:** [`d1wagon_p.mos`](https://github.com/fico-xpress/python-notebooks/blob/main/marimo/public/moselpy/models/loading_cutting_stock/d1wagon_p.mos), [`d1wagon2_p.mos`](https://github.com/fico-xpress/python-notebooks/blob/main/marimo/public/moselpy/models/loading_cutting_stock/d1wagon2_p.mos)

    Sixteen boxes of varying weights must be loaded onto three railway wagons. Each wagon has a weight capacity of 100 quintals. The goal is to assign boxes to wagons so that the heaviest wagon load is minimized (a minimax objective).

    **Sets:** $\text{BOXES} = 1..16$, $\text{WAGONS} = 1..3$

    **Decision variables:** $\mathit{ifload}_{b,w} \in \{0,1\}$ (1 if box $b$ goes to wagon $w$); $\mathit{maxweight} \geq 0$ (heaviest load)

    $$
    \begin{align*}
    \text{minimize}   \quad & \mathit{maxweight} \\
    \text{subject to} \quad & \sum_{w} \mathit{ifload}_{b,w} = 1 \quad \forall\, b \quad \text{(each box in one wagon)} \\
                              & \sum_{b} \text{WEIGHT}_b \cdot \mathit{ifload}_{b,w} \leq \mathit{maxweight} \quad \forall\, w \\
                              & \mathit{maxweight} \leq \text{WMAX} \\
                              & \mathit{maxweight} \geq \left\lceil \frac{\sum_b \text{WEIGHT}_b}{3} \right\rceil
    \end{align*}
    $$
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Define the 16 box weights and the wagon capacity limit in Python. Both are 1-indexed dicts.
    """)
    return


@app.cell
def _():
    WEIGHT = {i+1: v for i,v in enumerate([34,6,8,17,16,5,13,21,25,31,14,13,33,9,25,25])}
    WMAX   = 100
    return WEIGHT, WMAX


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Use the compile-load-run sequence. After `run()`, `model.export_problem(file_name=...)` writes the MIP formulation to an LP file. Pass the path as a keyword argument - the first positional argument is `options` (format flags), not the file name. The LP file is useful for inspecting the formulation in a text editor or external solver.
    """)
    return


@app.cell
def _(MODELS, WEIGHT, WMAX, mp):
    mp.compile_model(f'{MODELS}/d1wagon_p.mos', f'{MODELS}/d1wagon_p.bim')
    _model = mp.load_model(f'{MODELS}/d1wagon_p.bim')
    _model.set_default_stream(mp.StreamType.OUTPUT, 'null:')
    _output = _model.run(exec_params={'DATASOURCE': 'moselpy:', 'OUTFILE': 'moselpy:'}, input_data={'WEIGHT': WEIGHT, 'WMAX': WMAX})
    _model.export_problem(file_name=f'{MODELS}/d1wagon_p.lp')
    print('LP file written to ' + MODELS + '/d1wagon_p.lp')
    if _model.prob_status.is_solution_available:
        obj_val = _output['obj_val']
        sol_ifload = _output['sol_ifload']
    # Export the MIP formulation to LP format after solving (problem must be built first)
        print(f'\nMinimax wagon weight: {obj_val:.0f}')
        print()
        print(f'{'Wagon':<8} {'Boxes':<40} {'Total weight'}')
        for _w in range(1, 4):
            _boxes = [b for b in range(1, 17) if sol_ifload.get((b, _w), 0) > 0.5]
            _total = sum((WEIGHT[b] for b in _boxes))  # dict: (box, wagon) -> real
            print(f'  {_w:<6} {str(_boxes):<40} {_total}')
    else:
        print(f'No solution found ({_model.prob_status})')
    return obj_val, sol_ifload


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Stacked bar chart showing the box assignments across wagons. Each bar is one wagon; segments are individual boxes (width proportional to box weight). The red dashed line marks the WMAX capacity limit.
    """)
    return


@app.cell
def _(WEIGHT, WMAX, mo, obj_val, plt, sol_ifload):
    if 'sol_ifload' in locals():
        _colors = plt.cm.tab20.colors
        _fig, _ax = plt.subplots(figsize=(10, 4))
        for _w in range(1, 4):
            _boxes = sorted([b for b in range(1, 17) if sol_ifload.get((b, _w), 0) > 0.5])
            _left = 0
            for b in _boxes:
                wt = WEIGHT[b]
                _ax.barh(_w - 1, wt, left=_left, color=_colors[(b - 1) % 20], edgecolor='white', height=0.6)
                _ax.text(_left + wt / 2, _w - 1, str(b), ha='center', va='center', fontsize=7, fontweight='bold', color='white')
                _left = _left + wt
        _ax.axvline(WMAX, color='red', linestyle='--', linewidth=1.5, label=f'Capacity limit WMAX={WMAX}')
        _ax.axvline(obj_val, color='navy', linestyle=':', linewidth=1.5, label=f'Optimal max weight={obj_val:.0f}')
        _ax.set_yticks(range(3))
        _ax.set_yticklabels([f'Wagon {w}' for w in range(1, 4)])
        _ax.set_xlabel('Weight (quintals)')
        _ax.set_title('D-1 Wagon load balancing - box assignments')
        _ax.legend(loc='lower right')
        plt.tight_layout()
        mo.output.append(plt.gcf())
    else:
        print('No solution available - skipping wagon chart')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Warm-start from Python (d1wagon2_p)

    `d1wagon2_p.mos` uses a warm start to speed up the MIP. The LPT (Longest Processing Time) heuristic is implemented here in Python: boxes are sorted by weight descending and assigned one by one to the least-loaded wagon. The resulting assignment (`HeurSol`) is passed to Mosel via `input_data`. Inside the model, `addmipsol` feeds it to the Xpress branch-and-bound as an initial integer solution.

    This demonstrates a clean MoselPy pattern: **the heuristic lives in Python, the warm-start mechanism lives in Mosel**. The `solnotify` Mosel callback reports whether the optimizer accepted and used the solution.
    """)
    return


@app.cell
def _(WEIGHT):
    wagon_loads_h = {1: 0, 2: 0, 3: 0}
    heur_sol = {}
    for box in sorted(WEIGHT, key=WEIGHT.get, reverse=True):
        wagon = min(wagon_loads_h, key=wagon_loads_h.get)
        heur_sol[box] = wagon
        wagon_loads_h[wagon] = wagon_loads_h[wagon] + WEIGHT[box]
    heur_max = max(wagon_loads_h.values())
    print(f'LPT heuristic - max wagon weight: {heur_max}')
    for _w in range(1, 4):
        boxes_w = sorted((b for b in range(1, 17) if heur_sol[b] == _w))
        print(f'  Wagon {_w} ({wagon_loads_h[_w]} quintals): boxes {boxes_w}')
    return heur_max, heur_sol


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Run `d1wagon2_p.mos` with the Python-computed `HeurSol` passed via `input_data`. The model feeds it to the optimizer via `addmipsol` before branch-and-bound starts.
    """)
    return


@app.cell
def _(MODELS, WEIGHT, WMAX, heur_max, heur_sol, mp):
    mp.compile_model(f"{MODELS}/d1wagon2_p.mos", f"{MODELS}/d1wagon2_p.bim")
    with mp.load_model(f"{MODELS}/d1wagon2_p.bim") as model2:
        model2.set_default_stream(mp.StreamType.OUTPUT, "null:")
        out2 = model2.run(
            exec_params={"DATASOURCE": "moselpy:", "OUTFILE": "moselpy:"},
            input_data={"WEIGHT": WEIGHT, "WMAX": WMAX, "HeurSol": heur_sol},
        )
        ok2 = model2.prob_status.is_solution_available
        sol_ifload_opt = out2.get("sol_ifload", {}) if ok2 else {}

    if ok2:
        opt_max = out2["obj_val"]
        print(f"LPT heuristic max weight: {heur_max:.0f}")
        print(f"MIP optimal  max weight:  {opt_max:.0f}")
        print(f"Gap closed:  {heur_max - opt_max:.0f} quintals")
    else:
        print("No solution found for d1wagon2_p")
    return ok2, out2, sol_ifload_opt


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Side-by-side comparison of the LPT heuristic assignment (left) and the MIP optimal assignment (right). Each row is a wagon; segments represent individual boxes, width proportional to weight.
    """)
    return


@app.cell
def _(WEIGHT, WMAX, heur_max, heur_sol, mo, ok2, out2, plt, sol_ifload_opt):
    if ok2:
        _colors = plt.cm.tab20.colors
        _fig, _axes = plt.subplots(1, 2, figsize=(14, 4), sharey=True)

        def draw_wagons(ax, assignment_fn, title, max_w):
            for w in range(1, 4):
                boxes = sorted((b for b in range(1, 17) if assignment_fn(b) == w))
                left = 0
                for b in boxes:
                    wt = WEIGHT[b]
                    ax.barh(w - 1, wt, left=left, color=_colors[(b - 1) % 20], edgecolor='white', height=0.6)
                    ax.text(left + wt / 2, w - 1, str(b), ha='center', va='center', fontsize=7, fontweight='bold', color='white')
                    left = left + wt
            ax.axvline(WMAX, color='red', linestyle='--', linewidth=1.5, label=f'WMAX={WMAX}')
            ax.axvline(max_w, color='navy', linestyle=':', linewidth=1.5, label=f'Max load={max_w:.0f}')
            ax.set_yticks(range(3))
            ax.set_yticklabels([f'Wagon {w}' for w in range(1, 4)])
            ax.set_xlabel('Weight (quintals)')
            ax.set_title(title)
            ax.legend(loc='lower right')
        draw_wagons(_axes[0], lambda b: heur_sol[b], f'LPT heuristic (max={heur_max:.0f})', heur_max)
        draw_wagons(_axes[1], lambda b: round(sum((w * sol_ifload_opt.get((b, w), 0) for w in range(1, 4)))), f'MIP optimal (max={out2['obj_val']:.0f})', out2['obj_val'])
        plt.tight_layout()
        mo.output.append(plt.gcf())
    else:
        print('No solution available - skipping comparison chart')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## D-2 Ship loading (LP/MIP)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    *Applications Book Chapter D, Example 2*

    > **Mosel model:** [`d2ship_p.mos`](https://github.com/fico-xpress/python-notebooks/blob/main/marimo/public/moselpy/models/loading_cutting_stock/d2ship_p.mos)

    A shipper has 7 clients wishing to ship wheat. Each client offers varying numbers of lots, lot sizes, prices, and transport costs. The shipper maximizes profit subject to a ship capacity constraint. The model accepts a `VARIANT` parameter to select one of three progressively constrained variants:

    - **VARIANT=1 (LP):** unlimited lot availability per client.
    - **VARIANT=2 (LP):** each client has an upper bound on available lots.
    - **VARIANT=3 (MIP):** lots must be integer-valued.

    **Sets:** $\text{CLIENTS} = 1..7$

    **Decision variables:** $\mathit{loadqty}_c \geq 0$ (lots taken from client $c$)

    **Derived parameter:** $\text{PROF}_c = \text{PRICE}_c - \text{COST}_c \cdot \text{SIZE}_c$ (profit per lot from client $c$)

    $$
    \begin{align*}
    \text{maximize}   \quad & \sum_{c} \text{PROF}_c \cdot \mathit{loadqty}_c \\
    \text{subject to} \quad & \sum_{c} \text{SIZE}_c \cdot \mathit{loadqty}_c \leq \text{CAP} \\
                              & \mathit{loadqty}_c \leq \text{AVAIL}_c \quad \forall\, c \quad \text{(Problem 2 and 3 only)} \\
                              & \mathit{loadqty}_c \in \mathbb{Z}_{\geq 0} \quad \forall\, c \quad \text{(Problem 3 only)}
    \end{align*}
    $$
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Define client data in Python: available lots `AVAIL`, lot sizes `SIZE`, prices `PRICE`, transport costs `COST`, and ship capacity `CAP`, all as 1-indexed dicts.
    """)
    return


@app.cell
def _():
    AVAIL = {i + 1: v for i, v in enumerate([12, 31, 20, 25, 50, 40, 60])}
    SIZE = {i + 1: v for i, v in enumerate([10, 8, 6, 9, 15, 10, 12])}
    PRICE = {i + 1: v for i, v in enumerate([1000, 600, 600, 800, 1200, 800, 1100])}
    COST = {i + 1: v for i, v in enumerate([80, 70, 85, 80, 73, 70, 80])}
    CAP = 1500
    PROF = {c: PRICE[c] - COST[c] * SIZE[c] for c in range(1, 8)}
    # Derived: profit per lot (for display)
    print('Profit per lot by client:')
    for _c in range(1, 8):
        print(f'  Client {_c}: price={PRICE[_c]}, cost={COST[_c]}, size={SIZE[_c]} -> profit={PROF[_c]}')
    return AVAIL, CAP, COST, PRICE, PROF, SIZE


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Compile and load `d2ship_p.mos` once, then run it three times with `VARIANT=1`, `VARIANT=2`, and `VARIANT=3`. Each run returns `sol_obj` (the profit for that variant) and `sol_load` (the lots per client). Running separately lets you inspect the solution at each stage rather than only seeing the final MIP result.
    """)
    return


@app.cell
def _(AVAIL, CAP, COST, MODELS, PRICE, PROF, SIZE, mp):
    mp.compile_model(f'{MODELS}/d2ship_p.mos', f'{MODELS}/d2ship_p.bim')
    _model = mp.load_model(f'{MODELS}/d2ship_p.bim')
    _model.set_default_stream(mp.StreamType.OUTPUT, 'null:')
    _obj_labels = {1: 'LP, no limits', 2: 'LP, availability limits', 3: 'MIP, integer lots'}
    results = {}
    for _obj in [1, 2, 3]:
        _output = _model.run(exec_params={'DATASOURCE': 'moselpy:', 'OUTFILE': 'moselpy:', 'VARIANT': _obj}, input_data={'AVAIL': AVAIL, 'SIZE': SIZE, 'PRICE': PRICE, 'COST': COST, 'CAP': CAP})
        if _model.prob_status.is_solution_available:
            results[_obj] = _output
        else:
            print(f'MOD={_obj}: No solution found ({_model.prob_status})')
    for _obj, _output in results.items():
        sol_obj = _output['sol_obj']
        _sol_load = _output['sol_load']
        print(f'OBJ {_obj} ({_obj_labels[_obj]}): profit = {sol_obj:,.2f}')
        for _c in range(1, 8):
            q = _sol_load.get(_c, 0)
            if q > 0.001:
                print(f'  Client {_c}: {q:.4g} lots  (contribution: {PROF[_c] * q:,.0f})')
        print()
    return (results,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Left: bar chart comparing the three profit objectives. Right: per-client profit contribution for each variant, showing how availability and integrality constraints change the loading decision.
    """)
    return


@app.cell
def _(PROF, mo, np, plt, results):
    if results:
        _obj_labels = {1: 'OBJ 1\n(LP, unlimited)', 2: 'OBJ 2\n(LP, limited)', 3: 'OBJ 3\n(MIP, integer)'}
        _colors = {1: '#42A5F5', 2: '#FB8C00', 3: '#43A047'}
        _fig, _axes = plt.subplots(1, 2, figsize=(13, 4))
        _ax = _axes[0]
        labels = [_obj_labels[o] for o in [1, 2, 3]]
        values = [results[o]['sol_obj'] for o in [1, 2, 3]]  # Left: objective comparison
        bars = _ax.bar(labels, values, color=[_colors[o] for o in [1, 2, 3]], edgecolor='white')
        for bar, _val in zip(bars, values):
            _ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 200, f'{_val:,.0f}', ha='center', va='bottom', fontsize=9)
        _ax.set_ylabel('Profit')
        _ax.set_title('D-2 Ship loading - profit by variant')
        ax2 = _axes[1]
        x = np.arange(1, 8)
        width = 0.25
        for i, _obj in enumerate([1, 2, 3]):
            _sol_load = results[_obj]['sol_load']
            contribs = [PROF[c] * _sol_load.get(c, 0) for c in range(1, 8)]  # Right: per-client contributions per variant
            ax2.bar(x + (i - 1) * width, contribs, width=width, color=_colors[_obj], edgecolor='white', label=f'OBJ {_obj}')
        ax2.set_xticks(x)
        ax2.set_xticklabels([f'Client {c}' for c in range(1, 8)], fontsize=8)
        ax2.set_ylabel('Profit contribution')
        ax2.set_title('D-2 Client profit contributions by variant')
        ax2.legend(fontsize=8)
        plt.tight_layout()
        mo.output.append(plt.gcf())
    else:
        print('No solution available - skipping ship loading chart')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## D-3 Tank loading (MIP)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    *Applications Book Chapter D, Example 3*

    > **Mosel model:** [`d3tanks_p.mos`](https://github.com/fico-xpress/python-notebooks/blob/main/marimo/public/moselpy/models/loading_cutting_stock/d3tanks_p.mos)

    Five tanker ships carrying chemical liquids must be unloaded into 9 storage tanks. Liquids must not be mixed. Two tanks already have partial contents. The model is solved for two objectives in sequence:

    - **Objective 1:** minimize total capacity of tanks occupied (prefer filling fewer, larger tanks).
    - **Objective 2:** minimize number of tanks used.

    Entries of the decision variable array `ifload` are created dynamically via `create()` - only for the empty tanks. The `TINIT` and `QINIT` arrays record the initial partial contents.

    **Sets:** $\text{TANKS} = 1..9$, $\text{LIQ} = \{\text{Benzol, Butanol, Propanol, Styrene, THF}\}$

    **Decision variables:** $\mathit{ifload}_{l,t} \in \{0,1\}$ for $t$ with no initial contents (1 if liquid $l$ uses tank $t$)

    $$
    \begin{align*}
    \text{Obj 1:}\quad \text{minimize} \quad & \sum_{l,t} \text{CAP}_t \cdot \mathit{ifload}_{l,t} \\
    \text{Obj 2:}\quad \text{minimize} \quad & \sum_{l,t} \mathit{ifload}_{l,t} \\
    \text{subject to} \quad & \sum_{l} \mathit{ifload}_{l,t} \leq 1 \quad \forall\, t \quad \text{(no mixing)} \\
                              & \sum_{t} \text{CAP}_t \cdot \mathit{ifload}_{l,t} \geq \text{REST}_l \quad \forall\, l \quad \text{(satisfy remaining quantities)}
    \end{align*}
    $$

    where $\text{REST}_l = \text{ARR}_l - \sum_{t:\,\text{TINIT}_t=l}(\text{CAP}_t - \text{QINIT}_t)$ is the quantity not covered by the pre-filled tanks.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Define the 9 tank capacities, arriving quantities per liquid, initial tank assignments (`TINIT` and `QINIT` for the two pre-filled tanks), and pass them via `input_data`. The `LIQ` set is auto-populated from the string keys of the `ARR` dict.
    """)
    return


@app.cell
def _():
    CAP_1 = {i + 1: v for i, v in enumerate([500, 400, 400, 600, 600, 900, 800, 800, 800])}
    ARR = {'Benzol': 1200, 'Butanol': 700, 'Propanol': 1000, 'Styrene': 450, 'THF': 1200}
    TINIT = {2: 'Benzol', 7: 'THF'}
    QINIT = {2: 100, 7: 300}
    print('Tank capacities:', list(CAP_1.values()))
    print('Arriving quantities:', ARR)
    print('Pre-filled tanks:', {t: f'{TINIT[t]} ({QINIT[t]})' for t in TINIT})
    return ARR, CAP_1, QINIT, TINIT


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The model accepts an `OBJ` parameter (1 = minimize total capacity used, 2 = minimize number of tanks). Compile and load once, then run twice with `exec_params={"OBJ": 1}` and `exec_params={"OBJ": 2}`. Both runs return `sol_TankUse`, `sol_TankNum`, and `sol_ifload` (the detailed assignment), enabling a side-by-side comparison. Pre-filled tanks 2 (Benzol, 100) and 7 (THF, 300) are fixed and excluded from the counts.
    """)
    return


@app.cell
def _(ARR, CAP_1, MODELS, QINIT, TINIT, mp):
    mp.compile_model(f'{MODELS}/d3tanks_p.mos', f'{MODELS}/d3tanks_p.bim')
    _model = mp.load_model(f'{MODELS}/d3tanks_p.bim')
    _model.set_default_stream(mp.StreamType.OUTPUT, 'null:')
    prefilled_cap = sum((CAP_1[t] for t in QINIT))
    prefilled_num = len(QINIT)
    results_1 = {}
    for _obj in [1, 2]:
        _output = _model.run(exec_params={'DATASOURCE': 'moselpy:', 'OUTFILE': 'moselpy:', 'VARIANT': _obj}, input_data={'CAP': CAP_1, 'ARR': ARR, 'TINIT': TINIT, 'QINIT': QINIT})
        if _model.prob_status.is_solution_available:
            results_1[_obj] = _output
        else:
            print(f'MOD={_obj}: No solution found ({_model.prob_status})')
    _obj_labels = {1: 'min capacity', 2: 'min tanks'}
    for _obj, _output in results_1.items():
        sol_ifload_1 = {(l, t): v for (l, t), v in _output['sol_ifload'].items() if v > 0.5}
        sol_TankUse = _output['sol_TankUse']
        sol_TankNum = _output['sol_TankNum']
        print(f'OBJ {_obj} ({_obj_labels[_obj]}):')
        print(f'  Capacity of newly used tanks: {sol_TankUse:.0f}  (total incl. pre-filled: {sol_TankUse + prefilled_cap:.0f})')
        print(f'  Number  of newly used tanks:  {sol_TankNum:.0f}  (total incl. pre-filled: {sol_TankNum + prefilled_num:.0f})')
        for t in range(1, 10):
            if t in QINIT:
                print(f'    Tank {t} (cap={CAP_1[t]:>4}): {TINIT[t]} [pre-filled, qty={QINIT[t]}]')
            else:
                liq_here = [l for l, tk in sol_ifload_1 if tk == t]
                print(f'    Tank {t} (cap={CAP_1[t]:>4}): {(liq_here[0] if liq_here else 'empty')}')
        print()
    return prefilled_cap, prefilled_num, results_1


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Side-by-side bar charts comparing the two objective assignments. Each tank is colored by its assigned liquid. Pre-filled tanks are shown with a hatched pattern; empty tanks are gray.
    """)
    return


@app.cell
def _(ARR, CAP_1, QINIT, TINIT, mo, plt, prefilled_cap, prefilled_num, results_1):
    if results_1:
        liq_names = list(ARR.keys())
        liq_colors = dict(zip(liq_names, ['#1E88E5', '#FB8C00', '#43A047', '#E53935', '#8E24AA']))
        _obj_labels = {1: 'Obj 1: min capacity', 2: 'Obj 2: min tanks'}

        def draw_tanks(ax, assigned, sol_TankUse, sol_TankNum, title):
            seen = set()
            for t in range(1, 10):
                cap = CAP_1[t]
                if t in QINIT:
                    liq = TINIT[t]
                    label = f'{liq} (pre-filled)' if liq not in seen else ''
                    seen.add(liq)
                    ax.bar(t, cap, color=liq_colors.get(liq, '#90CAF9'), edgecolor='gray', hatch='///', alpha=0.7, label=label)
                else:
                    liq_here = [l for l, tk in assigned if tk == t]
                    if liq_here:
                        liq = liq_here[0]
                        label = liq if liq not in seen else ''
                        seen.add(liq)
                        ax.bar(t, cap, color=liq_colors.get(liq, '#90CAF9'), edgecolor='white', label=label)
                    else:
                        label = 'Empty' if 'Empty' not in seen else ''
                        seen.add('Empty')
                        ax.bar(t, cap, color='#BDBDBD', edgecolor='white', label=label)
            ax.set_xticks(range(1, 10))
            ax.set_xticklabels([f'T{t}' for t in range(1, 10)])
            ax.set_ylabel('Tank capacity')
            ax.set_title(f'{title}\n(cap used={sol_TankUse + prefilled_cap:.0f}, tanks used={sol_TankNum + prefilled_num:.0f})')
            ax.legend(loc='upper right', fontsize=7)
        _fig, _axes = plt.subplots(1, 2, figsize=(14, 4))
        for _obj, _ax in zip([1, 2], _axes):
            _output = results_1[_obj]
            assigned = {(l, t): v for (l, t), v in _output['sol_ifload'].items() if v > 0.5}
            draw_tanks(_ax, assigned, _output['sol_TankUse'], _output['sol_TankNum'], _obj_labels[_obj])
        plt.tight_layout()
        mo.output.append(plt.gcf())
    else:
        print('No solution available - skipping tank chart')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## D-4 Bin packing: file backup (MIP)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    *Applications Book Chapter D, Example 4*

    > **Mosel model:** [`d4backup_p.mos`](https://github.com/fico-xpress/python-notebooks/blob/main/marimo/public/moselpy/models/loading_cutting_stock/d4backup_p.mos)

    Sixteen files of varying sizes must be backed up onto external storage disks, each with capacity 1440 MB. The goal is to minimize the number of disks used. This is the classic bin-packing problem. The model computes the minimum number of disks required (`ND`) as an upper bound before building the MIP.

    **Sets:** $\text{FILES} = 1..16$, $\text{DISKS} = 1..\text{ND}$

    **Decision variables:** $\mathit{ifsave}_{f,d} \in \{0,1\}$ (1 if file $f$ saved on disk $d$); $\mathit{diskuse} \geq 0$ (index of last disk used)

    $$
    \begin{align*}
    \text{minimize}   \quad & \mathit{diskuse} \\
    \text{subject to} \quad & \mathit{diskuse} \geq \sum_d d \cdot \mathit{ifsave}_{f,d} \quad \forall\, f \\
                              & \sum_d \mathit{ifsave}_{f,d} = 1 \quad \forall\, f \quad \text{(each file on one disk)} \\
                              & \sum_f \text{SIZE}_f \cdot \mathit{ifsave}_{f,d} \leq \text{CAP} \quad \forall\, d
    \end{align*}
    $$
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Define file sizes and disk capacity in Python. `SIZE` is a 1-indexed dict; `CAP` is a scalar. The model computes `ND` internally using `ceil(sum(SIZE)/CAP)`.
    """)
    return


@app.cell
def _():
    SIZE_1 = {i + 1: v for i, v in enumerate([46, 55, 62, 87, 108, 114, 137, 164, 253, 364, 372, 388, 406, 432, 461, 851])}
    CAP_2 = 1440
    _total = sum(SIZE_1.values())
    nd_lb = -(-_total // CAP_2)
    print(f'Total file size: {_total} MB, disk capacity: {CAP_2} MB')
    print(f'Lower bound on disks needed: {nd_lb}')
    return CAP_2, SIZE_1


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Run `d4backup_p.mos` using the single execution command. The model computes `ND` internally and builds `DISKS = 1..ND` before declaring `ifsave`. After solving, `obj_val` is the number of disks used and `sol_ifsave` is the full assignment matrix.
    """)
    return


@app.cell
def _(CAP_2, MODELS, SIZE_1, mp):
    _model, _output = mp.execute_model(f'{MODELS}/d4backup_p.mos', exec_params={'DATASOURCE': 'moselpy:', 'OUTFILE': 'moselpy:'}, input_data={'SIZE': SIZE_1, 'CAP': CAP_2})
    if _output is not None:
        obj_val_d4 = _output['obj_val']
        sol_ifsave = _output['sol_ifsave']
        _nd_used = int(round(obj_val_d4))
        print(f'Minimum number of disks: {_nd_used}')
        print()
        for _d in range(1, _nd_used + 1):
            _files = [f for f in range(1, 17) if sol_ifsave.get((f, _d), 0) > 0.5]
            used = sum((SIZE_1[f] for f in _files))
            print(f'  Disk {_d}: files {_files}  used={used} MB  free={CAP_2 - used} MB')
    else:
        print('No output returned')
    return obj_val_d4, sol_ifsave


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Horizontal stacked bar chart of disk utilization. Each disk is a bar; segments are individual files (width = file size in MB). The dashed line marks the 1440 MB capacity.
    """)
    return


@app.cell
def _(CAP_2, SIZE_1, mo, obj_val_d4, plt, sol_ifsave):
    if 'sol_ifsave' in locals():
        _nd_used = int(round(obj_val_d4))
        file_colors = plt.cm.tab20.colors
        _fig, _ax = plt.subplots(figsize=(11, max(3, _nd_used * 0.6 + 1)))
        for _d in range(1, _nd_used + 1):
            _files = sorted([f for f in range(1, 17) if sol_ifsave.get((f, _d), 0) > 0.5])
            _left = 0
            for f in _files:
                sz = SIZE_1[f]
                _ax.barh(_d - 1, sz, left=_left, color=file_colors[(f - 1) % 20], edgecolor='white', height=0.6)
                _ax.text(_left + sz / 2, _d - 1, str(f), ha='center', va='center', fontsize=7, fontweight='bold', color='white')
                _left = _left + sz
        _ax.axvline(CAP_2, color='red', linestyle='--', linewidth=1.5, label=f'Capacity = {CAP_2} MB')
        _ax.set_yticks(range(_nd_used))
        _ax.set_yticklabels([f'Disk {d}' for d in range(1, _nd_used + 1)])
        _ax.set_xlabel('Size (MB)')
        _ax.set_title(f'D-4 Bin packing - {_nd_used} disks used')
        _ax.legend(loc='lower right')
        plt.tight_layout()
        mo.output.append(plt.gcf())
    else:
        print('No solution available - skipping backup chart')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## D-5 Sheet metal cutting (MIP)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    *Applications Book Chapter D, Example 5*

    > **Mosel model:** [`d5cutsh_p.mos`](https://github.com/fico-xpress/python-notebooks/blob/main/marimo/public/moselpy/models/loading_cutting_stock/d5cutsh_p.mos)

    A sheet metal shop cuts large sheets into 4 smaller sizes. There are 16 pre-computed cutting patterns. The goal is to satisfy demand for each size using the minimum number of large sheets. This is a covering (cutting stock) problem.

    **Sets:** $\text{PATTERNS} = 1..16$, $\text{SIZES} = 1..4$

    **Decision variables:** $\mathit{use}_p \in \mathbb{Z}_{\geq 0}$ (how many times to cut pattern $p$)

    $$
    \begin{align*}
    \text{minimize}   \quad & \sum_{p} \mathit{use}_p \\
    \text{subject to} \quad & \sum_{p} \text{CUT}_{s,p} \cdot \mathit{use}_p \geq \text{DEM}_s \quad \forall\, s \in \text{SIZES}
    \end{align*}
    $$
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Define demands `DEM` and the 4x16 cutting matrix `CUT` in Python. `CUT` is passed as a `pd.DataFrame` with size indices as rows and pattern indices as columns. Passing a DataFrame directly as `input_data` is a convenient way to supply 2D data without manually constructing a tuple-keyed dict.
    """)
    return


@app.cell
def _(pd):
    DEM = {1: 8, 2: 13, 3: 5, 4: 15}

    cut_rows = [
        [1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0],   # size 1
        [2,1,0,2,1,0,3,2,1,0,5,4,3,2,1,0],   # size 2
        [0,0,0,2,2,2,1,1,1,1,0,0,0,0,0,0],   # size 3
        [0,1,3,0,1,3,0,2,3,5,0,1,3,5,6,8],   # size 4
    ]
    CUT = pd.DataFrame(cut_rows, index=[1,2,3,4], columns=range(1,17))
    CUT.index.name   = "Size"
    CUT.columns.name = "Pattern"

    print("Demands:", DEM)
    print("\nCutting patterns (rows=sizes, columns=patterns):")
    print(CUT.to_string())
    return CUT, DEM


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Run the model passing `CUT` as a DataFrame in `input_data`. MoselPy maps the DataFrame's row/column indices directly to the Mosel 2D array. After solving, `sol_use` is a dict mapping pattern index to number of times it is used.
    """)
    return


@app.cell
def _(CUT, DEM, MODELS, mp):
    _model, _output = mp.execute_model(f'{MODELS}/d5cutsh_p.mos', exec_params={'DATASOURCE': 'moselpy:', 'OUTFILE': 'moselpy:'}, input_data={'DEM': DEM, 'CUT': CUT})
    if _output is not None:
        obj_val_d5 = _output['obj_val']
        sol_use_d5 = _output['sol_use']
        print(f'Minimum large sheets required: {obj_val_d5:.0f}')
        print()
        print('Patterns used:')
        for _p in range(1, 17):
            _qty = sol_use_d5.get(_p, 0)  # dict: pattern -> real
            if _qty > 0.5:
                _pieces = [f'size {s}: {CUT.at[s, _p]}' for s in range(1, 5) if CUT.at[s, _p] > 0]
                print(f'  Pattern {_p:2d} x {_qty:.0f}:  {', '.join(_pieces)}')
        print()
        for _s in range(1, 5):
            _produced = sum((CUT.at[_s, p] * sol_use_d5.get(p, 0) for p in range(1, 17)))
            print(f'  Size {_s}: demand={DEM[_s]}, produced={_produced:.0f}')
    else:
        print('No output returned')
    return obj_val_d5, sol_use_d5


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Heatmap of the 4x16 cutting pattern matrix. Darker cells indicate more pieces of that size cut per sheet. Patterns actually used in the solution are highlighted with a border.
    """)
    return


@app.cell
def _(CUT, mo, obj_val_d5, plt, sol_use_d5):
    if 'sol_use_d5' in locals():
        cut_matrix = CUT.values  # shape (4, 16)
        used_patterns = [p for p in range(1, 17) if sol_use_d5.get(p, 0) > 0.5]
        _fig, _ax = plt.subplots(figsize=(13, 3.5))
        im = _ax.imshow(cut_matrix, cmap='Blues', aspect='auto', vmin=0)
        plt.colorbar(im, ax=_ax, label='Pieces per sheet')
        for s_idx in range(4):
            for p_idx in range(16):
                _val = cut_matrix[s_idx, p_idx]
                _ax.text(p_idx, s_idx, str(_val), ha='center', va='center', fontsize=8, color='white' if _val > 3 else 'black')
        for _p in used_patterns:
            p_idx = _p - 1
            _ax.add_patch(plt.Rectangle((p_idx - 0.5, -0.5), 1, 4, fill=False, edgecolor='red', linewidth=2.5))
        _ax.set_xticks(range(16))
        _ax.set_xticklabels([f'P{p}' for p in range(1, 17)], fontsize=7)  # Highlight used patterns
        _ax.set_yticks(range(4))
        _ax.set_yticklabels([f'Size {s}' for s in range(1, 5)])
        _ax.set_title(f'D-5 Sheet cutting patterns (red border = patterns used, total sheets={obj_val_d5:.0f})')
        plt.tight_layout()
        mo.output.append(plt.gcf())
    else:
        print('No solution available - skipping pattern heatmap')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## D-6 Cutting steel bars (MIP)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    *Applications Book Chapter D, Example 6*

    > **Mosel model:** [`d6cutbar_p.mos`](https://github.com/fico-xpress/python-notebooks/blob/main/marimo/public/moselpy/models/loading_cutting_stock/d6cutbar_p.mos)

    A company produces school desks in three heights (40, 60, 70 cm). Desk legs are cut from steel bars of two lengths (150 cm and 200 cm). Each bar has its own set of pre-computed patterns. The goal is to minimize total material waste (trim loss).

    Note that `SIZES` is declared as `set of integer` in the Mosel model, which is more general than a range. When passing `DEM` from Python as a dict keyed by integer, MoselPy automatically populates `SIZES` from the dict keys.

    **Sets:** $\text{PAT1} = 1..6$, $\text{PAT2} = 7..12$, $\text{PATTERNS} = \text{PAT1} \cup \text{PAT2}$, $\text{SIZES} = \{40, 60, 70\}$

    **Decision variables:** $\mathit{use}_p \in \mathbb{Z}_{\geq 0}$ (how many times to use pattern $p$)

    $$
    \begin{align*}
    \text{minimize}   \quad & \sum_{p \in \text{PAT1}} \text{LEN}_1 \cdot \mathit{use}_p + \sum_{p \in \text{PAT2}} \text{LEN}_2 \cdot \mathit{use}_p - \sum_{s \in \text{SIZES}} 4 \cdot \text{DEM}_s \cdot s \\
    \text{subject to} \quad & \sum_{p \in \text{PATTERNS}} \text{CUT}_{p,s} \cdot \mathit{use}_p \geq 4 \cdot \text{DEM}_s \quad \forall\, s \in \text{SIZES}
    \end{align*}
    $$

    The factor of 4 accounts for 4 legs per desk. The objective is the total bar material used minus total leg material needed.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Define demands by desk height and the cutting patterns in Python. The data is defined here for readability, but the model reads from the `.dat` file. Unlike `set of string`, a `set of integer` index (`SIZES`) cannot be initialized via the `moselpy:` driver - this is the same limitation as `array of set of integer` seen in `a5mine2_p` and `b1stadium2_p`.
    """)
    return


@app.cell
def _():
    DEM_1 = {40: 108, 60: 125, 70: 100}
    LEN = {1: 150, 2: 200}
    CUT_1 = {(1, 40): 0, (1, 60): 0, (1, 70): 2, (2, 40): 0, (2, 60): 1, (2, 70): 1, (3, 40): 2, (3, 60): 0, (3, 70): 1, (4, 40): 0, (4, 60): 2, (4, 70): 0, (5, 40): 2, (5, 60): 1, (5, 70): 0, (6, 40): 3, (6, 60): 0, (6, 70): 0, (7, 40): 0, (7, 60): 1, (7, 70): 2, (8, 40): 0, (8, 60): 2, (8, 70): 1, (9, 40): 1, (9, 60): 0, (9, 70): 2, (10, 40): 3, (10, 60): 0, (10, 70): 1, (11, 40): 0, (11, 60): 3, (11, 70): 0, (12, 40): 5, (12, 60): 0, (12, 70): 0}
    print('Demands by height (x4 legs per desk):')
    for _s, _d in DEM_1.items():
        print(f'  Height {_s} cm: {_d} desks = {4 * _d} legs')
    print(f'\nBar lengths: {LEN}')
    return CUT_1, DEM_1, LEN


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Run `d6cutbar_p.mos` reading from the `.dat` file. After solving, `obj_val` is the trim loss in cm and `sol_use` maps pattern index to usage count.
    """)
    return


@app.cell
def _(CUT_1, DATA, DEM_1, LEN, MODELS, mp):
    _model, _output = mp.execute_model(f'{MODELS}/d6cutbar_p.mos', exec_params={'DATASOURCE': f'{DATA}/d6cutbar_p.dat', 'OUTFILE': 'moselpy:'})
    if _output is not None:
        obj_val_d6 = _output['obj_val']
        sol_use_d6 = _output['sol_use']
        short_used = sum((sol_use_d6.get(p, 0) for p in range(1, 7)))
        long_used = sum((sol_use_d6.get(p, 0) for p in range(7, 13)))
        print(f'Total trim loss: {obj_val_d6:.0f} cm')
        print(f'Short bars (150 cm) used: {short_used:.0f}')
        print(f'Long bars  (200 cm) used: {long_used:.0f}')
        print()
        print('Patterns used:')
        for _p in range(1, 13):
            _qty = sol_use_d6.get(_p, 0)
            if _qty > 0.5:
                bar_len = LEN[1] if _p <= 6 else LEN[2]
                _pieces = [f'{s}cm x{CUT_1.get((_p, s), 0)}' for s in [40, 60, 70] if CUT_1.get((_p, s), 0) > 0]
                print(f'  Pattern {_p:2d} (bar={bar_len}cm) x {_qty:.0f}:  {', '.join(_pieces)}')
        print()
        for _s in [40, 60, 70]:
            _produced = sum((CUT_1.get((p, _s), 0) * sol_use_d6.get(p, 0) for p in range(1, 13)))
            needed = 4 * DEM_1[_s]
            print(f'  Height {_s} cm: {_produced:.0f} legs produced, {needed} needed')
    else:
        print('No output returned')
    return


if __name__ == "__main__":
    app.run()
