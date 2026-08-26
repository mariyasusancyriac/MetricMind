import random
from datetime import date, timedelta

import pandas as pd

REGIONS = {
    "North America": ["USA", "Canada"],
    "Europe": ["Germany", "France", "UK"],
    "APAC": ["India", "Singapore", "Australia"],
    "Middle East": ["UAE", "Saudi Arabia"],
}

PRODUCTS = {
    "Basic": ["Standard Software", "Basic Support"],
    "Premium": ["Enterprise Software", "Premium Support"],
    "Enterprise": ["Cloud Platform", "Enterprise Services"],
}
REGION_COST_FACTORS = {
    "North America": 1.00,
    "Europe": 1.15,
    "APAC": 0.90,
    "Middle East": 1.10,
}

PRODUCT_PRICES = {
    "Basic": (500, 1500),
    "Premium": (1500, 5000),
    "Enterprise": (5000, 15000),
}
def generate_data(num_rows=1000):
    rows = []

    start_date = date(2026, 1, 1)

    for i in range(num_rows):
        region = random.choice(list(REGIONS.keys()))
        country = random.choice(REGIONS[region])

        product_tier = random.choice(list(PRODUCTS.keys()))
        product = random.choice(PRODUCTS[product_tier])

        order_date = start_date + timedelta(days=random.randint(0, 364))

        units_sold = random.randint(1, 50)

        price_min, price_max = PRODUCT_PRICES[product_tier]
        revenue_per_unit = random.uniform(price_min, price_max)

        revenue = units_sold * revenue_per_unit

        cost_factor = REGION_COST_FACTORS[region]

        material_cost = revenue * random.uniform(0.30, 0.45) * cost_factor
        shipping_cost = revenue * random.uniform(0.05, 0.12) * cost_factor
        labor_cost = revenue * random.uniform(0.08, 0.15)

        total_cost = material_cost + shipping_cost + labor_cost
        profit = revenue - total_cost
        margin = profit / revenue

        rows.append({
            "order_id": f"ORD-{i + 1:05d}",
            "date": order_date.isoformat(),
            "region": region,
            "country": country,
            "product": product,
            "product_tier": product_tier,
            "units_sold": units_sold,
            "revenue": round(revenue, 2),
            "material_cost": round(material_cost, 2),
            "shipping_cost": round(shipping_cost, 2),
            "labor_cost": round(labor_cost, 2),
            "total_cost": round(total_cost, 2),
            "profit": round(profit, 2),
            "margin": round(margin, 4),
        })

    return pd.DataFrame(rows)

if __name__ == "__main__":
    df = generate_data(1000)
    df.to_csv("data/enterprise_data.csv", index=False)
    print(f"Generated {len(df)} rows in data/enterprise_data.csv")
    