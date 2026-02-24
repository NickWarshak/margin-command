import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import random

# --- 0. THE REFINED STYLING (Modern Slate & Indigo) ---
st.set_page_config(page_title="Executive Command", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=JetBrains+Mono:wght@400&display=swap');
    
    /* Global Reset */
    .stApp { background-color: #0E1117; color: #E0E0E0; }
    html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }
    
    /* Sidebar Sophistication */
    [data-testid="stSidebar"] { 
        background-color: #0B0E14; 
        border-right: 1px solid rgba(255, 255, 255, 0.05); 
    }
    
    /* Card-like Containers */
    div.stElementContainer { margin-bottom: 0.5rem; }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] { 
        gap: 24px; 
        background-color: transparent; 
    }
    .stTabs [data-baseweb="tab"] { 
        height: 45px; 
        background-color: transparent; 
        border: none;
        color: #888;
        font-weight: 400;
        font-size: 14px;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] { 
        color: #6366F1 !important; 
        border-bottom: 2px solid #6366F1 !important;
        font-weight: 600;
    }

    /* Modern Table / DataFrame */
    [data-testid="stDataFrame"] {
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 8px;
    }
    
    /* Metrics Customization */
    [data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.03);
        padding: 15px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    [data-testid="stMetricValue"] { color: #FFFFFF !important; font-weight: 800 !important; }
    [data-testid="stMetricLabel"] { color: #6366F1 !important; text-transform: uppercase; font-size: 11px; letter-spacing: 1px; }

    /* Button Styling */
    .stButton>button { 
        border-radius: 8px; 
        background-color: #6366F1; 
        color: white; 
        border: none;
        font-weight: 600;
        padding: 0.5rem 1rem;
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: #4F46E5; border: none; color: white; }
    
    /* Hide Default Headers */
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 1. DATA LOGIC (UNCHANGED) ---
@st.cache_data
def get_model_key():
    data = [
        ["CARNIVAL", "MAC4225", "FWD LX"], ["CARNIVAL", "MAC4235", "FWD LXS"],
        ["CARNIVAL", "MAC4245", "FWD EX"], ["CARNIVAL", "MAC4285", "FWD SX"],
        ["CARNIVAL", "MAC4295", "FWD SX PRESTIGE"], ["EV6", "NAE2345", "RWD LIGHT(SR)"],
        ["EV6", "NAE4345", "RWD LIGHT(LR)"], ["EV6", "NAE4355", "RWD WIND"],
        ["K4", "2AC3214", "FWD LX"], ["K4", "2AC3224", "FWD LXS"],
        ["K5", "LAC4234", "FWD LXS"], ["K5", "LAC4254", "FWD GT-Line"],
        ["SPORTAGE", "4AC2225", "FWD LX"], ["SPORTAGE", "4AC2245", "FWD EX"],
        ["SPORTAGE", "4AC2425", "AWD LX"], ["SPORTAGE", "4AC2445", "AWD EX"],
        ["TELLURIDE", "JAC4225", "FWD LX"], ["TELLURIDE", "JAC4235", "FWD S"],
        ["TELLURIDE", "JAC4245", "FWD EX"], ["TELLURIDE", "JAC4445", "AWD EX"],
        ["TELLURIDE", "JAC4495", "AWD SX-PRESTIGE"]
    ]
    return pd.DataFrame(data, columns=["Series", "Model Code", "Trim"])

def generate_simulation():
    key_df = get_model_key()
    inv_rows, sales_rows = [], []
    colors = ["Glacial White Pearl", "Ebony Black", "Wolf Gray", "Gravity Gray", "Everlasting Silver", "Dawning Red"]
    
    for _ in range(180):
        row = key_df.sample(n=1).iloc[0]
        days = random.randint(1, 140)
        inv_rows.append({
            "Series": row["Series"], "Trim": row["Trim"], "DisplayColor": random.choice(colors),
            "VIN": f"5XX{random.randint(1000000, 9999999)}", "Status": random.choice(["GROUND", "TRANSIT"]),
            "Days_on_Lot": days, "Est_Bleed_Cost": days * 18, "Demand": random.randint(10, 95)
        })
    for _ in range(140):
        row = key_df.sample(n=1).iloc[0]
        sales_rows.append({
            "Series": row["Series"], "Trim": row["Trim"], "DisplayColor": random.choice(colors), "VIN": f"5XX{random.randint(1000000, 9999999)}"
        })
    return pd.DataFrame(inv_rows), pd.DataFrame(sales_rows)

# --- 2. SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='letter-spacing:-1px;'>Intelligence Engine</h2>", unsafe_allow_html=True)
    st.markdown("---")
    if st.button("Sync Data Feed", use_container_width=True):
        st.session_state["inv_data"], st.session_state["sales_data"] = generate_simulation()
        st.toast("Telemetry data synced.")

# --- 3. MAIN UI ---
if "inv_data" in st.session_state:
    f_inv, f_sales = st.session_state["inv_data"], st.session_state["sales_data"]
    
    # Filtering Sidebar
    all_series = sorted(f_inv['Series'].unique().tolist())
    selected_series = st.sidebar.multiselect("Active Filters", options=all_series, default=all_series)
    f_inv = f_inv[f_inv['Series'].isin(selected_series)]
    f_sales = f_sales[f_sales['Series'].isin(selected_series)]

    # Header Section
    st.markdown("<h1 style='font-weight: 800; font-size: 3rem; margin-bottom: 0;'>Inventory <span style='color:#6366F1'>Pulse</span></h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #888; margin-top: -10px;'>High-fidelity asset tracking and margin analytics.</p>", unsafe_allow_html=True)
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Assets", f"{len(f_inv)} Units")
    m2.metric("30D Throughput", f"{len(f_sales)} Units")
    m3.metric("Avg. Age", f"{int(f_inv['Days_on_Lot'].mean())} Days")
    m4.metric("Burn Rate", f"${f_inv['Est_Bleed_Cost'].sum():,}")

    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["[ Inventory Ledger ]", "[ Shortage Analysis ]", "[ Visual Mapping ]"])

    with tab1:
        st.dataframe(
            f_inv, 
            use_container_width=True, 
            hide_index=True,
            column_config={
                "Est_Bleed_Cost": st.column_config.NumberColumn("Est. Cost", format="$%d"),
                "Demand": st.column_config.ProgressColumn("Demand Score", min_value=0, max_value=100),
                "VIN": None # Hide VIN for cleanliness
            }
        )

    with tab2:
        inv_p = f_inv.pivot_table(index=['Series', 'Trim'], columns='DisplayColor', values='Status', aggfunc='count', fill_value=0)
        sal_p = f_sales.pivot_table(index=['Series', 'Trim'], columns='DisplayColor', values='VIN', aggfunc='count', fill_value=0)
        delta_pivot = inv_p.subtract(sal_p, fill_value=0).astype(int).reset_index()

        def color_logic(val):
            if not isinstance(val, int) or val == 0: return 'color: #444;'
            if val < 0: return 'background-color: rgba(239, 68, 68, 0.1); color: #F87171;'
            return 'background-color: rgba(34, 197, 94, 0.1); color: #4ADE80;'

        st.dataframe(delta_pivot.style.map(color_logic, subset=delta_pivot.columns[2:]), use_container_width=True, hide_index=True)

    with tab3:
        fig = px.sunburst(
            f_inv, path=['Series', 'Trim', 'DisplayColor'],
            color_discrete_sequence=["#4F46E5", "#6366F1", "#818CF8", "#A5B4FC", "#C7D2FE"]
        )
        fig.update_layout(
            height=600, margin=dict(t=0, l=0, r=0, b=0),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Outfit", size=14, color="#FFF")
        )
        st.plotly_chart(fig, use_container_width=True)

else:
    st.info("System Standby. Please initiate 'Sync Data Feed' from the command panel.")

st.markdown("<div style='margin-top: 100px; opacity: 0.3; font-size: 10px; text-align: center; letter-spacing: 2px;'>OPERATIONAL INTELLIGENCE SYSTEM // v2.0.4</div>", unsafe_allow_html=True)