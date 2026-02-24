import streamlit as st
from supabase import create_client, Client
import yaml
from yaml.loader import SafeLoader

# --- 1. CONNECTION & STATE ---
@st.cache_resource
def init_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_supabase()

def get_user_status(email):
    """Checks Supabase for payment status and caches it in session state."""
    if "is_paid" not in st.session_state:
        try:
            res = supabase.table("profiles").select("is_paid").eq("email", email).single().execute()
            st.session_state["is_paid"] = res.data["is_paid"] if res.data else False
        except:
            st.session_state["is_paid"] = False
    return st.session_state["is_paid"]

# --- 2. PAGE CONFIG ---
st.set_page_config(page_title="Kia Elite | Home", layout="wide")

# --- 3. LOGIN LOGIC ---
if not st.session_state.get("authentication_status"):
    st.title("Partner Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        try:
            # Login via Supabase
            auth_res = supabase.auth.sign_in_with_password({"email": email, "password": password})
            
            # If successful, set session variables
            st.session_state["authentication_status"] = True
            st.session_state["user_email"] = email
            
            # Immediately check their paid status
            get_user_status(email)
            st.rerun()
        except Exception:
            st.error("Invalid credentials. Please try again.")
    
    st.write("New dealership? [Create an account](/Signup)")

# --- 4. SUCCESS STATE (What the user sees after login) ---
else:
    st.success(f"Logged in as {st.session_state['user_email']}")
    if st.button("Enter Dashboard"):
        st.switch_page("pages/Dashboard.py")
    
    if st.button("Logout"):
        supabase.auth.sign_out()
        st.session_state.clear()
        st.rerun()

# --- 5. THEMING & UI ---
# (Your navy/green markdown styles go here)
st.markdown("""
    <style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@400;600&display=swap');
    
    .main {
        background-color: #FFFFFF;
    }

    /* Professional Navy & Green Gradient Hero */
    .hero-section {
        background: linear-gradient(135deg, #002349 0%, #2E7D32 100%);
        padding: 100px 50px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 50px;
    }

    .hero-title {
        font-family: 'Playfair Display', serif;
        font-size: 64px;
        margin-bottom: 10px;
    }

    .hero-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 20px;
        opacity: 0.9;
    }

    /* Hide the sidebar on the home page for a 'Landing Page' feel */
    section[data-testid="stSidebar"] {
        display: none;
    }
    
    /* Button Styling */
    .stButton>button {
        background-color: #2E7D32 !important;
        color: white !important;
        border: none !important;
        padding: 15px 30px !important;
        border-radius: 5px !important;
        font-weight: 600 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HERO CONTENT ---
st.markdown("""
    <div class="hero-section">
        <div class="hero-title">Kia Elite</div>
        <div class="hero-subtitle">Innovation in Dealership Inventory Intelligence</div>
    </div>
    """, unsafe_allow_html=True)

# --- FEATURES SECTION ---
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### Predictive Insights")
    st.write("Leverage advanced analytics to forecast shortages before they impact your month-end.")

with col2:
    st.markdown("### Inventory Control")
    st.write("A refined view of your lot that matches the precision of the Kia brand.")

with col3:
    st.markdown("### Executive Reporting")
    st.write("Generate clean, high-stakes reports for general managers and owners in seconds.")

st.divider()

# --- CALL TO ACTION ---
st.write("Ready to optimize your lot?")
if st.button("Access Dashboard"):
    st.switch_page("pages/Dashboard.py") # This takes them to your tool