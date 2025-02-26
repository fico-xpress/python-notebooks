# FICO Xpress Python notebook examples

The FICO&reg; Xpress Python interface is a powerful tool for optimization modeling and solving. It allows users to leverage the capabilities of the FICO&reg; Xpress Solver directly within Python. Here are some key features:

1. **Modeling**: You can create and manipulate optimization models using Python objects. This includes defining variables, constraints, and objective functions. It allows creating constraints and objectives using expressions with operator overloading.
2. **Integration with NumPy and SciPy**: The interface supports the use of NumPy and SciPy sparse arrays, making it easier and more efficient to handle large datasets and perform numerical operations.
3. **Solving**: It provides functions to solve various types of optimization problems, including linear programming (LP), mixed-integer programming (MIP), quadratic programming (QP) and (general) nonlinear programming (NLP), and access to the full set of solver features available with Xpress.
4. **Callbacks**: Users can implement custom callbacks to interact with the optimization process, such as monitoring progress or modifying the solver's behavior.
5. **[Examples](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/python/HTML/chExamples.html) and [Documentation](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/python/HTML)**: The interface comes with extensive examples and documentation to help users get started and explore advanced features.

## Contents

### Basic examples of API usage

Example name | Description | Notes
-------------|-------------|----------------------
[load_problem](basic_api_examples/load_problem.ipynb) | Comparison of model building performance between low-level and high-level methods | 
[loadlp](basic_api_examples/loadlp.ipynb) | Using the low-level API function *loadproblem()* | 
[logic_cons](basic_api_examples/logic_cons.ipynb) | Using general constraints for logical expressions | 
[modeling](basic_api_examples/modeling.ipynb) | Modeling a basic MIP problem | 
[numpy_arrays](basic_api_examples/numpy_arrays.ipynb) | Using the numerical library *NumPy* | 
[piecewise_linear](basic_api_examples/piecewise_linear.ipynb) | Using piecewise linear functions | 
[sos](basic_api_examples/sos.ipynb) | Defining Special Ordered Set (SOS) constraints | 
[write_read](basic_api_examples/write_read.ipynb) | Writing and reading a problem file | 

### Modeling examples

Example name | Description | Notes
-------------|-------------|----------------------
[facility_location](modeling_examples/facility_location.ipynb) | A basic facility location problem | 
[firestation_scipy](modeling_examples/firestation_scipy.ipynb) | Using a SciPy sparse matrix formulation to model the fire station location problem | 
[inscribed_square](modeling_examples/inscribed_square.ipynb) | Inscribed square problem solved with Xpress NonLinear or Xpress Global |
[markowitz_multiobj](modeling_examples/markowitz_multiobj.ipynb) | Multi-objective formulation of Markowitz portfolio optimization problem | 
[n_queens](modeling_examples/n_queens.ipynb) | The problem of placing $n$ queens on a chessboard | 
[sudoku](modeling_examples/sudoku.ipynb) | Solving a Sudoku problem | 
[tsp_callbacks](modeling_examples/tsp_callbacks.ipynb) | Solving a TSP problem using callbacks | This example requires a full license of the FICO&reg; Xpress Optimizer.
[unitcommitment_indicators](modeling_examples/unitcommitment_indicators.ipynb) | Unit commitment problem formulation with indicator constraints | 

## Documentation and other examples

* [Python Interface Reference Manual](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/python/HTML)
* [Xpress Python examples](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/python/HTML/chExamples.html)

## Running the examples using GitHub codespaces

1. **Open Codespaces and create a codespace**:
   - Click on the **"Code"** (green) button on the [repository page](https://github.com/fico-xpress/python-notebooks).
   - On the **"Codespaces"** tab, select **"Create a Codespace on main"**. This will set up a cloud-based development environment for you.

2. **Open Python Notebook**:
   - Once the Codespace is created and the environment is ready (wait for the README preview to appear), you can open a Python notebook.
   - Navigate to a notebook file (with a `.ipynb` extension) within the Codespace.
   - Click on the notebook file to open it in the Jupyter interface.

3. **Run the Notebook**:
   - Run a code cell in the Python notebook as you would normally do in a local environment.
   - When running for the first time, select "Install/Enable suggested extensions: Python + Jupyter" as suggested in the pop-up window at the top of the screen.
   - After installation, the Python environment is automatically selected when running the code cell again. You are all set to run all the code cells.

## Legal

See source code files for copyright notices.

## License

The examples in this repository are licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for the full license text. The examples use FICO&reg; Xpress software. By running it, you agree to the Community License terms of the [Xpress Shrinkwrap License Agreement](https://community.fico.com/s/contentdocument/06980000002h0i5AAA) with respect to the FICO&reg; Xpress software. See the [licensing options](https://www.fico.com/en/fico-xpress-trial-and-licensing-options) overview for additional details and information about obtaining a paid license.