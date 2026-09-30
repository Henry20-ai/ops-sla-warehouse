import psycopg2
from faker import Faker
import random
from datetime import timedelta

fake = Faker()

conn = psycopg2.connect(
    host="localhost", database="ops_warehouse",
    user="postgres", password="ZIKE1200UDO", port="5432"
)
cur = conn.cursor()

# Clear old data first so we don't duplicate
cur.execute("TRUNCATE TABLE raw_tickets RESTART IDENTITY;")

categories = ["Billing", "Technical Support", "Account Access", "Shipping", "Refund Request"]
priorities = ["Low", "Medium", "High", "Urgent"]
statuses_pool = ["Open", "In Progress", "Resolved", "Closed"]

# Realistic resolution windows per priority, in hours: (typical_min, typical_max, breach_chance)
sla_targets = {
    "Urgent": (1, 4, 0.15),      # most resolve within 4h, 15% breach
    "High": (2, 24, 0.20),        # most within 24h, 20% breach
    "Medium": (4, 72, 0.25),      # most within 72h, 25% breach
    "Low": (8, 120, 0.10),        # most within 120h, 10% breach
}

for _ in range(300):
    customer_name = fake.name()
    category = random.choice(categories)
    priority = random.choice(priorities)
    status = random.choice(statuses_pool)
    created_at = fake.date_time_between(start_date="-90d", end_date="now")

    if status in ("Resolved", "Closed"):
        typical_min, typical_max, breach_chance = sla_targets[priority]
        if random.random() < breach_chance:
            # deliberately breach: go past the typical max
            hours = random.randint(typical_max + 1, typical_max * 3)
        else:
            # resolve within the healthy window
            hours = random.randint(typical_min, typical_max)
        resolved_at = created_at + timedelta(hours=hours)
    else:
        resolved_at = None

    cur.execute("""
        INSERT INTO raw_tickets (customer_name, category, priority, status, created_at, resolved_at)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (customer_name, category, priority, status, created_at, resolved_at))

conn.commit()
cur.close()
conn.close()
print("300 tickets regenerated with realistic SLA distribution.")