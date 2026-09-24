# Marimo notebooks

FICO&reg; Xpress Python example notebooks built with [marimo](https://marimo.io/), a reactive, browser-based notebook format.

**Try an interactive example in your browser:** start with [molab](#running-marimo-notebooks-in-molab), a cloud-hosted marimo environment for learning and experimentation. Choose a notebook from the badges below; read the privacy notes before running it.

**Just want to take a look, not run code?** See the [live read-only gallery](https://fico-xpress.github.io/python-notebooks/), a static export of every notebook below, no installation or Codespace setup needed. Each page is a static snapshot: sliders and other interactive controls will not respond. Follow the steps below to run a notebook interactively.

## Getting started

* [Running marimo notebooks in molab](#running-marimo-notebooks-in-molab)
* [Running marimo notebooks in GitHub Codespaces](#running-marimo-notebooks-in-github-codespaces)
* [Running marimo notebooks locally](#running-marimo-notebooks-locally)

## Running marimo notebooks in molab

[molab](https://molab.marimo.io/) is marimo's free cloud-hosted notebook environment. Use it to learn from these public examples, explore the optimization models with interactive controls, and experiment with the code in your browser. You do not need to install Python locally or create a Codespace.

**Before you start:** molab notebooks are public but unlisted by default. Anyone with a notebook's link can view it; an unlisted link is not private access control. Use the public example data, and keep confidential customer data, proprietary models, credentials, and license keys out of notebook code, outputs, and uploaded files. For private work or a full development environment, use an appropriately configured [GitHub Codespace](#running-marimo-notebooks-in-github-codespaces) or [run locally](#running-marimo-notebooks-locally).

1. Choose an **Open in molab** badge below. It opens a preview of that notebook from this repository's `main` branch. GitHub remains the source of the shared example; the link follows updates to the original notebook.
2. Choose **Run it now** to run the notebook on a temporary server, or **Fork** to make an editable copy in your own molab workspace. Sign in or create a molab account when prompted.
3. If prompted, use marimo's package manager to install missing imports, including `xpress`. Then run the cells and try the sliders. These examples use the native Xpress solver, so use molab's server execution, not its WebAssembly preview. Changes to your fork do not update the FICO repository.

molab is an interactive notebook environment for exploration and teaching. Temporary runs are not saved to your workspace, and sessions have time limits. Fork a notebook to keep an editable copy, and download any results you need to retain. See the [molab documentation](https://docs.marimo.io/guides/molab/) for current execution, sharing, package, and storage behavior, and its [usage restrictions](https://molab.marimo.io/pages/molab/restrictions) for supported use.

### Open an example

| Notebook source | Topic | Run in molab |
| --- | --- | --- |
| [Project Assignment](01_assignment.py) | Binary assignment model | [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/fico-xpress/python-notebooks/blob/main/marimo/01_assignment.py) |
| [Facility Location](02_facility_location.py) | Mixed-integer location model | [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/fico-xpress/python-notebooks/blob/main/marimo/02_facility_location.py) |
| [Sudoku](03_sudoku.py) | Feasibility problem | [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/fico-xpress/python-notebooks/blob/main/marimo/03_sudoku.py) |
| [Portfolio Optimization](04_portfolio_pandas.py) | Pandas dataframes | [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/fico-xpress/python-notebooks/blob/main/marimo/04_portfolio_pandas.py) |
| [Campaign Conversion](05_campaign_polars.py) | Polars dataframes | [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/fico-xpress/python-notebooks/blob/main/marimo/05_campaign_polars.py) |
| [Circle Packing](06_circle_packing.py) | Nonlinear optimization with Xpress Global | [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/fico-xpress/python-notebooks/blob/main/marimo/06_circle_packing.py) |
| [Unit Commitment](07_unitcommitment_indicators.py) | Indicator constraints | [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/fico-xpress/python-notebooks/blob/main/marimo/07_unitcommitment_indicators.py) |
| [Markowitz Portfolio Optimization](08_markowitz_multiobj.py) | Multi-objective quadratic programming | [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/fico-xpress/python-notebooks/blob/main/marimo/08_markowitz_multiobj.py) |
| [TSP with Callbacks](09_tsp_callbacks.py) | Solver callbacks and cut generation | [![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/fico-xpress/python-notebooks/blob/main/marimo/09_tsp_callbacks.py) |

### Example data

The portfolio and campaign datasets are included in [public/data/](public/data/). molab imports this adjacent `public/` folder for both temporary runs and forks, so you do not need to upload the CSVs manually. The notebooks read the same files when run locally or in GitHub Codespaces.

## Running marimo notebooks in GitHub Codespaces

Please note that the creation of the codespace may take 3-4 minutes; we ask for your patience during this step.

1. On the repository's GitHub page, click **Code**, then open the **Codespaces** tab.
2. Click the **...** icon next to **Create codespace on master** and select **New with options**.

   <p align="center"><img src="docs/images/new_codespace.png" alt="create codespace on master" width="350"></p>

3. In the **Dev container configuration** dropdown, choose **Marimo Xpress Notebooks** (not the default "Jupyter" configuration).

   <p align="center"><img src="docs/images/dev_config.png" alt="select dev container configuration" width="550"></p>

4. Click **Create codespace**. Building the environment takes about 3-4 minutes. You can follow progress in the terminal panel at the bottom; the setup is finished once you see a message confirming marimo has started and is listening on port 2718.

   <p align="center"><img src="docs/images/terminal.png" alt="terminal showing marimo startup progress" width="550"></p>

5. At some point during setup, VS Code may show a **"Do you trust the authors of the files in this folder?"** popup. This is a one-time security prompt from VS Code itself (not something this repository controls), and it is expected. Click **Yes, I trust the authors** to continue.

   <p align="center"><img src="docs/images/trust.png" alt="workspace trust popup" width="400"></p>

6. Once the port is ready, VS Code shows a notification with an **Open in Browser** button. Click it to open the marimo home page in a new browser tab.

   <p align="center"><img src="docs/images/open_browser.png" alt="port forwarded notification with Open in Browser button" width="350"></p>

   If you miss the notification or it disappears, open the **Ports** tab next to the terminal instead. You should see port **2718** listed with the label `marimo`. Click the link under the **Forwarded Address** column for that row to open it in your browser (the **Add Port** button is for forwarding a *new* port and has no effect here, since port 2718 is already forwarded).

   <p align="center"><img src="docs/images/port.png" alt="Ports tab with port 2718 forwarded" width="550"></p>

7. Once the tab opens, you will see the marimo home page: a grid of notebook thumbnails, each with a title and short subtitle, similar to the screenshot below.

   <p align="center"><img src="docs/images/marimo_home.png" alt="marimo home page with notebook tiles" width="600"></p>

8. Click any notebook, for example **Project Assignment**. Every cell runs automatically as soon as the notebook opens. Try moving one of the sliders, for example the problem-size slider, and watch every dependent cell re-run automatically, updating the results table and chart in real time.

   <p align="center"><img src="docs/images/controls.png" alt="assignment notebook controls with sliders" width="550"></p>

## Running marimo notebooks locally

If you would rather not use Codespaces, you can run the notebooks on your own machine instead.

**Prerequisites:** [Python 3.13+](https://www.python.org/downloads/) and [Git](https://git-scm.com/downloads) installed.

1. Clone the repository and move into the `marimo/` folder:

   ```bash
   git clone https://github.com/fico-xpress/python-notebooks.git
   cd python-notebooks/marimo
   ```

2. Install the notebook dependencies. Using a virtual environment is optional but recommended so these packages don't clash with anything else on your machine:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate      # on Windows
   source .venv/bin/activate   # on macOS/Linux

   pip install -r requirements.txt
   ```

3. Launch any notebook with `marimo edit` (opens the notebook in editable mode, so you can also modify the code) or `marimo run` (opens it in read-only run mode, matching the Codespaces experience where all cells auto-run and only the modelling code stays visible):

   ```bash
   marimo edit 01_assignment.py
   # or, to browse all notebooks from a single home page like in Codespaces:
   marimo run .
   ```

   Either command starts a local server and should open a new browser tab automatically at `http://localhost:2718`. If it doesn't, copy that URL into your browser manually.

## Legal and license requirements

See [Legal and license requirements](../README.md#legal-and-license-requirements) in the main README.
