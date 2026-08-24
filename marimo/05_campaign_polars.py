# /// script
# [tool.marimo.opengraph]
# title = "Campaign Conversion"
# description = "Uses Polars Dataframes"
# image = "__marimo__/thumbnail-campaign.svg"
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
    # **Campaign conversion optimization using Polars dataframes**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    In this example, we load a dataset with customer information to optimize campaign channel assignments that maximize expected value subject to budget and channel capacity constraints. We showcase the capabilities of the Xpress Python API with the use of Polars dataframes to generate aggregate expressions for optimization.

    &copy; Copyright 2025-2026 Fair Isaac Corporation. The use of this example is subject to [legal and license requirements](https://github.com/fico-xpress/python-notebooks#legal-and-license-requirements).
    """)
    return


@app.cell
def _():
    # Install the necessary packages
    # '%pip install -q xpress polars matplotlib seaborn pyarrow' command supported automatically in marimo
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
    In this **campaign conversion optimization** problem, we want to contact customers through different channels (SMS, Mail, Phone) to maximize the total expected value from contacts. Each customer can be contacted through at most one channel, and we need to decide which channel to use for each customer.

    Customer data includes expected value and propensity to convert for each channel. Channel data includes contact costs and capacity constraints. **The optimized campaign must satisfy the following conditions**:

    * Each customer is contacted through at most one channel.
    * The total campaign cost must not exceed the available budget.
    * Each channel has a capacity limit (maximum percentage of customers that can be contacted).

    The input data file **[customers1000.csv](https://github.com/fico-xpress/python-notebooks/blob/main/modeling_examples/data/customers1000.csv)** provides customer data with the following fields:

    * *CustomerIds*: Unique customer identifier.
    * *Name*: Customer name.
    * *Value*: Expected customer value.
    * *PropSMS*: Propensity to convert via SMS.
    * *PropMail*: Propensity to convert via Mail.
    * *PropPhone*: Propensity to convert via Phone.

    The goal is to **maximize the total expected value while satisfying budget and channel capacity constraints**.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Model parameters

    **You can adjust the parameters below to change the problem instance and re-solve the model automatically.**
    """)
    return


@app.cell
def _(mo):
    num_customers_slider = mo.ui.slider(200, 1000, value=1000, step=100, label="Number of customers to load", show_value=True)
    budget_slider = mo.ui.slider(200, 3000, value=1000, step=100, label="Total campaign budget ($)", show_value=True)
    capacity_scale_slider = mo.ui.slider(0.5, 2.0, value=1.0, step=0.1, label="Channel capacity scale factor", show_value=True)
    goal_selector = mo.ui.radio(
        options={"Maximize total value": "value", "Maximize total propensity": "propensity", "Balanced (value + propensity)": "balanced"},
        value="Maximize total value",
        label="Goal"
    )
    mo.vstack([
        mo.hstack([num_customers_slider, budget_slider, capacity_scale_slider]),
        goal_selector,
    ])
    return budget_slider, capacity_scale_slider, goal_selector, num_customers_slider


@app.cell
def _(goal_selector, mo):
    # Only used when Goal is set to "Balanced" - disabled otherwise to make that dependency clear
    ratio_balance_slider = mo.ui.slider(
        0, 100, value=50, step=5,
        label="Balance ratio (% weight on value) - applies only when Goal is set to Balanced",
        show_value=True,
        disabled=goal_selector.value != "balanced",
    )
    ratio_balance_slider
    return (ratio_balance_slider,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Data preparation and analysis
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We start by importing the essential libraries for optimization (`xpress`), data manipulation (`polars`), and visualization (`matplotlib`, `seaborn`).

    After defining the values for the constants needed for the mathematical model, we load the customer dataset from the CSV file into a **Polars dataframe**. Then, we display the first five rows to give a quick overview of the data structure and contents.
    """)
    return


@app.cell
def _(mo, num_customers_slider, budget_slider):
    import xpress as xp
    import polars as pl
    import matplotlib.pyplot as plt
    import seaborn as sns

    NUM_CUSTOMERS = num_customers_slider.value      # Number of customers to load, must be <= 1000
    BUDGET = budget_slider.value                    # Total campaign budget

    # Load the customer dataset (resolved relative to this notebook's own directory,
    # so it works regardless of the current working directory)
    customers = pl.read_csv(mo.notebook_dir() / "data" / "customers1000.csv", n_rows=NUM_CUSTOMERS)

    # Customer data overview
    mo.show_code(mo.vstack([mo.md("**Data sample for the first 5 rows:**"), customers.head()]), position="above")
    return BUDGET, NUM_CUSTOMERS, customers, pl, plt, sns, xp


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The code below creates channel data and displays basic statistics about customers and their propensities across different channels.
    """)
    return


@app.cell
def _(customers, mo, pl):
    # Create channel dataframe using Polars
    channels = pl.from_dict({
        "ChannelIds": [0, 1, 2],
        "Name": ["SMS", "Mail", "Phone"],
        "Cost": [0.5, 1.2, 3.0],
        "Capacity": [100, 50, 40]       # Percentage of total customers
    })

    mo.show_code(mo.vstack([
        mo.md("**Channel information:**"),
        channels,
        mo.md(f"""
        **Customer statistics:**

        Total customers: {len(customers)} &nbsp;&nbsp; Average value: ${customers['Value'].mean():.2f} &nbsp;&nbsp; Min value: ${customers['Value'].min():.2f} &nbsp;&nbsp; Max value: ${customers['Value'].max():.2f} &nbsp;&nbsp; Median value: ${customers['Value'].median():.2f}

        **Average propensities:** SMS: {customers['PropSMS'].mean():.4f} &nbsp;&nbsp; Mail: {customers['PropMail'].mean():.4f} &nbsp;&nbsp; Phone: {customers['PropPhone'].mean():.4f}
        """),
    ]), position="above")
    return (channels,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The charts below show the distribution of values and propensities across customers, before the optimization.
    """)
    return


@app.cell
def _(customers, plt, sns):
    # Convert to pandas for visualization purposes
    customers_pd = customers.to_pandas()

    # Create visualizations
    fig1, axes1 = plt.subplots(2, 2, figsize=(14, 8))
    fig1.suptitle('Customer Data Analysis', fontsize=16, fontweight='bold')

    # Plot 1: Distribution of Customer Values
    ax1 = axes1[0, 0]
    sns.histplot(customers_pd['Value'], bins=30, kde=True, ax=ax1, color='#3498db')
    ax1.set_title('Distribution of Customer Values', fontweight='bold')
    ax1.set_xlabel('Customer Value ($)')
    ax1.set_ylabel('Frequency')
    ax1.axvline(customers_pd['Value'].mean(), color='red', linestyle='--', label=f'Mean: ${customers_pd["Value"].mean():.0f}')
    ax1.legend()

    # Plot 2: Distribution of PropSMS
    ax2 = axes1[0, 1]
    sns.histplot(customers_pd['PropSMS'], bins=30, kde=True, ax=ax2, color='#e74c3c')
    ax2.set_title('Distribution of SMS Propensity', fontweight='bold')
    ax2.set_xlabel('Propensity')
    ax2.set_ylabel('Frequency')

    # Plot 3: Distribution of PropMail
    ax3 = axes1[1, 0]
    sns.histplot(customers_pd['PropMail'], bins=30, kde=True, ax=ax3, color='#9b59b6')
    ax3.set_title('Distribution of Mail Propensity', fontweight='bold')
    ax3.set_xlabel('Propensity')
    ax3.set_ylabel('Frequency')

    # Plot 4: Distribution of PropPhone
    ax4 = axes1[1, 1]
    sns.histplot(customers_pd['PropPhone'], bins=30, kde=True, ax=ax4, color='#2ecc71')
    ax4.set_title('Distribution of Phone Propensity', fontweight='bold')
    ax4.set_xlabel('Propensity')
    ax4.set_ylabel('Frequency')

    plt.tight_layout(rect=(0, 0, 1, 0.97), h_pad=3.0)
    fig1
    return (customers_pd,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Model implementation and solution
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We define binary decision variables $contact_{i,j}$ that indicate whether customer $i \in \mathcal{C}$ is contacted through channel $j \in \mathcal{CH}$ ($=1$), or not ($=0$).

    Since Xpress variables cannot be directly stored in Polars dataframes, we create the variables using standard Python dictionaries indexed by (customer_id, channel_id) tuples.
    """)
    return


@app.cell
def _(channels, customers, mo, xp):
    # Create Xpress problem
    p = xp.problem("Campaign Conversion")

    # Extract index sets
    customer_ids = customers["CustomerIds"].to_list()
    channel_ids = channels["ChannelIds"].to_list()
    num_customers = len(customer_ids)

    # Decision variables: contact[i,j] = 1 if customer i contacted through channel j
    contact = p.addVariables(customer_ids, channel_ids, vartype=xp.binary, name='contact')

    # Metric tracking variables
    MetricTotalCost = p.addVariable(name='MetricTotalCost')
    MetricCostPerChannel = p.addVariables(channel_ids, vartype=xp.continuous, name='MetricCostPerChannel')
    MetricContactPerChannel = p.addVariables(channel_ids, vartype=xp.continuous, name='MetricContactPerChannel')

    mo.show_code(mo.md(f"""
    Created {len(customer_ids) * len(channel_ids)} contact decision variables and {len(channel_ids)*2 + 1} auxiliary variables for metric tracking.
    """))
    return (
        MetricContactPerChannel,
        MetricCostPerChannel,
        MetricTotalCost,
        channel_ids,
        contact,
        customer_ids,
        num_customers,
        p,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The objective is to maximize the expected value from customer contacts:
    $$\max \sum_{i \in \mathcal{C}} \sum_{j \in \mathcal{CH}} Value_i \cdot Prop_{i,j} \cdot Contact_{i,j}$$

    We build this objective by iterating through customers and channels, using Polars filtering to extract the relevant propensity and value for each customer-channel pair.

    **Polars Operations for Objective Function Building:**

    The objective function uses nested loops with Polars `filter()` operations:
    1. For each channel `j`, we extract the channel name: `channels.filter(pl.col("ChannelIds") == j)["Name"][0]`
    2. For each customer `i`, we dynamically access the right propensity column using that name: `customers.filter(pl.col("CustomerIds") == i)[f"Prop{channel_name}"][0]`
    3. We retrieve the customer value: `customers.filter(pl.col("CustomerIds") == i)["Value"][0]`

    This pattern demonstrates how Polars can be integrated with optimization modeling using efficient filtering to construct complex mathematical expressions.
    """)
    return


@app.cell
def _(channel_ids, channels, contact, customer_ids, customers, goal_selector, mo, pl, p, ratio_balance_slider, xp):
    # Build objective expression using Polars filtering
    ObjectiveValue = 0
    ObjectivePropensity = 0

    for j in channel_ids:
        # Get channel name using Polars filter
        channel_name = channels.filter(pl.col("ChannelIds") == j)["Name"][0]

        for i in customer_ids:
            # Get customer propensity for this channel using Polars filter
            customer_prop = customers.filter(pl.col("CustomerIds") == i)[f"Prop{channel_name}"][0]
            customer_value = customers.filter(pl.col("CustomerIds") == i)["Value"][0]

            ObjectiveValue += contact[i, j] * customer_prop * customer_value
            ObjectivePropensity += contact[i, j] * customer_prop

    # Set objective function according to the selected Goal parameter
    RatioBalance = ratio_balance_slider.value
    if goal_selector.value == "value":
        p.setObjective(ObjectiveValue, sense=xp.ObjSense.MAXIMIZE)
    elif goal_selector.value == "propensity":
        p.setObjective(ObjectivePropensity, sense=xp.ObjSense.MAXIMIZE)
    else:
        Balanced = (ObjectiveValue / 20 * RatioBalance) / 100 + ObjectivePropensity * 500 * (100 - RatioBalance) / 100
        p.setObjective(Balanced, sense=xp.ObjSense.MAXIMIZE)
    mo.show_code()
    return ObjectivePropensity, ObjectiveValue


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Next we model the following constraints:

    * Each customer must be contacted through at most one channel:
    $$\sum_{j \in \mathcal{CH}} contact_{i,j} \leq 1 \quad \forall i \in \mathcal{C}$$

    * Budget constraint: total cost must not exceed budget:
    $$\sum_{i \in \mathcal{C}} \sum_{j \in \mathcal{CH}} Cost_j \cdot contact_{i,j} \leq Budget$$

    * Channel capacity: number of customers contacted per channel cannot exceed capacity:
    $$\sum_{i \in \mathcal{C}} contact_{i,j} \leq Capacity_j \cdot |\mathcal{C}| / 100 \quad \forall j \in \mathcal{CH}$$

    **Polars Operations for Constraint Building:**

    The constraints building process leverages the Polars `filter()` method to extract specific values from dataframes. For example:

    * `channels.filter(pl.col("ChannelIds") == j)["Cost"][0]` retrieves the cost for channel `j`
    * `channels.filter(pl.col("ChannelIds") == j)["Capacity"][0]` retrieves the capacity limit for channel `j`

    This approach allows us to dynamically look up channel-specific parameters while building the optimization model, making the code more maintainable and easier to understand compared to pre-processing all data into lists or dictionaries.
    """)
    return


@app.cell
def _(
    BUDGET,
    MetricContactPerChannel,
    MetricCostPerChannel,
    MetricTotalCost,
    capacity_scale_slider,
    channel_ids,
    channels,
    contact,
    customer_ids,
    mo,
    num_customers,
    pl,
    p,
    xp,
):
    # Constraint 1: Each customer contacted through at most one channel
    p.addConstraint(xp.Sum(contact[i, j] for j in channel_ids) <= 1 for i in customer_ids)

    # Constraint 2: Budget constraint
    p.addConstraint(MetricTotalCost <= BUDGET)

    # Constraint 3: Channel capacity limits (using Polars filter)
    p.addConstraint(
        xp.Sum(contact[i, j] for i in customer_ids) <=
        channels.filter(pl.col("ChannelIds") == j)["Capacity"][0] / 100 * num_customers * capacity_scale_slider.value
        for j in channel_ids
    )

    # Constraint 4: Total contacts per channel (metric tracking)
    p.addConstraint(
        xp.Sum(contact[i, j] for i in customer_ids) == MetricContactPerChannel[j]
        for j in channel_ids
    )

    # Constraint 5: Total cost per channel (metric tracking)
    p.addConstraint(
        xp.Sum(contact[i, j] * channels.filter(pl.col("ChannelIds") == j)["Cost"][0]
        for i in customer_ids) == MetricCostPerChannel[j]
        for j in channel_ids
    )

    # Constraint 6: Total cost equals sum of costs per channel (metric tracking)
    p.addConstraint(
        xp.Sum(contact[i, j] * channels.filter(pl.col("ChannelIds") == j)["Cost"][0]
        for i in customer_ids for j in channel_ids) == MetricTotalCost
    )

    mo.show_code(mo.md(f"Model has {p.attributes.rows} constraints and {p.attributes.cols} variables."))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now we solve the problem and display the solution metrics and channel allocation.
    """)
    return


@app.cell
def _(
    MetricContactPerChannel,
    MetricCostPerChannel,
    MetricTotalCost,
    channels,
    contact,
    customers,
    mo,
    pl,
    p,
    xp,
):
    p.controls.outputlog = 0        # Suppress output log

    # Solve optimization problem
    solvestatus, solstatus = p.optimize()

    if solstatus in (xp.SolStatus.OPTIMAL, xp.SolStatus.FEASIBLE):
        # Process solution - add results to channels dataframe
        channels_solution = channels.sort("ChannelIds")
        channels_solution = channels_solution.with_columns([
            pl.Series(name="MetricCostPerChannel", values=list(p.getSolution(MetricCostPerChannel).values()), dtype=pl.Float64),
            pl.Series(name="MetricContactPerChannel", values=list(p.getSolution(MetricContactPerChannel).values()), dtype=pl.Float64)
        ])

        # Process solution - add assigned actions to customers dataframe
        customers_solution = customers.sort("CustomerIds")
        contact_solution = p.getSolution(contact)
        list_actions = [key[1] for key, value in contact_solution.items() if value > 0.5]

        customers_solution = customers_solution.with_columns([
            pl.Series(name="Action", values=list_actions, dtype=pl.Int64)
        ])

        # Add action names by mapping channel IDs to names
        list_action_names = [
            channels.filter(pl.col("ChannelIds") == action_id)["Name"][0]
            for action_id in customers_solution['Action']
        ]
        customers_solution = customers_solution.with_columns([
            pl.Series(name="ActionName", values=list_action_names)
        ])

        channel_display = channels_solution.select([
            "Name",
            "MetricContactPerChannel",
            "MetricCostPerChannel"
        ])

        assignment_summary = customers_solution.group_by("ActionName").agg([
            pl.len().alias("Count"),
            pl.col("Value").mean().alias("AvgValue")
        ]).sort("Count", descending=True)

        solve_summary = mo.vstack([
            mo.md(f"""
            **Objective value:** {p.attributes.objval:,.2f} &nbsp;&nbsp; **Total cost:** ${p.getSolution(MetricTotalCost):,.2f}

            **Channel allocation:**
            """),
            channel_display,
            mo.md("**Customer assignment summary:**"),
            assignment_summary,
        ])
    else:
        channels_solution = channels
        customers_solution = customers
        solve_summary = mo.md(f"""
        **Optimization did not find a solution.** Status: {p.attributes.solvestatus}
        """)
    mo.show_code(solve_summary, position="above")
    return channels_solution, customers_solution, solstatus


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Solution Visualization

    Now we visualize the campaign optimization results using multiple plots to show channel allocation, costs, and customer distribution.
    """)
    return


@app.cell
def _(channels_solution, customers_solution, mo, pl, plt, solstatus, xp):
    if solstatus in (xp.SolStatus.OPTIMAL, xp.SolStatus.FEASIBLE):
        # Set up the figure with subplots
        fig2, axes2 = plt.subplots(2, 2, figsize=(14, 10))
        fig2.suptitle('Campaign Optimization Results', fontsize=16, fontweight='bold')

        # Prepare data for visualization
        channel_names = channels_solution["Name"].to_list()
        contacts = channels_solution["MetricContactPerChannel"].to_list()
        costs = channels_solution["MetricCostPerChannel"].to_list()

        # Color scheme
        colors = ['#3498db', '#e74c3c', '#2ecc71']

        # Plot 1: Channel Contact Distribution (Bar Chart)
        bax1 = axes2[0, 0]
        bars1 = bax1.bar(channel_names, contacts, color=colors, alpha=0.8, edgecolor='black')
        bax1.set_title('Contacts per Channel', fontweight='bold', fontsize=12)
        bax1.set_ylabel('Number of Contacts', fontsize=10)
        bax1.set_xlabel('Channel', fontsize=10)
        bax1.grid(axis='y', alpha=0.3, linestyle='--')

        # Add value labels on bars
        for bar in bars1:
            height = bar.get_height()
            bax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontweight='bold')

        # Plot 2: Channel Cost Distribution (Bar Chart)
        bax2 = axes2[0, 1]
        bars2 = bax2.bar(channel_names, costs, color=colors, alpha=0.8, edgecolor='black')
        bax2.set_title('Cost per Channel', fontweight='bold', fontsize=12)
        bax2.set_ylabel('Cost ($)', fontsize=10)
        bax2.set_xlabel('Channel', fontsize=10)
        bax2.grid(axis='y', alpha=0.3, linestyle='--')

        # Add value labels on bars
        for bar in bars2:
            height = bar.get_height()
            bax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'${height:.1f}',
                    ha='center', va='bottom', fontweight='bold')

        # Plot 3: Customer Distribution by Channel (Pie Chart)
        bax3 = axes2[1, 0]
        wedges, texts, autotexts = bax3.pie(
            contacts,
            labels=channel_names,
            colors=colors,
            autopct='%1.1f%%',
            startangle=90,
            wedgeprops=dict(edgecolor='white', linewidth=2)
        )
        bax3.set_title('Customer Distribution by Channel', fontweight='bold', fontsize=12)

        # Make percentage text bold
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(10)

        # Plot 4: Average Customer Value by Channel
        bax4 = axes2[1, 1]

        # Calculate average value per channel using Polars
        avg_values_by_channel = customers_solution.group_by("ActionName").agg([
            pl.col("Value").mean().alias("AvgValue")
        ])

        # Sort to match channel order
        channel_avg_values = []
        for name in channel_names:
            val = avg_values_by_channel.filter(pl.col("ActionName") == name)["AvgValue"]
            if len(val) > 0:
                channel_avg_values.append(val[0])
            else:
                channel_avg_values.append(0)

        bars4 = bax4.bar(channel_names, channel_avg_values, color=colors, alpha=0.8, edgecolor='black')
        bax4.set_title('Average Customer Value by Channel', fontweight='bold', fontsize=12)
        bax4.set_ylabel('Average Value ($)', fontsize=10)
        bax4.set_xlabel('Channel', fontsize=10)
        bax4.grid(axis='y', alpha=0.3, linestyle='--')

        # Add value labels on bars
        for bar in bars4:
            height = bar.get_height()
            bax4.text(bar.get_x() + bar.get_width()/2., height,
                    f'${height:.0f}',
                    ha='center', va='bottom', fontweight='bold')

        # Adjust layout to prevent overlap
        plt.tight_layout(rect=(0, 0, 1, 0.97))
        chart = fig2
    else:
        chart = mo.md("No results to plot.")
    chart
    return


if __name__ == "__main__":
    app.run()
