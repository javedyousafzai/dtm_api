"""
IOM DTM Dashboard — Streamlit App
Run with: streamlit run dtm_dashboard.py
"""

import os
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from dtmapi import DTMApi

# ── Setup ─────────────────────────────────────────────────────────────────────
load_dotenv()
st.set_page_config(
    page_title="IOM DTM Explorer",
    page_icon="🌍",
    layout="wide"
)

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🌍 IOM DTM Displacement Data Explorer")
st.markdown("Data sourced from the [IOM Displacement Tracking Matrix API](https://dtm.iom.int/)")
st.divider()

# ── API Init ──────────────────────────────────────────────────────────────────
api_key = os.getenv("DTMAPI_SUBSCRIPTION_KEY")
if not api_key:
    st.error("⚠️ No API key found. Make sure `DTMAPI_SUBSCRIPTION_KEY` is set in your `.env` file.")
    st.stop()

api = DTMApi(subscription_key=api_key, api_version="v3")

# ── Sidebar Controls ──────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Filters")

    # Country input
    country = st.text_input("Country Name", value="Pakistan", help="e.g. Ukraine, Somalia, Sudan")

    # Admin level
    admin_level = st.selectbox(
        "Admin Level",
        options=["Admin 0 (National)", "Admin 1 (Regional)", "Admin 2 (District)"]
    )

    # Date range
    st.subheader("Date Range (optional)")
    col1, col2 = st.columns(2)
    with col1:
        from_date = st.date_input("From", value=None)
    with col2:
        to_date = st.date_input("To", value=None)

    fetch_btn = st.button("🔍 Fetch Data", use_container_width=True, type="primary")

# ── Fetch & Display ───────────────────────────────────────────────────────────
if fetch_btn:
    if not country:
        st.warning("Please enter a country name.")
        st.stop()

    # Build kwargs
    kwargs = {"CountryName": country}
    if from_date:
        kwargs["FromReportingDate"] = str(from_date)
    if to_date:
        kwargs["ToReportingDate"] = str(to_date)

    with st.spinner(f"Fetching {admin_level} data for **{country}**..."):
        try:
            if "Admin 0" in admin_level:
                data = api.get_idp_admin0_data(**kwargs)
            elif "Admin 1" in admin_level:
                data = api.get_idp_admin1_data(**kwargs)
            else:
                data = api.get_idp_admin2_data(**kwargs)
        except Exception as e:
            st.error(f"API Error: {e}")
            st.stop()

    # Normalise to DataFrame
    if data is None or (hasattr(data, "__len__") and len(data) == 0):
        st.warning("No data returned. Try a different country or date range.")
        st.stop()

    df = pd.DataFrame(data) if not isinstance(data, pd.DataFrame) else data

    # ── Summary metrics ───────────────────────────────────────────────────────
    st.subheader(f"📊 {country} — {admin_level}")

    m1, m2, m3 = st.columns(3)
    m1.metric("Total Rows", f"{len(df):,}")
    m2.metric("Columns", len(df.columns))

    # Try to show max IDP figure if column exists
    idp_cols = [c for c in df.columns if "idp" in c.lower() or "individual" in c.lower() or "figure" in c.lower()]
    if idp_cols:
        total = pd.to_numeric(df[idp_cols[0]], errors="coerce").sum()
        m3.metric(f"Total ({idp_cols[0]})", f"{int(total):,}")
    else:
        m3.metric("Country", country)

    st.divider()

    # ── Chart ──────────────────────────────────────────────────────────────────
    if idp_cols:
        chart_col = [c for c in df.columns if "name" in c.lower() or "admin" in c.lower()]
        if chart_col and len(df) <= 100:
            chart_df = df[[chart_col[0], idp_cols[0]]].copy()
            chart_df[idp_cols[0]] = pd.to_numeric(chart_df[idp_cols[0]], errors="coerce")
            chart_df = chart_df.dropna().sort_values(idp_cols[0], ascending=False).head(20)
            st.bar_chart(chart_df.set_index(chart_col[0]))

    # ── Full Data Table ────────────────────────────────────────────────────────
    st.subheader("📋 Full Data")
    st.dataframe(df, use_container_width=True, height=500)

    # ── Download ───────────────────────────────────────────────────────────────
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download as CSV",
        data=csv,
        file_name=f"dtm_{country.lower().replace(' ', '_')}_{admin_level.split()[0].lower()}.csv",
        mime="text/csv"
    )

else:
    st.info("👈 Set your filters in the sidebar and click **Fetch Data** to begin.")