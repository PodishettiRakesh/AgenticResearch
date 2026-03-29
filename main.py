"""
main.py
-------
Orchestrator for the Agentic Research Paper Evaluator.

Usage (CLI):
    python main.py --url https://arxiv.org/abs/2301.00001
    python main.py --url https://arxiv.org/abs/2301.00001 --output my_report.md
"""

import argparse
import sys
import os
import asyncio

# Disable ALL telemetry and tracing to avoid connection issues
os.environ["CREWAI_TELEMETRY_ENABLED"] = "false"
os.environ["OTEL_SDK_DISABLED"] = "true"
os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = ""
os.environ["OTEL_EXPORTER_OTLP_TRACES_ENDPOINT"] = ""

# Set environment variable to force synchronous transport before any imports
os.environ["GRPC_ASYNCIO_TRANSPORT"] = "None"

# Ensure project root is on the path when running directly
sys.path.insert(0, os.path.dirname(__file__))

from utils.scraping.scraper import scrape_arxiv
from utils.scraping.section_parser import parse_sections
from utils.processing.chunker import chunk_sections
from agents.crew_setup import run_agents
from report.generator import generate_report, save_report


def run_pipeline(arxiv_url: str, output_path: str = "reports/judgement_report.md") -> str:
    """
    Full end-to-end pipeline using original crew_setup with new utility structure.

    Args:
        arxiv_url:   The arXiv paper URL (abs format).
        output_path: Where to save the Markdown report.

    Returns:
        The Markdown report as a string.
    """
    
    # Generate unique filename based on paper ID or timestamp
    import re
    import time
    
    # Extract paper ID from URL for unique naming
    paper_id = re.search(r'(\d+\.\d+)', arxiv_url)
    if paper_id:
        base_name = f"judgement_report_{paper_id.group(1)}"
    else:
        base_name = f"judgement_report_{int(time.time())}"
    
    # Add timestamp to prevent overwrites
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    unique_filename = f"{base_name}_{timestamp}.md"
    
    # Use reports folder
    if not output_path.startswith("reports/"):
        output_path = f"reports/{unique_filename}"
    else:
        output_path = output_path.replace("judgement_report.md", unique_filename)
    
    print("=" * 60)
    print("  Agentic Research Paper Evaluator")
    print("=" * 60)
    print(f"\nURL: {arxiv_url}")
    print(f"Output: {output_path}\n")

    # ── Phase 1: Scrape ────────────────────────────────────────────────────
    print("-" * 40)
    print("Phase 1: Scraping paper...")
    scraped = scrape_arxiv(arxiv_url)
    if not scraped["full_text"]:
        print("ERROR: Could not extract text from the provided URL.")
        sys.exit(1)

    title = scraped.get("title", "Unknown Paper")
    print(f"   Title: {title}")
    print(f"   Source: {scraped['source']}")
    print(f"   Figures found: {len(scraped['figures'])}")

    # ── Phase 2: Section Parsing ───────────────────────────────────────────
    print("\n" + "-" * 40)
    print("Phase 2: Parsing sections...")
    sections = parse_sections(scraped["full_text"])

    # ── Phase 3: Chunking ──────────────────────────────────────────────────
    print("\n" + "-" * 40)
    print("Phase 3: Chunking sections...")
    chunked = chunk_sections(sections)

    # ── Phase 4 & 5: Agent Execution ──────────────────────────────────────
    print("\n" + "-" * 40)
    print("Phase 4: Running agents...")
    agent_results = run_agents(sections, chunked)

    # ── Phase 6: Report Generation ────────────────────────────────────────
    print("\n" + "-" * 40)
    print("Phase 5: Generating report...")
    report_md = generate_report(
        title=title,
        arxiv_url=arxiv_url,
        sections=sections,
        agent_results=agent_results,
    )
    save_report(report_md, output_path)

    print("\n" + "=" * 60)
    print(f"  Done! Report saved to: {output_path}")
    print("=" * 60)

    return report_md


# ── CLI entry point ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Agentic Research Paper Evaluator — powered by CrewAI + Gemini"
    )
    parser.add_argument(
        "--url",
        required=False,
        default="https://arxiv.org/html/2603.25702v1",
        help="arXiv paper URL (e.g. https://arxiv.org/html/2603.25702v1)",
    )
    parser.add_argument(
        "--output",
        default="reports/judgement_report.md",
        help="Output Markdown file path (default: reports/judgement_report.md)",
    )
    args = parser.parse_args()
    run_pipeline(args.url, args.output)
