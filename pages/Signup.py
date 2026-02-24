import streamlit as st
from supabase import create_client

# --- 1. PAGE CONFIG & THEME ---
st.set_page_config(page_title="Kia Elite | Join", layout="centered")

st.markdown("""
    <style>
    .stButton>button {
        background-color: #2E7D32 !important;
        color: white !important;
        width: 100%;
    }
    h1 { color: #002349; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SUPABASE CONNECTION ---
@st.cache_resource
def init_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_supabase()

# --- 3. SIGNUP FORM ---
st.title("Create Your Kia Elite Account")
st.write("Register your dealership email to begin inventory optimization.")

with st.form("registration_form"):
    new_email = st.text_input("Work Email")
    new_password = st.text_input("Create Password", type="password")
    full_name = st.text_input("Full Name / Title")
    
    submit = st.form_submit_button("Register Rooftop")
    
    if submit:
        if not new_email or not new_password:
            st.error("Email and Password are required.")
        else:
            try:
                # This creates the user in Supabase Auth
                res = supabase.auth.sign_up({
                    "email": new_email, 
                    "password": new_password,
                    "options": {"data": {"full_name": full_name}}
                })
                st.success("Registration successful!")
                st.balloons()
                st.info("Check your email for a confirmation link. Once verified, you can log in on the Home page.")
            except Exception as e:
                st.error(f"Registration failed: {e}")

st.markdown("---")
st.write("Already have an account? [Login here](/)")