import streamlit as st
import os

st.write("Current Working Directory:", os.getcwd())
st.write("All Detected Secrets:", st.secrets.to_dict())

if "SUPABASE_URL" in st.secrets:
    st.success("Found it!")
else:
    st.error("Still missing. Streamlit sees 0 secrets.")