"""Maintenance tracking page — view and manage maintenance records."""

import streamlit as st
import pandas as pd
import plotly.express as px
from database.db import query

st.set_page_config(page_title="Maintenance", page_icon="🔧", layout="wide")
st.title("🔧 Maintenance Tracker")
st.markdown("Monitor vehicle maintenance, track repairs, and manage work orders.")
st.divider()

# ── KPIs ─────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
total = query("SELECT COUNT(*) as cnt FROM MaintenanceRecords")[0]["cnt"]
open_issues = query("SELECT COUNT(*) as cnt FROM MaintenanceRecords WHERE status != 'Complete'")[0]["cnt"]
critical = query("SELECT COUNT(*) as cnt FROM MaintenanceRecords WHERE priority = 'Critical' AND status != 'Complete'")[0]["cnt"]
avg_cost = query("SELECT COALESCE(AVG(actual_cost), 0) as avg FROM MaintenanceRecords WHERE actual_cost IS NOT NULL")[0]["avg"]

k1.metric("Total Records", total)
k2.metric("Open Issues", open_issues)
k3.metric("Critical Open", critical, delta=None if critical == 0 else f"{critical} need attention")
k4.metric("Avg Repair Cost", f"${avg_cost:,.2f}")

st.divider()

# ── Charts ───────────────────────────────────────────────────
c1, c2 = st.columns(2)

with c1:
    st.subheader("Issues by Type")
    type_data = query("""
        SELECT issue_type, COUNT(*) as count FROM MaintenanceRecords GROUP BY issue_type ORDER BY count DESC
    """)
    if type_data:
        df_type = pd.DataFrame(type_data)
        fig = px.pie(df_type, values="count", names="issue_type",
                     color_discrete_sequence=px.colors.qualitative.Set2, hole=0.35)
        fig.update_layout(margin=dict(t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("Issues by Priority")
    pri_data = query("""
        SELECT priority, COUNT(*) as count FROM MaintenanceRecords GROUP BY priority
    """)
    if pri_data:
        df_pri = pd.DataFrame(pri_data)
        pri_colors = {"Critical": "#dc2626", "High": "#f59e0b", "Medium": "#3b82f6", "Low": "#22c55e"}
        fig = px.bar(df_pri, x="priority", y="count", color="priority",
                     color_discrete_map=pri_colors, text="count")
        fig.update_traces(textposition="outside")
        fig.update_layout(showlegend=False, margin=dict(t=20, b=20),
                          xaxis_title="", yaxis_title="Count")
        st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── Full Records ─────────────────────────────────────────────
st.subheader("All Maintenance Records")

f1, f2 = st.columns(2)
with f1:
    filter_status = st.selectbox("Filter by Status", ["All", "Reported", "In-Progress", "Awaiting Parts", "Complete", "Cancelled"])
with f2:
    filter_priority = st.selectbox("Filter by Priority", ["All", "Critical", "High", "Medium", "Low"])

where_parts = []
params = []
if filter_status != "All":
    where_parts.append("mr.status = ?")
    params.append(filter_status)
if filter_priority != "All":
    where_parts.append("mr.priority = ?")
    params.append(filter_priority)
where = "WHERE " + " AND ".join(where_parts) if where_parts else ""

records = query(f"""
    SELECT mr.record_id, v.make || ' ' || v.model as vehicle, v.license_plate,
           mr.issue_type, mr.priority, mr.description, mr.status,
           ms.first_name || ' ' || ms.last_name as assigned_to,
           mr.estimated_cost, mr.actual_cost, mr.incident_date, mr.resolved_at
    FROM MaintenanceRecords mr
    JOIN Vehicles v ON mr.vehicle_id = v.vehicle_id
    LEFT JOIN MaintenanceStaff ms ON mr.staff_id = ms.staff_id
    {where}
    ORDER BY
        CASE mr.priority WHEN 'Critical' THEN 1 WHEN 'High' THEN 2 WHEN 'Medium' THEN 3 ELSE 4 END,
        mr.incident_date DESC
""", tuple(params))

if records:
    df = pd.DataFrame(records)
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("No maintenance records match the current filters.")

# ── Staff Workload ───────────────────────────────────────────
st.divider()
st.subheader("Staff Workload")
staff_data = query("""
    SELECT ms.first_name || ' ' || ms.last_name as staff, ms.specialization,
           COUNT(mr.record_id) as total_jobs,
           SUM(CASE WHEN mr.status != 'Complete' THEN 1 ELSE 0 END) as open_jobs
    FROM MaintenanceStaff ms
    LEFT JOIN MaintenanceRecords mr ON ms.staff_id = mr.staff_id
    GROUP BY ms.staff_id ORDER BY open_jobs DESC
""")
if staff_data:
    df_staff = pd.DataFrame(staff_data)
    st.dataframe(df_staff, use_container_width=True, hide_index=True)
