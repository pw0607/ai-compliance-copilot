"""
Streamlit frontend for AI Compliance Copilot v2.1.

Features:
- Framework selector with descriptions
- Risk score visualization with color coding
- Metrics dashboard
- Interactive results table
- PDF report download
- Sidebar with project info and framework details
"""

import os
import sys
from pathlib import Path

import requests
import streamlit as st

# Allow imports from project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.report_generator import generate_report

API_URL = os.getenv("API_URL", "http://localhost:8000")

FRAMEWORKS = {
    "nist": {"name": "NIST AI RMF", "desc": "Governance, risk lifecycle, measurement, accountability"},
    "hipaa": {"name": "HIPAA", "desc": "PHI protection, encryption, access controls, audit logs"},
    "nist_csf": {"name": "NIST CSF", "desc": "Identify, Protect, Detect, Respond, Recover"},
    "fedramp": {"name": "FedRAMP", "desc": "Authentication, audit logs, boundary protection"},
    "iso": {"name": "ISO 27001", "desc": "ISMS, policies, incident management, governance"},
    "owasp": {"name": "OWASP LLM Top 10", "desc": "Prompt injection, data leakage, model security"},
    "gdpr": {"name": "GDPR", "desc": "Data minimization, privacy by design, DPIA"},
}

# --- Page config ---
st.set_page_config(page_title="AI Compliance Copilot", page_icon="🛡️", layout="wide")

# --- Sidebar ---
with st.sidebar:
    st.header("🛡️ AI Compliance Copilot")
    st.caption("v2.1.0")
    st.markdown("Evaluate AI systems against 7 regulatory compliance frameworks.")
    st.divider()
    st.subheader("Supported Frameworks")
    for key, info in FRAMEWORKS.items():
        st.markdown(f"**{info['name']}**  \n{info['desc']}")
    st.divider()
    st.markdown(
        "[📖 Docs](docs/architecture.md) · "
        "[🔗 API Docs](http://localhost:8000/docs) · "
        "[📝 Contributing](CONTRIBUTING.md)"
    )

# --- Main content ---
st.title("🛡️ AI Compliance Copilot")
st.markdown("Evaluate your AI system against regulatory compliance frameworks.")

# --- Input section ---
system_description = st.text_area(
    "Describe your AI system",
    height=180,
    placeholder=(
        "Example: A radiology AI model that analyzes chest X-rays to detect pneumonia. "
        "It processes patient DICOM images stored in a cloud database and returns "
        "diagnostic predictions to clinicians via a web dashboard."
    ),
    help="Provide a detailed description including data handling, security measures, and governance practices.",
)

col_fw, col_btn = st.columns([3, 1])
with col_fw:
    framework_key = st.selectbox(
        "Select compliance framework",
        options=list(FRAMEWORKS.keys()),
        format_func=lambda k: f"{FRAMEWORKS[k]['name']} — {FRAMEWORKS[k]['desc']}",
    )
with col_btn:
    st.markdown("<br>", unsafe_allow_html=True)
    run_clicked = st.button("🔍 Run Analysis", use_container_width=True)

# --- Analysis ---
if run_clicked:
    if not system_description or len(system_description.strip()) < 20:
        st.error("Please provide a system description of at least 20 characters.")
    else:
        with st.spinner("Analyzing compliance..."):
            try:
                response = requests.post(
                    f"{API_URL}/analyze",
                    json={"system_description": system_description, "framework": framework_key},
                    timeout=60,
                )
                response.raise_for_status()
                data = response.json()
            except requests.exceptions.ConnectionError:
                st.error(
                    "Cannot connect to the backend. "
                    "Make sure the FastAPI server is running on port 8000."
                )
                st.stop()
            except requests.exceptions.HTTPError as exc:
                st.error(f"Backend error: {exc.response.text}")
                st.stop()
            except requests.exceptions.Timeout:
                st.error("Request timed out. The backend may be overloaded.")
                st.stop()

        # Store in session state for persistence
        st.session_state["last_result"] = data

# --- Display results ---
data = st.session_state.get("last_result")
if data:
    st.divider()

    # Warnings
    if data.get("prompt_injection_detected"):
        st.warning("⚠️ Potential prompt injection detected. Results flagged for review.")
    if data.get("human_review_recommended"):
        st.info("ℹ️ Human review is recommended for this analysis.")

    # Risk score header
    score = data["risk_score"]
    if score <= 0.3:
        color, label = "🟢", "Low Risk"
    elif score <= 0.6:
        color, label = "🟡", "Medium Risk"
    else:
        color, label = "🔴", "High Risk"

    st.subheader(f"Overall Risk Score: {color} {score} — {label}")
    st.markdown(f"**{data.get('framework_name', '')}** — {data['summary']}")

    # Metrics row
    risk_summary = data.get("risk_summary", {})
    if risk_summary:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Controls", risk_summary.get("total_controls", 0))
        c2.metric("Compliant", risk_summary.get("compliant", 0))
        c3.metric("Partial", risk_summary.get("partial", 0))
        c4.metric("Non-Compliant", risk_summary.get("non_compliant", 0))

    # Results table
    st.subheader("Compliance Results")
    table_data = []
    for r in data.get("compliance_results", []):
        status = r["status"]
        icon = {"Yes": "✅", "Partial": "⚠️", "No": "❌"}.get(status, "")
        table_data.append({
            "Control ID": r["control_id"],
            "Title": r["control_title"],
            "Status": f"{icon} {status}",
            "Risk": r["risk_score"],
            "Explanation": r["explanation"],
            "Evidence": ", ".join(r.get("evidence_found", [])) or "—",
            "Gaps": ", ".join(r.get("gaps", [])) or "—",
        })
    st.dataframe(table_data, use_container_width=True, height=420)

    # Expandable detail per control
    with st.expander("View detailed per-control recommendations"):
        for r in data.get("compliance_results", []):
            status_icon = {"Yes": "✅", "Partial": "⚠️", "No": "❌"}.get(r["status"], "")
            st.markdown(f"**{r['control_id']}** — {r['control_title']} {status_icon}")
            st.markdown(f"  - {r['recommendation']}")

    # Top recommendations
    if data.get("recommendations"):
        st.subheader("Top Recommendations")
        for i, rec in enumerate(data["recommendations"], 1):
            st.markdown(f"{i}. {rec}")

    # PDF download
    st.divider()
    try:
        pdf_path = generate_report(data)
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="📄 Download PDF Report",
                data=f,
                file_name=pdf_path.split("/")[-1],
                mime="application/pdf",
                use_container_width=True,
            )
    except Exception as exc:
        st.error(f"Failed to generate PDF: {exc}")
