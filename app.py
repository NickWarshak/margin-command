import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import random

# --- 0. THE HUD STYLING (Jane & Rye Command Center) ---
st.set_page_config(page_title="Jane & Rye | Margin Command", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    /* 1. Target the Multiselect Pills (Series Names) */
    span[data-baseweb="tag"] {
        background-color: #1F2937 !important; /* Navy Blue background */
        border: 1px solid rgba(225, 29, 72, 0.2) !important; /* Subtle Red border for J&R feel */
    }

    /* 2. Target the Active Tab Underline (Inventory Matrix line) */
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: #1F2937 !important; /* Navy Blue line */
    }
    /* Dark Mode Global Background & Typography */
    @import url('https://fonts.googleapis.com/css2?family=Rockwell:ital,wght@0,400;0,700;1,400&family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');
    
    .stApp { background-color: #0A0A0A; color: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #050505; border-right: 1px solid rgba(255, 255, 255, 0.05); }
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    h1, h2, h3 { font-family: 'Rockwell', serif !important; color: #FFFFFF !important; font-weight: 400 !important; }

    /* Tab Styling (The HUD Toggles) */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; background-color: transparent; border-bottom: 1px solid rgba(255, 255, 255, 0.1); }
    .stTabs [data-baseweb="tab"] { 
        height: 50px; white-space: pre-wrap; background-color: transparent; border-radius: 0px; 
        border: 1px solid transparent; gap: 1px; padding-top: 10px; padding-bottom: 10px; 
        font-weight: 600; color: rgba(255, 255, 255, 0.4); text-transform: uppercase; 
        letter-spacing: 2px; font-size: 10px; transition: all 0.3s ease; 
    }
    .stTabs [aria-selected="true"] { 
        background-color: rgba(225, 29, 72, 0.05) !important; color: #e11d48 !important; 
        border: 1px solid rgba(225, 29, 72, 0.3) !important; border-bottom: 1px solid transparent !important; 
    }

    #MainMenu, footer, header {visibility: hidden;}

    /* THE TABLE UPGRADE: Aggressive "Terminal" Styling */
    [data-testid="stDataFrame"] {
        background-color: #050505;
        border: 1px solid rgba(225, 29, 72, 0.2);
        border-radius: 2px;
        box-shadow: inset 0 0 10px rgba(0,0,0,0.5);
    }
    [data-testid="stDataFrame"] table { font-family: 'JetBrains Mono', monospace !important; }

    [data-testid="stDataFrame"] th {
        background-color: #0A0A0A !important;
        color: #e11d48 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 10px !important;
        font-weight: 700 !important;
        border-bottom: 1px solid rgba(225, 29, 72, 0.5) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    [data-testid="stDataFrame"] td {
        background-color: transparent !important;
        color: rgba(255, 255, 255, 0.7) !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.02) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.02) !important;
        font-size: 11px !important;
        transition: all 0.1s ease;
    }
    [data-testid="stDataFrame"] tr:hover td {
        color: #FFFFFF !important;
        background-color: rgba(225, 29, 72, 0.1) !important;
    }

    /* High-Contrast Metrics */
    [data-testid="stMetricValue"] { color: #e11d48 !important; font-family: 'Rockwell', serif !important; }
    [data-testid="stMetricLabel"] { color: rgba(255, 255, 255, 0.4) !important; text-transform: uppercase; letter-spacing: 2px; font-size: 10px; }

    /* Buttons */
    .stButton>button { 
        width: 100%; background-color: transparent; border: 1px solid rgba(225, 29, 72, 0.4); 
        color: #e11d48; text-transform: uppercase; letter-spacing: 3px; font-size: 10px; 
        transition: all 0.3s ease; border-radius: 0px; 
    }
    .stButton>button:hover { background-color: #e11d48; color: white; border: 1px solid #e11d48; }
</style>
""", unsafe_allow_html=True)

# --- 1. THE REFERENCE CHART ---
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

# --- 2. DEMO DATA GENERATOR ---
DEMO_COLORS = ["Glacial White Pearl", "Ebony Black", "Wolf Gray", "Gravity Gray", "Everlasting Silver", "Dawning Red"]
STATUS_CODES = ["GROUND", "IN-TRANSIT", "PDI", "HOLD"]

def generate_simulation():
    key_df = get_model_key()
    inv_rows = []
    
    for _ in range(180):
        row = key_df.sample(n=1).iloc[0]
        days = random.randint(1, 140)
        bleed = days * 18
        demand = random.randint(10, 95)
        inv_rows.append({
            "Series": row["Series"],
            "MODEL": row["Model Code"],
            "Trim": row["Trim"],
            "DisplayColor": random.choice(DEMO_COLORS),
            "VIN": f"5XX{random.randint(1000000, 9999999)}",
            "Status": random.choices(STATUS_CODES, weights=[0.6, 0.2, 0.1, 0.1])[0],
            "Days_on_Lot": days,
            "Est_Bleed_Cost": f"${bleed:,}",
            "CRM_Demand_Score": demand
        })
    
    inv_df = pd.DataFrame(inv_rows)
    sales_rows = []
    
    for _ in range(140):
        weights = np.where(key_df["Series"].isin(["TELLURIDE", "SPORTAGE"]), 0.8, 0.2)
        row = key_df.sample(n=1, weights=weights).iloc[0]
        sales_rows.append({
            "Series": row["Series"],
            "MODEL": row["Model Code"],
            "Trim": row["Trim"],
            "DisplayColor": random.choice(DEMO_COLORS),
            "VIN": f"5XX{random.randint(1000000, 9999999)}",
            "Gross_Profit": random.randint(800, 4500)
        })
        
    sales_df = pd.DataFrame(sales_rows)
    return inv_df, sales_df

# --- 3. SIDEBAR UI ---
st.sidebar.markdown("<h1 style='font-family: \"Playfair Display\", serif; text-align: center; font-size: 32px; margin-bottom: 0; font-style: italic;'><span style='color: #e11d48;'>J</span>&R</h1>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align: center; color: rgba(255,255,255,0.4); font-size: 10px; letter-spacing: 4px; margin-bottom: 40px;'>MARGIN COMMAND</p>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='color: rgba(255,255,255,0.4); font-size: 10px; letter-spacing: 2px;'>TELEMETRY LINK</p>", unsafe_allow_html=True)

if st.sidebar.button("Run Simulation Engine"):
    with st.spinner("Compiling synthetic array..."):
        inv, sales = generate_simulation()
        st.session_state["inv_data"] = inv
        st.session_state["sales_data"] = sales
        st.sidebar.success("Telemetry Active")

# --- 4. MAIN DASHBOARD ---
if "inv_data" in st.session_state:
    f_inv = st.session_state["inv_data"]
    f_sales = st.session_state["sales_data"]

    all_series = sorted(f_inv['Series'].unique().tolist())
    selected_series = st.sidebar.multiselect("Filter Series", options=all_series, default=all_series)
    
    f_inv = f_inv[f_inv['Series'].isin(selected_series)]
    f_sales = f_sales[f_sales['Series'].isin(selected_series)]

    col_a, col_b, col_c = st.columns([2, 1, 1])
    with col_a:
        st.title("Strategic Overview")
    with col_b:
        st.metric("Units on Ground", len(f_inv))
    with col_c:
        st.metric("30-Day Velocity", len(f_sales))

    tab1, tab2, tab3 = st.tabs(["INVENTORY MATRIX", "DELTA ANALYSIS", "COMPOSITION"])

    with tab1:
        st.markdown("### Active Floorplan Distribution")
        st.markdown("<p style='color: rgba(255,255,255,0.5); font-size: 12px; font-style: italic; margin-bottom: 20px;'>Data Brief: A real-time ledger of your physical assets.</p>", unsafe_allow_html=True)
        st.dataframe(
            f_inv[['Series', 'Trim', 'DisplayColor', 'Status', 'Days_on_Lot', 'Est_Bleed_Cost', 'CRM_Demand_Score']].head(50),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Series": st.column_config.TextColumn("Model Family", width="medium"),
                "Trim": st.column_config.TextColumn("Trim Level", width="medium"),
                "DisplayColor": st.column_config.TextColumn("Exterior", width="medium"),
                "Status": st.column_config.TextColumn("DMS Status", width="small"),
                "Days_on_Lot": st.column_config.NumberColumn("Age (Days)", format="%d"),
                "Est_Bleed_Cost": st.column_config.TextColumn("Floorplan Bleed", width="small"),
                "CRM_Demand_Score": st.column_config.ProgressColumn("Demand Heat", format="%d", min_value=0, max_value=100)
            }
        )

    with tab2:
        st.markdown("### Performance Gap (Stock vs Velocity)")
        st.markdown("<p style='color: rgba(255,255,255,0.5); font-size: 12px; font-style: italic; margin-bottom: 20px;'>Data Brief: Shortage vs Overflow Analysis.</p>", unsafe_allow_html=True)
        
        inv_p = f_inv.pivot_table(index=['Series', 'Trim'], columns='DisplayColor', values='VIN', aggfunc='count', fill_value=0)
        sal_p = f_sales.pivot_table(index=['Series', 'Trim'], columns='DisplayColor', values='VIN', aggfunc='count', fill_value=0)
        delta_pivot = inv_p.subtract(sal_p, fill_value=0).fillna(0).astype(int).reset_index()

        def color_delta_dark(val):
            if isinstance(val, int):
                if val < 0: 
                    return 'background-color: rgba(225, 29, 72, 0.08); color: #ff4d4d; font-weight: bold;'
                elif val > 0: 
                    return 'background-color: rgba(34, 197, 94, 0.08); color: #4ade80; font-weight: bold;'
            return 'color: rgba(255, 255, 255, 0.1);'

        color_cols = [col for col in delta_pivot.columns if col not in ['Series', 'Trim']]
        styled_delta = delta_pivot.style.map(color_delta_dark, subset=color_cols)
        st.dataframe(styled_delta, use_container_width=True, hide_index=True)

    with tab3:
        st.markdown("### Asset Composition")
        # UPDATED PALETTE: Swapped dark navy/slates for dark reds/crimsons
        jr_palette = [
            "#e11d48", # J&R Red
            "#4c0519", # Darkest Crimson (Replacing Navy)
            "#FFFFFF", # White
            "#881337", # Deep Rose
            "#9f1239", # Deep Crimson
            "#fb7185", # Soft Red/Pink
            "#D1D5DB", # Light Gray
            "#be123c", # Solid Red
            "#450a0a", # Blood Red (Replacing Charcoal)
            "#F3F4F6", # Off White
            "#991b1b"  # Dark Red
        ]
        
        fig = px.sunburst(
            f_inv,
            path=['Series', 'Trim', 'DisplayColor'],
            color_discrete_sequence=jr_palette
        )
        fig.update_traces(
            hovertemplate='<b>%{label}</b><br>Count: %{value}',
            marker=dict(line=dict(color='#0A0A0A', width=2)),
            textfont=dict(size=13, family='Inter')
        )
        fig.update_layout(
            height=750,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=20, l=20, r=20, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Initialize the simulation engine in the sidebar to populate the dashboard.")
    st.markdown("<br><br><div style='text-align: center; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 20px; color: rgba(255,255,255,0.2); font-size: 10px; letter-spacing: 2px;'>JANE & RYE ELITE SYSTEMS</div>", unsafe_allow_html=True)