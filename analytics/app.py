import streamlit as st
from enum import Enum
from utils import load_data_from_r2, load_data_from_local
from streamlit_extras.chart_container import chart_container
from streamlit_ace import st_ace

# --- ENV Setup ---
class ENV(Enum):
    LOCAL = "local"
    R2 = "r2"

env = ENV.LOCAL

# --- Load Data ---
@st.cache_resource(ttl=3600)
def load_data():
    if env == ENV.LOCAL:
        con = load_data_from_local()
    else:
        con = load_data_from_r2()
    return con

con = load_data()

# --- Sidebar Page Selection ---
st.sidebar.title("☁️ Cloud Selection & SQL Playground")
page = st.sidebar.radio("Select Page", ["Dashboard", "SQL Editor"])

if page == "Dashboard":
    # --- Sidebar Cloud Selection ---
    clouds = con.execute("SELECT DISTINCT cloud FROM vms ORDER BY 1").fetchall()
    clouds = [c[0] for c in clouds]
    clouds.insert(0, "None")  # Insert 'None' at beginning
    selected_cloud = st.sidebar.selectbox("Choose Cloud Provider", clouds)

    # --- Main KPIs ---
    st.title("💸 GPU & CPU Price Analytics Dashboard")

    # If no cloud selected: show Global Metrics
    if selected_cloud == "None":
        st.subheader("🌎 Global Cloud KPIs")

        # Latest GPU Pricing across Clouds
        @st.cache_data(ttl=3600)
        def fetch_latest_prices():
            return con.execute("""
                SELECT
                    cloud,
                    AcceleratorName,
                    AVG(Price) as avg_price,
                    COUNT(DISTINCT InstanceType) as instance_types,
                    COUNT(*) as total_devices
                FROM vms
                WHERE AcceleratorName IS NOT NULL
                GROUP BY cloud, AcceleratorName
            """).fetch_df()

        latest_prices = fetch_latest_prices()
        
        with chart_container(latest_prices):
            st.dataframe(latest_prices, use_container_width=True)

        # Instances, GPUs, CPUs per Cloud
        @st.cache_data(ttl=3600)
        def fetch_inventory_summary():
            return con.execute("""
                SELECT
                    cloud,
                    COUNT(DISTINCT CASE WHEN AcceleratorName IS NOT NULL THEN InstanceType END) as gpu_instances,
                    COUNT(DISTINCT CASE WHEN AcceleratorName IS NULL THEN InstanceType END) as cpu_instances,
                    COUNT(DISTINCT Region) as regions_served,
                    COUNT(DISTINCT AvailabilityZone) as azs_served
                FROM vms
                GROUP BY cloud
            """).fetch_df()

        inventory_summary = fetch_inventory_summary()

        with chart_container(inventory_summary):
            st.dataframe(inventory_summary, use_container_width=True)

    else:
        # Specific Cloud selected: Drilldown
        st.subheader(f"🔎 Detailed Metrics for {selected_cloud}")

        @st.cache_data(ttl=3600)
        def fetch_cloud_kpis(selected_cloud):
            return con.execute(f"""
                SELECT
                    AcceleratorName,
                    AVG(Price) as avg_price,
                    AVG(SpotPrice) as avg_spot_price,
                    COUNT(DISTINCT Region) as regions,
                    COUNT(DISTINCT AvailabilityZone) as availability_zones,
                    COUNT(DISTINCT InstanceType) as total_instance_types
                FROM vms
                WHERE cloud = '{selected_cloud}'
                GROUP BY AcceleratorName
            """).fetch_df()

        cloud_kpis = fetch_cloud_kpis(selected_cloud)

        with chart_container(cloud_kpis):
            st.dataframe(cloud_kpis, use_container_width=True)

        # GPU-specific breakdown: H100, H200 etc.
        st.subheader("🎯 GPU Breakdown")

        @st.cache_data(ttl=3600)
        def fetch_gpu_types(selected_cloud):
            return con.execute(f"""
                SELECT
                    AcceleratorName,
                    COUNT(*) as device_count,
                    AVG(Price) as avg_price
                FROM vms
                WHERE cloud = '{selected_cloud}' AND AcceleratorName IS NOT NULL
                GROUP BY AcceleratorName
            """).fetch_df()

        gpu_types = fetch_gpu_types(selected_cloud)

        with chart_container(gpu_types):
            st.dataframe(gpu_types, use_container_width=True)

        # Price Trends for H100, H200 if available
        st.subheader("📈 Price Trend Analysis for Top GPUs")

        top_gpus = gpu_types['AcceleratorName'].tolist()

        if top_gpus:
            selected_gpu = st.selectbox("Select GPU Accelerator", top_gpus)

            @st.cache_data(ttl=3600)
            def fetch_gpu_trend(selected_cloud, selected_gpu):
                return con.execute(f"""
                    SELECT
                        date,
                        Price,
                        SpotPrice,
                        Region,
                        AvailabilityZone
                    FROM vms
                    WHERE cloud = '{selected_cloud}'
                      AND AcceleratorName = '{selected_gpu}'
                    ORDER BY date ASC
                """).fetch_df()

            gpu_trend_df = fetch_gpu_trend(selected_cloud, selected_gpu)

            with chart_container(gpu_trend_df):
                st.line_chart(gpu_trend_df.set_index('date')[['Price', 'SpotPrice']])

        # Weekday vs Weekend Analysis
        st.subheader("📅 Weekday vs Weekend Price Analysis")

        @st.cache_data(ttl=3600)
        def fetch_weekday_vs_weekend(selected_cloud):
            return con.execute(f"""
                SELECT
                    CASE WHEN weekday(strptime(date,'%Y-%m-%d %H:%M:%S')) IN (0,6) THEN 'Weekend' ELSE 'Weekday' END as day_type,
                    AVG(Price) as avg_price,
                    AVG(SpotPrice) as avg_spot_price
                FROM vms
                WHERE cloud = '{selected_cloud}'
                GROUP BY day_type
            """).fetch_df()

        weekday_weekend_df = fetch_weekday_vs_weekend(selected_cloud)

        with chart_container(weekday_weekend_df):
            st.bar_chart(weekday_weekend_df.set_index('day_type')[['avg_price', 'avg_spot_price']])

elif page == "SQL Editor":
    st.title("📝 SQL Editor for Analyisng the GPU avalabiliy across clouds")

    query = st_ace(language="sql", theme="monokai", height=300)

    if query:
        try:
            with st.spinner('Executing your query...'):
                result = con.execute(query).fetch_df()
            with chart_container(result):
                st.dataframe(result, use_container_width=True)
        except Exception as e:
            st.error(f"Error running query: {e}")

# --- Footer ---
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit, DuckDB, Iceberg, and R2 Catalogs.")
