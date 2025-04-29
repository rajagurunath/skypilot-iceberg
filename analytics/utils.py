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
    import daft
    from daft import Session

    df = daft.read_iceberg(table)
    sess = Session()

    sess.create_temp_table("vms", df)

    # con = table.scan().to_duckdb(table_name="vms")
    
    return sess


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
    import daft
    from daft import Session

    df = daft.read_iceberg(table)
    sess = Session()

    sess.create_temp_table("vms", df)

    # con = table.scan().to_duckdb(table_name="vms")
    return sess