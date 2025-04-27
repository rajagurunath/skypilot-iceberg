# /scripts/ddl.py

from pyiceberg.schema import Schema, NestedField
from pyiceberg.types import StringType, DoubleType, IntegerType, TimestampType

# Define schema using NestedField instead of tuples
# vms_schema = Schema(
#     NestedField("instanceType", StringType(), description="Instance type (e.g., t2.micro)"),
#     NestedField("Region", StringType(), description="AWS region / Azure region / GCP region"),
#     NestedField("AvailabilityZone", StringType(), description="Specific availability zone"),
#     NestedField("price", DoubleType(), description="Instance price in USD"),
#     NestedField("cpu", IntegerType(), description="Number of vCPUs"),
#     NestedField("memory_gb", DoubleType(), description="Memory size in GB"),
#     NestedField("cloud", StringType(), description="Cloud provider name"),
#     NestedField("author", StringType(), description="Author of the commit"),
#     NestedField("date", TimestampType(), description="Commit date"),
#     NestedField("message", StringType(), description="Commit message"),
#     NestedField("commit", StringType(), description="Git commit hash"),
#     NestedField("created_at", TimestampType(), description="Row created timestamp"),
#     NestedField("updated_at", TimestampType(), description="Row updated timestamp"),
# )


vms_schema = Schema(
    NestedField(1,"author", StringType(), description="Author of the commit"),
    NestedField(2,"date", StringType(), description="Commit date"),
    NestedField(3,"message", StringType(), description="Commit message"),
    NestedField(4,"InstanceType", StringType(), description="Instance type (e.g., t2.micro)"),
    NestedField(6,"AcceleratorName", StringType(), description="AcceleratorName (e.g., H100)"),
    NestedField(7,"AcceleratorCount", DoubleType(), description="AcceleratorCount  (e.g., 1,2,8)"),

    NestedField(8,"Region", StringType(), description="AWS region / Azure region / GCP region"),
    NestedField(9,"AvailabilityZone", StringType(), description="Specific availability zone"),
    NestedField(10,"Price", DoubleType(), description="Instance price in USD"),
    NestedField(11,"SpotPrice", DoubleType(), description="Spot Instance price in USD"),
    NestedField(12,"vCPUs", DoubleType(), description="Number of vCPUs"),
    NestedField(13,"MemoryGiB", DoubleType(), description="Memory size in GB"),
    NestedField(14,"cloud", StringType(), description="Cloud provider name"),
    NestedField(15,"commit", StringType(), description="Git commit hash"),
    NestedField(16,"Generation", StringType(), description="Generation"),
    NestedField(17,"GpuInfo", StringType(), description="Generation"),
    NestedField(18,"created_at", StringType(), description="Row created timestamp"),
    NestedField(19,"updated_at", TimestampType(), description="Row updated timestamp"),
)