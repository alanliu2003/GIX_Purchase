from decimal import Decimal

import streamlit as st

from gix import service

st.set_page_config(page_title="Student — GIX", layout="wide")
st.title("Submit a purchase")
st.caption(
    "New purchases start as **Under process**. The coordinator sets **Arrived** when appropriate; "
    "the budget is deducted only when status becomes Arrived."
)

with st.form("purchase"):
    team_number = st.number_input("Team number", min_value=1, step=1, value=1)
    cfo_name = st.text_input("CFO name")
    purchase_link = st.text_input("Purchase link", placeholder="https://...")
    price_per_item = st.number_input("Price per item ($)", min_value=0.0, format="%.2f")
    quantity = st.number_input("Quantity", min_value=1, step=1, value=1)
    notes = st.text_area("Notes")
    instructor_approved = st.checkbox("Instructor approved")
    submitted = st.form_submit_button("Submit purchase")

if submitted:
    try:
        p = service.create_purchase(
            team_number=int(team_number),
            cfo_name=cfo_name,
            purchase_link=purchase_link,
            price_per_item=Decimal(str(price_per_item)),
            quantity=int(quantity),
            notes=notes,
            instructor_approved=instructor_approved,
        )
        st.success(f"Recorded purchase #{p['id']} for team {p['team_number']}.")
    except ValueError as e:
        st.error(str(e))
