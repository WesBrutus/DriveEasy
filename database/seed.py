"""
Seed the DriveEasy database with realistic sample data.
Run:  python -m database.seed
"""

import random
from datetime import datetime, timedelta
from database.db import init_db, get_connection


def seed():
    """Populate all tables with sample data."""
    init_db(force=True)
    conn = get_connection()

    # ------------------------------------------------------------------
    # Branches (5 South-Florida locations)
    # ------------------------------------------------------------------
    branches = [
        ("DriveEasy Miami Downtown", "100 Biscayne Blvd", "Miami", "FL", "33132", "(305) 555-0101", "downtown@driveeasy.com"),
        ("DriveEasy Miami Airport", "4200 NW 21st St", "Miami", "FL", "33142", "(305) 555-0102", "airport@driveeasy.com"),
        ("DriveEasy Fort Lauderdale", "801 E Broward Blvd", "Fort Lauderdale", "FL", "33301", "(954) 555-0201", "ftl@driveeasy.com"),
        ("DriveEasy West Palm Beach", "500 Clematis St", "West Palm Beach", "FL", "33401", "(561) 555-0301", "wpb@driveeasy.com"),
        ("DriveEasy Homestead", "33 S Krome Ave", "Homestead", "FL", "33030", "(305) 555-0401", "homestead@driveeasy.com"),
    ]
    conn.executemany(
        "INSERT INTO Branches (name, address, city, state, zip_code, phone_number, email) VALUES (?,?,?,?,?,?,?)",
        branches,
    )

    # ------------------------------------------------------------------
    # Vehicle Types
    # ------------------------------------------------------------------
    vtypes = [
        ("Economy", "Compact and fuel-efficient cars"),
        ("Standard", "Mid-size sedans for everyday comfort"),
        ("SUV", "Sport utility vehicles for families and adventure"),
        ("Luxury", "Premium vehicles for a refined experience"),
        ("Van", "Passenger and cargo vans"),
        ("Truck", "Pickup trucks for hauling and towing"),
        ("Electric", "Zero-emission electric vehicles"),
        ("Convertible", "Open-top cars for sunshine driving"),
    ]
    conn.executemany("INSERT INTO VehicleTypes (type_name, description) VALUES (?,?)", vtypes)

    # ------------------------------------------------------------------
    # Vehicles (40 vehicles spread across branches)
    # ------------------------------------------------------------------
    makes_models = [
        ("Toyota", "Corolla", 1), ("Honda", "Civic", 1), ("Nissan", "Sentra", 1),
        ("Hyundai", "Elantra", 2), ("Toyota", "Camry", 2), ("Honda", "Accord", 2),
        ("Ford", "Explorer", 3), ("Toyota", "RAV4", 3), ("Jeep", "Grand Cherokee", 3),
        ("Chevrolet", "Tahoe", 3), ("BMW", "5 Series", 4), ("Mercedes-Benz", "E-Class", 4),
        ("Audi", "A6", 4), ("Chrysler", "Pacifica", 5), ("Toyota", "Sienna", 5),
        ("Ford", "F-150", 6), ("Ram", "1500", 6), ("Tesla", "Model 3", 7),
        ("Tesla", "Model Y", 7), ("Ford", "Mustang Convertible", 8),
    ]
    colors = ["White", "Black", "Silver", "Blue", "Red", "Gray", "Green"]
    fuels = {"Electric": "Electric"}
    transmissions = ["Automatic", "Automatic", "Automatic", "Manual"]

    vehicles = []
    for i in range(40):
        make, model, vtype = makes_models[i % len(makes_models)]
        year = random.randint(2020, 2025)
        color = random.choice(colors)
        daily = round(random.uniform(35, 180), 2) if vtype != 4 else round(random.uniform(150, 350), 2)
        mileage = random.randint(1000, 85000)
        fuel = fuels.get(vtypes[vtype - 1][0], random.choice(["Gasoline", "Gasoline", "Hybrid"]))
        trans = random.choice(transmissions)
        seats = 5 if vtype not in (5,) else 7
        branch = random.randint(1, 5)
        plate = f"FL-{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.randint(1000,9999)}"
        vehicles.append((plate, make, model, year, color, daily, mileage, fuel, trans, seats, "Available", vtype, branch))

    conn.executemany(
        """INSERT INTO Vehicles
        (license_plate, make, model, year, color, daily_rate, current_mileage,
         fuel_type, transmission, seats, availability, vehicle_type_id, branch_id)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        vehicles,
    )

    # ------------------------------------------------------------------
    # Customers (30)
    # ------------------------------------------------------------------
    first_names = ["James", "Maria", "Robert", "Linda", "Carlos", "Patricia", "David", "Jennifer",
                   "Michael", "Elizabeth", "William", "Ana", "John", "Sarah", "Kevin", "Laura",
                   "Daniel", "Emily", "Brian", "Nicole", "Alex", "Sophia", "Marcus", "Isabella",
                   "Tyler", "Mia", "Nathan", "Olivia", "Ryan", "Camila"]
    last_names = ["Smith", "Garcia", "Johnson", "Martinez", "Williams", "Rodriguez", "Brown", "Lopez",
                  "Jones", "Hernandez", "Davis", "Gonzalez", "Miller", "Wilson", "Moore", "Anderson",
                  "Taylor", "Thomas", "Jackson", "White", "Lee", "Harris", "Clark", "Perez",
                  "Robinson", "Walker", "Hall", "Allen", "Young", "King"]

    customers = []
    for i in range(30):
        fn, ln = first_names[i], last_names[i]
        addr = f"{random.randint(100,9999)} {random.choice(['NW','SW','NE','SE'])} {random.randint(1,200)}th St"
        city = random.choice(["Miami", "Fort Lauderdale", "West Palm Beach", "Coral Gables", "Homestead"])
        phone = f"(305) {random.randint(100,999)}-{random.randint(1000,9999)}"
        email = f"{fn.lower()}.{ln.lower()}@email.com"
        lic = f"FL-{random.randint(100000000,999999999)}"
        exp = (datetime.now() + timedelta(days=random.randint(90, 1800))).strftime("%Y-%m-%d")
        dob = (datetime.now() - timedelta(days=random.randint(7300, 22000))).strftime("%Y-%m-%d")
        pts = random.randint(0, 500)
        customers.append((fn, ln, addr, city, "FL", "33100", phone, email, lic, exp, dob, pts))

    conn.executemany(
        """INSERT INTO Customers
        (first_name, last_name, address, city, state, zip_code,
         phone_number, email, license_number, license_expiry, date_of_birth, loyalty_points)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
        customers,
    )

    # ------------------------------------------------------------------
    # Maintenance Staff (10)
    # ------------------------------------------------------------------
    staff_names = [
        ("Carlos", "Mendez", "Engine & Transmission"),
        ("Tyrone", "Washington", "Electrical Systems"),
        ("Maria", "Santos", "Body & Paint"),
        ("Jake", "O'Brien", "General"),
        ("Anil", "Patel", "Tire & Brake"),
        ("Fatima", "Al-Rashid", "HVAC & Cooling"),
        ("Pierre", "Dupont", "General"),
        ("Yuki", "Tanaka", "Electric Vehicles"),
        ("Diego", "Ramirez", "General"),
        ("Olga", "Petrov", "Diagnostics"),
    ]
    staff = []
    for i, (fn, ln, spec) in enumerate(staff_names):
        branch = (i % 5) + 1
        phone = f"(305) {random.randint(100,999)}-{random.randint(1000,9999)}"
        email = f"{fn.lower()}.{ln.lower()}@driveeasy.com"
        hire = (datetime.now() - timedelta(days=random.randint(180, 2500))).strftime("%Y-%m-%d")
        staff.append((fn, ln, spec, f"OFF-{100+i}", phone, email, hire, branch))

    conn.executemany(
        """INSERT INTO MaintenanceStaff
        (first_name, last_name, specialization, office_number, phone_number, email, hire_date, branch_id)
        VALUES (?,?,?,?,?,?,?,?)""",
        staff,
    )

    # ------------------------------------------------------------------
    # Rental Agreements (80)
    # ------------------------------------------------------------------
    statuses = ["Booked", "Active", "Completed", "Completed", "Completed", "Cancelled", "Overdue"]
    insurance = ["None", "Basic", "Basic", "Premium", "Full"]
    payments = ["Credit Card", "Credit Card", "Debit Card", "Online", "Cash"]

    rentals = []
    for _ in range(80):
        vid = random.randint(1, 40)
        cid = random.randint(1, 30)
        pb = random.randint(1, 5)
        rb = random.randint(1, 5)
        days_ago = random.randint(1, 365)
        pickup = datetime.now() - timedelta(days=days_ago)
        duration = random.randint(1, 14)
        ret = pickup + timedelta(days=duration)
        est = round(random.uniform(50, 2000), 2)
        status = random.choice(statuses)
        act_cost = round(est * random.uniform(0.9, 1.3), 2) if status == "Completed" else None
        act_pickup = pickup.strftime("%Y-%m-%d %H:%M") if status in ("Active", "Completed", "Overdue") else None
        act_return = ret.strftime("%Y-%m-%d %H:%M") if status == "Completed" else None
        ins = random.choice(insurance)
        pay = random.choice(payments)
        rentals.append((
            vid, cid, pb, rb,
            pickup.strftime("%Y-%m-%d %H:%M"), ret.strftime("%Y-%m-%d %H:%M"),
            act_pickup, act_return, est, act_cost, ins, pay, status,
        ))

    conn.executemany(
        """INSERT INTO RentalAgreements
        (vehicle_id, customer_id, pickup_branch_id, return_branch_id,
         scheduled_pickup, scheduled_return, actual_pickup, actual_return,
         estimated_cost, actual_cost, insurance_type, payment_method, status)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        rentals,
    )

    # ------------------------------------------------------------------
    # Maintenance Records (25)
    # ------------------------------------------------------------------
    issues = [
        ("Routine", "Oil change and filter replacement", "Medium"),
        ("Routine", "Tire rotation and balancing", "Low"),
        ("Urgent", "Engine warning light — diagnostic needed", "High"),
        ("Urgent", "Brake pad replacement — grinding noise", "Critical"),
        ("Routine", "Air filter and cabin filter replacement", "Low"),
        ("Inspection", "Annual safety inspection", "Medium"),
        ("Recall", "Manufacturer recall — airbag module update", "High"),
        ("Routine", "Wiper blade replacement", "Low"),
        ("Urgent", "AC compressor failure — no cooling", "High"),
        ("Routine", "Transmission fluid flush", "Medium"),
    ]
    maint_statuses = ["Reported", "In-Progress", "Complete", "Complete", "Awaiting Parts"]

    maint = []
    for _ in range(25):
        vid = random.randint(1, 40)
        cust = random.randint(1, 30) if random.random() > 0.3 else None
        days_ago = random.randint(1, 180)
        inc_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d %H:%M")
        issue = random.choice(issues)
        status = random.choice(maint_statuses)
        est_cost = round(random.uniform(50, 1500), 2)
        act_cost = round(est_cost * random.uniform(0.8, 1.2), 2) if status == "Complete" else None
        resolved = (datetime.now() - timedelta(days=days_ago - random.randint(1, 10))).strftime("%Y-%m-%d %H:%M") if status == "Complete" else None
        sid = random.randint(1, 10)
        maint.append((vid, cust, inc_date, issue[0], issue[1], status, issue[2], est_cost, act_cost, resolved, "", sid))

    conn.executemany(
        """INSERT INTO MaintenanceRecords
        (vehicle_id, reporting_customer_id, incident_date, issue_type, description,
         status, priority, estimated_cost, actual_cost, resolved_at, notes, staff_id)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
        maint,
    )

    # ------------------------------------------------------------------
    # Payments (for completed rentals)
    # ------------------------------------------------------------------
    completed = conn.execute(
        "SELECT agreement_id, actual_cost, payment_method FROM RentalAgreements WHERE status = 'Completed' AND actual_cost IS NOT NULL"
    ).fetchall()
    pay_records = []
    for r in completed:
        pay_records.append((r["agreement_id"], r["actual_cost"], r["payment_method"], "Completed"))
    conn.executemany(
        "INSERT INTO Payments (agreement_id, amount, method, status) VALUES (?,?,?,?)",
        pay_records,
    )

    conn.commit()
    conn.close()
    print(f"Database seeded at: {get_connection().execute('SELECT 1').connection}")
    print("Done! All tables populated with sample data.")


if __name__ == "__main__":
    seed()
