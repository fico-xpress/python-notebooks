# /// script
# [tool.marimo.opengraph]
# title = "MoselPy: Timetabling"
# description = "Nurses, schools, exams, staffing"
# image = "__marimo__/thumbnail-moselpy-timetabling.svg"
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
    # **FICO&reg; Xpress MoselPy - Chapter I: Timetabling and Personnel**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ***moselpy_timetabling_personnel.py*** - Timetabling and personnel scheduling problems from the Xpress Applications Book - worker assignment, nurse scheduling, school timetabling, exam scheduling, production planning with transfers, and construction site staffing, solved with MoselPy.

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
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import numpy as np
    import pandas as pd

    _root = mo.notebook_dir() / "public" / "moselpy"
    MODELS = str(_root / "models" / "timetabling_personnel")
    DATA   = str(_root / "data" / "timetabling_personnel")

    print(f"MoselPy {mp.version}  |  Mosel {mp.mosel_version}  |  Xpress {mp.xpress_version}")
    mp.config.set_default_stream(mp.StreamType.OUTPUT, "null:")
    return MODELS, mp, np, pd, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Timetabling and personnel scheduling problems
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    This notebook covers six IP examples from Chapter I of the Xpress Applications Book, solved via [MoselPy](https://pypi.org/project/moselpy/). Examples include worker-to-machine assignment, nurse scheduling with cyclic shifts, school timetabling, exam scheduling, production planning with personnel transfers, and construction site staffing.

    > **Mosel source files:** [`models/timetabling_personnel/`](https://github.com/fico-xpress/python-notebooks/tree/main/marimo/public/moselpy/models/timetabling_personnel) &nbsp;|&nbsp; **Data files:** [`data/timetabling_personnel/`](https://github.com/fico-xpress/python-notebooks/tree/main/marimo/public/moselpy/data/timetabling_personnel)

    > **Requirements:** `pip install moselpy mosellibs xpresslibs` - `mosellibs` provides the Mosel runtime and `xpresslibs` the Xpress solver libraries. No local Xpress installation is needed to run these notebooks, as long as the packages with libraries have been installed.

    > A local FICO&reg; Xpress installation is recommended if you want access to the full set of examples, user guides and documentation, solver libraries, and Xpress Workbench. Obtain one via the [FICO&reg; Xpress community license](https://www.fico.com/en/fico-xpress-community-license) page. If a local installation is present, set `XPRESSDIR` before starting marimo to use it instead of the `mosellibs` and `xpresslibs` packages.

    > **MoselPy documentation:** [MoselPy User Guide and Reference Manual](https://www.fico.com/fico-xpress-optimization/docs/latest/mosel/MoselPy/dhtml)

    > **Mosel examples on the web:** [examples.xpress.fico.com](https://examples.xpress.fico.com/example.pl?id=mosel_app_9)

    ### MoselPy features demonstrated in this chapter

    - **Two sequential solves in one call**: the model solves LP relaxation then MIP (I-1), or solves with then without a constraint (I-2, I-5), returning all results from a single `execute_model`.
    - **Named `linctr` constraints reassigned between solves**: `Load` in I-5 and `Period` in I-2 are redefined in-place without rebuilding the model.
    - **Dynamic arrays with `exists()` and `create()`**: transfer variables created only for permitted line pairs (I-5).
    - **Feasibility solve**: `minimize(0)` finds any feasible timetable; `is_solution_available` confirms feasibility (I-4).
    - **3D array result from Python**: `sol_teach` indexed by (teacher, class, slot) reconstructed as a weekly grid (I-3).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## I-1 Personnel assignment (IP)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    *Applications Book Chapter I, Example 1*

    > **Mosel model:** [`i1assign_p.mos`](https://github.com/fico-xpress/python-notebooks/blob/main/marimo/public/moselpy/models/timetabling_personnel/i1assign_p.mos)

    Six operators must each be assigned to one of six machines in a workshop. Two objectives are considered: (1) **parallel machines** - maximize total productivity across all assignments; (2) **serial machines** - maximize the bottleneck (minimum) productivity, since overall throughput is limited by the slowest assignment.

    The model solves both problems in sequence: the LP relaxation of the parallel problem is solved first (which happens to produce integer values due to total unimodularity), then binary constraints and the bottleneck variable are added for the serial solve.

    **Sets:** $\text{PERS} = 1..6$, $\text{MACH} = 1..6$

    **Parameters:** $\text{OUTP}_{p,m}$ - productivity of person $p$ on machine $m$

    **Decision variables:** $\mathit{assign}_{p,m} \in \{0,1\}$ - 1 if person $p$ assigned to machine $m$; $\mathit{pmin}$ - minimum productivity (serial problem only)

    $$
    \begin{align*}
    \text{(parallel)} \quad \text{maximize} \quad & \sum_{p,m} \text{OUTP}_{p,m} \cdot \mathit{assign}_{p,m} \\
    \text{(serial)}   \quad \text{maximize} \quad & \mathit{pmin} \\
    \text{subject to} \quad & \sum_m \mathit{assign}_{p,m} = 1 \quad \forall\, p \\
                              & \sum_p \mathit{assign}_{p,m} = 1 \quad \forall\, m \\
                              & \sum_m \text{OUTP}_{p,m} \cdot \mathit{assign}_{p,m} \geq \mathit{pmin} \quad \forall\, p \quad \text{(serial only)}
    \end{align*}
    $$
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Define the 6x6 productivity matrix as a dict with `(person, machine)` tuple keys.
    """)
    return


@app.cell
def _(pd):
    OUTP = {
        (1,1):13,(1,2):24,(1,3):31,(1,4):19,(1,5):40,(1,6):29,
        (2,1):18,(2,2):25,(2,3):30,(2,4):15,(2,5):43,(2,6):22,
        (3,1):20,(3,2):20,(3,3):27,(3,4):25,(3,5):34,(3,6):33,
        (4,1):23,(4,2):26,(4,3):28,(4,4):18,(4,5):37,(4,6):30,
        (5,1):28,(5,2):33,(5,3):34,(5,4):17,(5,5):38,(5,6):20,
        (6,1):19,(6,2):36,(6,3):25,(6,4):27,(6,5):45,(6,6):24,
    }

    outp_df = pd.DataFrame(
        {f"M{m}": [OUTP[(p,m)] for p in range(1,7)] for m in range(1,7)},
        index=[f"P{p}" for p in range(1,7)],
    )
    outp_df.index.name = "Person"
    print("Productivity matrix (person x machine):")
    print(outp_df.to_string())
    return (OUTP,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Use the single execution command. The model solves both the parallel and serial problems in a single call, returning `obj_parallel`, `obj_serial`, `par_sol`, and `ser_sol` (each a dict with `(person, machine)` keys).
    """)
    return


@app.cell
def _(MODELS, OUTP, mp):
    model, _output = mp.execute_model(f'{MODELS}/i1assign_p.mos', exec_params={'DATASOURCE': 'moselpy:', 'OUTFILE': 'moselpy:'}, input_data={'OUTP': OUTP})
    if model.prob_status.is_solution_available:
        obj_par = _output['obj_parallel']
        obj_ser = _output['obj_serial']
        par_sol = _output['par_sol']
        ser_sol = _output['ser_sol']
        outp_out = _output['OUTP']
        print(f'Parallel machines - total productivity: {obj_par:.0f}')
        for _p in range(1, 7):
            _m = next((m for m in range(1, 7) if par_sol.get((_p, m), 0) > 0.5))
            print(f'  Person {_p} -> Machine {_m}  ({OUTP[_p, _m]})')
        print(f'\nSerial machines - bottleneck productivity: {obj_ser:.0f}')
        for _p in range(1, 7):
            _m = next((m for m in range(1, 7) if ser_sol.get((_p, m), 0) > 0.5))
            print(f'  Person {_p} -> Machine {_m}  ({OUTP[_p, _m]})')
    else:
        print(f'No solution found ({model.prob_status})')
    return obj_par, obj_ser, par_sol, ser_sol


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Side-by-side assignment matrices showing which person operates which machine for the parallel and serial solutions. Cell colour reflects productivity.
    """)
    return


@app.cell
def _(OUTP, mo, np, obj_par, obj_ser, par_sol, plt, ser_sol):
    if 'par_sol' in locals():
        _fig, _axes = plt.subplots(1, 2, figsize=(12, 4))
        for _ax, sol, _title in [(_axes[0], par_sol, f'I-1 Parallel (total={obj_par:.0f})'), (_axes[1], ser_sol, f'I-1 Serial (bottleneck={obj_ser:.0f})')]:
            matrix = np.array([[OUTP[p, m] * (sol.get((p, m), 0) > 0.5) for m in range(1, 7)] for p in range(1, 7)])
            _im = _ax.imshow(matrix, cmap='Blues', aspect='auto')
            plt.colorbar(_im, ax=_ax, label='Productivity')
            _ax.set_xticks(range(6))
            _ax.set_xticklabels([f'M{m}' for m in range(1, 7)])
            _ax.set_yticks(range(6))
            _ax.set_yticklabels([f'P{p}' for p in range(1, 7)])
            for _p in range(6):
                for _m in range(6):
                    if matrix[_p, _m] > 0:
                        _ax.text(_m, _p, str(matrix[_p, _m]), ha='center', va='center', fontsize=9, color='white')
            _ax.set_title(_title)
        plt.tight_layout()
        mo.output.append(plt.gcf())
    else:
        print('No solution available - skipping assignment chart')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## I-2 Nurse scheduling (IP)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    *Applications Book Chapter I, Example 2*

    > **Mosel model:** [`i2nurse_p.mos`](https://github.com/fico-xpress/python-notebooks/blob/main/marimo/public/moselpy/models/timetabling_personnel/i2nurse_p.mos)

    A hospital schedules nurses across 12 two-hour periods in a day. Nurses work 8 consecutive hours (4 periods) with a 2-hour break after 6 hours; they may start in any period. The model first minimizes total nurse headcount. A second variant caps the total at 80 nurses and minimizes overtime (nurses who extend shifts into an adjacent period).

    The demand constraints are modeled as named `linctr` objects (`Period`) which are reassigned in-place when extending the model for overtime, without removing and recreating constraints.

    **Sets:** $\text{PERIODS} = \{0..11\}$, $\text{WORK} = \{0,-1,-3,-4\}$

    **Decision variables:** $\mathit{start}_t \in \mathbb{Z}_{\geq 0}$ - nurses starting in period $t$; $\mathit{overt}_t$ - nurses working overtime in period $t$ (variant 2)

    $$
    \begin{align*}
    \text{(v1)} \quad \text{minimize} \quad & \sum_t \mathit{start}_t \\
    \text{subject to} \quad & \sum_{i \in \text{WORK}} \mathit{start}_{(t+i) \bmod 12} \geq \text{REQ}_t \quad \forall\, t
    \end{align*}
    $$
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Define hourly nurse requirements as a 0-indexed dict. The second variant's staff cap is set via `exec_params`.
    """)
    return


@app.cell
def _():
    REQ = {0: 15, 1: 15, 2: 15, 3: 35, 4: 40, 5: 40, 6: 35, 7: 30, 8: 30, 9: 35, 10: 30, 11: 20}
    NUM = 80  # staff cap for variant 2
    period_labels = [f'{t * 2:02d}:00' for t in range(12)]
    print('Nurse requirements per 2-hour period:')
    for _t in range(12):
        print(f'  {period_labels[_t]}-{(_t + 1) * 2:02d}:00: {REQ[_t]:>3} nurses required')
    return NUM, REQ, period_labels


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Use the compile-load-run sequence to allow rerunning with different `NUM` values. The model solves both variants in a single `run()` call, returning results for minimum headcount (`obj_total`, `sol_start1`) and minimum overtime (`obj_overt`, `sol_start2`, `sol_overt`).

    Named `linctr` constraints (`Period`) are redefined inside the model between the two solves - this is a key Mosel capability for progressively tightening or modifying a formulation without starting over.
    """)
    return


@app.cell
def _(MODELS, NUM, REQ, mp, period_labels):
    mp.compile_model(f'{MODELS}/i2nurse_p.mos', f'{MODELS}/i2nurse_p.bim')
    model_1 = mp.load_model(f'{MODELS}/i2nurse_p.bim')
    model_1.set_default_stream(mp.StreamType.OUTPUT, 'null:')
    _output = model_1.run(exec_params={'DATASOURCE': 'moselpy:', 'OUTFILE': 'moselpy:', 'NUM': NUM}, input_data={'REQ': REQ})
    if model_1.prob_status.is_solution_available:
        obj_total = _output['obj_total']
        obj_overt = _output['obj_overt']
        sol_start1 = _output['sol_start1']
        sol_start2 = _output['sol_start2']
        sol_overt = _output['sol_overt']
        print(f'Variant 1 - minimum total nurses: {obj_total:.0f}')
        print(f'Variant 2 - overtime nurses (cap={NUM}): {obj_overt:.0f}')
        print()
        print(f'{'Period':<12} {'Req':>4} {'Start v1':>9} {'Start v2':>9} {'Overtime':>9}')
        for _t in range(12):
            _s1 = round(sol_start1.get(_t, 0))
            _s2 = round(sol_start2.get(_t, 0))
            _ov = round(sol_overt.get(_t, 0))
            print(f'  {period_labels[_t]:<10} {REQ[_t]:>4} {_s1:>9} {_s2:>9} {_ov:>9}')
    else:
        print(f'No solution found ({model_1.prob_status})')
    return obj_overt, obj_total, sol_overt, sol_start1, sol_start2


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Two-panel chart for both variants. Bars show nurses *starting* their shift in each period; these are always lower than the requirement because a single nurse covers 4 consecutive periods (at offsets 0, 1, 3, 4 from start time). The orange line shows total *active* nurses per period (summing starters at those offsets), which meets or exceeds the red requirement line at every period.
    """)
    return


@app.cell
def _(NUM, REQ, mo, obj_overt, obj_total, period_labels, plt, sol_overt, sol_start1, sol_start2):
    if 'sol_start1' in locals():
        _s1 = [round(sol_start1.get(t, 0)) for t in range(12)]
        _s2 = [round(sol_start2.get(t, 0)) for t in range(12)]
        _ov = [round(sol_overt.get(t, 0)) for t in range(12)]
        req = [REQ[t] for t in range(12)]
        offsets = [0, -1, -3, -4]
        active1 = [sum((_s1[(t + o) % 12] for o in offsets)) for t in range(12)]  # Active nurses per period: sum of starters at offsets {0,-1,-3,-4}
        active2 = [sum((_s2[(t + o) % 12] + _ov[(t + o) % 12] for o in offsets)) for t in range(12)]
        _fig, _axes = plt.subplots(1, 2, figsize=(13, 4))
        for _ax, starts, overt_vals, active, _title in [(_axes[0], _s1, [0] * 12, active1, f'Variant 1 (total={obj_total:.0f})'), (_axes[1], _s2, _ov, active2, f'Variant 2 (overtime={obj_overt:.0f}, cap={NUM})')]:
            _ax.bar(range(12), starts, color='#1E88E5', label='Nurses starting', edgecolor='white')
            _ax.bar(range(12), overt_vals, bottom=starts, color='#FB8C00', label='Overtime', edgecolor='white')
            _ax.step(range(12), req, where='mid', color='#E53935', linewidth=2, label='Requirement')
            _ax.step(range(12), active, where='mid', color='#FB8C00', linewidth=2, linestyle='--', label='Active nurses')
            _ax.set_xticks(range(12))
            _ax.set_xticklabels(period_labels, rotation=45, ha='right', fontsize=7)
            _ax.set_ylabel('Nurses')
            _ax.set_title(f'I-2 Nurse scheduling - {_title}')
            _ax.legend(fontsize=8)
        plt.tight_layout()
        mo.output.append(plt.gcf())
    else:
        print('No solution available - skipping nurse schedule chart')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## I-3 School timetable (IP)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    *Applications Book Chapter I, Example 3*

    > **Mosel model:** [`i3school_p.mos`](https://github.com/fico-xpress/python-notebooks/blob/main/marimo/public/moselpy/models/timetabling_personnel/i3school_p.mos)

    A weekly timetable must be determined for two classes sharing nine teachers. Teachers have specific lesson counts per class and subject. The objective minimizes 'holes' - courses scheduled at the start or end of a day, which leave gaps in the students' timetable. Several hard constraints encode specific scheduling requirements (sport on Thursday afternoon, no Monday morning lessons, etc.).

    **Sets:** $\text{TEACHERS}$ (9 teachers, auto-populated), $\text{CLASS} = \{1,2\}$, $\text{SLOTS} = 1..20$ (5 days x 4 periods)

    **Parameters:** $\text{COURSE}_{t,c}$ - lessons teacher $t$ must give to class $c$

    **Decision variables:** $\mathit{teach}_{t,c,l} \in \{0,1\}$ - 1 if teacher $t$ gives class $c$ in slot $l$
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Define the lesson counts as a dict with `(teacher_name, class)` tuple keys. The `TEACHERS` set of strings auto-populates from the dict keys. The slot structure uses 4 periods per day across 5 days (slots 1-4 = Monday, 5-8 = Tuesday, ..., 17-20 = Friday).
    """)
    return


@app.cell
def _():
    COURSE = {
        ("Mr Cheese",    1): 1, ("Mr Cheese",    2): 1,
        ("Mrs Insulin",  1): 3, ("Mrs Insulin",  2): 3,
        ("Mr Map",       1): 2, ("Mr Map",       2): 2,
        ("Mr Effofecks", 1): 0, ("Mr Effofecks", 2): 4,
        ("Mrs Derivate", 1): 4, ("Mrs Derivate", 2): 0,
        ("Mrs Electron", 1): 3, ("Mrs Electron", 2): 3,
        ("Mr Wise",      1): 1, ("Mr Wise",      2): 1,
        ("Mr Muscle",    1): 1, ("Mr Muscle",    2): 0,
        ("Mrs Biceps",   1): 0, ("Mrs Biceps",   2): 1,
    }
    TEACHERS = sorted({t for (t, _) in COURSE})
    NP, ND = 4, 5  # periods per day, days per week
    DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri"]

    total_lessons = {c: sum(COURSE.get((t,c),0) for t in TEACHERS) for c in [1,2]}
    print(f"Total lessons: Class 1 = {total_lessons[1]}, Class 2 = {total_lessons[2]}")
    print(f"Slots = {NP} periods/day x {ND} days = {NP*ND} total")
    return COURSE, DAY_NAMES, ND, NP, TEACHERS


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Use the single execution command. `COURSE` is the only required input; the `TEACHERS` set auto-populates from the dict keys. The result `sol_teach` is a dict with `(teacher, class, slot)` keys.
    """)
    return


@app.cell
def _(COURSE, DAY_NAMES, MODELS, ND, NP, TEACHERS, mp):
    model_2, _output = mp.execute_model(f'{MODELS}/i3school_p.mos', exec_params={'DATASOURCE': 'moselpy:', 'OUTFILE': 'moselpy:'}, input_data={'COURSE': COURSE})
    if model_2.prob_status.is_solution_available:
        obj_val_i3 = _output['obj_val']
        sol_teach = _output['sol_teach']
        print(f'Courses at start/end of day (holes): {obj_val_i3:.0f}')
        print()
        for _cls in [1, 2]:
            print(f'Class {_cls} timetable:')
            for _d in range(ND):
                day_slots = range(_d * NP + 1, (_d + 1) * NP + 1)
                assigned = {}
                for _l in day_slots:
                    for _t in TEACHERS:
                        if sol_teach.get((_t, _cls, _l), 0) > 0.5:
                            assigned[_l] = _t
                slot_strs = [f'  {assigned.get(l, '(free)'):<18}' for l in day_slots]
                print(f'  {DAY_NAMES[_d]}: {''.join(slot_strs)}')
            print()
    else:
        print(f'No solution found ({model_2.prob_status})')
    return obj_val_i3, sol_teach


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Timetable grid for each class: rows = days, columns = periods. Colored cells show which teacher is assigned; empty cells are free periods.
    """)
    return


@app.cell
def _(DAY_NAMES, ND, NP, TEACHERS, mo, np, obj_val_i3, plt, sol_teach):
    if 'sol_teach' in locals():
        teacher_colors = {t: plt.cm.tab20(i / len(TEACHERS)) for i, t in enumerate(sorted(TEACHERS))}
        _fig, _axes = plt.subplots(1, 2, figsize=(14, 5))
        for _cls, _ax in enumerate([_axes[0], _axes[1]], start=1):
            grid = np.zeros((ND, NP))
            annotations = [['' for _ in range(NP)] for _ in range(ND)]
            cell_colors = [['white' for _ in range(NP)] for _ in range(ND)]
            for _d in range(ND):
                for _p in range(NP):
                    _l = _d * NP + _p + 1
                    for _t in TEACHERS:
                        if sol_teach.get((_t, _cls, _l), 0) > 0.5:
                            annotations[_d][_p] = _t.split()[-1]
                            cell_colors[_d][_p] = teacher_colors[_t]
            _ax.set_xlim(0, NP)
            _ax.set_ylim(0, ND)  # last name only
            _ax.set_xticks(range(NP))
            _ax.set_xticklabels([f'P{p + 1}' for p in range(NP)])
            _ax.set_yticks(range(ND))
            _ax.set_yticklabels(DAY_NAMES)
            _ax.invert_yaxis()
            for _d in range(ND):
                for _p in range(NP):
                    color = cell_colors[_d][_p]
                    _ax.add_patch(plt.Rectangle((_p, _d), 1, 1, color=color, alpha=0.8))
                    if annotations[_d][_p]:
                        _ax.text(_p + 0.5, _d + 0.5, annotations[_d][_p], ha='center', va='center', fontsize=7, fontweight='bold')
            _ax.set_title(f'I-3 Class {_cls} timetable (holes={obj_val_i3:.0f})')
            _ax.grid(True, color='gray', linewidth=0.5)
        plt.tight_layout()
        mo.output.append(plt.gcf())
    else:
        print('No solution available - skipping timetable chart')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## I-4 Exam scheduling (IP, feasibility)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    *Applications Book Chapter I, Example 4*

    > **Mosel model:** [`i4exam_p.mos`](https://github.com/fico-xpress/python-notebooks/blob/main/marimo/public/moselpy/models/timetabling_personnel/i4exam_p.mos)

    Eleven exams must be scheduled across 8 time slots for fourth-year students. Students taking certain pairs of exams cannot have them in the same slot (incompatibility constraints). Since any valid schedule is acceptable, there is no objective - the model finds a feasible assignment by minimizing 0.

    This demonstrates how to use MoselPy for **feasibility problems**: `model.prob_status.is_solution_available` is checked (not `is_solution_optimal`) since there is no meaningful objective value to verify.

    **Sets:** $\text{EXAM}$ (11 exams, auto-populated from `INCOMP`), $\text{TIME} = 1..8$

    **Parameters:** $\text{INCOMP}_{d,e}$ - 1 if exams $d$ and $e$ cannot be in the same slot

    **Decision variables:** $\mathit{plan}_{e,t} \in \{0,1\}$ - 1 if exam $e$ scheduled in slot $t$
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Define the incompatibility matrix as a dict with `(exam1, exam2)` string tuple keys. The `EXAM` set auto-populates from the dict keys. Only entries equal to 1 need to be listed; missing entries default to 0.
    """)
    return


@app.cell
def _():
    EXAM_NAMES = ["DA","NA","C++","SE","PM","J","GMA","LP","MP","S","DSE"]

    incomp_pairs = [
        ("DA","NA"),("DA","PM"),("DA","GMA"),("DA","S"),("DA","DSE"),
        ("NA","DA"),("NA","PM"),("NA","GMA"),("NA","S"),("NA","DSE"),
        ("C++","SE"),("C++","PM"),("C++","J"),("C++","GMA"),("C++","MP"),("C++","S"),("C++","DSE"),
        ("SE","C++"),("SE","PM"),("SE","J"),("SE","GMA"),("SE","S"),("SE","DSE"),
        ("PM","DA"),("PM","NA"),("PM","C++"),("PM","SE"),("PM","J"),
        ("PM","GMA"),("PM","LP"),("PM","MP"),("PM","S"),("PM","DSE"),
        ("J","C++"),("J","SE"),("J","PM"),("J","GMA"),("J","MP"),("J","S"),("J","DSE"),
        ("GMA","DA"),("GMA","NA"),("GMA","C++"),("GMA","SE"),("GMA","PM"),
        ("GMA","J"),("GMA","LP"),("GMA","MP"),("GMA","S"),("GMA","DSE"),
        ("LP","PM"),("LP","GMA"),("LP","S"),("LP","DSE"),
        ("MP","C++"),("MP","PM"),("MP","J"),("MP","GMA"),("MP","S"),("MP","DSE"),
        ("S","DA"),("S","NA"),("S","C++"),("S","SE"),("S","PM"),
        ("S","J"),("S","GMA"),("S","LP"),("S","MP"),("S","DSE"),
        ("DSE","DA"),("DSE","NA"),("DSE","C++"),("DSE","SE"),("DSE","PM"),
        ("DSE","J"),("DSE","GMA"),("DSE","LP"),("DSE","MP"),("DSE","S"),
    ]
    INCOMP = {pair: 1 for pair in incomp_pairs}

    print(f"Exams to schedule: {EXAM_NAMES}")
    print(f"Incompatibility pairs: {len(incomp_pairs)}")
    print(f"Available time slots: 8")
    return (INCOMP,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Use the single execution command. Since the objective is 0 (feasibility), `is_solution_available` is the relevant check - `is_solution_optimal` would also be true since minimizing 0 trivially achieves optimality. `sol_plan` maps `(exam, slot)` pairs to binary values.
    """)
    return


@app.cell
def _(INCOMP, MODELS, mp):
    model_3, _output = mp.execute_model(f'{MODELS}/i4exam_p.mos', exec_params={'DATASOURCE': 'moselpy:', 'OUTFILE': 'moselpy:'}, input_data={'INCOMP': INCOMP})
    if model_3.prob_status.is_solution_available:
        sol_plan = _output['sol_plan']
        _slot_of = {e: t for (e, t), v in sol_plan.items() if v > 0.5}
        print(f'Feasible exam schedule found:')
        print()
        for _t in range(1, 9):
            exams_in_slot = sorted((e for e, s in _slot_of.items() if s == _t))
            print(f'  Slot {_t}: {(', '.join(exams_in_slot) if exams_in_slot else '(empty)')}')
        violations = [(d, e) for (d, e), v in INCOMP.items() if v == 1 and _slot_of.get(d) == _slot_of.get(e)]
        print(f'\nIncompatibility violations: {len(violations)} (should be 0)')
    else:
        print(f'No feasible schedule found ({model_3.prob_status})')
    return model_3, sol_plan


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Slot assignment chart showing which exams are scheduled in each slot, with the incompatibility graph summarized as a heatmap.
    """)
    return


@app.cell
def _(INCOMP, mo, model_3, np, plt, sol_plan):
    if 'sol_plan' in locals() and model_3.prob_status.is_solution_available:
        _slot_of = {e: t for (e, t), v in sol_plan.items() if v > 0.5}
        exams_sorted = sorted(_slot_of.keys())
        _fig, _axes = plt.subplots(1, 2, figsize=(13, 4))
        _ax = _axes[0]
        colors_slot = plt.cm.Set3(np.linspace(0, 1, 8))
        for e in exams_sorted:
            _t = _slot_of.get(e, 0) - 1
            _ax.barh(e, 1, left=_t, color=colors_slot[_t], edgecolor='white', height=0.6)
            _ax.text(_t + 0.5, e, str(_t + 1), ha='center', va='center', fontsize=8)
        _ax.set_xlim(0, 8)
        _ax.set_xticks(range(8))
        _ax.set_xticklabels([f'Slot {t}' for t in range(1, 9)], fontsize=8)
        _ax.set_title('I-4 Exam schedule')
        _ax2 = _axes[1]
        n = len(exams_sorted)
        incomp_matrix = np.array([[INCOMP.get((d, e), 0) for e in exams_sorted] for d in exams_sorted])
        _im = _ax2.imshow(incomp_matrix, cmap='Reds', aspect='auto')
        _ax2.set_xticks(range(n))
        _ax2.set_xticklabels(exams_sorted, rotation=45, ha='right', fontsize=7)
        _ax2.set_yticks(range(n))
        _ax2.set_yticklabels(exams_sorted, fontsize=7)
        _ax2.set_title('Incompatibility matrix')
        plt.tight_layout()
        mo.output.append(plt.gcf())
    else:
        print('No solution available - skipping exam chart')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## I-5 Production planning with personnel (LP)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    *Applications Book Chapter I, Example 5*

    > **Mosel model:** [`i5pplan_p.mos`](https://github.com/fico-xpress/python-notebooks/blob/main/marimo/public/moselpy/models/timetabling_personnel/i5pplan_p.mos)

    A company produces four products on five production lines. Processing times and line capacities are known. In a first solve, no transfers are allowed. In a second solve, working hours can be transferred between certain line pairs (up to a maximum per line). Maximize total profit in both cases.

    Transfer variables are created via `create()` only for permitted line pairs (dynamic array). Named `linctr` constraints (`Load`) are reassigned in-place to replace fixed-capacity limits with effective-hours limits, without removing the existing constraints.

    **Sets:** $\text{PRODS} = 1..4$, $\text{LINES} = 1..5$

    **Parameters:** $\text{DUR}_{p,l}$, $\text{CAP}_l$, $\text{PROFIT}_p$, $\text{TRANSF}_{k,l}$, $\text{TMAX}_l$

    **Decision variables:** $\mathit{produce}_p \geq 0$; $\mathit{hours}_l \geq 0$; $\mathit{transfer}_{k,l} \geq 0$ (if permitted)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Define the duration matrix, capacities, and profits as 1-indexed dicts. `TRANSF` is a sparse dict indicating which transfers are allowed (only entries with value 1 are needed). `TMAX` caps outgoing transfers per line.
    """)
    return


@app.cell
def _():
    dur_raw = [[1.3, 0.9, 2.0, 0.3, 0.9], [1.8, 1.7, 1.4, 0.6, 1.1], [1.3, 1.2, 1.3, 1.0, 1.4], [0.9, 1.1, 1.0, 0.9, 1.0]]
    DUR = {(p + 1, l + 1): dur_raw[p][l] for p in range(4) for l in range(5)}
    CAP = {1: 4500, 2: 5000, 3: 4500, 4: 1500, 5: 2500}
    PROFIT = {1: 7, 2: 8, 3: 9, 4: 7}
    TRANSF = {(1, 2): 1, (1, 3): 1, (1, 4): 1, (2, 3): 1, (2, 5): 1, (3, 1): 1, (3, 2): 1, (3, 4): 1, (4, 5): 1, (5, 1): 1, (5, 2): 1, (5, 3): 1}
    TMAX = {1: 400, 2: 800, 3: 200, 4: 500, 5: 300}
    print('Permitted transfer routes:')
    for _k, _l in sorted(TRANSF):
        print(f'  Line {_k} -> Line {_l}  (max from line {_k}: {TMAX[_k]} hrs)')
    return CAP, DUR, PROFIT, TMAX, TRANSF


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Use the compile-load-run sequence to allow running with different capacities. The model solves both variants in a single call. `Load` constraints are redefined in-place inside the Mosel model between the two solves: this is a key feature for extending a model without re-specifying all constraints.
    """)
    return


@app.cell
def _(CAP, DUR, MODELS, PROFIT, TMAX, TRANSF, mp):
    mp.compile_model(f'{MODELS}/i5pplan_p.mos', f'{MODELS}/i5pplan_p.bim')
    model_4 = mp.load_model(f'{MODELS}/i5pplan_p.bim')
    model_4.set_default_stream(mp.StreamType.OUTPUT, 'null:')
    _output = model_4.run(exec_params={'DATASOURCE': 'moselpy:', 'OUTFILE': 'moselpy:'}, input_data={'PROFIT': PROFIT, 'DUR': DUR, 'CAP': CAP, 'TRANSF': TRANSF, 'TMAX': TMAX})
    if model_4.prob_status.is_solution_available:
        obj_notrans = _output['obj_notrans']
        obj_trans = _output['obj_trans']
        sol_produce1 = _output['sol_produce1']
        sol_produce2 = _output['sol_produce2']
        sol_transfer = _output['sol_transfer']
        print(f'Without transfers: total profit = {obj_notrans:,.1f}')
        for _p in range(1, 5):
            print(f'  Product {_p}: {sol_produce1.get(_p, 0):,.2f} units')
        print(f'\nWith transfers: total profit = {obj_trans:,.1f}  (+{obj_trans - obj_notrans:,.1f})')
        for _p in range(1, 5):
            print(f'  Product {_p}: {sol_produce2.get(_p, 0):,.2f} units')
        active_transfers = {(k, l): v for (k, l), v in sol_transfer.items() if v > 0.01}
        if active_transfers:
            print('\nHours transferred:')
            for (_k, _l), v in sorted(active_transfers.items()):
                print(f'  Line {_k} -> Line {_l}: {v:,.1f} hrs')
    else:
        print(f'No solution found ({model_4.prob_status})')
    return obj_notrans, obj_trans, sol_produce1, sol_produce2, sol_transfer


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Side-by-side comparison of production volumes without and with personnel transfers, plus a transfer flow diagram.
    """)
    return


@app.cell
def _(mo, np, obj_notrans, obj_trans, plt, sol_produce1, sol_produce2, sol_transfer):
    if 'sol_produce1' in locals():
        _fig, _axes = plt.subplots(1, 2, figsize=(12, 4))
        _ax = _axes[0]
        x = np.arange(4)  # Left: production comparison
        p1 = [sol_produce1.get(p, 0) for p in range(1, 5)]
        p2 = [sol_produce2.get(p, 0) for p in range(1, 5)]
        _ax.bar(x - 0.2, p1, 0.35, label=f'No transfer ({obj_notrans:,.0f})', color='#90CAF9', edgecolor='white')
        _ax.bar(x + 0.2, p2, 0.35, label=f'With transfer ({obj_trans:,.0f})', color='#1E88E5', edgecolor='white')
        _ax.set_xticks(x)
        _ax.set_xticklabels([f'Product {p}' for p in range(1, 5)])
        _ax.set_ylabel('Units produced')
        _ax.set_title('I-5 Production planning')
        _ax.legend(fontsize=8)
        _ax2 = _axes[1]
        active_t = {(k, l): v for (k, l), v in sol_transfer.items() if v > 0.01}
        lines_with_flow = sorted(set((k for k, l in active_t)) | set((l for k, l in active_t)))
        if active_t:
            labels_t = [f'L{k}->L{l}' for k, l in sorted(active_t)]  # Right: transfer flows
            values_t = [active_t[k, l] for k, l in sorted(active_t)]
            _ax2.barh(labels_t, values_t, color='#43A047', edgecolor='white')
            _ax2.set_xlabel('Hours transferred')
            _ax2.set_title('I-5 Working hours transferred')
        else:
            _ax2.text(0.5, 0.5, 'No transfers active', ha='center', va='center', transform=_ax2.transAxes)
            _ax2.set_title('I-5 Working hours transferred')
        plt.tight_layout()
        mo.output.append(plt.gcf())
    else:
        print('No solution available - skipping production chart')
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## I-6 Construction site personnel planning (IP)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    *Applications Book Chapter I, Example 6*

    > **Mosel model:** [`i6build_p.mos`](https://github.com/fico-xpress/python-notebooks/blob/main/marimo/public/moselpy/models/timetabling_personnel/i6build_p.mos)

    A company plans its workforce at a construction site over 6 months (March to August). Workers may arrive from other sites (up to 3 per month) or depart (up to 1/3 of current staff). Overstaffing and understaffing each carry a penalty cost per worker per month. The target is to end at the same staff level as the start. Minimize total cost.

    **Sets:** $\text{MONTHS} = \{3..8\}$ (March to August)

    **Parameters:** $\text{REQ}_m$, $\text{CARR}$, $\text{CLEAVE}$, $\text{COVER}$, $\text{CUNDER}$, $\text{NSTART}$, $\text{NFINAL}$

    **Decision variables:** $\mathit{onsite}_m$, $\mathit{arrive}_m$, $\mathit{leave}_m$, $\mathit{over}_m$, $\mathit{under}_m \in \mathbb{Z}_{\geq 0}$

    $$
    \begin{align*}
    \text{minimize} \quad & \sum_m (\text{CARR} \cdot \mathit{arrive}_m + \text{CLEAVE} \cdot \mathit{leave}_m + \text{COVER} \cdot \mathit{over}_m + \text{CUNDER} \cdot \mathit{under}_m)
    \end{align*}
    $$
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Define the monthly worker requirements and all cost/staffing parameters as Python scalars and dicts. The planning horizon is months 3-8 (March to August).
    """)
    return


@app.cell
def _():
    MONTH_NAMES = {3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug'}
    REQ_1 = {3: 4, 4: 6, 5: 7, 6: 4, 7: 6, 8: 2}
    CARR = 100
    CLEAVE = 160
    COVER = 200
    CUNDER = 200
    NSTART = 3
    NFINAL = 3
    print('Monthly requirements:')
    for _m, name in MONTH_NAMES.items():
        print(f'  {name}: {REQ_1[_m]} workers required')
    print(f'\nStart/end: {NSTART}/{NFINAL} workers')
    print(f'Costs: arrive={CARR}, leave={CLEAVE}, over={COVER}, under={CUNDER}')
    return CARR, CLEAVE, COVER, CUNDER, MONTH_NAMES, NFINAL, NSTART, REQ_1


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Use the single execution command. All staffing data is passed via `input_data`. The planning horizon endpoints (`FIRST=3`, `LAST=8`) use the model defaults; they can be overridden via `exec_params` for different scenarios.
    """)
    return


@app.cell
def _(
    CARR,
    CLEAVE,
    COVER,
    CUNDER,
    MODELS,
    MONTH_NAMES,
    NFINAL,
    NSTART,
    REQ_1,
    mp,
):
    model_5, _output = mp.execute_model(f'{MODELS}/i6build_p.mos', exec_params={'DATASOURCE': 'moselpy:', 'OUTFILE': 'moselpy:'}, input_data={'REQ': REQ_1, 'CARR': CARR, 'CLEAVE': CLEAVE, 'COVER': COVER, 'CUNDER': CUNDER, 'NSTART': NSTART, 'NFINAL': NFINAL})
    if model_5.prob_status.is_solution_available:
        obj_val_i6 = _output['obj_val']
        sol_onsite = _output['sol_onsite']
        sol_arrive = _output['sol_arrive']
        sol_leave = _output['sol_leave']
        sol_over = _output['sol_over']
        sol_under = _output['sol_under']
        print(f'Total staffing cost: {obj_val_i6:,.0f}')
        print()
        print(f'{'Month':<6} {'Req':>4} {'OnSite':>7} {'Arrive':>7} {'Leave':>7} {'Over':>5} {'Under':>6}')
        for _m in range(3, 9):
            print(f'  {MONTH_NAMES[_m]:<4} {REQ_1[_m]:>4} {round(sol_onsite.get(_m, 0)):>7} {round(sol_arrive.get(_m, 0)):>7} {round(sol_leave.get(_m, 0)):>7} {round(sol_over.get(_m, 0)):>5} {round(sol_under.get(_m, 0)):>6}')
    else:
        print(f'No solution found ({model_5.prob_status})')
    return obj_val_i6, sol_arrive, sol_leave, sol_onsite, sol_over, sol_under


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Staffing timeline showing workers on site each month (blue) with overstaffing (orange) stacked on top and the monthly requirement (red line). Note that the requirement is a *soft* target: understaffing is permitted by the model but penalized (cost `CUNDER` per worker per month). Months where `onsite < REQ` are shown with a hatched gap; this is the deliberate optimizer trade-off when the cost of extra arrivals or delayed departures exceeds the understaffing penalty.
    """)
    return


@app.cell
def _(MONTH_NAMES, REQ_1, mo, obj_val_i6, plt, sol_arrive, sol_leave, sol_onsite, sol_over, sol_under):
    if 'sol_onsite' in locals():
        months = list(range(3, 9))
        names = [MONTH_NAMES[m] for m in months]
        on_site = [round(sol_onsite.get(m, 0)) for m in months]
        arrives = [round(sol_arrive.get(m, 0)) for m in months]
        leaves = [round(sol_leave.get(m, 0)) for m in months]
        overs = [round(sol_over.get(m, 0)) for m in months]
        unders = [round(sol_under.get(m, 0)) for m in months]
        reqs = [REQ_1[m] for m in months]
        _fig, _ax = plt.subplots(figsize=(9, 4))
        _ax.bar(names, on_site, color='#1E88E5', label='On site', edgecolor='white')
        _ax.bar(names, overs, bottom=on_site, color='#FB8C00', label='Overstaffing (+penalty)', edgecolor='white', alpha=0.8)
        for i, (s, r, u) in enumerate(zip(on_site, reqs, unders)):
            if u > 0:
                _ax.bar(names[i], u, bottom=s, color='#E53935', alpha=0.4, hatch='///', edgecolor='#E53935', linewidth=0.5, label='Understaffing (+penalty)' if i == 0 else '')
        _ax.step(range(6), reqs, where='mid', color='#E53935', linewidth=2, label='Requirement (soft)')
        for i, _m in enumerate(months):
            a, _l = (arrives[i], leaves[i])
            if a > 0:
                _ax.annotate(f'+{a}', (i, on_site[i] / 2), ha='center', va='center', fontsize=8, color='white', fontweight='bold')
            if _l > 0:
                _ax.annotate(f'-{_l}', (i, on_site[i] + 0.2), ha='center', va='bottom', fontsize=8, color='#555')
        _ax.set_xticks(range(6))
        _ax.set_xticklabels(names)
        _ax.set_ylabel('Workers')
        _ax.set_title(f'I-6 Construction site staffing (cost={obj_val_i6:,.0f})')
        _ax.legend(fontsize=8)
        plt.tight_layout()
        mo.output.append(plt.gcf())
    else:
        print('No solution available - skipping staffing chart')
    return


if __name__ == "__main__":
    app.run()
