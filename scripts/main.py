# scripts/main.py

import os
from pathlib import Path
from scripts import (
    reconstruct_git_files,
    convert_to_iceberg,
    update_silver,
)

def main():
    os.chdir(Path(__file__).parent.parent)

    print("🔨 Reconstructing Git Files...")
    reconstruct_git_files.reconstruct_history(output_csv="git_file_history.csv", resume=True)

    print("🔨 Ingesting to Bronze Table...")
    convert_to_iceberg.convert_to_iceberg(csv_path="git_file_history.csv", storage_target="local")

    print("🔨 Updating Silver Table...")
    update_silver.update_silver(storage_target="local")

if __name__ == "__main__":
    main()