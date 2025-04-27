# Makefile

.PHONY: all reconstruct bronze silver full-clean

all: reconstruct bronze silver

reconstruct:
	@echo "🔨 Reconstructing Git Files..."
	python scripts/1_reconstruct_git_files.py --output git_file_history.csv --resume

bronze:
	@echo "🔨 Ingesting to Bronze Table..."
	python scripts/2_convert_to_iceberg.py --csv git_file_history.csv --storage local

silver:
	@echo "🔨 Updating Silver Table..."
	python scripts/3_update_silver.py --storage local

full-clean:
	@echo "🧹 Cleaning Iceberg warehouse..."
	rm git_file_history.csv
	rm -rf tmp/warehouse