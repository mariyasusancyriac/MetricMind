import streamlit as st
import pandas as pd
import random
import sys
import os

# Ensure project root is in Python PATH for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.orchestrator import AgenticSemanticOrchestrator

st.set_page_config(page_title="MetricMind: Governed BI Portal", layout="wide", page_icon="🧠")

# Session state initialization for Email + OTP authentication
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "otp_secret" not in st.session_state:
    st.session_state["otp_secret"] = None

# --- AUTHENTICATION GATEWAY ---
if not st.session_state["authenticated"]:
    st.title("🔐 MetricMind Enterprise Authentication")
    st.markdown("Please authenticate with your corporate credentials to access the Governed Semantic BI Engine.")
    
    email = st.text_input("Corporate Email", placeholder="analyst@axlero.com")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("Request 6-Digit OTP"):
            if "@" in email and "." in email:
                st.session_state["otp_secret"] = str(random.randint(100000, 999999))
                st.success(f"Verification OTP Generated: **{st.session_state['otp_secret']}**")
            else:
                st.error("Please enter a valid corporate email.")
                
    user_otp = st.text_input("Enter Received OTP", type="password", max_chars=6)
    
    if st.button("Verify & Sign In"):
        if st.session_state["otp_secret"] and user_otp == st.session_state["otp_secret"]:
            st.session_state["authenticated"] = True
            st.success("Authentication successful! Loading workspace...")
            st.rerun()
        else:
            st.error("Invalid OTP code. Please verify and retry.")
    st.stop()

# --- MAIN GOVERNED BI INTERFACE ---
st.title("🧠 MetricMind: Agentic Semantic BI Engine")
st.caption("Governed Multi-Cube Conversational Analytics with Zero SQL Hallucinations")

# Executive Metric Cards (Aggregated Overview)
data_path = os.path.join(os.path.dirname(__file__), "..", "data", "enterprise_data.csv")
if os.path.exists(data_path):
    raw_df = pd.read_csv(data_path)
    tot_rev = raw_df["gross_revenue"].sum()
    tot_cogs = raw_df["cogs"].sum()
    tot_margin = raw_df["net_margin"].sum()
    margin_pct = (tot_margin / tot_rev * 100) if tot_rev else 0.0

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Governed Gross Revenue", f"${tot_rev:,.2f}")
    kpi2.metric("Total COGS", f"${tot_cogs:,.2f}")
    kpi3.metric("Net Margin", f"${tot_margin:,.2f}")
    kpi4.metric("Profit Margin %", f"{margin_pct:.1f}%")

st.divider()

# Conversational Interface
user_query = st.text_input(
    "Enter business query:",
    value="Why did our European margins drop last quarter?"
)

if st.button("Run Governed Semantic Query"):
    with st.spinner("Translating intent & consulting Query Cost Governor..."):
        orchestrator = AgenticSemanticOrchestrator()
        response = orchestrator.run_agentic_flow(user_query)

    if response.get("status") == "blocked":
        st.error(f"🛑 {response['message']}")
    else:
        st.subheader("💡 Multi-Step Root-Cause Diagnostic")
        st.info(response["diagnostic_summary"])

        results = response.get("governed_data", [])
        if results:
            res_df = pd.DataFrame(results)
            col_a, col_b = st.columns([1, 1])

            with col_a:
                st.markdown("#### Governed Data Table")
                st.dataframe(res_df, use_container_width=True)

            with col_b:
                st.markdown("#### Trend Line Visualization")
                if "quarter" in res_df.columns and "profit_margin_pct" in res_df.columns:
                    chart_data = res_df.set_index("quarter")["profit_margin_pct"]
                    st.line_chart(chart_data)
                elif "quarter" in res_df.columns and "total_revenue" in res_df.columns:
                    st.bar_chart(res_df.set_index("quarter")["total_revenue"])

        # Audit Trail Inspector
        with st.expander("🔍 Inspect Governed Origin & Audit Trail"):
            st.markdown("**Compiled Governed SQL (Semantic Layer):**")
            st.code(response.get("compiled_sql", "N/A"), language="sql")
            st.markdown("**Semantic API Request Payload:**")
            st.json(response.get("semantic_payload", {}))
            st.markdown("**Cost Governor Circuit-Breaker Status:**")
            st.json(response.get("cost_evaluation", {}))