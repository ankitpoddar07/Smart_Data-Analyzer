def generate_insight(df):
    if df.empty:
        return "No data to analyze."

    top_product = df.groupby('product_detail')['Total Bill'].sum().idxmax()
    top_amount = df.groupby('product_detail')['Total Bill'].sum().max()
    best_hour = df.groupby('Hour')['Total Bill'].sum().idxmax()

    return (
        f"The top-selling product is '{top_product}' with ₹{top_amount:.2f} in sales. "
        f"Most sales occur around {best_hour}:00 hours."
    )