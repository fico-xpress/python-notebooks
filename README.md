# FICO Xpress Python notebook examples

This repository contains Jupyter notebook examples for two complementary Python interfaces to FICO&reg; Xpress:

* **`xpress`** — the FICO&reg; Xpress Python API for building and solving optimization models directly in Python. Key features include:
  1. **Modeling**: Create and manipulate optimization models using Python objects, with operator overloading for constraints and objectives.
  2. **Integration with NumPy and SciPy**: Support for NumPy and SciPy sparse arrays for efficient large-scale model building.
  3. **Solving**: LP, MIP, QP and general NLP, with access to the full Xpress solver feature set.
  4. **Callbacks**: Custom callbacks to monitor or modify the solver's behavior during branch-and-bound.
  5. **[Examples](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/python/HTML/chExamples.html) and [Documentation](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/python/HTML)**

* **`moselpy`** — Python API for FICO&reg; Xpress Mosel, for compiling and running Mosel models from Python and exchanging data bidirectionally. Ideal for integrating existing Mosel models into Python data science workflows. See [moselpy on PyPI](https://pypi.org/project/moselpy/) and the [MoselPy User Guide and Reference Manual](https://www.fico.com/fico-xpress-optimization/docs/latest/mosel/MoselPy/dhtml).

## Contents

* [XpressPythonAPI](XpressPythonAPI.pdf): A slide deck with descriptions, examples and links for the most relevant API methods. 
* A [Youtube playlist](https://www.youtube.com/playlist?list=PL5Gy03AelO437-l8n4GyTwUbpZEIhJyDn) with several videos containing slides readouts and demos using Python notebooks is available. Links to individual videos are provided below.

### Basic examples of API usage

Example name | Description | Notes | Video
-------------|-------------|-------|------
[callback_newnode](basic_api_examples/callback_newnode.ipynb) | Using a callback function during the branch and bound search | | [Link](https://youtu.be/Ej75QhxTQYg?si=Ha8xCx3ItliNTxna&t=183)
[indicators](basic_api_examples/indicators.ipynb) | Using indicator constraints | | [Link](https://youtu.be/GPYZkf3J1Zk?si=YYL5jnHdClz7_APD&t=49)
[load_problem](basic_api_examples/load_problem.ipynb) | Comparison of model building performance between low-level and high-level methods | | [Link](https://youtu.be/z0YnDks8AJU?si=DUkQFIe80_RHHjV2&t=149)
[loadlp](basic_api_examples/loadlp.ipynb) | Using the low-level API function *loadLP()* | |
[logic_cons](basic_api_examples/logic_cons.ipynb) | Using general constraints for logical expressions | | [Link](https://youtu.be/HppWH2xS4ks?si=D2ddQD365Fb15xl2&t=146)
[modeling](basic_api_examples/modeling.ipynb) | Modeling a basic MIP problem | Requires Xpress version 9.9 or later | [Link](https://youtu.be/t9jvl9pCHOg?si=9arlsZFnqwvtBA85&t=291)
[multiobj_knapsack.ipynb](basic_api_examples/multiobj_knapsack.ipynb) | Multi-objective knapsack problem with blended and lexicographic approaches | |
[numpy_arrays](basic_api_examples/numpy_arrays.ipynb) | Using the numerical library *NumPy* | | [Link](https://youtu.be/JK4GqNp_h9E?si=BkWsZk1xPqK9JY4C&t=114)
[piecewise_linear](basic_api_examples/piecewise_linear.ipynb) | Using piecewise linear functions | | [Link](https://youtu.be/IefpyeLH8BE?si=eEIQmXhiD50n61yB&t=125)
[sos](basic_api_examples/sos.ipynb) | Defining Special Ordered Set (SOS) constraints | | [Link](https://youtu.be/zgK96WHroRI?si=UIw45GZrwl1twlRb&t=84)
[write_read](basic_api_examples/write_read.ipynb) | Writing and reading a problem file | | [Link](https://youtu.be/boZ4EbydWQ4?si=QG1JFfoyD-rwpqSu&t=62)

### Modeling examples

Example name | Description | Notes | Video
-------------|-------------|-------|------
[assignment](modeling_examples/assignment.ipynb) | One-to-one assignment of projects to persons to maximize the overall preference level | |
[bin_packing](modeling_examples/bin_packing.ipynb) | Pack items into bins to minimize the number of bins used | Showcases the use of the `xp.Dot` operator |
[campaign_polars](modeling_examples/campaign_polars.ipynb) | Campaign conversion optimization to maximize expected value subject to budget and channel capacity constraints | Showcases the use of Polars dataframes to generate aggregate expressions |
[circle_packing](modeling_examples/circle_packing.ipynb) | Place $N$ disjoint circles in the unit square with Xpress Global | |
[diagnose_infeasible](modeling_examples/diagnose_infeasible.ipynb) | Diagnosing infeasible problems using IIS (Irreducible Infeasible Sets) | Includes a reusable helper function. Requires Xpress version 9.9 or later | |
[diagnose_unbounded](modeling_examples/diagnose_unbounded.ipynb) | Diagnosing unbounded LP problems using primal rays | Includes a reusable helper function |
[facility_location](modeling_examples/facility_location.ipynb) | A basic facility location problem | Requires Xpress version 9.9 or later |
[firestation_scipy](modeling_examples/firestation_scipy.ipynb) | Using a SciPy sparse matrix formulation to model the fire station location problem | |
[inscribed_square](modeling_examples/inscribed_square.ipynb) | Inscribed square problem solved with Xpress NonLinear or Xpress Global | To run Xpress NonLinear with Knitro, a Knitro license is required. | [Link](https://youtu.be/kOmJ1NltlnY?si=C7AZKQjR8xiA7VBs&t=86)
[markowitz_multiobj](modeling_examples/markowitz_multiobj.ipynb) | Multi-objective formulation of Markowitz portfolio optimization problem | | [Link](https://youtu.be/DkEmAyCttyA?si=pUeOItR7YQ1QO8Qy&t=192)
[max_flow](modeling_examples/max_flow.ipynb) | Finding the maximum number of vertex-disjoint paths between two nodes in a telecommunications network | |
[n_queens](modeling_examples/n_queens.ipynb) | The problem of placing $n$ queens on a chessboard | |
[pairwise_distance](modeling_examples/pairwise_distance.ipynb) | Determine the positions of $N$ points in $D$-dimensional space | Interactive 3D visualization |
[portfolio_pandas](modeling_examples/portfolio_pandas.ipynb) | Showcases the use of Pandas operations to generate expressions and constraints for a portfolio selection problem | Requires Xpress version 9.8 or later |
[sudoku](modeling_examples/sudoku.ipynb) | Solving a Sudoku problem | |
[tsp_callbacks](modeling_examples/tsp_callbacks.ipynb) | Solving a TSP problem using callbacks | This example requires a full license of the FICO&reg; Xpress Optimizer. |
[unitcommitment_indicators](modeling_examples/unitcommitment_indicators.ipynb) | Unit commitment problem formulation with indicator constraints | |

### MoselPy examples

[MoselPy](https://pypi.org/project/moselpy/) is a Python API for FICO&reg; Xpress Mosel. These notebooks show how to compile and run Mosel models from Python, exchange data bidirectionally, and integrate Mosel optimization into Python data workflows. They are based on examples from the book *Applications of Optimization with Xpress-MP* (Dash Associates, 2002). The original Mosel models are available at [examples.xpress.fico.com](https://examples.xpress.fico.com/example.pl#mosel_app).

> **Requirements:** `pip install moselpy mosellibs xpresslibs` - install all three packages to get the Mosel runtime and solver libraries. No local Xpress installation is needed to run these notebooks. A local FICO&reg; Xpress installation is recommended if you want access to the full set of examples, user guides and documentation, solver libraries, and Xpress Workbench. Obtain one via the [FICO&reg; Xpress community license](https://www.fico.com/en/fico-xpress-community-license) page. If a local installation is present, set `XPRESSDIR` before starting Jupyter to use it instead of the bundled libraries.

Example name | Description | Highlighted Features
------------- | ------------- | -------
[intro](moselpy_examples/intro.ipynb) | Introductory examples (Chapters 1-5): LP, MIP, knapsack and pricebreak discount models | Single execution command vs compile-load-run sequence, `exec_params`, `input_data`, OUTFILE pattern, `find_identifier`, visualizations
[mining_process](moselpy_examples/mining_process.ipynb) | Mining and process industries (Chapter A): alloy blending, food production, refinery, sugar, opencast mining, electricity dispatch | Pandas Series/DataFrame input, `find_identifier(use_pandas=True)`, multi-panel dashboards, sensitivity analysis
[scheduling_sequencing](moselpy_examples/scheduling_sequencing.ipynb) | Scheduling and Sequencing (Chapter B): stadium construction, flowshop, jobshop, sequencing, painting, line balancing | Model introspection, context manager, `pd.DataFrame` input, `find_identifier` + `unstack`, `StringIO` output capture, iterative solving
[production_planning](moselpy_examples/production_planning.ipynb) | Production planning (Chapter C): bicycle, glassware, toys, components, fiber, assignment | Parametric scan with `pd.Series`, sensitivity heatmap, binary I/O, infeasibility detection
[loading_cutting_stock](moselpy_examples/loading_cutting_stock.ipynb) | Loading and cutting stock (Chapter D): wagon load balancing, ship loading, tank filling, bin packing, sheet and bar cutting | `model.export_problem`, warm-start via `addmipsol`, parametric variant and objective selection, `pd.DataFrame` 2D input
[ground_transport](moselpy_examples/ground_transport.ipynb) | Ground transport (Chapter E): car rental fleet management, min-cost flow, depot location, heating oil delivery, combined transport, van rental | `copy.deepcopy` for scenario cloning, sparse dict input, `model.stop()` with threading, `exec_params` sensitivity analysis
[air_transport](moselpy_examples/air_transport.ipynb) | Air transport and logistics (Chapter F): flight connection planning, crew composition, landing scheduling, hub network design, tour planning with subtour elimination | Dynamic set computation with `finalize`, sequential multi-objective MIP, model introspection (`model.name`, `model.version`, `model.size`), context manager (`with mp.load_model`)
[telecomm](moselpy_examples/telecomm.ipynb) | Telecommunications network design (Chapter G): network reliability (max flow), mobile network dimensioning, telephone call routing, cable network design, satellite scheduling, transmitter placement | Dynamic sparse arrays with `exists()` and `create()`, `pd.DataFrame` 2D cost input, two consecutive `initializations from` blocks, context manager with iterative in-Mosel algorithm, `exec_params` parametric sensitivity loop
[economics_finance](moselpy_examples/economics_finance.ipynb) | Economics and finance (Chapter H): loan selection, publicity planning, portfolio composition, retirement funding, family budgeting, company expansion, mean-variance portfolio | String-keyed dict auto-populates `set of string`, `set of integer` passed from Python, LP relaxation via `XPRS_LIN` flag, `mmnl` module for quadratic objectives, efficient frontier parametric loop
[timetabling_personnel](moselpy_examples/timetabling_personnel.ipynb) | Timetabling and personnel scheduling (Chapter I): worker assignment, nurse scheduling, school timetabling, exam scheduling, production planning with transfers, construction site staffing | Two sequential solves in one call, named `linctr` constraints reassigned between solves, dynamic arrays with `exists()` and `create()`, feasibility solve with `minimize(0)`, 3D array result reconstructed as weekly grid
[public_services](moselpy_examples/public_services.ipynb) | Public services and utilities (Chapter J): water supply max flow, CCTV camera placement, electoral redistricting, road gritting circuits, tax office location, hospital DEA efficiency | `ARCS: range` auto-populated from arc data, in-Mosel preprocessing before solve (district enumeration, Floyd-Warshall), Eulerian circuit extracted inside Mosel, `linctr` loop for DEA, `exec_params` sensitivity on office count

## Documentation and other examples

* [Python Interface Reference Manual](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/python/HTML)
* [Xpress Python examples](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/python/HTML/chExamples.html)
* [MoselPy User Guide and Reference Manual](https://www.fico.com/fico-xpress-optimization/docs/latest/mosel/MoselPy/dhtml)

## Running the examples using GitHub codespaces

1. **Open Codespaces and create a codespace**:
   - Click on the **"Code"** (green) button on this [repository page](https://github.com/fico-xpress/python-notebooks).
   - On the **"Codespaces"** tab, select **"Create a Codespace on main"**. This will set up a cloud-based development environment for you.

2. **Open Python Notebook**:
   - Once the Codespace is created and the environment is ready (wait for the README preview to appear), you can open a Python notebook.
   - Navigate to a notebook file (with a `.ipynb` extension) within the Codespace.
   - Click on the notebook file to open it in the Jupyter interface.

3. **Run the Notebook**:
   - Run a code cell in the Python notebook as you would normally do in a local environment.
   - When running for the first time, select "Install/Enable suggested extensions: Python + Jupyter" as suggested in the pop-up window at the top of the screen.
   - After installation, select the installed Python environment and wait for the code cell to be executed. You are all set to run all the code cells.

## Legal and license requirements

The examples in this repository are licensed under the Apache License, Version 2.0. You may not use these files except in compliance with the License. You may obtain a copy of the License at [http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0), or see [LICENSE](LICENSE) for the full license text. Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

The examples use FICO&reg; Xpress software. By running them, you agree to the Community License terms of the [Xpress Shrinkwrap License Agreement](https://www.fico.com/en/shrinkwrap-license-agreement-fico-xpress-optimization-suite-on-premises) with respect to the FICO&reg; Xpress software. See the [licensing options](https://www.fico.com/en/fico-xpress-trial-and-licensing-options) overview for additional details and information about obtaining a paid license.
