"""Fleet Management page — view, filter, and manage vehicles."""

import streamlit as st
import pandas as pd
import plotly.express as px
from database.db import query, execute

st.set_page_config(page_title="Fleet Management", page_icon="🚗", layout="wide")
st.title("🚗 Fleet Management")
st.markdown("Browse, filter, and manage all vehicles in the DriveEasy fleet.")
st.divider()

# ── Filters ──────────────────────────────────────────────────
f1, f2, f3, f4 = st.columns(4)

branches = query("SELECT branch_id, name FROM Branches ORDER BY name")
branch_opts = {b["name"]: b["branch_id"] for b in branches}
with f1:
    sel_branch = st.selectbox("Branch", ["All"] + list(branch_opts.keys()))

vtypes = query("SELECT type_id, type_name FROM VehicleTypes ORDER BY type_name")
vtype_opts = {v["type_name"]: v["type_id"] for v in vtypes}
with f2:
    sel_type = st.selectbox("Vehicle Type", ["All"] + list(vtype_opts.keys()))

with f3:
    sel_avail = st.selectbox("Availability", ["All", "Available", "Rented", "Maintenance", "Retired"])

with f4:
    sel_fuel = st.selectbox("Fuel Type", ["All", "Gasoline", "Diesel", "Electric", "Hybrid"])

# Build query
where_clauses = []
params = []
if sel_branch != "All":
    where_clauses.append("v.branch_id = ?")
    params.append(branch_opts[sel_branch])
if sel_type != "All":
    where_clauses.append("v.vehicle_type_id = ?")
    params.append(vtype_opts[sel_type])
if sel_avail != "All":
    where_clauses.append("v.availability = ?")
    params.append(sel_avail)
if sel_fuel != "All":
    where_clauses.append("v.fuel_type = ?")
    params.append(sel_fuel)

where = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

vehicles = query(f"""
    SELECT v.vehicle_id, v.license_plate, v.make, v.model, v.year, v.color,
           v.daily_rate, v.current_mileage, v.fuel_type, v.transmission, v.seats,
           v.availability, vt.type_name as vehicle_type, b.name as branch
    FROM Vehicles v
    LEFT JOIN VehicleTypes vt ON v.vehicle_type_id = vt.type_id
    JOIN Branches b ON v.branch_id = b.branch_id
    {where}
    ORDER BY v.make, v.model
""", tuple(params))

st.markdown(f"**Showing {len(vehicles)} vehicles**")

if vehicles:
    df = pd.DataFrame(vehicles)

    # Summary metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Vehicles", len(df))
    m2.metric("Avg Daily Rate", f"${df['daily_rate'].mean():.2f}")
    m3.metric("Avg Mileage", f"{df['current_mileage'].mean():,.0f} mi")
    m4.metric("Available", len(df[df["availability"] == "Available"]))

    st.divider()

    # Vehicle table
    st.dataframe(
        df[["license_plate", "make", "model", "year", "color", "vehicle_type",
            "daily_rate", "fuel_type", "transmission", "availability", "branch"]],
        use_container_width=True, hide_index=True,
    )

    # Charts
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Daily Rate Distribution")
        fig = px.histogram(df, x="daily_rate", nbins=20,
                           color_discrete_sequence=["#0F4C81"])
        fig.update_layout(xaxis_title="Daily Rate ($)", yaxis_title="Count",
                          margin=dict(t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Fleet by Make")
        make_counts = df["make"].value_counts().reset_index()
        make_counts.columns = ["make", "count"]
        fig = px.bar(make_counts.head(10), x="count", y="make", orientation="h",
                     color_discrete_sequence=["#0F4C81"])
        fig.update_layout(yaxis_title="", xaxis_title="Count",
                          margin=dict(t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No vehicles match the current filters.")
