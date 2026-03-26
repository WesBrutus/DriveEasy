"""Customer management page."""

import streamlit as st
import pandas as pd
import plotly.express as px
from database.db import query

st.set_page_config(page_title="Customers", page_icon="👥", layout="wide")
st.title("👥 Customer Management")
st.markdown("View customer profiles, rental history, and loyalty standings.")
st.divider()

# ── KPIs ─────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
total_cust = query("SELECT COUNT(*) as cnt FROM Customers")[0]["cnt"]
avg_loyalty = query("SELECT COALESCE(AVG(loyalty_points), 0) as avg FROM Customers")[0]["avg"]
top_spender = query("""
    SELECT c.first_name || ' ' || c.last_name as name, COALESCE(SUM(ra.actual_cost), 0) as total
    FROM Customers c JOIN RentalAgreements ra ON c.customer_id = ra.customer_id
    WHERE ra.status = 'Completed'
    GROUP BY c.customer_id ORDER BY total DESC LIMIT 1
""")
repeat_customers = query("""
    SELECT COUNT(*) as cnt FROM (
        SELECT customer_id FROM RentalAgreements GROUP BY customer_id HAVING COUNT(*) > 1
    )
""")[0]["cnt"]

k1.metric("Total Customers", total_cust)
k2.metric("Avg Loyalty Points", f"{avg_loyalty:.0f}")
k3.metric("Top Spender", top_spender[0]["name"] if top_spender else "N/A")
k4.metric("Repeat Customers", repeat_customers)

st.divider()

# ── Search ───────────────────────────────────────────────────
search = st.text_input("🔍 Search customers by name or email")

where = ""
params = []
if search:
    where = "WHERE c.first_name || ' ' || c.last_name LIKE ? OR c.email LIKE ?"
    params = [f"%{search}%", f"%{search}%"]

customers = query(f"""
    SELECT c.customer_id, c.first_name, c.last_name, c.email, c.phone_number,
           c.city, c.license_number, c.license_expiry, c.loyalty_points,
           COUNT(ra.agreement_id) as total_rentals,
           COALESCE(SUM(ra.actual_cost), 0) as total_spent
    FROM Customers c
    LEFT JOIN RentalAgreements ra ON c.customer_id = ra.customer_id AND ra.status = 'Completed'
    {where}
    GROUP BY c.customer_id
    ORDER BY total_spent DESC
""", tuple(params))

if customers:
    df = pd.DataFrame(customers)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Top spenders chart
    st.subheader("Top 10 Customers by Revenue")
    top10 = df.nlargest(10, "total_spent")
    fig = px.bar(top10, x="total_spent", y=top10["first_name"] + " " + top10["last_name"],
                 orientation="h", color="total_spent", color_continuous_scale="Blues",
                 text_auto="$.2s")
    fig.update_layout(yaxis_title="", xaxis_title="Total Spent ($)",
                      coloraxis_showscale=False, margin=dict(t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)

    # Loyalty distribution
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Loyalty Points Distribution")
        fig = px.histogram(df, x="loyalty_points", nbins=15,
                           color_discrete_sequence=["#0F4C81"])
        fig.update_layout(xaxis_title="Loyalty Points", yaxis_title="Customers",
                          margin=dict(t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Customers by City")
        city_counts = df["city"].value_counts().reset_index()
        city_counts.columns = ["city", "count"]
        fig = px.pie(city_counts, values="count", names="city",
                     color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_layout(margin=dict(t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No customers found.")
