import great_expectations as gx
import pandas as pd
import psycopg2

# Pull data from Postgres into a DataFrame
conn = psycopg2.connect(
    host="localhost",
    database="ops_warehouse",
    user="postgres",
    password="ZIKE1200UDO",
    port="5432"
)
df = pd.read_sql("SELECT * FROM raw_tickets", conn)
conn.close()

print(f"Loaded {len(df)} rows for validation.\n")

# Set up a Great Expectations context (GX 1.x API)
context = gx.get_context()

# Register a pandas data source, asset, and batch definition
data_source = context.data_sources.add_pandas("tickets_source")
data_asset = data_source.add_dataframe_asset(name="raw_tickets_asset")
batch_definition = data_asset.add_batch_definition_whole_dataframe("raw_tickets_batch")
batch = batch_definition.get_batch(batch_parameters={"dataframe": df})

results = []

# 1. Primary key should never be null
results.append(batch.validate(
    gx.expectations.ExpectColumnValuesToNotBeNull(column="ticket_id")
))

# 2. Priority should only be one of these four values
results.append(batch.validate(
    gx.expectations.ExpectColumnValuesToBeInSet(
        column="priority", value_set=["Low", "Medium", "High", "Urgent"]
    )
))

# 3. Status should only be one of these four values
results.append(batch.validate(
    gx.expectations.ExpectColumnValuesToBeInSet(
        column="status", value_set=["Open", "In Progress", "Resolved", "Closed"]
    )
))

# 4. customer_name should never be null
results.append(batch.validate(
    gx.expectations.ExpectColumnValuesToNotBeNull(column="customer_name")
))

# 5. resolved_at should never be before created_at (manual logic check, not GX)
invalid_rows = df[df["resolved_at"].notna() & (df["resolved_at"] < df["created_at"])]
print(f"Rows where resolved_at is before created_at: {len(invalid_rows)}")

# Print a clean pass/fail summary
print("\n--- Validation Summary ---")
for r in results:
    status = "PASS" if r.success else "FAIL"
    print(f"{status}: {r.expectation_config.type}")