import sqlite3
import random
from faker import Faker

# Initialize Faker for sample data
fake = Faker()

# Connect to (or create) the SQLite database
conn = sqlite3.connect("gross.db")
cursor = conn.cursor()

# Enable foreign key constraints
cursor.execute("PRAGMA foreign_keys = ON;")

# Drop existing tables for a clean reset
cursor.executescript("""
DROP TABLE IF EXISTS Orders;
DROP TABLE IF EXISTS Products;
DROP TABLE IF EXISTS Users;
""")

# ------------------------------
# Create tables (no license types)
# ------------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS Users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone_number TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10, 2),
    status TEXT DEFAULT 'paid',
    payment_method TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (product_id) REFERENCES Products(product_id)
);
""")

# ------------------------------
# Insert fixed products
# ------------------------------

products_info = [
    ("flamehamster", "Web browser", 99.99),
    ("rumblechirp", "Email client", 149.99),
    ("verbiage++", "Content management system", 299.99),
    ("gunieapigment", "SVG drawing/editing tool", 249.99),
    ("emrgency", "Electronic medical record system", 399.99),
]

for name, desc, price in products_info:
    cursor.execute("""
        INSERT INTO Products (product_name, description, price)
        VALUES (?, ?, ?);
    """, (name, desc, price))

# ------------------------------
# Insert sample users
# ------------------------------

users = []
for _ in range(20):
    first = fake.first_name()
    last = fake.last_name()
    email = fake.unique.email()
    phone = fake.phone_number()
    cursor.execute("""
        INSERT INTO Users (first_name, last_name, email, phone_number)
        VALUES (?, ?, ?, ?);
    """, (first, last, email, phone))
    users.append(cursor.lastrowid)

# ------------------------------
# Insert sample orders
# ------------------------------

product_ids = [1, 2, 3, 4, 5]
statuses = ["paid", "pending", "canceled"]
methods = ["credit card", "paypal", "bank transfer"]

for _ in range(50):
    user_id = random.choice(users)
    product_id = random.choice(product_ids)
    cursor.execute("SELECT price FROM Products WHERE product_id = ?", (product_id,))
    price = cursor.fetchone()[0]
    cursor.execute("""
        INSERT INTO Orders (user_id, product_id, total_amount, status, payment_method)
        VALUES (?, ?, ?, ?, ?);
    """, (
        user_id,
        product_id,
        price,
        random.choice(statuses),
        random.choice(methods)
    ))

# Commit and close
conn.commit()
conn.close()

print("✅ Database created and populated with 5 products, 20 users, and 50 orders (no license types).")
