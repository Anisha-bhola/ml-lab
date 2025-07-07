import pandas as pd
import streamlit as st
import plotly.express as px
from streamlit_option_menu import option_menu
from streamlit_autorefresh import st_autorefresh
from streamlit_echarts import st_echarts

# Auto-refresh every 2 minutes (optional)
st_autorefresh(interval=2 * 60 * 1000, key="dashboard_refresh")

# Load data
df = pd.read_excel("Cleaned_Medical_Bills_Processed.xlsx", sheet_name="All_Cleaned_Data")

st.set_page_config(layout="wide", page_title="Medical Claims Dashboard", page_icon="🩺")
st.title("🩺 Medical Claims Dashboard")

# Sidebar Navigation using option-menu
with st.sidebar:
    selected = option_menu(
        menu_title="Navigation",
        options=["Dashboard", "ECharts View", "Raw Data"],
        icons=["bar-chart", "pie-chart", "table"],
        default_index=0,
    )

    paid_filter = st.selectbox("Filter by Paid Status", ['All', 'YES', 'NO'])
    high_claims = st.checkbox("Only High Claims (> ₹50,000)")

# Filter logic
if paid_filter != 'All':
    df = df[df['Paid_Status'] == paid_filter]
if high_claims:
    df = df[df['Claim_Amount'] > 50000]

# OPD vs Non-OPD
df['Type'] = df['Pay_Text'].apply(lambda x: 'OPD' if 'OPD' in str(x).upper() else 'Non-OPD')
opd_count = df['Type'].value_counts()
grouped = df.groupby('Type')[['Claim_Amount', 'Approved_Amount']].sum().reset_index()

# --- Dashboard Section ---
if selected == "Dashboard":
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Claim Type Distribution (Plotly)")
        fig = px.pie(names=opd_count.index, values=opd_count.values, title="OPD vs Non-OPD")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Claimed vs Approved Amounts (Bar)")
        fig2 = px.bar(grouped, x='Type', y=['Claim_Amount', 'Approved_Amount'], barmode='group', title="Amounts by Type")
        st.plotly_chart(fig2, use_container_width=True)

# --- ECharts View ---
elif selected == "ECharts View":
    st.subheader("OPD vs Non-OPD (ECharts Donut)")
    options = {
        "tooltip": {"trigger": "item"},
        "legend": {"top": "5%", "left": "center"},
        "series": [
            {
                "name": "Claim Type",
                "type": "pie",
                "radius": ["40%", "70%"],
                "avoidLabelOverlap": False,
                "itemStyle": {
                    "borderRadius": 10,
                    "borderColor": "#fff",
                    "borderWidth": 2
                },
                "label": {"show": False, "position": "center"},
                "emphasis": {"label": {"show": True, "fontSize": 16, "fontWeight": "bold"}},
                "labelLine": {"show": False},
                "data": [{"value": int(opd_count[k]), "name": k} for k in opd_count.index],
            }
        ],
    }
    st_echarts(options=options, height="400px")

# --- Raw Data View ---
elif selected == "Raw Data":
    st.markdown("### 📋 Filtered Data Table")
    st.dataframe(df)
