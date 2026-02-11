import streamlit as st
import pandas as pd
import plotly.express as px
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth

# 1. MUST BE THE VERY FIRST STREAMLIT COMMAND
st.set_page_config(page_title="Kia Digital Dashboard", layout="wide")

# 2. LOAD AUTHENTICATION CONFIG
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# 3. RENDER LOGIN (Lowercase 'main')
authenticator.login('main')

# 4. CHECK AUTHENTICATION STATUS
if st.session_state["authentication_status"]:
    # --- AUTHENTICATED AREA ---
    authenticator.logout('Logout', 'sidebar')
    st.sidebar.write(f"Welcome, *{st.session_state['name']}*")
    st.title("Kia Inventory Dashboard")

    @st.cache_data(ttl=5)
    def load_data():
        file_path = "data/KDealerCleanup.xlsx"
        xl = pd.ExcelFile(file_path)
        sheets = xl.sheet_names
        
        # Case-insensitive search for sheets
        inv_s = [s for s in sheets if 'dealer' in s.lower()][0]
        key_s = [s for s in sheets if 'key' in s.lower()][0]
        sal_s = [s for s in sheets if 'sales' in s.lower()][0]

        inventory_df = pd.read_excel(file_path, sheet_name=inv_s)
        key_df = pd.read_excel(file_path, sheet_name=key_s)
        sales_df = pd.read_excel(file_path, sheet_name=sal_s)

        # --- CLEANING ---
        inventory_df = inventory_df.dropna(subset=['VIN']).copy()
        inventory_df['VIN'] = inventory_df['VIN'].astype(str)
        inventory_df = inventory_df[inventory_df['VIN'].str.contains(r'\d', na=False)]
        inventory_df['STATUS'] = inventory_df['STATUS'].astype(str).str.strip().str.upper()

        key_df = key_df.drop_duplicates(subset=['Model Code']).copy()
        sales_df = sales_df.dropna(subset=['VIN']).copy()

        for df_tmp in [inventory_df, key_df, sales_df]:
            col = 'MODEL' if 'MODEL' in df_tmp.columns else 'Model Code'
            df_tmp[col] = df_tmp[col].astype(str).str.strip()

        # --- MERGE ---
        inv_final = pd.merge(inventory_df, key_df, left_on='MODEL', right_on='Model Code', how='left')
        sales_final = pd.merge(sales_df, key_df, left_on='MODEL', right_on='Model Code', how='left')

        # --- DATA SAFETY ---
        for df_f in [inv_final, sales_final]:
            df_f['Series'] = df_f['Series'].fillna('Unknown').astype(str)
            df_f['Trim'] = df_f['Trim'].fillna('Unknown').astype(str)
            if 'COLOR' in df_f.columns:
                df_f['EXT/INT'] = df_f['COLOR'].fillna('No Color').astype(str)
            else:
                df_f['EXT/INT'] = df_f['EXT/INT'].fillna('No Color').astype(str)

        return inv_final, sales_final

    try:
        inv_df, sales_df = load_data()

        # --- SIDEBAR & STATUS HEADERS ---
        all_series = sorted(inv_df['Series'].unique().tolist())
        default_val = ['Carnival'] if 'Carnival' in all_series else [all_series[0]]
        selected_series = st.sidebar.multiselect("Select Series:", options=all_series, default=default_val)

        f_inv = inv_df[inv_df['Series'].isin(selected_series)]
        f_sales = sales_df[sales_df['Series'].isin(selected_series)]

        status_counts = f_inv['STATUS'].value_counts()
        def get_count(code): return status_counts.get(code, 0)

        st.write(f"### Total stock: {len(f_inv)}")
        st.write(f"###### DS: {get_count('DS')} | AA: {get_count('AA')} | FA: {get_count('FA')} | IT: {get_count('IT')} | PA: {get_count('PA')} | TN: {get_count('TN')} | VA: {get_count('VA')}")

        # --- VELOCITY TABLE ---
        inv_pivot = f_inv.pivot_table(index='Trim', columns='EXT/INT', values='VIN', aggfunc='count', fill_value=0)
        sales_pivot = f_sales.pivot_table(index='Trim', columns='EXT/INT', values='VIN', aggfunc='count', fill_value=0)
        final_pivot = inv_pivot.subtract(sales_pivot, fill_value=0).fillna(0).astype(int)

        def color_delta(val):
            if val > 0: return 'color: green; font-weight: bold'
            elif val < 0: return 'color: red; font-weight: bold'
            return 'color: black'

        st.subheader("Current Stock - Last Month Sales")
        styled_pivot = final_pivot.style.applymap(color_delta).format(lambda x: "" if x == 0 else x)
        st.dataframe(styled_pivot, use_container_width=True)

        # --- SUNBURST ---
        st.subheader("Interactive Inventory Drill-Down")
        fig = px.sunburst(f_inv, path=['Series', 'Trim', 'EXT/INT', 'OPT GRP'], color='Trim', color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_traces(textinfo="label", maxdepth=3, hovertemplate='<b>%{label}</b><br>Count: %{value}')
        fig.update_layout(height=500, margin=dict(t=10, l=10, r=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Dashboard Error: {e}")

    # --- FOOTER ---
    st.markdown("---")
    st.markdown('<div style="text-align: center; color: gray;">created by nick warshak</div>', unsafe_allow_html=True)

elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')