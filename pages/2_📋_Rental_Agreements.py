"""Rental Agreements page — view and create rental agreements."""

import streamlit as st
import pandas as pd
import plotly.express as px
from database.db import query, execute
from datetime import datetime, timedelta

st.set_page_config(page_title="Rental Agreements", page_icon="📋", layout="wide")
st.title("📋 Rental Agreements")
st.markdown("View rental history, create new bookings, and track active rentals.")
st.divider()

# ── Tabs ─────────────────────────────────────────────────────
tab_view, tab_new = st.tabs(["📊 View Agreements", "➕ New Booking"])

with tab_view:
    # Filters
    f1, f2, f3 = st.columns(3)
    with f1:
        status_filter = st.selectbox("Status", ["All", "Booked", "Active", "Completed", "Cancelled", "Overdue"])
    with f2:
        sort_by = st.selectbox("Sort By", ["Newest First", "Oldest First", "Highest Cost", "Lowest Cost"])
    with f3:
        limit = st.slider("Max Results", 10, 100, 25)

    where = ""
    params = []
    if status_filter != "All":
        where = "WHERE ra.status = ?"
        params.append(status_filter)

    order_map = {
        "Newest First": "ra.scheduled_pickup DESC",
        "Oldest First": "ra.scheduled_pickup ASC",
        "Highest Cost": "COALESCE(ra.actual_cost, ra.estimated_cost) DESC",
        "Lowest Cost": "COALESCE(ra.actual_cost, ra.estimated_cost) ASC",
    }

    rentals = query(f"""
        SELECT ra.agreement_id, c.first_name || ' ' || c.last_name as customer,
               v.make || ' ' || v.model as vehicle, v.license_plate,
               b1.name as pickup_branch, b2.name as return_branch,
               ra.scheduled_pickup, ra.scheduled_return,
               ra.estimated_cost, ra.actual_cost, ra.insurance_type,
               ra.payment_method, ra.status
        FROM RentalAgreements ra
        JOIN Customers c ON ra.customer_id = c.customer_id
        JOIN Vehicles v ON ra.vehicle_id = v.vehicle_id
        JOIN Branches b1 ON ra.pickup_branch_id = b1.branch_id
        JOIN Branches b2 ON ra.return_branch_id = b2.branch_id
        {where}
        ORDER BY {order_map[sort_by]}
        LIMIT ?
    """, tuple(params + [limit]))

    if rentals:
        df = pd.DataFrame(rentals)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Shown", len(df))
        m2.metric("Total Est. Cost", f"${df['estimated_cost'].sum():,.2f}")
        completed_cost = df[df['actual_cost'].notna()]['actual_cost'].sum()
        m3.metric("Total Actual Cost", f"${completed_cost:,.2f}")
        m4.metric("Avg Rental Cost", f"${df['estimated_cost'].mean():,.2f}")

        st.dataframe(df, use_container_width=True, hide_index=True)

        # Status distribution chart
        st.subheader("Status Distribution")
        status_counts = df["status"].value_counts().reset_index()
        status_counts.columns = ["status", "count"]
        colors = {"Completed": "#22c55e", "Active": "#3b82f6", "Booked": "#f59e0b",
                  "Cancelled": "#ef4444", "Overdue": "#dc2626"}
        fig = px.pie(status_counts, values="count", names="status",
                     color="status", color_discrete_map=colors)
        fig.update_layout(margin=dict(t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No rental agreements found with the current filters.")

with tab_new:
    st.subheader("Create New Booking")

    n1, n2 = st.columns(2)

    customers = query("SELECT customer_id, first_name || ' ' || last_name as name FROM Customers ORDER BY name")
    vehicles = query("""
        SELECT v.vehicle_id, v.make || ' ' || v.model || ' (' || v.license_plate || ') — $' ||
               CAST(v.daily_rate AS TEXT) || '/day' as label, v.daily_rate
        FROM Vehicles v WHERE v.availability = 'Available' ORDER BY v.make
    """)
    branches = query("SELECT branch_id, name FROM Branches ORDER BY name")

    with n1:
        cust = st.selectbox("Customer", options=customers, format_func=lambda x: x["name"])
        vehicle = st.selectbox("Vehicle", options=vehicles, format_func=lambda x: x["label"])
        pickup_date = st.date_input("Pickup Date", value=datetime.now().date())
        pickup_branch = st.selectbox("Pickup Branch", options=branches, format_func=lambda x: x["name"])

    with n2:
        return_date = st.date_input("Return Date", value=(datetime.now() + timedelta(days=3)).date())
        return_branch = st.selectbox("Return Branch", options=branches, format_func=lambda x: x["name"], key="ret_branch")
        insurance = st.selectbox("Insurance", ["Basic", "Premium", "Full", "None"])
        payment = st.selectbox("Payment Method", ["Credit Card", "Debit Card", "Cash", "Online"])

    if vehicle and return_date > pickup_date:
        days = (return_date - pickup_date).days
        est_cost = round(vehicle["daily_rate"] * days, 2)
        st.info(f"**Estimated Cost:** {days} days × ${vehicle['daily_rate']:.2f}/day = **${est_cost:,.2f}**")

        if st.button("📝 Create Booking", type="primary"):
            execute("""
                INSERT INTO RentalAgreements
                (vehicle_id, customer_id, pickup_branch_id, return_branch_id,
                 scheduled_pickup, scheduled_return, estimated_cost, insurance_type,
                 payment_method, status)
                VALUES (?,?,?,?,?,?,?,?,?,?)
            """, (
                vehicle["vehicle_id"], cust["customer_id"],
                pickup_branch["branch_id"], return_branch["branch_id"],
                pickup_date.strftime("%Y-%m-%d 10:00"),
                return_date.strftime("%Y-%m-%d 10:00"),
                est_cost, insurance, payment, "Booked",
            ))
            st.success("Booking created successfully!")
            st.balloons()
    elif return_date <= pickup_date:
        st.warning("Return date must be after the pickup date.")
