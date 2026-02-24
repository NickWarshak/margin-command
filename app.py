import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import random

# --- 0. THE LIGHT GALLERY STYLING ---
st.set_page_config(page_title="Margin Command | Elite", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Inter:wght@300;400;600&family=JetBrains+Mono:wght@400&display=swap');
    
    /* Global Styles */
    .stApp { background-color: #F9F7F2; color: #1A1A1A; }
    [data-testid="stSidebar"] { background-color: #F1EEE6; border-right: 1px solid #E0DDD5; }
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    h1, h2, h3 { font-family: 'DM Serif Display', serif !important; color: #1A1A1A !important; font-weight: 400 !important; }

    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] { gap: 24px; background-color: transparent; border-bottom: 2px solid #E0DDD5; }
    .stTabs [data-baseweb="tab"] { 
        height: 60px; 
        background-color: transparent; 
        border: none; 
        font-weight: 600; 
        color: #888; 
        text-transform: uppercase; 
        letter-spacing: 1px; 
        font-size: 12px; 
    }
    .stTabs [aria-selected="true"] { 
        color: #1A1A1A !important; 
        border-bottom: 2px solid #1A1A1A !important; 
    }

    #MainMenu, footer, header {visibility: hidden;}
    
    /* Elegant Dataframe */
    [data-testid="stDataFrame"] {
        border: 1px solid #E0DDD5; 
        border-radius: 8px; 
        background-color: #FFFFFF;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] { color: #1A1A1A !important; font-family: 'DM Serif Display', serif !important; font-size: 3rem !important; }
    [data-testid="stMetricLabel"] { color: #666 !important; text-transform: uppercase; letter-spacing: 1px; }

    /* Buttons - Clean & Minimal */
    .stButton>button { 
        width: 100%; 
        background-color: #1A1A1A; 
        color: white; 
        border: none; 
        border-radius: 4px; 
        padding: 12px;
        font-weight: 600;
        transition: all 0.2s;
    }
    .stButton>button:hover { background-color: #444; color: white; }
    
    /* Sidebar Text */
    .sidebar-label { color: #888; font-size: 10px; letter-spacing: 2px; font-weight: 600; margin-bottom: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. DATA GENERATION (Unchanged Logic) ---
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
    inv_rows = []
    colors = ["Glacial White", "Ebony Black", "Wolf Gray", "Gravity Gray", "Everlasting Silver", "Dawning Red"]
    for _ in range(180):
        row = key_df.sample(n=1).iloc[0]
        days = random.randint(1, 140)
        inv_rows.append({
            "Series": row["Series"], "MODEL": row["Model Code"], "Trim": row["Trim"],
            "DisplayColor": random.choice(colors), "VIN": f"5XX{random.randint(1000000, 9999999)}",
            "Status": random.choice(["GROUND", "TRANSIT", "PDI"]),
            "Days_on_Lot": days, "Est_Bleed_Cost": f"${days * 18:,}",
            "CRM_Demand_Score": random.randint(10, 95)
        })
    inv_df = pd.DataFrame(inv_rows)
    sales_rows = []
    for _ in range(140):
        row = key_df.sample(n=1).iloc[0]
        sales_rows.append({
            "Series": row["Series"], "Trim": row["Trim"], "DisplayColor": random.choice(colors),
            "VIN": f"5XX{random.randint(1000000, 9999999)}", "Gross_Profit": random.randint(800, 4500)
        })
    return inv_df, pd.DataFrame(sales_rows)

# --- 2. SIDEBAR ---
st.sidebar.markdown("<h1 style='font-size: 40px;'>M.C.</h1>", unsafe_allow_html=True)
st.sidebar.markdown("<div class='sidebar-label'>CONTROL PANEL</div>", unsafe_allow_html=True)

if st.sidebar.button("Initialize Data Engine"):
    inv, sales = generate_simulation()
    st.session_state["inv_data"] = inv
    st.session_state["sales_data"] = sales

# --- 3. MAIN DASHBOARD ---
if "inv_data" in st.session_state:
    f_inv = st.session_state["inv_data"]
    f_sales = st.session_state["sales_data"]

    # Filters
    all_series = sorted(f_inv['Series'].unique().tolist())
    selected_series = st.sidebar.multiselect("Active Inventory Filters", options=all_series, default=all_series)
    f_inv = f_inv[f_inv['Series'].isin(selected_series)]
    f_sales = f_sales[f_sales['Series'].isin(selected_series)]

    # Header
    col_a, col_b, col_c = st.columns([2, 1, 1])
    with col_a:
        st.title("Inventory & Velocity")
    with col_b:
        st.metric("Units Grounded", len(f_inv))
    with col_c:
        st.metric("30-Day Turn", len(f_sales))

    tab1, tab2, tab3 = st.tabs(["Stock Ledger", "Shortage Delta", "Asset Distribution"])

    with tab1:
        st.dataframe(
            f_inv[['Series', 'Trim', 'DisplayColor', 'Status', 'Days_on_Lot', 'Est_Bleed_Cost', 'CRM_Demand_Score']], 
            use_container_width=True, hide_index=True,
            column_config={"CRM_Demand_Score": st.column_config.ProgressColumn("Demand Heat", min_value=0, max_value=100)}
        )

    with tab2:
        inv_p = f_inv.pivot_table(index=['Series', 'Trim'], columns='DisplayColor', values='VIN', aggfunc='count', fill_value=0)
        sal_p = f_sales.pivot_table(index=['Series', 'Trim'], columns='DisplayColor', values='VIN', aggfunc='count', fill_value=0)
        delta_pivot = inv_p.subtract(sal_p, fill_value=0).fillna(0).astype(int).reset_index()
        
        def color_delta(val):
            if not isinstance(val, int): return ''
            if val < 0: return 'background-color: #FFE5E5; color: #D00000; font-weight: bold;'
            if val > 0: return 'background-color: #E5F9E5; color: #008000; font-weight: bold;'
            return 'color: #CCC;'

        color_cols = [c for c in delta_pivot.columns if c not in ['Series', 'Trim']]
        st.dataframe(delta_pivot.style.map(color_delta, subset=color_cols), use_container_width=True, hide_index=True)

    with tab3:
        # --- FIXED SUNBURST WHEEL ---
        # I used 'color=Series' and a categorical scale to ensure every slice is distinct.
        fig = px.sunburst(
            f_inv, 
            path=['Series', 'Trim', 'DisplayColor'],
            color='Series', 
            color_discrete_sequence=px.colors.qualitative.Pastel,
            template="plotly_white"
        )
        
        fig.update_traces(
            hovertemplate='<b>%{label}</b><br>Stock: %{value}',
            marker=dict(line=dict(color='#FFFFFF', width=1.5)),
            textinfo="label"
        )
        
        fig.update_layout(
            height=700,
            margin=dict(t=0, l=0, r=0, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Awaiting system initialization via sidebar.")

st.markdown("---")
st.markdown("<div style='text-align: center; color: #AAA; font-size: 11px;'>EST. 2026 | MARGIN CONTROL SYSTEMS</div>", unsafe_allow_html=True)