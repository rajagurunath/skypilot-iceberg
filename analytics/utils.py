import os
from pyiceberg.catalog.rest import RestCatalog
from pyiceberg.catalog import load_catalog
from dotenv import load_dotenv
import streamlit as st
load_dotenv()

def load_data_from_r2():
    WAREHOUSE = st.secrets["R2_WAREHOUSE"]
    TOKEN = st.secrets["R2_TOKEN"]
    CATALOG_URI = st.secrets["R2_CATALOG_URI"]

    catalog = RestCatalog(
        name="default",
        warehouse=WAREHOUSE,
        uri=CATALOG_URI,
        token=TOKEN,
    )

    table = catalog.load_table('bronze.vms')
    con = table.scan().to_duckdb(table_name="vms")
    
    return con


def load_data_from_local():
    WAREHOUSE_LOCAL = "./tmp/warehouse"
    os.makedirs(WAREHOUSE_LOCAL, exist_ok=True)
    
    catalog = load_catalog(
        "default",
        **{
            "type": "sql",
            "uri": f"sqlite:///{WAREHOUSE_LOCAL}/pyiceberg_catalog.db",
            "warehouse": f"file://{WAREHOUSE_LOCAL}",
        },
    )

    table = catalog.load_table('skypilot.bronze.vms')
    con = table.scan().to_duckdb(table_name="vms")
    return con