import csv
import json
import os
import random
from datetime import datetime, timedelta
from pathlib import Path


random.seed(42)

BASE_DIR = Path(__file__).resolve().parent
INCLUDE_DIR = BASE_DIR.parent
DATA_DIR = INCLUDE_DIR / "data" / "raw"
CSV_DIR = DATA_DIR / "csv"
JSON_DIR = DATA_DIR / "json"

CSV_DIR.mkdir(parents=True, exist_ok=True)
JSON_DIR.mkdir(parents=True, exist_ok=True)


# =============================================================================
# Configuration: row counts
# =============================================================================
NUM_CATEGORIES = 5
NUM_CUSTOMERS = 20
NUM_PRODUCTS = 30
NUM_ORDERS = 80
MIN_ITEMS_PER_ORDER = 1
MAX_ITEMS_PER_ORDER = 4
NUM_REVIEWS = 40


# =============================================================================
# Helper functions
# =============================================================================
def write_csv(filename: str, fieldnames: list[str], rows: list[dict]) -> None:
    path = CSV_DIR / filename
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Created {path} ({len(rows)} rows)")


def write_json(filename: str, rows: list[dict]) -> None:
    path = JSON_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print(f"Created {path} ({len(rows)} records)")


def random_date(start_date: datetime, end_date: datetime) -> datetime:
    delta = end_date - start_date
    return start_date + timedelta(days=random.randint(0, delta.days))


def random_date_str(start_date: datetime, end_date: datetime) -> str:
    return random_date(start_date, end_date).strftime("%Y-%m-%d")


def random_datetime_between(start_date: datetime, end_date: datetime) -> datetime:
    delta_seconds = int((end_date - start_date).total_seconds())
    return start_date + timedelta(seconds=random.randint(0, delta_seconds))


def random_datetime_iso(start_date: datetime, end_date: datetime) -> str:
    return random_datetime_between(start_date, end_date).strftime("%Y-%m-%dT%H:%M:%S")


def weighted_choice(options: list[tuple]) -> str | int:
    values = [x[0] for x in options]
    weights = [x[1] for x in options]
    return random.choices(values, weights=weights, k=1)[0]


def clean_money(value: float) -> float:
    return round(value, 2)


# =============================================================================
# Base dictionaries / source values
# =============================================================================
first_names = [
    "Olena", "Anna", "Maksym", "Iryna", "Sofiia", "Andrii", "Dmytro", "Kateryna",
    "Yulia", "Taras", "Oksana", "Ivan", "Natalia", "Mykhailo", "Viktoriia",
    "Denys", "Alina", "Bohdan", "Marta", "Artem", "Tetiana", "Roman"
]

last_names = [
    "Kovalenko", "Shevchenko", "Bondarenko", "Tkachenko", "Melnyk", "Kravchenko",
    "Polishchuk", "Boyko", "Tkachuk", "Savchenko", "Lysenko", "Moroz",
    "Rudenko", "Petrenko", "Koval", "Marchenko"
]

cities = ["Kyiv", "Lviv", "Odesa", "Dnipro", "Kharkiv", "Vinnytsia", "Poltava"]
country = "Ukraine"

carriers = ["Nova Poshta", "Ukrposhta", "Meest Express"]
payment_methods = ["card", "apple_pay", "google_pay", "cash_on_delivery"]
review_sources = ["website", "mobile_app", "email_followup"]

category_definitions = [
    {"category_id": 1, "category_name": "Smartphones", "department_name": "Electronics"},
    {"category_id": 2, "category_name": "Laptops", "department_name": "Electronics"},
    {"category_id": 3, "category_name": "Kitchen", "department_name": "Home Goods"},
    {"category_id": 4, "category_name": "Fitness", "department_name": "Sports"},
    {"category_id": 5, "category_name": "Accessories", "department_name": "Lifestyle"},
]

brands_by_category = {
    "Smartphones": ["Apple", "Samsung", "Xiaomi", "Google"],
    "Laptops": ["Lenovo", "HP", "Dell", "Asus"],
    "Kitchen": ["Philips", "Tefal", "Bosch", "Xiaomi Home"],
    "Fitness": ["Xiaomi", "Fitbit", "Adidas", "Nike"],
    "Accessories": ["Baseus", "Anker", "Logitech", "Belkin"],
}

product_names_by_category = {
    "Smartphones": ["Phone Case", "Wireless Charger", "Screen Protector", "Power Bank", "Smartphone"],
    "Laptops": ["Laptop Sleeve", "Laptop Stand", "Wireless Mouse", "USB-C Hub", "Laptop"],
    "Kitchen": ["Blender", "Kettle", "Air Fryer", "Toaster", "Coffee Maker"],
    "Fitness": ["Yoga Mat", "Resistance Bands", "Fitness Tracker", "Dumbbells", "Water Bottle"],
    "Accessories": ["Headphones", "Bluetooth Speaker", "Keyboard", "Mouse Pad", "Cable Organizer"],
}

review_texts = [
    "great product",
    "good value for money",
    "quality is decent",
    "fast delivery and nice packaging",
    "works as expected",
    "not bad overall",
    "excellent quality",
    "would buy again",
    "battery life could be better",
    "size was a bit smaller than expected",
]


# =============================================================================
# Date ranges
# =============================================================================
signup_start = datetime(2024, 1, 1)
signup_end = datetime(2025, 6, 30)

product_start = datetime(2024, 1, 1)
product_end = datetime(2025, 6, 30)

order_start = datetime(2025, 1, 1)
order_end = datetime(2025, 6, 30)


# =============================================================================
# 1. categories.csv
# =============================================================================
categories = category_definitions[:NUM_CATEGORIES]

write_csv(
    "categories.csv",
    ["category_id", "category_name", "department_name"],
    categories,
)


# =============================================================================
# 2. customers.csv
# =============================================================================
customers = []
used_emails = set()

for customer_id in range(1, NUM_CUSTOMERS + 1):
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)

    email = f"{first_name.lower()}.{last_name.lower()}{customer_id}@example.com"
    while email in used_emails:
        email = f"{first_name.lower()}.{last_name.lower()}{customer_id}{random.randint(1,999)}@example.com"

    used_emails.add(email)

    phone = f"+38067{random.randint(1000000, 9999999)}"
    city = random.choice(cities)
    signup_date = random_date_str(signup_start, signup_end)

    customer_status = weighted_choice([
        ("active", 0.80),
        ("inactive", 0.15),
        ("blocked", 0.05),
    ])

    customers.append({
        "customer_id": customer_id,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone": phone,
        "city": city,
        "country": country,
        "signup_date": signup_date,
        "customer_status": customer_status,
    })

write_csv(
    "customers.csv",
    [
        "customer_id", "first_name", "last_name", "email", "phone",
        "city", "country", "signup_date", "customer_status"
    ],
    customers,
)


# =============================================================================
# 3. products.csv
# =============================================================================
products = []
product_id = 1

for _ in range(NUM_PRODUCTS):
    category = random.choice(categories)
    category_name = category["category_name"]

    product_root = random.choice(product_names_by_category[category_name])
    brand = random.choice(brands_by_category[category_name])
    product_name = f"{brand} {product_root} {random.choice(['Mini', 'Pro', 'Plus', 'Max', 'Lite'])}"

    if category_name == "Smartphones":
        price = random.randint(8000, 45000)
    elif category_name == "Laptops":
        price = random.randint(15000, 70000)
    elif category_name == "Kitchen":
        price = random.randint(900, 9000)
    elif category_name == "Fitness":
        price = random.randint(300, 7000)
    else:
        price = random.randint(200, 6000)

    cost = clean_money(price * random.uniform(0.55, 0.80))
    is_active = random.choice(["true", "false"]) if random.random() < 0.10 else "true"
    created_at = random_date_str(product_start, product_end)

    products.append({
        "product_id": product_id,
        "product_name": product_name,
        "category_id": category["category_id"],
        "brand": brand,
        "price": clean_money(price),
        "cost": cost,
        "is_active": is_active,
        "created_at": created_at,
    })

    product_id += 1

write_csv(
    "products.csv",
    ["product_id", "product_name", "category_id", "brand", "price", "cost", "is_active", "created_at"],
    products,
)


# =============================================================================
# 4. orders.csv
# =============================================================================
orders = []
order_records_for_children = []

for order_id in range(1, NUM_ORDERS + 1):
    customer = random.choice(customers)
    order_dt = random_date(order_start, order_end)
    order_date = order_dt.strftime("%Y-%m-%d")

    order_status = weighted_choice([
        ("delivered", 0.60),
        ("shipped", 0.15),
        ("processing", 0.10),
        ("cancelled", 0.10),
        ("returned", 0.05),
    ])

    orders.append({
        "order_id": order_id,
        "customer_id": customer["customer_id"],
        "order_date": order_date,
        "order_status": order_status,
        "shipping_city": customer["city"],
        "shipping_country": customer["country"],
    })

    order_records_for_children.append({
        "order_id": order_id,
        "customer_id": customer["customer_id"],
        "order_date": order_dt,
        "order_status": order_status,
        "shipping_city": customer["city"],
        "shipping_country": customer["country"],
    })

write_csv(
    "orders.csv",
    ["order_id", "customer_id", "order_date", "order_status", "shipping_city", "shipping_country"],
    orders,
)


# =============================================================================
# 5. order_items.csv
# =============================================================================
order_items = []
order_item_id = 1
order_totals = {}

for order in order_records_for_children:
    items_count = random.randint(MIN_ITEMS_PER_ORDER, MAX_ITEMS_PER_ORDER)
    selected_products = random.sample(products, k=min(items_count, len(products)))
    total_amount = 0.0

    for product in selected_products:
        quantity = random.randint(1, 3)
        unit_price = float(product["price"])
        gross_amount = unit_price * quantity

        discount_amount = 0.0
        net_amount = gross_amount - discount_amount
        total_amount += net_amount

        order_items.append({
            "order_item_id": order_item_id,
            "order_id": order["order_id"],
            "product_id": product["product_id"],
            "quantity": quantity,
            "unit_price": clean_money(unit_price),
            "discount_amount": clean_money(discount_amount),
        })

        order_item_id += 1

    order_totals[order["order_id"]] = clean_money(total_amount)

write_csv(
    "order_items.csv",
    ["order_item_id", "order_id", "product_id", "quantity", "unit_price", "discount_amount"],
    order_items,
)


# =============================================================================
# 6. payments.csv
# =============================================================================
payments = []
payment_id = 1

for order in order_records_for_children:
    if order["order_status"] == "cancelled" and random.random() < 0.5:
        continue

    payment_date = order["order_date"] + timedelta(days=random.randint(0, 2))

    if order["order_status"] == "cancelled":
        payment_status = random.choice(["failed", "refunded"])
    elif order["order_status"] == "returned":
        payment_status = "refunded"
    else:
        payment_status = "paid"

    payment_amount = order_totals.get(order["order_id"], 0.0)
    if payment_status == "failed":
        payment_amount = 0.0

    payments.append({
        "payment_id": payment_id,
        "order_id": order["order_id"],
        "payment_date": payment_date.strftime("%Y-%m-%d"),
        "payment_method": random.choice(payment_methods),
        "payment_status": payment_status,
        "payment_amount": clean_money(payment_amount),
    })

    payment_id += 1

write_csv(
    "payments.csv",
    ["payment_id", "order_id", "payment_date", "payment_method", "payment_status", "payment_amount"],
    payments,
)


# =============================================================================
# 7. shipments.csv
# =============================================================================
shipments = []
shipment_id = 1

for order in order_records_for_children:
    if order["order_status"] in ("cancelled", "processing"):
        continue

    shipment_date = order["order_date"] + timedelta(days=random.randint(1, 3))

    if order["order_status"] == "shipped":
        delivery_date = ""
        shipment_status = "in_transit"
    else:
        delivery_delay = random.randint(1, 6)
        delivery_date_dt = shipment_date + timedelta(days=delivery_delay)

        if order["order_status"] == "returned":
            shipment_status = "returned"
        else:
            shipment_status = "delivered"

        delivery_date = delivery_date_dt.strftime("%Y-%m-%d")

    shipments.append({
        "shipment_id": shipment_id,
        "order_id": order["order_id"],
        "shipment_date": shipment_date.strftime("%Y-%m-%d"),
        "delivery_date": delivery_date,
        "shipment_status": shipment_status,
        "carrier": random.choice(carriers),
        "shipping_cost": clean_money(random.uniform(50, 250)),
    })

    shipment_id += 1

write_csv(
    "shipments.csv",
    ["shipment_id", "order_id", "shipment_date", "delivery_date", "shipment_status", "carrier", "shipping_cost"],
    shipments,
)


# =============================================================================
# 8. reviews.json
# Nested metadata structure
# =============================================================================
reviews = []
review_id = 1

delivered_or_returned_orders = [
    o for o in order_records_for_children
    if o["order_status"] in ("delivered", "returned")
]

review_candidates = []
for oi in order_items:
    order_id = oi["order_id"]
    matching_order = next(
        (o for o in delivered_or_returned_orders if o["order_id"] == order_id),
        None,
    )
    if matching_order:
        review_candidates.append((matching_order, oi))

random.shuffle(review_candidates)
review_candidates = review_candidates[:NUM_REVIEWS]

for order, item in review_candidates:
    review_date = order["order_date"] + timedelta(days=random.randint(3, 14))

    review_datetime_start = datetime(
        review_date.year, review_date.month, review_date.day, 8, 0, 0
    )
    review_datetime_end = datetime(
        review_date.year, review_date.month, review_date.day, 22, 0, 0
    )

    rating = weighted_choice([
        (5, 0.35),
        (4, 0.30),
        (3, 0.20),
        (2, 0.10),
        (1, 0.05),
    ])

    reviews.append({
        "review_id": review_id,
        "customer_id": order["customer_id"],
        "product_id": item["product_id"],
        "rating": rating,
        "review_text": random.choice(review_texts),
        "metadata": {
            "review_created_at": random_datetime_iso(review_datetime_start, review_datetime_end),
            "source": random.choice(review_sources),
            "verified_purchase": True,
            "order_id": order["order_id"],
        },
    })

    review_id += 1

write_json("reviews.json", reviews)

print("\nAll source files were generated successfully.")
print(f"CSV files directory:  {CSV_DIR}")
print(f"JSON files directory: {JSON_DIR}")
