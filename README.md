# 🚗 DriveEasy Rentals — Vehicle Rental Management System (VRMS)

A full-stack vehicle rental management dashboard built with **Python**, **Streamlit**, **SQLite**, and **Plotly**. Designed for a South Florida car rental agency with 5 branch locations.

## Features

- **Dashboard** — Real-time KPIs: revenue, fleet utilization, active rentals, maintenance alerts
- **Fleet Management** — Browse, filter, and manage 40+ vehicles across 8 types
- **Rental Agreements** — View rental history, create new bookings with cost estimation
- **Maintenance Tracker** — Priority-based issue tracking, staff workload monitoring
- **Customer Management** — Profiles, loyalty points, rental history, revenue analytics

## Database Schema

Enhanced relational database with **8 tables**, full referential integrity, and performance indexes:

| Table | Description |
|-------|-------------|
| `Branches` | 5 South Florida locations with contact info |
| `Customers` | Customer profiles with license & loyalty tracking |
| `VehicleTypes` | Lookup table for vehicle categories |
| `Vehicles` | Fleet inventory with availability & specs |
| `MaintenanceStaff` | Technicians with specializations |
| `RentalAgreements` | Bookings with pickup/return branches, insurance |
| `MaintenanceRecords` | Work orders with priority & cost tracking |
| `Payments` | Payment ledger linked to agreements |

## Quick Start

```bash
# Clone the repository
git clone https://github.com/WesBrutus/DriveEasy.git
cd DriveEasy

# Install dependencies
pip install -r requirements.txt

# Run the dashboard (auto-seeds the database on first run)
streamlit run app.py
```

## Tech Stack

- **Python 3.10+**
- **Streamlit** — Interactive web dashboard
- **SQLite** — Embedded relational database
- **Plotly** — Interactive charts and visualizations
- **Pandas** — Data manipulation

## Project Structure

```
DriveEasy/
├── app.py                  # Main dashboard
├── pages/
│   ├── 1_🚗_Fleet_Management.py
│   ├── 2_📋_Rental_Agreements.py
│   ├── 3_🔧_Maintenance.py
│   └── 4_👥_Customers.py
├── database/
│   ├── db.py               # Connection & query helpers
│   ├── schema.sql           # Full DDL with constraints & indexes
│   └── seed.py             # Sample data generator
├── data/                   # SQLite database (auto-generated)
├── .streamlit/config.toml  # Theme configuration
├── requirements.txt
└── README.md
```

## Author

**Wesley Brutus** — Group Project, DriveEasy Rentals VRMS
