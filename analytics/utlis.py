import os
from pyiceberg.catalog.rest import RestCatalog
from dotenv import load_dotenv
load_dotenv()

def load_data_from_r2():
    WAREHOUSE = os.getenv("R2_WAREHOUSE", "default_warehouse")
    TOKEN = os.getenv("R2_TOKEN", "default_token")
    CATALOG_URI = os.getenv("R2_CATALOG_URI", "https://default.catalog.uri")

    catalog = RestCatalog(
        name="default",
        warehouse=WAREHOUSE,
        uri=CATALOG_URI,
        token=TOKEN,
    )

    table = catalog.load_table('bronze.vms')
    con = table.scan().to_duckdb(table_name="vms")
    
    return con
