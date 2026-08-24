# /// script
# [tool.marimo.opengraph]
# title = "Portfolio Optimization"
# description = "Uses Pandas Dataframes"
# image = "__marimo__/thumbnail-portfolio.svg"
# ///

import marimo

__generated_with = "0.23.13"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # **Portfolio Optimization using Pandas dataframes**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    In this example, we load a dataset with stock information to select a portfolio that maximizes returns subject to a wide range of constraints including sector, risk and ESG restrictions. We showcase the capabilitites of the Xpress Python API regarding the use of Pandas operations to generate aggregate expressions, as well as vector or matrix-based formulations for constraints and the objective function.

    &copy; Copyright 2025-2026 Fair Isaac Corporation. The use of this example is subject to [legal and license requirements](https://github.com/fico-xpress/python-notebooks#legal-and-license-requirements).
    """)
    return


@app.cell
def _():
    # Install the necessary packages
    # '%pip install -q xpress pandas matplotlib seaborn' command supported automatically in marimo
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Problem description
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    In this **portfolio optimization** problem, we wish to select stocks to form a portfolio for an asset allocation strategy. A list of stocks is available to be selected and we want to decide the fraction of the available budget to be allocated to each of the selected stocks that maximizes the total expected return.

    Stock data comprises an expected return for the coming investment period, an industry sector, an ESG (Environmental, Social, and Governance) score and a coefficient of variation (CV) representing the risk associated with each stock. **The selected portfolio must satisfy the following conditions**:

    * If a particular stock is selected then the total investment on this stock should not be lower than 1% and should not exceed 20% of the available budget.
    * The investment in each of the 8 industry sectors should not exceed 25% of the available budget.
    * At least 10 different stocks must be purchased.
    * The ESG score amongst the selected stocks, weighted by fraction, needs to be at least 70.
    * The weighted average CV score should not exceed 0.5.

    The input data file **[shares100.csv](https://github.com/fico-xpress/python-notebooks/blob/main/modeling_examples/data/shares100.csv)** provides data, in tabular form, related to 100 stocks with the following fields:

    * *Stock*: Name of the stock.
    * *Return*: The expected return for the investment cycle ahead, per unit of stock.
    * *Sector*: The industry sector the stock belongs to (e.g., Technology, Healthcare, Energy).
    * *ESG score*: The Environmental, Social, and Governance score, which evaluates a company's sustainability and ethical impact.
    * *CV*: the coefficient of variation (CV) representing the volatility (risk) associated with each stock.

    The goal is to select the **portfolio that ensures maximum returns while satisfying all constraints**. We further evaluate the impact of setting a range of different thresholds on the maximum average risk and minimum ESG requirements on the optimal return.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Model parameters

    **You can adjust the parameters below to change the portfolio constraints and re-solve the model automatically.**
    """)
    return


@app.cell
def _(mo):
    minpershare_slider = mo.ui.slider(0.0, 0.1, value=0.01, step=0.01, label="Min. fraction of capital per share", show_value=True)
    maxpershare_slider = mo.ui.slider(0.05, 0.5, value=0.2, step=0.05, label="Max. fraction of capital per share", show_value=True)
    maxpersector_slider = mo.ui.slider(0.1, 0.5, value=0.25, step=0.05, label="Max. fraction of capital per sector", show_value=True)
    minnumstocks_slider = mo.ui.slider(1, 30, value=10, step=1, label="Min. number of stocks in portfolio", show_value=True)
    minesg_slider = mo.ui.slider(50, 89, value=70, step=1, label="Min. average ESG score", show_value=True)
    maxrisk_slider = mo.ui.slider(0.1, 0.75, value=0.5, step=0.05, label="Max. average risk (CV)", show_value=True)
    mo.vstack([
        mo.hstack([minpershare_slider, maxpershare_slider, maxpersector_slider]),
        mo.hstack([minnumstocks_slider, minesg_slider, maxrisk_slider]),
    ])
    return (
        maxpersector_slider,
        maxpershare_slider,
        maxrisk_slider,
        minesg_slider,
        minnumstocks_slider,
        minpershare_slider,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Data preparation, analysis and visualization
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We start by importing the essential libraries for optimization (`xpress`), data manipulation (`pandas`, `numpy`), and visualization (`matplotlib`, `seaborn`).

    After defining the value for the constants needed for the mathematical model (from the **Model parameters** controls above), we load the dataset included in the file named **[shares100.csv](https://github.com/fico-xpress/python-notebooks/blob/main/modeling_examples/data/shares100.csv)** (which must be present in the "data" directory) containing stock information into a Pandas dataframe. Then, we display the first five rows to give a quick overview of the data structure and contents.
    """)
    return


@app.cell
def _(
    maxpersector_slider,
    maxpershare_slider,
    maxrisk_slider,
    minesg_slider,
    minnumstocks_slider,
    minpershare_slider,
    mo,
):
    import xpress as xp
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns

    MinPerShare = minpershare_slider.value      # Minimum fraction of capital to invest in a single share
    MaxPerShare = maxpershare_slider.value      # Maximum fraction of capital to invest in a single share
    MaxPerSector = maxpersector_slider.value    # Maximum fraction of capital to invest in a single sector
    MinNumStocks = minnumstocks_slider.value    # Minimum number of stocks in the portfolio
    MinESG = minesg_slider.value                # Minimum average ESG score allowed in the portfolio
    MaxRisk = maxrisk_slider.value              # Maximum average risk allowed in the portfolio

    # Load the shares dataset (resolved relative to this notebook's own directory,
    # so it works regardless of the current working directory)
    shares_df = pd.read_csv(mo.notebook_dir() / "data" / "shares100.csv")

    # Share data overview
    mo.show_code(mo.vstack([mo.md("**Data sample for the first 5 rows:**"), shares_df.head()]), position="above")
    return (
        MaxPerSector,
        MaxPerShare,
        MaxRisk,
        MinESG,
        MinNumStocks,
        MinPerShare,
        np,
        pd,
        plt,
        shares_df,
        sns,
        xp,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The code below creates four subplots with stock distributions using Seaborn and Matplotlib. The subplots in the first row show the distribution of **Returns** and **Sectors**, while the second row displays the distribution of **ESG scores** and **CV scores**.

    Both plots use histograms and contain kernel density estmation curves to further highlight the shape of the data.
    """)
    return


@app.cell
def _(plt, shares_df, sns):
    # Plot distributions
    dist_fig = plt.figure(figsize=(12, 10))

    num_bins = 25

    # Plotting the distribution of returns
    plt.subplot(2, 2, 1)
    sns.histplot(shares_df['Return'], bins=num_bins, kde=True)
    plt.title('Distribution of Returns')

    # Plotting the distribution of Sector
    plt.subplot(2, 2, 2)
    plt.xticks(rotation=45)
    sns.histplot(shares_df['Sector'], bins=num_bins, kde=True)
    plt.title('Distribution by Sector')

    # Plotting the distribution of ESG scores
    plt.subplot(2, 2, 3)
    sns.histplot(shares_df['ESG score'], bins=num_bins, kde=True)
    plt.title('Distribution of ESG Scores')

    # Plotting the distribution of risk scores
    plt.subplot(2, 2, 4)
    sns.histplot(shares_df['CV'], bins=num_bins, kde=True)
    plt.title('Distribution of CV scores')

    plt.tight_layout()
    dist_fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The code cell below plots a **sector-wise analysis** using boxplots, depicting the spread of **returns** and **risk scores** across different sectors. It shows that sectors with higher expected returns are also the most volatile sectors.
    """)
    return


@app.cell
def _(plt, shares_df, sns):
    # Set the plot layout
    sector_fig = plt.figure(figsize=(12, 5))

    # Boxplot for Return by Sector
    plt.subplot(1, 2, 1)
    sns.boxplot(data=shares_df, x='Sector', y='Return')
    plt.xticks(rotation=45)
    plt.title('Return distribution by Sector')

    # Boxplot for CV score by Sector
    plt.subplot(1, 2, 2)
    sns.boxplot(data=shares_df, x='Sector', y='CV')
    plt.xticks(rotation=45)
    plt.title('Risk distribution by Sector')

    plt.tight_layout()
    sector_fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Model implementation and solution printing
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We start by defining a set of continuous decision variables $frac_i$ that represent the fraction ($>= 0, <= 1$) of the available budget to be allocated to each stock $i \in \mathcal{S}$, and the auxiliary binary variables $buy_i$ to decide whether stock $i$ is included in the portfolio ($=1$), or not ($=0$).

    To take advantage of the **improved Pandas compatibility features introduced in Xpress 9.8**, Pandas series containing Xpress variables or expressions should have the data type set to `xpressobj`, as shown by the code below where the two sets of variables are added to the previously created Xpress problem.

    The NumPy arrays returned by [problem.addVariables](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/python/HTML/problem.addVariables.html) are wrapped into Pandas series, which must be added as a new column to the dataframe in order to enable performing the intended Pandas operations.
    """)
    return


@app.cell
def _(mo, pd, shares_df, xp):
    # Create Xpress problem and variables
    p = xp.problem("Portfolio Selection")
    shares_df['frac'] = pd.Series(p.addVariables(len(shares_df), vartype=xp.continuous, name='frac'), dtype='xpressobj')
    shares_df['buy'] = pd.Series(p.addVariables(len(shares_df), vartype=xp.binary, name='buy'), dtype='xpressobj')
    mo.show_code()
    return (p,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The objective of maximizing the expected returns is defined the sum of the product between the expected return (`RET`) of each stock and the corresponding `frac` variable: $$\max \sum_{i \in \mathcal{S}} RET_i \cdot frac_i$$

    As shown in the code cell below, the objective expression can be created using the element-wise product (`*`) of the `Return` and `frac` columns followed by the summation (`sum`) of the resulting series **using Pandas-specific methods**.

    The call to [problem.setObjective](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/python/HTML/problem.setObjective.html) then adds the objective function to the problem, specifying that it is to be maximized.
    """)
    return


@app.cell
def _(mo, p, shares_df, xp):
    # Objective function: minimize total return
    obj = (shares_df['Return'] * shares_df['frac']).sum()
    p.setObjective(obj, sense=xp.ObjSense.MAXIMIZE)
    mo.show_code()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Next we model the following 2 constraints:

    * The sum of the portfolio stock allocations should be equal to 1 (fully invested portfolio):
    $$\sum_{i \in \mathcal{S}} frac_i = 1$$

    * Diversification: ensure a minimum number of assets:
    $$\sum_{i \in \mathcal{S}} buy_i \geq \text{MinNumStocks}$$

    We simply use the Pandas `sum` operator on the corresponding dataframe column to represent the left-hand side of each constraint. The call to [problem.addConstraint](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/python/HTML/problem.addConstraint.html) adds the constraint to the model.
    """)
    return


@app.cell
def _(MinNumStocks, mo, p, shares_df):
    # Spend all the capital
    p.addConstraint(shares_df['frac'].sum() == 1)

    # Ensure a minimum total number of assets
    p.addConstraint(shares_df['buy'].sum() >= MinNumStocks)
    mo.show_code()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The code below ensures that if a share is selected ($buy$ = 1), then the fraction bought must be at least `MinPerShare` and not exceed `MaxPerShare`. In either case, if the share is not selected ($buy$ = 0), then the fraction must be zero.

    $$
    \text{MinPerShare} \cdot buy_i \leq frac_i \leq \text{MaxPerShare} \cdot buy_i \quad \forall i \in \mathcal{S}
    $$

    We model those constraints by doing an element-wise product between the corresponding scalar and the `buy` column elements using the multiplication operator (`*`), and equivalently by using the `mul` Pandas method.
    """)
    return


@app.cell
def _(MaxPerShare, MinPerShare, mo, p, shares_df):
    # Linking constraints defining minimum and maximum fraction per share
    p.addConstraint(shares_df['frac'] >= MinPerShare * shares_df['buy'])
    p.addConstraint(shares_df['frac'] <= shares_df['buy'].mul(MaxPerShare))     # Alternative way of multiplying column x scalar
    mo.show_code()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Just like with the objective function expression, we define the ESG and risk constraints as:

    * Minimum average ESG score constraint:
    $$\sum_{i \in \mathcal{S}} \text{ESG}_i \cdot frac_i \geq \text{MinESG}$$

    * Maximum average risk (CV) constraint:
    $$\sum_{i \in \mathcal{S}} \text{CV}_i \cdot frac_i \leq \text{MaxRisk}$$

    These constraints can be modeled by using the element-wise product of the corresponding column and the `frac` column, followed by the summation of the resulting series using the `sum` method to build the left-hand side of the constraint.
    """)
    return


@app.cell
def _(MaxRisk, MinESG, mo, p, shares_df):
    # Average ESG score constraint: the weighted average ESG score must be at least MinAvgESG
    avg_esg = (shares_df['ESG score'] * shares_df['frac']).sum() >= MinESG

    # Risk constraint: average risk (CV) must be less than or equal to MaxRisk
    avg_risk = (shares_df['CV'] * shares_df['frac']).sum() <= MaxRisk

    p.addConstraint(avg_esg, avg_risk)
    mo.show_code()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The constraint that ensures that the total fraction of shares bought in any given sector does not exceed `MaxPerSector`:
     $$\sum_{i \in \mathcal{S}: Sector[i] = n} frac_i \leq \text{MaxPerSector}, \forall n \in SECTORS$$

    This constraint can be easily modeled using Pandas by applying the `groupby()` method to group shares by their sector (e.g., Technology, Healthcare, etc.), and then calling the `sum` function to sum the variables representing fractional purchases (`frac`) within each sector. This expression produces a series of constraints, one for each sector, which are then added to the problem by a single call to `addConstraint`.
    """)
    return


@app.cell
def _(MaxPerSector, mo, p, shares_df):
    # Maximum per sector: total fraction invested in each sector does not exceed MaxPerSector
    p.addConstraint(shares_df.groupby('Sector')['frac'].sum() <= MaxPerSector)
    mo.show_code()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Lastly, we turn off the solver logs by using the [outputlog](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/HTML/OUTPUTLOG.html) control, and then solve the problem by calling [problem.optimize](https://www.fico.com/fico-xpress-optimization/docs/latest/solver/optimizer/python/HTML/problem.optimize.html) which returns a solve status (completed, stopped, ...) and solution status (optimal, infeasible, ...).

    In case a (feasible or optimal) solution has been found, we display the computed metrics and plot the final solution (i.e. the portfolio composition) using a donut plot with selected stocks in descending order of fraction value.
    """)
    return


@app.cell
def _(mo, np, p, pd, plt, shares_df, xp):
    p.controls.outputlog = 0        # Suppress output log

    # Solve optimization problem
    solvestatus, solstatus = p.optimize()

    if solstatus in (xp.SolStatus.OPTIMAL,xp.SolStatus.FEASIBLE):
        # Get solution
        shares_df["fraction"] = p.getSolution(shares_df['frac'])

        # Compute metrics
        SummaryValues = pd.Series({
            "Expected return": p.attributes.objval,
            "Average risk (CV)": (shares_df["CV"] * shares_df["fraction"]).sum(),
            "Average ESG": (shares_df["ESG score"] * shares_df["fraction"]).sum(),
            "# selected stocks": (shares_df["fraction"] > 0).sum(),
            "Largest position": (shares_df["fraction"]).max(),
            "Smallest position": shares_df[shares_df["fraction"] > 0]["fraction"].min(),
            "MaxPerSector": shares_df.groupby('Sector')['fraction'].sum().max(),
        })

        # Plot portfolio composition
        filtered_df = shares_df[shares_df["fraction"] >= 0.005] # Filter rows where fraction is greater than or equal to 0.005
        plot_df = filtered_df.sort_values('fraction', ascending=False) # Sort so the largest slices are first

        sizes = plot_df['fraction'].astype(float).values        # The wedge sizes
        labels = plot_df['Stock'].astype(str).values            # The labels for each wedge

        colors = plt.cm.tab20(np.linspace(0, 1, len(sizes)))    # Color palette
        threshold_pct = 3.0                                     # Only show % on wedges >= this threshold

        fig, ax = plt.subplots(figsize=(9, 8))
        wedges, _, autotexts = ax.pie(
            sizes,
            colors=colors,
            startangle=90,
            counterclock=False,
            autopct=lambda p: f'{p:.1f}%' if p >= threshold_pct else '',
            pctdistance=0.72,
            wedgeprops=dict(width=0.55, edgecolor='white'),     # Donut style (more readable)
            textprops=dict(color='black', fontsize=10)
        )

        ax.legend(
            wedges, labels,
            title='Stock',
            loc='center left',
            bbox_to_anchor=(1.0, 0.5)
        )

        ax.set_title('Selected portfolio and fractions')
        ax.set_aspect('equal')
        plt.tight_layout()
        result = mo.vstack([mo.as_html(SummaryValues), fig])
    else:
        result = mo.md(f"""
        **Optimization did not find a solution.** Status: {p.attributes.solvestatus}
        """)
    mo.show_code(result, position="above")
    return


if __name__ == "__main__":
    app.run()
