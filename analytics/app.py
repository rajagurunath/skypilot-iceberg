import streamlit as st
from enum import Enum
from utils import load_data_from_r2, load_data_from_local
from streamlit_extras.chart_container import chart_container
from streamlit_ace import st_ace
import plotly.express as px
import plotly.graph_objects as go

# --- ENV Setup ---
class ENV(Enum):
    LOCAL = "local"
    R2 = "r2"

env = ENV.R2

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
page = st.sidebar.radio("Select Page", ["Home", "Dashboard", "SQL Editor"])

# --- Home Page / README ---
if page == "Home":
    st.title("📚 Welcome to GPU & CPU Price Analytics Dashboard!")

    st.markdown("""
    ### What this app offers:
    - View real-time **GPU & CPU prices** across **16+ cloud providers**.
    - Deep dive into specific cloud providers' offerings.
    - Analyze trends, spot prices, and historical shifts.
    - Run **your own SQL queries** against the dataset in a live SQL editor.
    - Instantly compare **weekday vs weekend** price behaviors.

    All Thanks to [Skypilot-Catalog](https://github.com/skypilot-org/skypilot-catalog)! 🚀 
                
    **Built using**:
    - Skypilot-Catalog
    - Streamlit
    - DuckDB
    - Iceberg Table Format
    - Cloudflare R2 (for cost-efficient storage)
    
    """)

# --- Dashboard Page ---
elif page == "Dashboard":
    clouds = con.execute("SELECT DISTINCT cloud FROM vms ORDER BY 1").fetchall()
    clouds = [c[0] for c in clouds]
    clouds.insert(0, "None")  # Insert 'None'
    selected_cloud = st.sidebar.selectbox("Choose Cloud Provider", clouds)

    st.title("💸 GPU & CPU Price Analytics Dashboard")

    if selected_cloud == "None":
        st.subheader("🌎 Global Cloud KPIs")

        @st.cache_data(ttl=3600)
        def fetch_global_kpis():
            return con.execute("""
                SELECT
                    COUNT(DISTINCT cloud) as clouds,
                    COUNT(DISTINCT InstanceType) as instance_types,
                    COUNT(DISTINCT Region) as regions,
                    COUNT(DISTINCT AcceleratorName) as gpu_types
                FROM vms
            """).fetch_df()

        global_kpis = fetch_global_kpis()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Cloud Providers", int(global_kpis['clouds'][0]))
        col2.metric("Instance Types", int(global_kpis['instance_types'][0]))
        col3.metric("Regions", int(global_kpis['regions'][0]))
        col4.metric("GPU Types", int(global_kpis['gpu_types'][0]))

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

        fig = px.scatter(latest_prices, x="AcceleratorName", y="avg_price", color="cloud",
                         size="total_devices",
                         title="Average GPU Prices by Cloud")
        with chart_container(latest_prices):
            st.plotly_chart(fig, use_container_width=True)

    else:
        st.subheader(f"🔎 Detailed Metrics for {selected_cloud}")

        @st.cache_data(ttl=3600)
        def fetch_cloud_kpis(selected_cloud):
            return con.execute("""
                SELECT
                    COUNT(DISTINCT InstanceType) as total_instance_types,
                    COUNT(DISTINCT AcceleratorName) as gpu_types,
                    COUNT(DISTINCT Region) as regions,
                    AVG(Price) as avg_price,
                    AVG(SpotPrice) as avg_spot_price
                FROM vms
                WHERE cloud = ?
            """, (selected_cloud,)).fetch_df()

        cloud_kpis = fetch_cloud_kpis(selected_cloud)

        col1, col2, col3 = st.columns(3)
        col1.metric("Instance Types", int(cloud_kpis['total_instance_types'][0]))
        col2.metric("GPU Types", int(cloud_kpis['gpu_types'][0]))
        col3.metric("Regions", int(cloud_kpis['regions'][0]))

        @st.cache_data(ttl=3600)
        def fetch_gpu_types(selected_cloud):
            return con.execute("""
                SELECT
                    AcceleratorName,
                    COUNT(*) as device_count,
                    AVG(Price) as avg_price
                FROM vms
                WHERE cloud = ? AND AcceleratorName IS NOT NULL
                GROUP BY AcceleratorName
            """, (selected_cloud,)).fetch_df()

        gpu_types = fetch_gpu_types(selected_cloud)

        fig = px.bar(gpu_types, x="AcceleratorName", y="avg_price", color="device_count",
                     title="Average Price per GPU Type", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("📈 Price Trends")

        top_gpus = gpu_types['AcceleratorName'].tolist()

        if top_gpus:
            selected_gpu = st.selectbox("Select GPU Accelerator", top_gpus)

            @st.cache_data(ttl=3600)
            def fetch_gpu_trend(selected_cloud, selected_gpu):
                return con.execute("""
                    SELECT
                        date,
                        Price,
                        SpotPrice
                    FROM vms
                    WHERE cloud = ? AND AcceleratorName = ?
                    ORDER BY date ASC
                """, (selected_cloud, selected_gpu)).fetch_df()

            gpu_trend_df = fetch_gpu_trend(selected_cloud, selected_gpu)

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=gpu_trend_df['date'], y=gpu_trend_df['Price'], mode='lines', name='Price'))
            fig.add_trace(go.Scatter(x=gpu_trend_df['date'], y=gpu_trend_df['SpotPrice'], mode='lines', name='Spot Price'))
            fig.update_layout(template="plotly_dark", title="Price vs Spot Price Trend")
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("📅 Weekday vs Weekend Analysis")

        @st.cache_data(ttl=3600)
        def fetch_weekday_vs_weekend(selected_cloud):
            return con.execute("""
                SELECT
                    CASE WHEN weekday(strptime(date,'%Y-%m-%d %H:%M:%S')) IN (0,6) THEN 'Weekend' ELSE 'Weekday' END as day_type,
                    AVG(Price) as avg_price,
                    AVG(SpotPrice) as avg_spot_price
                FROM vms
                WHERE cloud = ?
                GROUP BY day_type
            """, (selected_cloud,)).fetch_df()

        weekday_weekend_df = fetch_weekday_vs_weekend(selected_cloud)

        fig = px.bar(weekday_weekend_df, x="day_type", y=["avg_price", "avg_spot_price"], barmode="group",
                     title="Weekday vs Weekend Prices", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

# --- SQL Editor ---
elif page == "SQL Editor":
    st.title("📝 SQL Editor for Analyzing GPU Availability")
    st.markdown("Run your SQL queries against the dataset (table name: `vms`)")
    query = st_ace(language="sql", theme="monokai", height=300,placeholder="SELECT * FROM vms WHERE cloud = 'aws'")


    if query:
        try:
            with st.spinner('Executing your query...'):
                result = con.execute(query).fetch_df()
                if len(result) > 500:
                    st.warning(f"Showing first 500 rows out of {len(result)}.")
                    result = result.head(500)
            with chart_container(result):
                st.dataframe(result, use_container_width=True)
        except Exception as e:
            st.error(f"Error running query: {e}")

# --- Footer ---
st.markdown("---")
st.markdown("Built with ❤️ using Skypilot-Catalog, Streamlit, DuckDB, Iceberg, and R2 Catalogs.")
