"""
GIX Wayfinder — Component E: campus resources with local in-memory dictionary storage.
"""

from __future__ import annotations

import streamlit as st

from gix.wayfinder_data import CAMPUS_RESOURCES, REQUIRED_RESOURCE_KEYS

st.set_page_config(page_title="GIX Wayfinder", layout="wide")
st.title("GIX Wayfinder")
st.caption(
    "Find campus resources (makerspace, printing, study spots, and more). "
    "Data is stored locally in a Python dictionary — nothing is sent to a database."
)


def _categories(resources: dict[str, dict]) -> list[str]:
    cats = {r["category"] for r in resources.values() if isinstance(r.get("category"), str)}
    return sorted(cats)


def _matches_query(record: dict, q: str) -> bool:
    normalized = (q or "").strip().lower()
    if not normalized:
        return True
    q_lower = normalized
    haystack: list[str] = []
    for key in REQUIRED_RESOURCE_KEYS:
        v = record.get(key)
        if isinstance(v, str):
            haystack.append(v.lower())
    tags = record.get("tags")
    if isinstance(tags, list):
        haystack.extend(t.lower() for t in tags if isinstance(t, str))
    return any(q_lower in part for part in haystack)


def _filter_resources(
    resources: dict[str, dict],
    query: str,
    selected_categories: list[str],
) -> list[tuple[str, dict]]:
    out: list[tuple[str, dict]] = []
    for rid, record in resources.items():
        if selected_categories and record.get("category") not in selected_categories:
            continue
        if not _matches_query(record, query):
            continue
        out.append((rid, record))
    out.sort(key=lambda x: str(x[1].get("name", x[0])).lower())
    return out


with st.sidebar:
    st.header("Search & filters")
    search = st.text_input(
        "Search",
        placeholder="e.g. printing, bike, quiet…",
        help="Matches name, description, building, category, and tags (substring, case-insensitive).",
    )
    all_cats = _categories(CAMPUS_RESOURCES)
    categories = st.multiselect(
        "Categories",
        options=all_cats,
        default=[],
        help="Leave empty to include all categories.",
    )

filtered = _filter_resources(CAMPUS_RESOURCES, search, categories)

st.subheader("Matching resources")
if not filtered:
    st.info(
        "No resources match your search and category filters. "
        "Try clearing the category filter or using a shorter search term."
    )
else:
    st.metric("Results", len(filtered))
    for rid, r in filtered:
        name = str(r.get("name", rid))
        cat = str(r.get("category", ""))
        building = str(r.get("building", ""))
        desc = str(r.get("description", ""))
        tags = r.get("tags")
        tag_line = ""
        if isinstance(tags, list) and tags:
            tag_line = " · ".join(str(t) for t in tags if isinstance(t, str))

        with st.container(border=True):
            st.markdown(f"### {name}")
            st.caption(f"**{cat}** · {building}")
            st.write(desc)
            if tag_line:
                st.markdown(f"*Tags:* {tag_line}")
