"""
DriveEasy Rentals — Vehicle Rental Management System (VRMS)
Main Streamlit dashboard entry-point.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database.db import init_db, query
from pathlib import Path


# ── Page Config ──────────────────────────────────────────────
st.set_page_config(
    page_title="DriveEasy Rentals VRMS",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .main .block-container { padding-top: 1.5rem; }
    h1, h2, h3 { color: #0F4C81; font-weight: 700; }
    .stMetric > div { background: #f8fafc; border-radius: 10px; padding: 12px; }
    .stButton>button { background-color: #0F4C81; color: white; border-radius: 8px; font-weight: 600; }
    .stButton>button:hover { background-color: #1a6bb5; }
</style>
""", unsafe_allow_html=True)

# ── Initialize DB ────────────────────────────────────────────
init_db()

# Check if data exists; if not, seed
row_count = query("SELECT COUNT(*) AS cnt FROM Branches")
if row_count[0]["cnt"] == 0:
    from database.seed import seed
    seed()

# ── Sidebar ──────────────────────────────────────────────────
st.sidebar.image("https://img.icons8.com/color/96/car-rental.png", width=64)
st.sidebar.title("🚗 DriveEasy VRMS")
st.sidebar.markdown("**Vehicle Rental Management System**")
st.sidebar.divider()

branch_data = query("SELECT branch_id, name FROM Branches ORDER BY name")
branch_names = ["All Branches"] + [b["name"] for b in branch_data]
selected_branch = st.sidebar.selectbox("Filter by Branch", branch_names)

st.sidebar.divider()
st.sidebar.markdown("**Quick Stats**")
total_vehicles = query("SELECT COUNT(*) as cnt FROM Vehicles")[0]["cnt"]
total_customers = query("SELECT COUNT(*) as cnt FROM Customers")[0]["cnt"]
active_rentals = query("SELECT COUNT(*) as cnt FROM RentalAgreements WHERE status = 'Active'")[0]["cnt"]
st.sidebar.metric("Total Vehicles", total_vehicles)
st.sidebar.metric("Total Customers", total_customers)
st.sidebar.metric("Active Rentals", active_rentals)

# ── Main Title ───────────────────────────────────────────────
st.title("🚗 DriveEasy Rentals Dashboard")
st.markdown("**Real-time fleet management | Rental analytics | Maintenance tracking**")
st.divider()

# ── KPI Row ──────────────────────────────────────────────────
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

total_revenue = query("SELECT COALESCE(SUM(actual_cost), 0) as rev FROM RentalAgreements WHERE status='Completed'")[0]["rev"]
avg_daily_rate = query("SELECT COALESCE(AVG(daily_rate), 0) as avg_rate FROM Vehicles")[0]["avg_rate"]
completed_rentals = query("SELECT COUNT(*) as cnt FROM RentalAgreements WHERE status='Completed'")[0]["cnt"]
pending_maintenance = query("SELECT COUNT(*) as cnt FROM MaintenanceRecords WHERE status IN ('Reported','In-Progress','Awaiting Parts')")[0]["cnt"]
fleet_utilization = round((active_rentals / total_vehicles * 100), 1) if total_vehicles > 0 else 0

kpi1.metric("💰 Total Revenue", f"${total_revenue:,.2f}")
kpi2.metric("📊 Avg Daily Rate", f"${avg_daily_rate:,.2f}")
kpi3.metric("✅ Completed Rentals", completed_rentals)
kpi4.metric("🔧 Pending Maintenance", pending_maintenance)
kpi5.metric("🚘 Fleet Utilization", f"{fleet_utilization}%")

st.divider()

# ── Charts Row 1 ─────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("Fleet by Vehicle Type")
    vtype_data = query("""
        SELECT vt.type_name, COUNT(*) as count
        FROM Vehicles v JOIN VehicleTypes vt ON v.vehicle_type_id = vt.type_id
        GROUP BY vt.type_name ORDER BY count DESC
    """)
    if vtype_data:
        df_vtype = pd.DataFrame(vtype_data)
        fig = px.pie(df_vtype, values="count", names="type_name",
                     color_discrete_sequence=px.colors.qualitative.Set2,
                     hole=0.4)
        fig.update_traces(textposition="inside", textinfo="percent+label")
        fig.update_layout(showlegend=False, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Rental Status Breakdown")
    status_data = query("""
        SELECT status, COUNT(*) as count
        FROM RentalAgreements GROUP BY status ORDER BY count DESC
    """)
    if status_data:
        df_status = pd.DataFrame(status_data)
        colors = {"Completed": "#22c55e", "Active": "#3b82f6", "Booked": "#f59e0b",
                  "Cancelled": "#ef4444", "Overdue": "#dc2626"}
        fig = px.bar(df_status, x="status", y="count", color="status",
                     color_discrete_map=colors, text="count")
        fig.update_layout(showlegend=False, margin=dict(t=20, b=20, l=20, r=20),
                          xaxis_title="", yaxis_title="Count")
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

# ── Charts Row 2 ─────────────────────────────────────────────
col3, col4 = st.columns(2)

with col3:
    st.subheader("Revenue by Branch")
    rev_data = query("""
        SELECT b.name as branch, COALESCE(SUM(ra.actual_cost), 0) as revenue
        FROM Branches b
        LEFT JOIN RentalAgreements ra ON ra.pickup_branch_id = b.branch_id AND ra.status = 'Completed'
        GROUP BY b.name ORDER BY revenue DESC
    """)
    if rev_data:
        df_rev = pd.DataFrame(rev_data)
        fig = px.bar(df_rev, x="revenue", y="branch", orientation="h",
                     color="revenue", color_continuous_scale="Blues", text_auto="$.2s")
        fig.update_layout(margin=dict(t=20, b=20, l=20, r=20),
                          xaxis_title="Revenue ($)", yaxis_title="",
                          coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

with col4:
    st.subheader("Vehicle Availability")
    avail_data = query("""
        SELECT availability, COUNT(*) as count FROM Vehicles GROUP BY availability
    """)
    if avail_data:
        df_avail = pd.DataFrame(avail_data)
        avail_colors = {"Available": "#22c55e", "Rented": "#3b82f6",
                        "Maintenance": "#f59e0b", "Retired": "#9ca3af"}
        fig = px.pie(df_avail, values="count", names="availability",
                     color="availability", color_discrete_map=avail_colors)
        fig.update_traces(textposition="inside", textinfo="percent+label")
        fig.update_layout(showlegend=False, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── Recent Rentals Table ─────────────────────────────────────
st.subheader("📋 Recent Rental Agreements")
rentals = query("""
    SELECT ra.agreement_id, c.first_name || ' ' || c.last_name as customer,
           v.make || ' ' || v.model as vehicle, v.license_plate,
           b1.name as pickup_branch, b2.name as return_branch,
           ra.scheduled_pickup, ra.scheduled_return,
           ra.estimated_cost, ra.actual_cost, ra.status, ra.insurance_type
    FROM RentalAgreements ra
    JOIN Customers c ON ra.customer_id = c.customer_id
    JOIN Vehicles v ON ra.vehicle_id = v.vehicle_id
    JOIN Branches b1 ON ra.pickup_branch_id = b1.branch_id
    JOIN Branches b2 ON ra.return_branch_id = b2.branch_id
    ORDER BY ra.scheduled_pickup DESC LIMIT 15
""")
if rentals:
    df_rentals = pd.DataFrame(rentals)
    st.dataframe(df_rentals, use_container_width=True, hide_index=True)

st.divider()

# ── Maintenance Overview ─────────────────────────────────────
st.subheader("🔧 Open Maintenance Issues")
maint = query("""
    SELECT mr.record_id, v.make || ' ' || v.model as vehicle, v.license_plate,
           mr.issue_type, mr.priority, mr.description, mr.status,
           ms.first_name || ' ' || ms.last_name as assigned_to, mr.incident_date
    FROM MaintenanceRecords mr
    JOIN Vehicles v ON mr.vehicle_id = v.vehicle_id
    LEFT JOIN MaintenanceStaff ms ON mr.staff_id = ms.staff_id
    WHERE mr.status != 'Complete'
    ORDER BY
        CASE mr.priority WHEN 'Critical' THEN 1 WHEN 'High' THEN 2 WHEN 'Medium' THEN 3 ELSE 4 END,
        mr.incident_date DESC
""")
if maint:
    df_maint = pd.DataFrame(maint)
    st.dataframe(df_maint, use_container_width=True, hide_index=True)
else:
    st.success("No open maintenance issues!")

# ── Footer ───────────────────────────────────────────────────
st.divider()
st.markdown("""
<div style='text-align: center; color: #888; padding: 16px;'>
    <strong>DriveEasy Rentals VRMS</strong> — Vehicle Rental Management System<br>
    Built with Streamlit &bull; SQLite &bull; Plotly &bull; Python<br>
    <em>Group Project — Wesley Brutus</em>
</div>
""", unsafe_allow_html=True)
