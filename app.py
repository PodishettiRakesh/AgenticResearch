"""
app.py
------
Streamlit UI for the Agentic Research Paper Evaluator.

Run with:
    streamlit run app.py
"""

import sys
import os
import re
import asyncio

import streamlit as st

# Set environment variable to force synchronous transport before any imports
os.environ["GRPC_ASYNCIO_TRANSPORT"] = "None"

# Ensure project root is importable
sys.path.insert(0, os.path.dirname(__file__))

# Fix event loop issue for Streamlit
try:
    asyncio.get_running_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

from main import run_pipeline

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Agentic Paper Evaluator",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://arxiv.org/static/browse/0.3.4/images/arxiv-logo-one-color-white.svg", width=120)
    st.title("⚙️ Settings")
    output_filename = st.text_input("Report filename", value="judgement_report.md")
    st.markdown("---")
    st.markdown(
        """
        **Agents running:**
        - 🧠 Consistency Agent
        - ✍️ Grammar Agent
        - 🧪 Novelty Agent
        - 🔍 Fact-Check Agent
        - 📊 Fabrication Aggregator
        """
    )
    st.markdown("---")
    st.caption("Powered by **CrewAI** + **Gemini 1.5 Flash**")

# ── Main header ───────────────────────────────────────────────────────────────
st.title("🔬 Agentic Research Paper Evaluator")
st.markdown(
    "Enter an **arXiv paper URL** below and click **Evaluate** to run the full "
    "multi-agent peer-review simulation."
)

# ── Input ─────────────────────────────────────────────────────────────────────
arxiv_url = st.text_input(
    "📎 arXiv Paper URL",
    placeholder="https://arxiv.org/abs/2301.00001",
    help="Paste the full arXiv abstract URL here.",
)

col1, col2 = st.columns([1, 5])
with col1:
    evaluate_btn = st.button("🚀 Evaluate", type="primary", use_container_width=True)
with col2:
    st.empty()

# ── Validation helper ─────────────────────────────────────────────────────────
def _is_valid_arxiv_url(url: str) -> bool:
    return bool(re.match(r"https?://arxiv\.org/(abs|html|pdf)/[\d\.]+", url))

# ── Pipeline execution ────────────────────────────────────────────────────────
if evaluate_btn:
    if not arxiv_url.strip():
        st.error("⚠️ Please enter an arXiv URL before clicking Evaluate.")
    elif not _is_valid_arxiv_url(arxiv_url.strip()):
        st.error("⚠️ URL doesn't look like a valid arXiv link. Example: `https://arxiv.org/abs/2301.00001`")
    else:
        st.info(f"🔄 Analysing: **{arxiv_url.strip()}**")

        # Progress bar + status messages
        progress = st.progress(0, text="Starting pipeline…")
        status   = st.empty()

        try:
            status.markdown("📥 **Phase 1:** Scraping paper from arXiv…")
            progress.progress(10, text="Scraping…")

            # We run the full pipeline (it prints to console too)
            with st.spinner("🤖 Agents are analysing the paper — this may take 1–3 minutes…"):
                report_md = run_pipeline(
                    arxiv_url=arxiv_url.strip(),
                    output_path=output_filename,
                )

            progress.progress(100, text="Done!")
            status.success("✅ Analysis complete!")

            # ── Display report ─────────────────────────────────────────────
            st.markdown("---")
            st.subheader("📄 Judgement Report")

            # Tabs: rendered Markdown | raw Markdown | download
            tab_render, tab_raw, tab_download = st.tabs(
                ["📊 Rendered Report", "📝 Raw Markdown", "⬇️ Download"]
            )

            with tab_render:
                st.markdown(report_md, unsafe_allow_html=False)

            with tab_raw:
                st.code(report_md, language="markdown")

            with tab_download:
                st.download_button(
                    label="⬇️ Download Judgement Report (.md)",
                    data=report_md,
                    file_name=output_filename,
                    mime="text/markdown",
                )
                st.caption(f"Report also saved locally as `{output_filename}`")

        except EnvironmentError as e:
            st.error(f"🔑 API Key Error: {e}")
            st.info("Make sure your `GEMINI_API_KEY` is set in the `.env` file.")
        except Exception as e:
            st.error(f"❌ An error occurred: {e}")
            st.exception(e)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption(
    "Agentic Research Paper Evaluator · Built with CrewAI + Gemini · "
    "For academic use only."
)
