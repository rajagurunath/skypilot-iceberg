import streamlit as st
import duckdb
from utlis import load_data_from_r2

# --- Load Data ---
st.cache_data(ttl=3600)  # cache for 1 hour
def load_data():
    # con = duckdb.connect()
    con = load_data_from_r2()
    return con

con = load_data()

# --- Sidebar ---
st.sidebar.title("☁️ Cloud Selection")
clouds = con.execute("SELECT DISTINCT cloud FROM vms").fetchall()
clouds = [c[0] for c in clouds]
selected_cloud = st.sidebar.selectbox("Choose Cloud Provider", clouds)

# --- Main KPIs ---
st.title("💸 GPU Price Analytics Dashboard")
st.subheader("Latest GPU Pricing Snapshot")

latest_data_query = """
    SELECT
        InstanceType,
        Region,
        MAX(date) as latest_date,
        MAX(Price) as latest_price,
        MAX(SpotPrice) as latest_spot_price,
        cloud
    FROM vms
    WHERE AcceleratorName IS NOT NULL
    GROUP BY InstanceType, Region, cloud
"""
latest_df = con.execute(latest_data_query).fetch_df()

st.dataframe(latest_df, use_container_width=True)

# --- Price Trends for Selected Cloud ---
st.header(f"📈 Price Trends for {selected_cloud}")

# Fetch instance types with GPUs
instance_query = f"""
    SELECT DISTINCT InstanceType
    FROM vms
    WHERE cloud = '{selected_cloud}' AND AcceleratorName IS NOT NULL
"""
instances = con.execute(instance_query).fetchall()
instances = [i[0] for i in instances]

selected_instance = st.selectbox("Select Instance Type", instances)

if selected_instance:
    price_trend_query = f"""
        SELECT
            date,
            Price,
            SpotPrice,
            Region,
            AvailabilityZone
        FROM vms
        WHERE cloud = '{selected_cloud}'
          AND InstanceType = '{selected_instance}'
        ORDER BY date ASC
    """
    trend_df = con.execute(price_trend_query).fetch_df()

    st.line_chart(trend_df.set_index('date')[['Price', 'SpotPrice']])

# --- Weekday vs Weekend Analysis ---
st.header("📅 Weekday vs Weekend Analysis")

weekday_analysis_query = f"""
    SELECT
        CASE WHEN EXTRACT(DOW FROM date) IN (0, 6) THEN 'Weekend' ELSE 'Weekday' END as day_type,
        AVG(Price) as avg_price,
        AVG(SpotPrice) as avg_spot_price
    FROM vms
    WHERE cloud = '{selected_cloud}'
    GROUP BY day_type
"""
weekday_df = con.execute(weekday_analysis_query).fetch_df()

st.bar_chart(weekday_df.set_index('day_type')[['avg_price', 'avg_spot_price']])

# --- Holiday Analysis (basic placeholder) ---
# Later we can improve it with actual holiday calendars

st.header("🎉 Holiday Analysis (Placeholder)")

st.info("Holiday analysis coming soon based on real-world cloud provider calendars.")

# --- Footer ---
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit, DuckDB, Iceberg, and R2 Catalogs.")
