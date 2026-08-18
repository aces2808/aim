import numpy as np

# ============================================================
# SUPPLIER CONFIGURATION
# ============================================================

suppliers = {
    "FarFarAway": {"lead": 4, "capacity": 60, "setup_cost": 1_000_000, "cost_A": 165, "cost_B": 185},
    "FarAway": {"lead": 3, "capacity": 60, "setup_cost": 2_000_000, "cost_A": 165, "cost_B": 185},
    "PrettyClose": {"lead": 0, "capacity": 35, "setup_cost": 1_000_000, "cost_A": 175, "cost_B": 195},
    "VeryClose": {"lead": 0, "capacity": 40, "setup_cost": 2_000_000, "cost_A": 175, "cost_B": 195},
}

# Demand per month (in thousand units)
demand_A = np.array([0, 0, 0, 0, 54, 54, 54, 54, 54, 54, 54, 54])
demand_B = np.array([0, 0, 0, 0, 31, 31, 31, 31, 31, 31, 31, 31])

# Selling prices
price_A = 300
price_B = 350

# Costs
inventory_cost = 2
liquidation_loss = 50

# ============================================================
# SIMULATION ENGINE — dynamic supplier selection
# ============================================================


def simulate_model(demand, production_plan, model_costs, price):
    inventory = 0
    revenue = 0
    cost = 0
    inventory_cost_total = 0
    liquidation_total = 0

    used_suppliers = set()
    deliveries = np.zeros(12)

    # Build delivery schedule based on lead times + begin month
    for supplier, config in production_plan.items():
        monthly_units = config["units"]
        begin_month = config["begin"]
        lead = suppliers[supplier]["lead"]

        for month in range(begin_month, 12):
            units = monthly_units[month]
            if units > 0:
                used_suppliers.add(supplier)
                delivery_month = month + lead
                if delivery_month < 12:
                    deliveries[delivery_month] += units

    # Monthly simulation
    for month in range(12):
        inventory += deliveries[month]

        sold = min(inventory, demand[month])
        revenue += sold * price
        inventory -= sold

        inventory_cost_total += inventory * inventory_cost

        if month == 11 and inventory > 0:
            liquidation_total += inventory * liquidation_loss

    # Production cost
    for supplier, config in production_plan.items():
        monthly_units = config["units"]
        for month in range(12):
            cost += monthly_units[month] * model_costs[supplier]

    # Setup cost
    setup_cost_total = sum(suppliers[s]["setup_cost"] for s in used_suppliers)

    gross_margin = revenue - cost - inventory_cost_total - liquidation_total - setup_cost_total
    return gross_margin


# ============================================================
# DYNAMIC PRODUCTION PLAN BUILDER
# ============================================================


def build_production_plan(selected_suppliers):
    """
    selected_suppliers is a dict like:
    {
        "FarFarAway": {
            "units": [...12 values...],
            "begin": 1
        },
        "FarAway": {
            "units": [...12 values...],
            "begin": 2
        }
    }

    Any supplier NOT included defaults to:
    units = [0]*12
    begin = 0
    """

    plan = {}

    for supplier in suppliers.keys():
        if supplier in selected_suppliers:
            plan[supplier] = {"units": selected_suppliers[supplier]["units"], "begin": selected_suppliers[supplier]["begin"]}
        else:
            plan[supplier] = {"units": [0] * 12, "begin": 0}

    return plan


# ============================================================
# EXAMPLE: USER INPUT PRODUCTION PLAN
# ============================================================

selected_suppliers_A = {"FarFarAway": {"units": [50] * 12, "begin": 1}, "FarAway": {"units": [20] * 12, "begin": 1}}

selected_suppliers_B = {"FarAway": {"units": [30] * 12, "begin": 1}, "PrettyClose": {"units": [0, 0, 0, 0, 0, 5, 5, 0, 0, 0, 0, 0], "begin": 5}}

plan_A = build_production_plan(selected_suppliers_A)
plan_B = build_production_plan(selected_suppliers_B)

margin_A = simulate_model(demand_A, plan_A, {s: suppliers[s]["cost_A"] for s in suppliers}, price_A)

margin_B = simulate_model(demand_B, plan_B, {s: suppliers[s]["cost_B"] for s in suppliers}, price_B)

print("Model A Margin:", margin_A)
print("Model B Margin:", margin_B)
print("Total Margin:", margin_A + margin_B)
