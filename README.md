# FICO Xpress Python notebook examples

This repository contains Python notebook examples for two complementary Python interfaces to FICO&reg; Xpress:

* **`xpress`** — the FICO&reg; Xpress Python API for building and solving optimization models directly in Python. See [xpress on PyPI](https://pypi.org/project/xpress/) and the [Python Interface Reference Manual](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/python/HTML).

* **`moselpy`** — Python API for FICO&reg; Xpress Mosel, for compiling and running Mosel models from Python and exchanging data bidirectionally. Ideal for integrating existing Mosel models into Python data science workflows. See [moselpy on PyPI](https://pypi.org/project/moselpy/) and the [MoselPy User Guide and Reference Manual](https://www.fico.com/fico-xpress-optimization/docs/latest/mosel/MoselPy/dhtml).

The examples are organized into three top-level folders, one per notebook engine/API:

* **[xpress-api/](xpress-api/README.md)** — Jupyter notebooks for the Xpress Python API ([basic_api_examples/](xpress-api/basic_api_examples/), [modeling_examples/](xpress-api/modeling_examples/)).
* **[moselpy/](moselpy/README.md)** — Jupyter notebooks for MoselPy.
* **[marimo/](marimo/README.md)** — reactive, browser-based [marimo](https://marimo.io/) notebooks for the Xpress Python API. Alternatively, you can browse a [live read-only gallery](https://fico-xpress.github.io/python-notebooks/) of all marimo notebooks, no installation required.

## Running the examples using GitHub codespaces

### Jupyter notebooks (`xpress-api/`, `moselpy/`)

1. **Open Codespaces and create a codespace**:
   * Click on the **"Code"** (green) button on this [repository page](https://github.com/fico-xpress/python-notebooks).
   * On the **"Codespaces"** tab, select **"Create a Codespace on main"**. This will set up a cloud-based development environment for you.

2. **Open Python Notebook**:
   * Once the Codespace is created and the environment is ready (wait for the README preview to appear), you can open a Python notebook.
   * Navigate to a notebook file (with a `.ipynb` extension) within the Codespace.
   * Click on the notebook file to open it in the Jupyter interface.

3. **Run the Notebook**:
   * Run a code cell in the Python notebook as you would normally do in a local environment.
   * When running for the first time, select "Install/Enable suggested extensions: Python + Jupyter" as suggested in the pop-up window at the top of the screen.
   * After installation, select the installed Python environment and wait for the code cell to be executed. You are all set to run all the code cells.

### marimo notebooks (`marimo/`)

marimo notebooks require an extra step not needed for Jupyter: when creating the codespace, you must explicitly choose the **"Marimo Xpress Notebooks"** dev container configuration from the dropdown (via **Create codespace** > **...** > **New with options**), instead of the default **"Default (Jupyter)"** configuration.

See [marimo/README.md](marimo/README.md) for the full walkthrough with screenshots.

## Documentation and other examples

* [Python Interface Reference Manual](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/python/HTML)
* [Xpress Python examples](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/python/HTML/chExamples.html)
* [MoselPy User Guide and Reference Manual](https://www.fico.com/fico-xpress-optimization/docs/latest/mosel/MoselPy/dhtml)

## Legal and license requirements

The examples in this repository are licensed under the Apache License, Version 2.0. You may not use these files except in compliance with the License. You may obtain a copy of the License at [http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0), or see [LICENSE](LICENSE) for the full license text. Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

The examples use FICO&reg; Xpress software. By running them, you agree to the Community License terms of the [Xpress Shrinkwrap License Agreement](https://www.fico.com/en/shrinkwrap-license-agreement-fico-xpress-optimization-suite-on-premises) with respect to the FICO&reg; Xpress software. See the [licensing options](https://www.fico.com/en/fico-xpress-trial-and-licensing-options) overview for additional details and information about obtaining a paid license.
