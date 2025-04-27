# /scripts/2_convert_to_iceberg.py

import pandas as pd
import pyarrow as pa
import os
from io import StringIO
import argparse
from pathlib import Path
from pyiceberg.catalog import load_catalog
from pyiceberg.table import Table
from lib.iceberg_helpers import load_catalog_by_storage
# Load DDL schema (optional if using Iceberg-managed schema later)
from ddl import vms_schema
from pyiceberg.partitioning import PartitionSpec, PartitionField
from pyiceberg.transforms import IdentityTransform
from datetime import datetime


WAREHOUSE_LOCAL = "./tmp/warehouse"


def convert_to_iceberg(csv_path, storage_target="local"):
    # Load git file history
    df = pd.read_csv(csv_path)

    # Load or create catalog
    catalog = load_catalog_by_storage(storage_target)

    # Create namespace if not exists
    catalog.create_namespace_if_not_exists("bronze")

    # Try load table, else create it
    if not catalog.table_exists("bronze.vms"):
        print("⚡ Table not found. Creating a new one...")
        cloud_partition_spec = PartitionSpec(
                     PartitionField(field_id=1, source_id=14, name="cloud",transform=IdentityTransform())
        )
        table = catalog.create_table(
            identifier="bronze.vms",
            schema=vms_schema,
            location=None,  # Let Iceberg manage location inside warehouse
            partition_spec=cloud_partition_spec
        )
    else:
        table = catalog.load_table("bronze.vms")

    # Process each record
    records = []
    for _, r in df.iterrows():
        if not r['content']:
            continue

        try:
        
            temp_df = pd.read_csv(StringIO(r['content']))
            # Enrich with metadata
            temp_df["author"] = r['author']
            temp_df["date"]   =  pd.to_datetime(r['date']).strftime("%Y-%m-%d %H:%M:%S")
            temp_df["message"] = r['message']
            temp_df["commit"] = r['commit']
            temp_df["created_at"] = pd.to_datetime(r['date']).strftime("%Y-%m-%d %H:%M:%S")
            temp_df["updated_at"] = datetime.now()
            # temp_df["created_at"]  = pd.to_datetime(temp_df['created_at'], utc=True).dt.tz_localize(None)
            # Add cloud field from file path (e.g., last folder name)
            dir_path = os.path.dirname(r['file'])
            cloud = dir_path.split("/")[-1] if "/" in dir_path else dir_path
            temp_df["cloud"] = cloud

            records.append(temp_df)
        except Exception as e:
            print(f"⚠️ Failed to parse row: {e}")

    # Merge all mini DataFrames into one
    if not records:
        print("❌ No records to process.")
        return

    final_df = pd.concat(records, ignore_index=True)

    # Map to PyArrow Table
    arrow_table = pa.Table.from_pandas(final_df)

    # Append to Iceberg
    table.append(arrow_table)

    print(f"✅ Ingested {len(final_df)} rows into bronze.vms.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert Git file history to Iceberg Bronze Table.")
    parser.add_argument("--csv", type=str, default="git_file_history.csv", help="Path to CSV file")
    parser.add_argument("--storage", type=str, default="local", choices=["local", "r2"], help="Storage target: local or r2")
    args = parser.parse_args()

    os.chdir(Path(__file__).parent.parent)
    convert_to_iceberg(csv_path=args.csv, storage_target=args.storage)