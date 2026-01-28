# FICO Xpress Python notebook examples

The FICO&reg; Xpress Python interface is a powerful tool for optimization modeling and solving. It allows users to leverage the capabilities of the FICO&reg; Xpress Solver directly within Python. Here are some key features:

1. **Modeling**: You can create and manipulate optimization models using Python objects. This includes defining variables, constraints, and objective functions. It allows creating constraints and objectives using expressions with operator overloading.
2. **Integration with NumPy and SciPy**: The interface supports the use of NumPy and SciPy sparse arrays, making it easier and more efficient to handle large datasets and perform numerical operations.
3. **Solving**: It provides functions to solve various types of optimization problems, including linear programming (LP), mixed-integer programming (MIP), quadratic programming (QP) and (general) nonlinear programming (NLP), and access to the full set of solver features available with Xpress.
4. **Callbacks**: Users can implement custom callbacks to interact with the optimization process, such as monitoring progress or modifying the solver's behavior.
5. **[Examples](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/python/HTML/chExamples.html) and [Documentation](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/python/HTML)**: The interface comes with extensive examples and documentation to help users get started and explore advanced features.

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
[modeling](basic_api_examples/modeling.ipynb) | Modeling a basic MIP problem | | [Link](https://youtu.be/t9jvl9pCHOg?si=9arlsZFnqwvtBA85&t=291)
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
[facility_location](modeling_examples/facility_location.ipynb) | A basic facility location problem | |
[firestation_scipy](modeling_examples/firestation_scipy.ipynb) | Using a SciPy sparse matrix formulation to model the fire station location problem | |
[inscribed_square](modeling_examples/inscribed_square.ipynb) | Inscribed square problem solved with Xpress NonLinear or Xpress Global | To run Xpress NonLinear with Knitro, a Knitro license is required. | [Link](https://youtu.be/kOmJ1NltlnY?si=C7AZKQjR8xiA7VBs&t=86)
[markowitz_multiobj](modeling_examples/markowitz_multiobj.ipynb) | Multi-objective formulation of Markowitz portfolio optimization problem | | [Link](https://youtu.be/DkEmAyCttyA?si=pUeOItR7YQ1QO8Qy&t=192)
[max_flow](modeling_examples/max_flow.ipynb) | Finding the maximum number of vertex-disjoint paths between two nodes in a telecommunications network | |
[n_queens](modeling_examples/n_queens.ipynb) | The problem of placing $n$ queens on a chessboard | |
[pairwise_distance](modeling_examples/pairwise_distance.ipynb) | Determine the positions of $N$ points in $D$-dimensional space | Interactive 3D visualization |
[portfolio_pandas](modeling_examples/portfolio_pandas.ipynb) | Showcases the use of Pandas operations to generate expressions and constraints for a portfolio selection problem | Requires Xpress version 9.8 or later, and a Pandas version < 3.0 |
[sudoku](modeling_examples/sudoku.ipynb) | Solving a Sudoku problem | |
[tsp_callbacks](modeling_examples/tsp_callbacks.ipynb) | Solving a TSP problem using callbacks | This example requires a full license of the FICO&reg; Xpress Optimizer. |
[unitcommitment_indicators](modeling_examples/unitcommitment_indicators.ipynb) | Unit commitment problem formulation with indicator constraints | |

## Documentation and other examples

* [Python Interface Reference Manual](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/python/HTML)
* [Xpress Python examples](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/python/HTML/chExamples.html)

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

## Legal

See source code files for copyright notices.

## License


The examples in this repository are licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for the full license text. The examples use FICO&reg; Xpress software. By running it, you agree to the Community License terms of the [Xpress Shrinkwrap License Agreement](https://www.fico.com/en/shrinkwrap-license-agreement-fico-xpress-optimization-suite-on-premises) with respect to the FICO&reg; Xpress software. See the [licensing options](https://www.fico.com/en/fico-xpress-trial-and-licensing-options) overview for additional details and information about obtaining a paid license.
