# /// script
# [tool.marimo.opengraph]
# title = "MoselPy: Telecommunications"
# description = "Network reliability, dimensioning, routing"
# image = "__marimo__/thumbnail-moselpy-telecomm.svg"
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
    # **FICO&reg; Xpress MoselPy - Chapter G: Telecommunications**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ***moselpy_telecomm.py*** - Telecommunications network design problems from the Xpress Applications Book - network reliability, mobile network dimensioning, call routing, cable networks, satellite scheduling, and transmitter placement, solved with MoselPy.

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
    MODELS = str(_root / "models" / "telecomm")
    DATA   = str(_root / "data" / "telecomm")

    print(f"MoselPy {mp.version}  |  Mosel {mp.mosel_version}  |  Xpress {mp.xpress_version}")
    mp.config.set_default_stream(mp.StreamType.OUTPUT, "null:")
    return MODELS, mp, mpatches, pd, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Telecommunications network design
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    This notebook covers six LP and MIP examples from Chapter G of the Xpress Applications Book, solved via [MoselPy](https://pypi.org/project/moselpy/). Examples span network reliability analysis, mobile network dimensioning, telephone call routing, cable network design, satellite scheduling, and transmitter placement.

    > **Mosel source files:** [`models/telecomm/`](https://github.com/fico-xpress/python-notebooks/tree/main/marimo/public/moselpy/models/telecomm) &nbsp;|&nbsp; **Data files:** [`data/telecomm/`](https://github.com/fico-xpress/python-notebooks/tree/main/marimo/public/moselpy/data/telecomm)

    > **Requirements:** `pip install moselpy mosellibs xpresslibs` - `mosellibs` provides the Mosel runtime and `xpresslibs` the Xpress solver libraries. No local Xpress installation is needed to run these notebooks, as long as the packages with libraries have been installed.

    > A local FICO&reg; Xpress installation is recommended if you want access to the full set of examples, user guides and documentation, solver libraries, and Xpress Workbench. Obtain one via the [FICO&reg; Xpress community license](https://www.fico.com/en/fico-xpress-community-license) page. If a local installation is present, set `XPRESSDIR` before starting marimo to use it instead of the `mosellibs` and `xpresslibs` packages.

    > **MoselPy documentation:** [MoselPy User Guide and Reference Manual](https://www.fico.com/fico-xpress-optimization/docs/latest/mosel/MoselPy/dhtml)

    > **Mosel examples on the web:** [examples.xpress.fico.com](https://examples.xpress.fico.com/example.pl?id=mosel_app_7)

    ### MoselPy features demonstrated in this chapter

    - **Dynamic sparse arrays**: G-1 uses Mosel `dynamic array` with `exists()` and `create()` to build flow variables only for existing network arcs. MoselPy reads these from a sparse Python dict automatically.
    - **`pd.DataFrame` for 2D cost input**: G-2 passes a 10x5 cost matrix as a DataFrame; MoselPy maps rows and columns to the Mosel 2D array index.
    - **Two consecutive `initializations from` blocks**: G-3 reads arc capacities and demands first, computes the number of arcs dynamically, then reads the route array in a second block - both from the same Python `input_data` dict.
    - **Model introspection before running**: G-4 calls `model.name`, `model.version`, and `model.size` after `load_model()` but before `run()`.
    - **Context manager + iterative in-Mosel algorithm**: G-5 uses `with mp.load_model(...) as model:` and runs an iterative scheduling algorithm that modifies and re-solves inside Mosel, returning the complete schedule to Python.
    - **`exec_params` sensitivity loop**: G-6 varies `BUDGET` across a parametric run to show how population coverage changes with the available budget.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## G-1 Network reliability (max flow)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    *Applications Book Chapter G, Example 1*

    > **Mosel model:** [`g1rely_p.mos`](https://github.com/fico-xpress/python-notebooks/blob/main/marimo/public/moselpy/models/telecomm/g1rely_p.mos)

    A military telecommunications network has 11 sites connected by bidirectional links. Due to reliability requirements, nodes 10 (SOURCE) and 11 (SINK) must be able to communicate even if any three other sites are destroyed. This is equivalent to asking whether the network contains at least 4 vertex-disjoint paths from SOURCE to SINK (by Menger's theorem).

    The model is formulated as a maximum flow problem. Flow variables are created only for existing arcs using Mosel's `dynamic array` pattern with `exists()` and `create()`.

    **Sets:** $\text{NODES} = \{1, \ldots, 11\}$ (auto-sized from arc data); SOURCE $= 10$; SINK $= 11$

    **Parameters:** $\text{ARC}_{n,m}$ - 1 if a bidirectional link exists between nodes $n$ and $m$

    **Decision variables:** $\mathit{flow}_{n,m} \in \{0,1\}$ - 1 if flow uses arc $(n,m)$, created only for existing arcs

    $$
    \begin{align*}
    \text{maximize}   \quad & \sum_{n \in \text{NODES}} \mathit{flow}_{\text{SOURCE},n} \\
    \text{subject to} \quad & \sum_m \mathit{flow}_{m,n} = \sum_m \mathit{flow}_{n,m} \quad \forall\, n \notin \{\text{SOURCE}, \text{SINK}\} \\
                              & \sum_m \mathit{flow}_{n,m} \leq 1 \quad \forall\, n \notin \{\text{SOURCE}, \text{SINK}\}
    \end{align*}
    $$
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Define the arc set as a sparse Python dict. Only the upper-triangle arcs `(n,m)` with $n < m$ are provided; the Mosel model fills in the reverse direction internally using `ARC(m,n) := ARC(n,m)`. MoselPy reads this dict into a `dynamic array`, creating array entries only for the keys present.
    """)
    return


@app.cell
def _():
    # Upper-triangle arcs only (n < m). Model adds reverse direction.
    ARC = {
        (1,2):1,(1,3):1,(1,11):1,
        (2,3):1,(2,8):1,(2,9):1,
        (3,4):1,(3,9):1,(3,10):1,(3,11):1,
        (4,5):1,(4,6):1,(4,11):1,
        (5,9):1,(5,11):1,
        (6,7):1,(6,9):1,(6,10):1,
        (7,8):1,(7,10):1,
        (8,10):1,
        (9,10):1,
    }
    print(f"Network: 11 nodes, {len(ARC)} undirected links")
    print(f"Reliability question: can SOURCE(10) reach SINK(11) via 4+ vertex-disjoint paths?")
    return (ARC,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Use the single execution command. The `ARC` dict is passed as `input_data`; Mosel creates `flow` variables only for entries where `exists(ARC(n,m))` is true. After solving, `sol_flow` is a sparse dict containing only the arcs that were created (i.e. the 22 undirected links, represented as directed arcs in both directions).
    """)
    return


@app.cell
def _(ARC, MODELS, mp):
    _model, _output = mp.execute_model(f'{MODELS}/g1rely_p.mos', exec_params={'DATASOURCE': 'moselpy:', 'OUTFILE': 'moselpy:'}, input_data={'ARC': ARC})
    if _model.prob_status.is_solution_available:
        obj_val_g1 = _output['obj_val']
        sol_flow = _output['sol_flow']
        SOURCE, SINK = (10, 11)
        paths = []
        for start in range(1, 12):
            if sol_flow.get((SOURCE, start), 0) > 0.5:
                _path = [SOURCE, start]
                curr = start
                for _ in range(12):  # Reconstruct the 4 vertex-disjoint paths
                    if curr == SINK:
                        break
                    nxt = next((m for m in range(1, 12) if sol_flow.get((curr, m), 0) > 0.5), None)
                    if nxt is None:
                        break
                    _path.append(nxt)
                    curr = nxt
                paths.append(_path)
        reliable = obj_val_g1 >= 4
        print(f'Maximum vertex-disjoint paths from {SOURCE} to {SINK}: {obj_val_g1:.0f}')
        print(f'Network reliable (>= 4 paths): {reliable}')
        print()
        for _i, _path in enumerate(paths, 1):
            print(f'  Path {_i}: {' -> '.join((str(n) for n in _path))}')
    else:
        print(f'No solution found ({_model.prob_status})')
    return SINK, SOURCE, obj_val_g1, paths


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Network graph showing all 11 nodes and 22 links. The 4 vertex-disjoint paths from SOURCE (10) to SINK (11) are highlighted in distinct colors.
    """)
    return


@app.cell
def _(ARC, SINK, SOURCE, mo, mpatches, obj_val_g1, paths, plt):
    if 'paths' in locals():
        node_pos = {1: (1, 3), 2: (2, 4), 3: (2, 2), 4: (3, 3), 5: (4, 4), 6: (4, 2), 7: (5, 3), 8: (3, 5), 9: (3, 1), 10: (5, 2), 11: (0, 2)}
        path_colors = ['#E53935', '#1E88E5', '#43A047', '#FB8C00']
        path_edges = set()
        for _path in paths:
            for k in range(len(_path) - 1):
                path_edges.add((_path[k], _path[k + 1]))
        _fig, _ax = plt.subplots(figsize=(10, 6))
        all_arcs = set()
        for _n, _m in ARC:
            all_arcs.add((_n, _m))
            all_arcs.add((_m, _n))
        for _n, _m in all_arcs:
            if (_n, _m) not in path_edges:
                _x0, _y0 = node_pos[_n]
                _x1, _y1 = node_pos[_m]
                _ax.plot([_x0, _x1], [_y0, _y1], color='#CFD8DC', lw=1.5, zorder=1)
        for _i, _path in enumerate(paths):
            for k in range(len(_path) - 1):
                _n, _m = (_path[k], _path[k + 1])
                _x0, _y0 = node_pos[_n]
                _x1, _y1 = node_pos[_m]
                _ax.annotate('', xy=(_x1, _y1), xytext=(_x0, _y0), arrowprops=dict(arrowstyle='->', color=path_colors[_i], lw=2.5, connectionstyle='arc3,rad=0.1'))
        for node, (_x, _y) in node_pos.items():
            _color = '#E53935' if node == SOURCE else '#1E88E5' if node == SINK else '#90CAF9'
            _ax.scatter(_x, _y, s=500, color=_color, zorder=4, edgecolors='white', linewidths=1.5)
            _ax.text(_x, _y, str(node), ha='center', va='center', fontsize=9, fontweight='bold', color='white', zorder=5)
        _legend = [mpatches.Patch(color=path_colors[i], label=f'Path {i + 1}: {' -> '.join((str(n) for n in paths[i][:3]))}...') for i in range(len(paths))]
        _legend = _legend + [mpatches.Patch(color='#E53935', label='SOURCE (10)'), mpatches.Patch(color='#1E88E5', label='SINK (11)')]
        _ax.legend(handles=_legend, fontsize=8, loc='upper left')
        _ax.set_title(f'G-1 Network reliability: {obj_val_g1:.0f} vertex-disjoint paths (>= 4 required)')
        _ax.axis('off')
        plt.tight_layout()
        mo.output.append(plt.gcf())
    else:
        print('No solution available - skipping network chart')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## G-2 Mobile network dimensioning (MIP)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    *Applications Book Chapter G, Example 2*

    > **Mosel model:** [`g2dimens_p.mos`](https://github.com/fico-xpress/python-notebooks/blob/main/marimo/public/moselpy/models/telecomm/g2dimens_p.mos)

    A mobile phone network has 10 cells that must each be connected to a 5-node hub ring: 4 simple hubs (nodes 1-4) and one MTSO (node 5). Each cell must make a fixed number of connections to the ring, constrained by ring capacity. The model minimizes total connection cost.

    **Sets:** $\text{CELLS} = \{1, \ldots, 10\}$; $\text{NODES} = \{1, \ldots, 5\}$ (hubs 1-4 + MTSO 5)

    **Parameters:** $\text{COST}_{c,n}$ - cost to connect cell $c$ to node $n$; $\text{TRAF}_c$ - traffic from cell $c$; $\text{CNCT}_c$ - required connections; $\text{CAP}$ - ring segment capacity

    **Decision variables:** $\mathit{ifconnect}_{c,n} \in \{0,1\}$ - 1 if cell $c$ connected to node $n$

    $$
    \begin{align*}
    \text{minimize}   \quad & \sum_{c,n} \text{COST}_{c,n} \cdot \mathit{ifconnect}_{c,n} \\
    \text{subject to} \quad & \sum_n \mathit{ifconnect}_{c,n} = \text{CNCT}_c \quad \forall\, c \\
                              & \sum_{c,n \in \text{HUBS}} (\text{TRAF}_c / \text{CNCT}_c) \cdot \mathit{ifconnect}_{c,n} \leq 2 \cdot \text{CAP}
    \end{align*}
    $$
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Define the cost matrix as a `pd.DataFrame` with cells as rows (1..10) and nodes as columns (1..5). Passing a DataFrame lets MoselPy map rows and columns directly to the Mosel 2D array `COST(CELLS, NODES)`. Traffic, connection counts, and ring capacity are 1-indexed dicts.
    """)
    return


@app.cell
def _(pd):
    cost_rows = [
        [15, 8, 7,11,10],
        [ 9,11, 8, 5,14],
        [12, 6, 7,15,15],
        [17, 5, 9,18,24],
        [ 8,22,21,19, 6],
        [ 7,25,15, 9,17],
        [19,25,21,20,22],
        [20, 9,15,18,25],
        [21,22,14,16,20],
        [25,24,13, 4,11],
    ]
    COST_G2 = pd.DataFrame(cost_rows, index=range(1,11), columns=range(1,6))
    COST_G2.index.name   = "Cell"
    COST_G2.columns.name = "Node"

    TRAF = {i: v for i, v in enumerate([22,12,20,12,15,25,15,14, 8,22], 1)}
    CNCT = {i: v for i, v in enumerate([ 2, 2, 2, 2, 3, 1, 3, 2, 2, 2], 1)}
    CAP_G2 = 48

    print(f"Total traffic: {sum(TRAF.values())}  |  Ring capacity per segment: {CAP_G2}")
    print(f"Maximum ring load (2*CAP): {2*CAP_G2}")
    print(f"\nCost matrix (cells x nodes):")
    print(COST_G2.to_string())
    return CAP_G2, CNCT, COST_G2, TRAF, cost_rows


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Use the single execution command. `COST_G2` is passed as a DataFrame; MoselPy maps it to the Mosel 2D array. `CAP` is passed as a scalar via `input_data` to match the Mosel identifier name.
    """)
    return


@app.cell
def _(CAP_G2, CNCT, COST_G2, MODELS, TRAF, cost_rows, mp):
    _model, _output = mp.execute_model(f'{MODELS}/g2dimens_p.mos', exec_params={'DATASOURCE': 'moselpy:', 'OUTFILE': 'moselpy:'}, input_data={'COST': COST_G2, 'TRAF': TRAF, 'CNCT': CNCT, 'CAP': CAP_G2})
    if _model.prob_status.is_solution_available:
        obj_val_g2 = _output['obj_val']
        sol_ifconnect = _output['sol_ifconnect']
        assignment = {c: [n for n in range(1, 6) if sol_ifconnect.get((c, n), 0) > 0.5] for c in range(1, 11)}
        print(f'Minimum connection cost: {obj_val_g2:.0f}')
        total_ring = sum((TRAF[c] / CNCT[c] * (sol_ifconnect.get((c, n), 0) > 0.5) for c in range(1, 11) for n in range(1, 5)))
        print(f'Total ring traffic load: {total_ring:.1f} (limit: {2 * CAP_G2})')
        print()
        for _c in range(1, 11):
            nodes_str = ' '.join((str(n) for n in assignment[_c]))  # Build assignment: cell -> list of connected nodes
            cost_c = sum((cost_rows[_c - 1][n - 1] for n in assignment[_c]))
            print(f'  Cell {_c:>2} -> nodes [{nodes_str}]  cost={cost_c}')
    else:
        print(f'No solution found ({_model.prob_status})')
    return obj_val_g2, sol_ifconnect


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Grid showing which cells connect to which hub nodes. Each cell row shows its required number of connections (CNCT) as filled squares. Node 5 is the MTSO.
    """)
    return


@app.cell
def _(cost_rows, mo, mpatches, obj_val_g2, plt, sol_ifconnect):
    if 'assignment' in locals():
        _fig, _ax = plt.subplots(figsize=(8, 6))
        node_labels = {1: 'Hub 1', 2: 'Hub 2', 3: 'Hub 3', 4: 'Hub 4', 5: 'MTSO'}
        colors = {'Hub 1': '#1E88E5', 'Hub 2': '#43A047', 'Hub 3': '#FB8C00', 'Hub 4': '#8E24AA', 'MTSO': '#E53935'}
        for _c in range(1, 11):
            for _n in range(1, 6):
                connected = sol_ifconnect.get((_c, _n), 0) > 0.5
                _color = list(colors.values())[_n - 1] if connected else '#ECEFF1'
                rect = plt.Rectangle((_n - 1, 11 - _c), 1, 1, facecolor=_color, edgecolor='white', linewidth=2)
                _ax.add_patch(rect)
                if connected:
                    _ax.text(_n - 0.5, 11 - _c + 0.5, str(cost_rows[_c - 1][_n - 1]), ha='center', va='center', fontsize=8, color='white', fontweight='bold')
        _ax.set_xlim(0, 5)
        _ax.set_ylim(1, 11)
        _ax.set_xticks([0.5, 1.5, 2.5, 3.5, 4.5])
        _ax.set_xticklabels([node_labels[n] for n in range(1, 6)])
        _ax.set_yticks([i + 0.5 for i in range(1, 11)])
        _ax.set_yticklabels([f'Cell {11 - i}' for i in range(1, 11)])
        _ax.set_title(f'G-2 Cell-to-hub assignments (total cost={obj_val_g2:.0f})')
        _legend = [mpatches.Patch(color=c, label=l) for l, c in colors.items()]
        _ax.legend(handles=_legend, loc='lower right', fontsize=8)
        plt.tight_layout()
        mo.output.append(plt.gcf())
    else:
        print('No solution available - skipping assignment grid')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## G-3 Routing telephone calls (MIP)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    *Applications Book Chapter G, Example 3*

    > **Mosel model:** [`g3routing_p.mos`](https://github.com/fico-xpress/python-notebooks/blob/main/marimo/public/moselpy/models/telecomm/g3routing_p.mos)

    A private telephone network connects 5 French cities (Nantes, Nice, Paris, Troyes, Valenciennes) via 6 bidirectional arcs with known capacities. Five call demands between city pairs must be routed through the network. Each demand can be split across multiple paths. The model maximizes total routed traffic.

    The model reads data in two `initializations from` blocks: the first populates arc capacities, demands, and the path-to-demand mapping; the second reads the route definitions once the number of arcs (`NARC`) is known.

    **Sets:** $\text{CALLS}$ (city pairs, auto-populated from DEM); $\text{ARCS}$ (network links, auto-populated from CAP); $\text{PATHS} = \{1,\ldots,17\}$

    **Decision variables:** $\mathit{flow}_p \geq 0$ integer - calls routed on path $p$

    $$
    \begin{align*}
    \text{maximize}   \quad & \sum_{p} \mathit{flow}_p \\
    \text{subject to} \quad & \sum_{p:\, \text{CINDEX}_p = d} \mathit{flow}_p \leq \text{DEM}_d \quad \forall\, d \in \text{CALLS} \\
                              & \sum_{p,b:\, \text{ROUTE}_{p,b} = a} \mathit{flow}_p \leq \text{CAP}_a \quad \forall\, a \in \text{ARCS}
    \end{align*}
    $$
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Define arc capacities `CAP` and call demands `DEM` as string-keyed dicts. The `CINDEX` dict maps each path index to its demand pair. The route array `ROUTE` uses `(path, arc_position)` tuple keys; only non-empty positions need to be specified (Mosel string arrays default to `"\"`).
    """)
    return


@app.cell
def _():
    CAP = {
        "Nantes-Paris":300, "Nantes-Nice":120, "Paris-Nice":300,
        "Paris-Valenciennes":200, "Troyes-Nice":80, "Troyes-Valenciennes":70,
    }
    DEM = {
        "Nantes-Nice":100, "Nantes-Troyes":80, "Nantes-Valenciennes":75,
        "Nice-Valenciennes":100, "Paris-Troyes":70,
    }
    CINDEX = {
        1:"Nantes-Nice",   2:"Nantes-Nice",   3:"Nantes-Nice",
        4:"Nantes-Troyes", 5:"Nantes-Troyes", 6:"Nantes-Troyes", 7:"Nantes-Troyes",
        8:"Nantes-Valenciennes", 9:"Nantes-Valenciennes",
        10:"Nantes-Valenciennes",11:"Nantes-Valenciennes",
        12:"Nice-Valenciennes",  13:"Nice-Valenciennes", 14:"Nice-Valenciennes",
        15:"Paris-Troyes", 16:"Paris-Troyes", 17:"Paris-Troyes",
    }
    routes_raw = {
        1: ["Nantes-Nice"],
        2: ["Nantes-Paris","Paris-Nice"],
        3: ["Nantes-Paris","Paris-Valenciennes","Valenciennes-Troyes","Troyes-Nice"],
        4: ["Nantes-Paris","Paris-Valenciennes","Valenciennes-Troyes"],
        5: ["Nantes-Paris","Paris-Nice","Troyes-Nice"],
        6: ["Nantes-Nice","Troyes-Nice"],
        7: ["Nantes-Nice","Paris-Nice","Paris-Valenciennes","Valenciennes-Troyes"],
        8: ["Nantes-Paris","Paris-Valenciennes"],
        9: ["Nantes-Nice","Paris-Nice","Paris-Valenciennes"],
        10:["Nantes-Paris","Paris-Nice","Troyes-Nice","Valenciennes-Troyes"],
        11:["Nantes-Nice","Troyes-Nice","Valenciennes-Troyes"],
        12:["Nantes-Nice","Nantes-Paris","Paris-Valenciennes"],
        13:["Paris-Nice","Paris-Valenciennes"],
        14:["Troyes-Nice","Valenciennes-Troyes"],
        15:["Paris-Valenciennes","Valenciennes-Troyes"],
        16:["Nantes-Paris","Nantes-Nice","Troyes-Nice"],
        17:["Paris-Nice","Troyes-Nice"],
    }
    # Only non-empty (path, arc_position) entries needed - string arrays default to ""
    ROUTE = {(p, b+1): arc for p, arcs in routes_raw.items() for b, arc in enumerate(arcs)}

    print(f"Demands: {len(DEM)} city pairs  |  Arcs: {len(CAP)}  |  Paths: {len(routes_raw)}")
    print(f"Total demand: {sum(DEM.values())} calls")
    return CAP, CINDEX, DEM, ROUTE


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Use the compile-load-run sequence. The model reads data in two consecutive `initializations from "moselpy:"` blocks. Both blocks draw from the same `input_data` dict; the second block reads `ROUTE` after the model has computed `NARC = getsize(ARCS)` from the first block.
    """)
    return


@app.cell
def _(CAP, CINDEX, DEM, MODELS, ROUTE, mp):
    mp.compile_model(f'{MODELS}/g3routing_p.mos', f'{MODELS}/g3routing_p.bim')
    _model = mp.load_model(f'{MODELS}/g3routing_p.bim')
    _model.set_default_stream(mp.StreamType.OUTPUT, 'null:')
    _output = _model.run(exec_params={'DATASOURCE': 'moselpy:', 'OUTFILE': 'moselpy:'}, input_data={'CAP': CAP, 'DEM': DEM, 'CINDEX': CINDEX, 'ROUTE': ROUTE})
    if _model.prob_status.is_solution_available:
        obj_val_g3 = _output['obj_val']
        sol_flow_1 = _output['sol_flow']
        sol_route = _output['sol_route']
        print(f'Total routed calls: {obj_val_g3:.0f}  (total demand: {sum(DEM.values())})')
        print()
        for _demand, dem_val in sorted(DEM.items()):
            _routed = sum((sol_flow_1.get(p, 0) for p, d in CINDEX.items() if d == _demand))
            unmet = dem_val - _routed
            print(f'  {_demand:<25}  demand={dem_val:>3}  routed={_routed:.0f}' + (f'  UNMET={unmet:.0f}' if unmet > 0.5 else ''))
            for p in sorted((k for k, d in CINDEX.items() if d == _demand and sol_flow_1.get(k, 0) > 0.5)):
                arcs = [sol_route.get((p, b + 1), '') for b in range(6) if sol_route.get((p, b + 1), '')]
                print(f'    Path {p:>2}: {sol_flow_1[p]:.0f} calls via {' | '.join(arcs)}')
    else:
        print(f'No solution found ({_model.prob_status})')
    return obj_val_g3, sol_flow_1


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Bar chart comparing demand vs routed calls for each city pair. Unmet demand is shown as a lighter overlay.
    """)
    return


@app.cell
def _(CINDEX, DEM, mo, obj_val_g3, plt, sol_flow_1):
    if 'sol_flow' in locals():
        demands_list = sorted(DEM.keys())
        routed_vals = []
        unmet_vals = []
        for _demand in demands_list:
            _routed = sum((sol_flow_1.get(p, 0) for p, d in CINDEX.items() if d == _demand))
            routed_vals.append(_routed)
            unmet_vals.append(DEM[_demand] - _routed)
        _fig, _ax = plt.subplots(figsize=(10, 4))
        _x = range(len(demands_list))
        _ax.bar(_x, routed_vals, color='#1E88E5', edgecolor='white', label='Routed')
        _ax.bar(_x, unmet_vals, bottom=routed_vals, color='#FFCDD2', edgecolor='white', label='Unmet demand')
        for _i, (r, u) in enumerate(zip(routed_vals, unmet_vals)):
            _ax.text(_i, r / 2, f'{r:.0f}', ha='center', va='center', fontsize=9, color='white', fontweight='bold')
            if u > 0:
                _ax.text(_i, r + u / 2, f'-{u:.0f}', ha='center', va='center', fontsize=8, color='#C62828')
        _ax.set_xticks(_x)
        _ax.set_xticklabels([d.replace('-', '-\n') for d in demands_list], fontsize=8)
        _ax.set_ylabel('Calls')
        _ax.set_title(f'G-3 Telephone routing - total routed: {obj_val_g3:.0f} / {sum(DEM.values())}')
        _ax.legend()
        plt.tight_layout()
        mo.output.append(plt.gcf())
    else:
        print('No solution available - skipping routing chart')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## G-4 Cabled network (MIP)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    *Applications Book Chapter G, Example 4*

    > **Mosel model:** [`g4cable_p.mos`](https://github.com/fico-xpress/python-notebooks/blob/main/marimo/public/moselpy/models/telecomm/g4cable_p.mos)

    A university wants to connect 6 terminal buildings with underground cables. Cables must form a connected spanning tree (no closed loops). A simple degree constraint is insufficient to avoid sub-cycles, so each node is assigned a level variable used in additional linear constraints to enforce a spanning tree structure rooted at terminal 1.

    **Sets:** $\text{TERMINALS} = \{1, \ldots, 6\}$

    **Parameters:** $\text{DIST}_{s,t}$ - distance between terminals (meters)

    **Decision variables:** $\mathit{ifconnect}_{s,t} \in \{0,1\}$; $\mathit{level}_t \geq 0$

    $$
    \begin{align*}
    \text{minimize}   \quad & \sum_{s \neq t} \text{DIST}_{s,t} \cdot \mathit{ifconnect}_{s,t} \\
    \text{subject to} \quad & \sum_{s \neq t} \mathit{ifconnect}_{s,t} = 5 \quad (\text{spanning tree}) \\
                              & \sum_{t \neq s} \mathit{ifconnect}_{s,t} = 1 \quad \forall\, s \in \{2,\ldots,6\} \quad (\text{each non-root connects once}) \\
                              & \mathit{level}_t \geq \mathit{level}_s + 1 - 6 + 6 \cdot \mathit{ifconnect}_{s,t} \quad (\text{no sub-cycles})
    \end{align*}
    $$
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Define the 6x6 distance matrix as a Python dict with `(s,t)` tuple keys. The matrix is symmetric; all 30 off-diagonal entries are provided.
    """)
    return


@app.cell
def _(pd):
    dist_rows = [
        [  0, 120,  92, 265, 149, 194],
        [120,   0, 141, 170,  93, 164],
        [ 92, 141,   0, 218, 103, 116],
        [265, 170, 218,   0, 110, 126],
        [149,  93, 103, 110,   0,  72],
        [194, 164, 116, 126,  72,   0],
    ]
    DIST_G4 = {(i+1, j+1): dist_rows[i][j] for i in range(6) for j in range(6)}

    print("Distance matrix (meters):")
    dm = pd.DataFrame(dist_rows, index=range(1,7), columns=range(1,7))
    dm.index.name = dm.columns.name = "Terminal"
    print(dm.to_string())
    return DIST_G4, dist_rows


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Use the compile-load-run sequence. Before running the model, inspect its metadata using `model.name`, `model.version`, and `model.size` - these properties are available immediately after `load_model()` without executing the model.
    """)
    return


@app.cell
def _(DIST_G4, MODELS, dist_rows, mp):
    mp.compile_model(f'{MODELS}/g4cable_p.mos', f'{MODELS}/g4cable_p.bim')
    _model = mp.load_model(f'{MODELS}/g4cable_p.bim')
    _model.set_default_stream(mp.StreamType.OUTPUT, 'null:')
    print('Model metadata (before run):')
    print(f'  name:    {_model.name}')
    print(f'  version: {_model.version}')
    print(f'  size:    {_model.size:,} bytes')
    print()
    _output = _model.run(exec_params={'DATASOURCE': 'moselpy:', 'OUTFILE': 'moselpy:'}, input_data={'DIST': DIST_G4})
    if _model.prob_status.is_solution_available:
        obj_val_g4 = _output['obj_val']
        sol_ifconnect_1 = _output['sol_ifconnect']
        edges = [(s, t) for s in range(1, 7) for t in range(1, 7) if s != t and sol_ifconnect_1.get((s, t), 0) > 0.5]
        print(f'Minimum cable length: {obj_val_g4:.0f} meters')
        print(f'Connections (directed, rooted at terminal 1):')
        for _s, _t in sorted(edges):
            print(f'  Terminal {_s} -> Terminal {_t}  ({dist_rows[_s - 1][_t - 1]} m)')
    else:
        print(f'No solution found ({_model.prob_status})')
    return edges, obj_val_g4


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Spanning tree visualization. Terminals are arranged by distance from the root (terminal 1). Selected cable connections are shown as solid lines.
    """)
    return


@app.cell
def _(dist_rows, edges, mo, mpatches, obj_val_g4, plt):
    if 'edges' in locals():
        import math
        _fig, _ax = plt.subplots(figsize=(8, 6))
        tpos = {1: (3, 4), 2: (5, 3), 3: (2, 3), 4: (5, 1), 5: (4, 2), 6: (5, 2)}
        for _s in range(1, 7):  # Manual positions for a clear spanning tree layout
            for _t in range(_s + 1, 7):
                _x0, _y0 = tpos[_s]
                _x1, _y1 = tpos[_t]  # Draw all terminal pairs (light background)
                _ax.plot([_x0, _x1], [_y0, _y1], color='#ECEFF1', lw=1, zorder=1)
        for _s, _t in edges:
            _x0, _y0 = tpos[_s]
            _x1, _y1 = tpos[_t]
            _ax.plot([_x0, _x1], [_y0, _y1], color='#1E88E5', lw=3, zorder=2)
            mx, my = ((_x0 + _x1) / 2, (_y0 + _y1) / 2)  # Draw cable connections
            _ax.text(mx, my + 0.08, f'{dist_rows[_s - 1][_t - 1]}m', ha='center', va='bottom', fontsize=8, color='#1565C0')
        for _t, (_x, _y) in tpos.items():
            _color = '#E53935' if _t == 1 else '#43A047'
            _ax.scatter(_x, _y, s=500, color=_color, zorder=4, edgecolors='white', linewidths=2)
            _ax.text(_x, _y, str(_t), ha='center', va='center', fontsize=10, fontweight='bold', color='white', zorder=5)
        root_p = mpatches.Patch(color='#E53935', label='Root terminal (1)')
        term_p = mpatches.Patch(color='#43A047', label='Terminal')
        _ax.legend(handles=[root_p, term_p], fontsize=9)  # Draw terminals
        _ax.set_title(f'G-4 Cable network spanning tree - total length = {obj_val_g4:.0f} m')
        _ax.set_xlim(0.5, 6.5)
        _ax.set_ylim(0, 5)
        _ax.axis('off')
        plt.tight_layout()
        mo.output.append(plt.gcf())
    else:
        print('No solution available - skipping cable network chart')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## G-5 Satellite scheduling (iterative MIP)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    *Applications Book Chapter G, Example 5*

    > **Mosel model:** [`g5satell_p.mos`](https://github.com/fico-xpress/python-notebooks/blob/main/marimo/public/moselpy/models/telecomm/g5satell_p.mos)

    A satellite serves 4 U.S. transmitters and 4 European receivers. In each time slot (mode), each transmitter is paired with exactly one receiver. A mode duration equals the minimum traffic packet that can be served. The model uses the Gonzalez-Sahni algorithm: it transforms the traffic matrix into a quasi-bistochastic form, then iteratively solves a matching MIP to find the longest serviceable packet, updates the traffic matrix, and repeats until all traffic is served.

    The entire iterative algorithm runs inside a single Mosel model execution. MoselPy calls `execute_model()` once and receives the complete schedule as output.

    **Sets:** $\text{TRANSM} = \{1,\ldots,4\}$; $\text{RECV} = \{1,\ldots,4\}$; $\text{MODES}$ (dynamic range, grows per iteration)

    **Decision variables per iteration:** $\mathit{flow}_{t,r} \in \{0,1\}$ (transmitter-receiver pairing); $\mathit{pmin} \geq 0$ (mode duration)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Define the 4x4 traffic matrix `TRAF` as a dict with `(transmitter, receiver)` tuple keys. Traffic values represent units of data to be transmitted between each station pair.
    """)
    return


@app.cell
def _(pd):
    traf_raw = [
        [ 0,  7, 11, 15],
        [15,  8, 13,  9],
        [17, 12,  6, 10],
        [ 6, 13, 15,  4],
    ]
    TRAF_G5 = {(i+1, j+1): traf_raw[i][j] for i in range(4) for j in range(4)}

    traf_df = pd.DataFrame(traf_raw, index=[f"T{i+1}" for i in range(4)],
                           columns=[f"R{j+1}" for j in range(4)])
    traf_df.index.name = "Transmitter"
    traf_df.columns.name = "Receiver"
    print("Traffic matrix (units to transmit):")
    print(traf_df.to_string())
    print(f"Total traffic: {sum(traf_raw[i][j] for i in range(4) for j in range(4))}")
    return (TRAF_G5,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Use the context manager form of `mp.load_model()`. The iterative algorithm inside the Mosel model solves multiple MIP problems in a `while` loop, updating the traffic matrix after each mode until all traffic is scheduled. Python receives the complete schedule (mode durations and pairings) in a single `output` dict.
    """)
    return


@app.cell
def _(MODELS, TRAF_G5, mp):
    mp.compile_model(f'{MODELS}/g5satell_p.mos', f'{MODELS}/g5satell_p.bim')
    with mp.load_model(f'{MODELS}/g5satell_p.bim') as _model:
        _model.set_default_stream(mp.StreamType.OUTPUT, 'null:')
        _output = _model.run(exec_params={'DATASOURCE': 'moselpy:', 'OUTFILE': 'moselpy:'}, input_data={'TRAF': TRAF_G5})
        prob_ok = _model.prob_status.is_solution_available
    if prob_ok:
        obj_val_g5 = _output['obj_val']
        solpmin = _output['solpmin']
        solflowt = _output['solflowt']
        solflowr = _output['solflowr']
        nmodes = max((m for t, m in solflowr.keys()))
        schedule = {(t, m): int(solflowr.get((t, m), 0)) for t in range(1, 5) for m in range(1, nmodes + 1)}
        print(f'Total schedule duration: {obj_val_g5:.0f}')
        print(f'Number of modes: {nmodes}')
        print()
        print(f'{'Mode':>5}  {'Duration':>9}  {'T1->':>5}  {'T2->':>5}  {'T3->':>5}  {'T4->':>5}')
        _cumtime = 0
        for _m in range(1, nmodes + 1):
            _dur = int(solpmin.get(_m, 0))
            pairs = [f'R{schedule[t, _m]}' if schedule[t, _m] > 0 else '  -' for t in range(1, 5)]
            print(f'  {_m:>3}    {_cumtime:>4}-{_cumtime + _dur:<4}   {'  '.join(pairs)}')
            _cumtime = _cumtime + _dur
    else:
        print('No solution found')
    return nmodes, obj_val_g5, schedule, solpmin


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Gantt chart of the satellite schedule. Each row represents one transmitter; colored blocks show which receiver it is paired with in each mode. Block width is proportional to mode duration.
    """)
    return


@app.cell
def _(mo, mpatches, nmodes, obj_val_g5, plt, schedule, solpmin):
    if 'schedule' in locals():
        recv_colors = {1: '#1E88E5', 2: '#43A047', 3: '#FB8C00', 4: '#8E24AA'}
        _fig, _axes = plt.subplots(4, 1, figsize=(12, 6), sharex=True)
        for _t in range(1, 5):
            _ax = _axes[_t - 1]
            _cumtime = 0
            for _m in range(1, nmodes + 1):
                _dur = int(solpmin.get(_m, 0))
                recv = schedule[_t, _m]
                _color = recv_colors.get(recv, '#90CAF9')
                _ax.barh(0, _dur, left=_cumtime, height=0.7, color=_color, edgecolor='white')
                if _dur >= 2:
                    _ax.text(_cumtime + _dur / 2, 0, f'R{recv}', ha='center', va='center', fontsize=8, color='white', fontweight='bold')
                _cumtime = _cumtime + _dur
            _ax.set_yticks([0])
            _ax.set_yticklabels([f'T{_t}'], fontsize=9)
            _ax.set_xlim(0, obj_val_g5)
            _ax.axvline(obj_val_g5, color='#90A4AE', lw=1, linestyle='--')
        _axes[-1].set_xlabel('Time (data units)')
        _axes[0].set_title(f'G-5 Satellite schedule - total duration = {obj_val_g5:.0f}  ({nmodes} modes)')
        _legend = [mpatches.Patch(color=recv_colors[r], label=f'Receiver R{r}') for r in range(1, 5)]
        _fig.legend(handles=_legend, loc='lower right', ncol=4, fontsize=8)
        plt.tight_layout()
        mo.output.append(plt.gcf())
    else:
        print('No solution available - skipping Gantt chart')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## G-6 Transmitter placement (MIP)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    *Applications Book Chapter G, Example 6*

    > **Mosel model:** [`g6transmit_p.mos`](https://github.com/fico-xpress/python-notebooks/blob/main/marimo/public/moselpy/models/telecomm/g6transmit_p.mos)

    A mobile phone operator plans to equip an uncovered region. There are 7 candidate transmitter locations. Each location can cover a subset of 15 communities with known populations. Which transmitters should be built to maximize total population covered, subject to a budget constraint?

    The coverage data is sparse: only `(place, community)` pairs where `COVER(p,c) = 1` are specified; all other entries default to 0 in Mosel's dense array.

    **Sets:** $\text{PLACES} = \{1,\ldots,7\}$; $\text{COMMS} = \{1,\ldots,15\}$

    **Decision variables:** $\mathit{build}_p \in \{0,1\}$; $\mathit{covered}_c \in \{0,1\}$

    $$
    \begin{align*}
    \text{maximize}   \quad & \sum_c \text{POP}_c \cdot \mathit{covered}_c \\
    \text{subject to} \quad & \sum_p \text{COVER}_{p,c} \cdot \mathit{build}_p \geq \mathit{covered}_c \quad \forall\, c \\
                              & \sum_p \text{COST}_p \cdot \mathit{build}_p \leq \text{BUDGET}
    \end{align*}
    $$
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Define `COST` as a 1-indexed dict and `POP` as a 1-indexed dict. The `COVER` array is provided as a sparse dict with only the non-zero `(place, community)` entries. Mosel initializes the remaining 2D array entries to 0. `BUDGET` is an integer passed via `exec_params` to enable easy sensitivity analysis.
    """)
    return


@app.cell
def _():
    COST_G6 = {i: v for i, v in enumerate([1.8, 1.3, 4.0, 3.5, 3.8, 2.6, 2.1], 1)}
    POP_G6  = {i: v for i, v in enumerate([2,4,13,6,9,4,8,12,10,11,6,14,9,3,6], 1)}

    # Sparse coverage: only (place, community) pairs that equal 1
    cover_entries = [
        (1,1),(1,2),(1,4),
        (2,2),(2,3),(2,5),
        (3,4),(3,7),(3,8),(3,10),
        (4,5),(4,6),(4,8),(4,9),
        (5,8),(5,9),(5,12),
        (6,7),(6,10),(6,11),(6,12),(6,15),
        (7,12),(7,13),(7,14),(7,15),
    ]
    COVER_G6 = {(p,c): 1 for p,c in cover_entries}

    BUDGET_DEFAULT = 10

    total_pop = sum(POP_G6.values())
    print(f"Communities: 15  |  Candidate sites: 7  |  Total population: {total_pop}")
    print(f"Default budget: {BUDGET_DEFAULT}  |  Total cost if all built: {sum(COST_G6.values()):.1f}")
    return BUDGET_DEFAULT, COST_G6, COVER_G6, POP_G6, total_pop


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Sensitivity analysis: varying BUDGET

    Compile and load the model once. Run it multiple times with different `BUDGET` values via `exec_params`. Each run finds the maximum coverage achievable within the given budget. Results are collected into a `pd.Series` indexed by budget value.
    """)
    return


@app.cell
def _(BUDGET_DEFAULT, COST_G6, COVER_G6, MODELS, POP_G6, mp, pd):
    mp.compile_model(f'{MODELS}/g6transmit_p.mos', f'{MODELS}/g6transmit_p.bim')
    _model = mp.load_model(f'{MODELS}/g6transmit_p.bim')
    _model.set_default_stream(mp.StreamType.OUTPUT, 'null:')
    budget_values = [5, 6, 7, 8, 9, 10, 11, 12, 15]
    # Parametric run: vary BUDGET
    sensitivity = {}
    for budget in budget_values:
        out = _model.run(exec_params={'DATASOURCE': 'moselpy:', 'OUTFILE': 'moselpy:', 'BUDGET': budget}, input_data={'COST': COST_G6, 'COVER': COVER_G6, 'POP': POP_G6})
        if _model.prob_status.is_solution_available:
            sensitivity[budget] = out['obj_val']
        else:
            print(f'BUDGET={budget}: no solution ({_model.prob_status})')
    coverage_series = pd.Series(sensitivity, name='Population covered')
    coverage_series.index.name = 'Budget'
    print('Coverage sensitivity:')
    print(coverage_series.apply(lambda v: f'{v:.0f}').to_string())
    out_default = _model.run(exec_params={'DATASOURCE': 'moselpy:', 'OUTFILE': 'moselpy:', 'BUDGET': BUDGET_DEFAULT}, input_data={'COST': COST_G6, 'COVER': COVER_G6, 'POP': POP_G6})
    if _model.prob_status.is_solution_available:
        obj_val_g6 = out_default['obj_val']
        sol_build = out_default['sol_build']
        sol_covered = out_default['sol_covered']
        built_sites = [p for p in range(1, 8) if sol_build.get(p, 0) > 0.5]
        actual_cost = sum((COST_G6[p] for p in built_sites))
    # Best solution at default budget
        print()
        print(f'Default solution (budget={BUDGET_DEFAULT}): coverage={obj_val_g6:.0f}, sites={built_sites}, cost={actual_cost:.1f}')
    return coverage_series, obj_val_g6, sensitivity, sol_covered


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Two-panel visualization: (left) coverage sensitivity curve vs budget; (right) coverage breakdown at the default budget showing which communities are covered and which are not.
    """)
    return


@app.cell
def _(BUDGET_DEFAULT, POP_G6, coverage_series, mo, mpatches, obj_val_g6, plt, sensitivity, sol_covered, total_pop):
    if coverage_series is not None and (not coverage_series.empty):
        _fig, _axes = plt.subplots(1, 2, figsize=(13, 5))
        _ax = _axes[0]
        _ax.plot(coverage_series.index, coverage_series.values, marker='o', color='#1E88E5', linewidth=2)  # Left: sensitivity curve
        _ax.axvline(BUDGET_DEFAULT, color='#E53935', linestyle='--', lw=1.5, label=f'Default budget={BUDGET_DEFAULT}')
        _ax.axhline(total_pop, color='#90A4AE', linestyle=':', lw=1.5, label=f'Total population={total_pop}')
        for b, v in sensitivity.items():
            _ax.annotate(f'{v:.0f}', (b, v), textcoords='offset points', xytext=(0, 8), ha='center', fontsize=8)
        _ax.set_xlabel('Budget')
        _ax.set_ylabel('Population covered (thousands)')
        _ax.set_title('G-6 Transmitter placement - coverage sensitivity')
        _ax.legend(fontsize=8)
        ax2 = _axes[1]
        if 'sol_covered' in locals():
            pops = [POP_G6[c] for c in range(1, 16)]
            covered = [sol_covered.get(c, 0) > 0.5 for c in range(1, 16)]
            colors_c = ['#1E88E5' if cv else '#BDBDBD' for cv in covered]
            bars = ax2.bar(range(1, 16), pops, color=colors_c, edgecolor='white')
            ax2.set_xticks(range(1, 16))  # Right: community coverage at default budget
            ax2.set_xticklabels([f'C{c}' for c in range(1, 16)], fontsize=7)
            ax2.set_ylabel('Population (thousands)')
            ax2.set_title(f'Coverage at budget={BUDGET_DEFAULT}  ({obj_val_g6:.0f}/{total_pop}k covered)')
            cov_p = mpatches.Patch(color='#1E88E5', label='Covered')
            unc_p = mpatches.Patch(color='#BDBDBD', label='Not covered')
            ax2.legend(handles=[cov_p, unc_p], fontsize=8)
        plt.tight_layout()
        mo.output.append(plt.gcf())
    else:
        print('No results available - skipping transmitter charts')
    return


if __name__ == "__main__":
    app.run()
