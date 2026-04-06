# GIX team purchase tracker — Streamlit home page.
# Students use sidebar pages to submit purchases; coordinator reviews in MySQL-backed UI.
# I manually changed: service.py error messages.
import streamlit as st

st.set_page_config(page_title="GIX Purchases", layout="wide")
st.title("GIX team purchases")
st.markdown(
    "Use the sidebar for **Student** (submit purchases), **Coordinator** (review and set status), "
    "or **GIX Wayfinder** (campus resources — local dictionary, no database). "
    "Purchase data uses **MySQL** — configure `MYSQL_*` in `.env` and run `python init_db.py` once.\n\n"
    "The web UI also runs via FastAPI: `uvicorn api.main:app --reload` → http://127.0.0.1:8000"
)
