# /scripts/3_update_silver.py

import argparse
import pandas as pd
import pyarrow as pa
import os
from pathlib import Path
from ddl import vms_schema
from lib.iceberg_helpers import load_catalog_by_storage
from pyiceberg.utils import truncate
WAREHOUSE_LOCAL = "./tmp/warehouse"

def update_silver(storage_target="local"):
    # Load catalog
    catalog = load_catalog_by_storage(storage_target)

    # Load Bronze table
    bronze_table = catalog.load_table("bronze.vms")

    # Create Silver namespace if not exists
    catalog.create_namespace_if_not_exists("silver")

    # Try to load Silver table
    try:
        silver_table = catalog.load_table("silver.vms")
        print("✅ Loaded existing Silver table: silver.vms")
    except Exception:
        print("⚡ Silver table not found. Creating a new one...")
        silver_table = catalog.create_table(
            identifier="silver.vms",
            schema=vms_schema,
            location=None,
        )

    # Read Bronze table fully (for now)
    bronze_arrow = bronze_table.scan().to_arrow()
    bronze_df = bronze_arrow.to_pandas()

    if bronze_df.empty:
        print("❌ No data in Bronze to merge into Silver.")
        return

    print(f"🔎 Bronze table contains {len(bronze_df)} rows.")

    # Deduplicate to latest snapshot
    bronze_df["created_at"] = pd.to_datetime(bronze_df["created_at"]).dt.strftime("%Y-%m-%d %H:%M:%S")
    bronze_df = bronze_df.sort_values("created_at", ascending=False)

    deduped = (
        bronze_df
        .drop_duplicates(
            subset=["cloud", "InstanceType", "Region", "AvailabilityZone"], keep="first"
        )
    ).reset_index(drop=True)

    print(f"✨ After deduplication: {len(deduped)} rows remain.")
    
    # Delete all existing rows (brute force for now)
    # silver_table.delete(delete_filter="1==1")

    # Insert latest
    silver_arrow = pa.Table.from_pandas(deduped)
    silver_table.append(silver_arrow)

    print("✅ Silver table updated successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update Silver Iceberg Table from Bronze.")
    parser.add_argument("--storage", type=str, default="local", choices=["local", "r2"], help="Storage backend")
    args = parser.parse_args()

    os.chdir(Path(__file__).parent.parent)
    update_silver(storage_target=args.storage)