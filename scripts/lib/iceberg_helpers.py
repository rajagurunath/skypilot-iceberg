# /lib/iceberg_helpers.py

from pyiceberg.catalog import load_catalog
from pyiceberg.catalog.rest import RestCatalog
from dotenv import load_dotenv
import os
load_dotenv()
WAREHOUSE_LOCAL = "./tmp/warehouse"

def load_catalog_by_storage(storage_target="local"):
    os.makedirs(WAREHOUSE_LOCAL, exist_ok=True)
    if storage_target == "local":
        return load_catalog(
            "default",
            **{
                "type": "sql",
                "uri": f"sqlite:///{WAREHOUSE_LOCAL}/pyiceberg_catalog.db",
                "warehouse": f"file://{WAREHOUSE_LOCAL}",
            },
        )
    elif storage_target == "r2":
        # Define catalog connection details (replace variables)
        WAREHOUSE = os.getenv("R2_WAREHOUSE", "default_warehouse")
        TOKEN = os.getenv("R2_TOKEN", "default_token")
        CATALOG_URI = os.getenv("R2_CATALOG_URI", "https://default.catalog.uri")

        # Connect to R2 Data Catalog
        catalog = RestCatalog(
            name="default",
            warehouse=WAREHOUSE,
            uri=CATALOG_URI,
            token=TOKEN,
        )

        return catalog
    else:
        raise ValueError("Unsupported storage target.")