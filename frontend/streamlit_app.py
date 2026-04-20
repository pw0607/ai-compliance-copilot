"""
Streamlit frontend for AI Compliance Copilot v3.

Features:
- Single and multi-framework analysis
- Remediation priority plan
- Compliance history viewer
- JSON + PDF export
- Framework comparison dashboard
"""

import json
import os
import sys
from pathlib import Path

import requests
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.report_generator import generate_report

API_URL = os.getenv("API_URL", "http://localhost:8000")

FRAMEWORKS = {
    "nist": {"name": "NIST AI RMF", "desc": "Governance, risk lifecycle, measurement"},
    "hipaa": {"name": "HIPAA", "desc": "PHI protection, encryption, access controls"},
    "nist_csf": {"name": "NIST CSF", "desc": "Identify, Protect, Detect, Respond, Recover"},
    "fedramp": {"name": "FedRAMP", "desc": "Authentication, audit logs, boundary protection"},
    "iso": {"name": "ISO 27001", "desc": "ISMS, policies, incident management"},
    "owasp": {"name": "OWASP LLM Top 10", "desc": "Prompt injection, data leakage, model security"},
    "gdpr": {"name": "GDPR", "desc": "Data minimization, privacy by design, DPIA"},
}

SEVERITY_COLORS = {"critical": "red", "high": "orange", "medium": "blue", "low": "green"}

st.set_page_config(page_title="AI Compliance Copilot", page_icon="🛡️", layout="wide")

# --- Sidebar ---
with st.sidebar:
    st.header("🛡️ AI Compliance Copilot")
    st.caption("v3.0.0")
    st.divider()
    st.subheader("Frameworks")
    for info in FRAMEWORKS.values():
        st.markdown(f"**{info['name']}** - {info['desc']}")
    st.divider()
    st.markdown("API Docs: `localhost:8000/docs`")

# --- Tabs ---
tab_single, tab_multi, tab_history = st.tabs(["Single Analysis", "Multi-Framework Comparison", "History"])

# ===== SINGLE ANALYSIS TAB =====
with tab_single:
    st.subheader("Evaluate against a single framework")

    system_desc = st.text_area("Describe your AI system", height=160, key="single_desc",
        placeholder="Example: A radiology AI that analyzes chest X-rays to detect pneumonia...")

    col_fw, col_btn = st.columns([3, 1])
    with col_fw:
        fw_key = st.selectbox("Framework", options=list(FRAMEWORKS.keys()),
            format_func=lambda k: FRAMEWORKS[k]["name"])
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        run_single = st.button("Run Analysis", key="run_single", use_container_width=True)

    if run_single:
        if not system_desc or len(system_desc.strip()) < 20:
            st.error("Description must be at least 20 characters.")
        else:
            with st.spinner("Analyzing..."):
                try:
                    resp = requests.post(f"{API_URL}/analyze",
                        json={"system_description": system_desc, "framework": fw_key}, timeout=60)
                    resp.raise_for_status()
                    st.session_state["single_result"] = resp.json()
                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to backend. Is it running on port 8000?")
                except requests.exceptions.HTTPError as exc:
                    st.error(f"Error: {exc.response.text}")

    data = st.session_state.get("single_result")
    if data:
        st.divider()
        if data.get("prompt_injection_detected"):
            st.warning("Potential prompt injection detected.")
        if data.get("human_review_recommended"):
            st.info("Human review recommended.")

        score = data["risk_score"]
        color = "🟢" if score <= 0.3 else "🟡" if score <= 0.6 else "🔴"
        label = "Low" if score <= 0.3 else "Medium" if score <= 0.6 else "High"
        st.subheader(f"Risk Score: {color} {score} ({label})")
        st.markdown(f"**{data.get('framework_name', '')}** -- {data['summary']}")

        rs = data.get("risk_summary", {})
        if rs:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total", rs.get("total_controls", 0))
            c2.metric("Compliant", rs.get("compliant", 0))
            c3.metric("Partial", rs.get("partial", 0))
            c4.metric("Non-Compliant", rs.get("non_compliant", 0))

        # Results table
        st.subheader("Compliance Results")
        table = []
        for r in data.get("compliance_results", []):
            icon = {"Yes": "✅", "Partial": "⚠️", "No": "❌"}.get(r["status"], "")
            sev = r.get("severity", "medium").upper()
            table.append({
                "ID": r["control_id"], "Title": r["control_title"],
                "Severity": sev, "Status": f"{icon} {r['status']}",
                "Explanation": r["explanation"],
                "Evidence": ", ".join(r.get("evidence_found", [])) or "--",
                "Gaps": ", ".join(r.get("gaps", [])) or "--",
            })
        st.dataframe(table, use_container_width=True, height=400)

        # Remediation plan
        plan = data.get("remediation_plan", [])
        if plan:
            st.subheader("Prioritized Remediation Plan")
            for i, item in enumerate(plan, 1):
                sev = item.get("severity", "medium")
                st.markdown(
                    f"**{i}. [{sev.upper()}] {item['control_id']} -- {item['control_title']}** "
                    f"(priority: {item['priority_score']})"
                )
                st.markdown(f"   {item['recommendation']}")

        # Export buttons
        st.divider()
        col_pdf, col_json = st.columns(2)
        with col_pdf:
            try:
                pdf_path = generate_report(data)
                with open(pdf_path, "rb") as f:
                    st.download_button("Download PDF", data=f,
                        file_name=pdf_path.split("/")[-1], mime="application/pdf",
                        use_container_width=True)
            except Exception as exc:
                st.error(f"PDF error: {exc}")
        with col_json:
            json_str = json.dumps(data, indent=2)
            st.download_button("Download JSON", data=json_str,
                file_name=f"compliance_{data.get('framework','')}.json",
                mime="application/json", use_container_width=True)

# ===== MULTI-FRAMEWORK TAB =====
with tab_multi:
    st.subheader("Compare across multiple frameworks")

    multi_desc = st.text_area("Describe your AI system", height=160, key="multi_desc",
        placeholder="Paste the same system description to compare across frameworks...")

    selected_fws = st.multiselect("Select frameworks to compare",
        options=list(FRAMEWORKS.keys()),
        default=["nist", "hipaa"],
        format_func=lambda k: FRAMEWORKS[k]["name"])

    run_multi = st.button("Run Comparison", key="run_multi", use_container_width=True)

    if run_multi:
        if not multi_desc or len(multi_desc.strip()) < 20:
            st.error("Description must be at least 20 characters.")
        elif len(selected_fws) < 2:
            st.error("Select at least 2 frameworks to compare.")
        else:
            with st.spinner("Running multi-framework analysis..."):
                try:
                    resp = requests.post(f"{API_URL}/analyze/multi",
                        json={"system_description": multi_desc, "frameworks": selected_fws}, timeout=120)
                    resp.raise_for_status()
                    st.session_state["multi_result"] = resp.json()
                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to backend.")
                except requests.exceptions.HTTPError as exc:
                    st.error(f"Error: {exc.response.text}")

    multi_data = st.session_state.get("multi_result")
    if multi_data:
        comparison = multi_data.get("comparison", [])
        if comparison:
            st.divider()
            st.subheader("Framework Comparison")

            # Summary table
            comp_table = []
            for c in comparison:
                score = c["risk_score"]
                icon = "🟢" if score <= 0.3 else "🟡" if score <= 0.6 else "🔴"
                comp_table.append({
                    "Framework": c["framework_name"],
                    "Risk Score": f"{icon} {score}",
                    "Compliant": c["compliant"],
                    "Partial": c["partial"],
                    "Non-Compliant": c["non_compliant"],
                })
            st.dataframe(comp_table, use_container_width=True)

            # Per-framework details in expanders
            results = multi_data.get("results", {})
            for fw_key, fw_result in results.items():
                if "error" in fw_result:
                    st.error(f"{fw_key}: {fw_result['error']}")
                    continue
                fw_name = fw_result.get("framework_name", fw_key)
                with st.expander(f"{fw_name} -- Risk: {fw_result['risk_score']}"):
                    for r in fw_result.get("compliance_results", []):
                        icon = {"Yes": "✅", "Partial": "⚠️", "No": "❌"}.get(r["status"], "")
                        st.markdown(f"{icon} **{r['control_id']}** {r['control_title']} [{r.get('severity','medium').upper()}]")

            # Export full comparison as JSON
            st.divider()
            st.download_button("Download Full Comparison JSON",
                data=json.dumps(multi_data, indent=2),
                file_name="multi_framework_comparison.json",
                mime="application/json", use_container_width=True)

# ===== HISTORY TAB =====
with tab_history:
    st.subheader("Analysis History")

    col_refresh, col_clear = st.columns([1, 1])
    with col_refresh:
        if st.button("Refresh", key="refresh_history", use_container_width=True):
            st.session_state.pop("history_data", None)
    with col_clear:
        if st.button("Clear History", key="clear_history", use_container_width=True):
            try:
                requests.delete(f"{API_URL}/history", timeout=10)
                st.session_state.pop("history_data", None)
                st.success("History cleared.")
            except Exception:
                st.error("Failed to clear history.")

    # Load history
    if "history_data" not in st.session_state:
        try:
            resp = requests.get(f"{API_URL}/history", timeout=10)
            resp.raise_for_status()
            st.session_state["history_data"] = resp.json().get("history", [])
        except Exception:
            st.session_state["history_data"] = []

    history = st.session_state.get("history_data", [])
    if history:
        hist_table = []
        for h in reversed(history):
            score = h.get("risk_score", 0)
            icon = "🟢" if score <= 0.3 else "🟡" if score <= 0.6 else "🔴"
            hist_table.append({
                "ID": h.get("id", ""),
                "Timestamp": h.get("timestamp", "")[:19],
                "Framework": h.get("framework_name", ""),
                "Risk": f"{icon} {score}",
                "Compliant": h.get("compliant", 0),
                "Partial": h.get("partial", 0),
                "Non-Compliant": h.get("non_compliant", 0),
            })
        st.dataframe(hist_table, use_container_width=True)
    else:
        st.info("No analysis history yet. Run an analysis to get started.")
