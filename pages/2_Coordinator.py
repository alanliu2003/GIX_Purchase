import streamlit as st

from gix import service

st.set_page_config(page_title="Coordinator — GIX", layout="wide")
st.title("Coordinator dashboard")
st.caption(
    "Set status: **Under process**, **Arrived** (deducts budget when first marked), or **Problematic**."
)

if st.button("Refresh"):
    st.rerun()

teams = service.list_teams()
if teams:
    cols = st.columns(min(len(teams), 6))
    for i, t in enumerate(teams):
        with cols[i % len(cols)]:
            st.metric(f"Team {t['team_number']}", f"${t['budget_remaining']:.2f}")

purchases = service.list_purchases()
if not purchases:
    st.info("No purchases yet.")
else:
    status_labels = {
        "under_process": "Under process",
        "arrived": "Arrived",
        "problematic": "Problematic",
    }
    for p in purchases:
        with st.container():
            c1, c2 = st.columns([3, 1])
            with c1:
                st.subheader(f"#{p['id']} — Team {p['team_number']} — {p['cfo_name']}")
                st.write(f"Link: {p['purchase_link']}")
                line = float(p["price_per_item"]) * p["quantity"]
                st.write(
                    f"${p['price_per_item']:.2f} × {p['quantity']} = **${line:.2f}** | "
                    f"Instructor approved: **{'Yes' if p['instructor_approved'] else 'No'}**"
                )
                if p.get("notes"):
                    st.write("Notes:", p["notes"])
            with c2:
                new_status = st.selectbox(
                    "Status",
                    options=list(status_labels.keys()),
                    format_func=lambda k: status_labels[k],
                    key=f"status_{p['id']}",
                    index=list(status_labels.keys()).index(p["status"]),
                )
                if st.button("Apply", key=f"apply_{p['id']}"):
                    try:
                        service.update_purchase_status(p["id"], new_status)
                        st.success("Updated.")
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))
