#!/usr/bin/env python3
"""
debug.py
-------
Comprehensive debugging tool for the Agentic Research Paper Evaluator.

Usage:
    python debug.py --url https://arxiv.org/abs/2301.00001
    python debug.py --test-scraping
    python debug.py --test-parsing
    python debug.py --test-chunking
    python debug.py --test-llm
    python debug.py --test-agents
    python debug.py --full-pipeline
"""

import argparse
import sys
import os
import time
import json
from typing import Dict, Any, List

# Set environment variable to force synchronous transport before any imports
os.environ["GRPC_ASYNCIO_TRANSPORT"] = "None"

# Ensure project root is importable
sys.path.insert(0, os.path.dirname(__file__))

# Fix event loop issue
import asyncio
try:
    asyncio.get_running_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

# Import project modules
from utils.scraper import scrape_arxiv
from utils.section_parser import parse_sections
from utils.chunker import chunk_sections
from utils.llm import get_llm
from agents.crew_setup import run_agents
from report.generator import generate_report, save_report


class DebugLogger:
    """Custom logger for debugging with timestamps and structured output."""
    
    def __init__(self, log_file: str = "debug_output.log"):
        self.log_file = log_file
        self.start_time = time.time()
        
    def log(self, message: str, level: str = "INFO"):
        """Log message with timestamp."""
        timestamp = time.strftime("%H:%M:%S", time.localtime())
        elapsed = f"{time.time() - self.start_time:.2f}s"
        formatted_msg = f"[{timestamp}] [{elapsed}] [{level}] {message}"
        print(formatted_msg)
        
        # Also write to file
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(formatted_msg + "\n")
    
    def section(self, title: str):
        """Print section separator."""
        self.log(f"\n{'='*60}")
        self.log(f"🔍 {title}")
        self.log(f"{'='*60}")
    
    def subsection(self, title: str):
        """Print subsection separator."""
        self.log(f"\n--- {title} ---")
    
    def dict_info(self, data: Dict[str, Any], title: str = ""):
        """Print dictionary information."""
        if title:
            self.subsection(title)
        
        for key, value in data.items():
            if isinstance(value, str):
                self.log(f"  {key}: {len(value)} chars | {len(value.split())} words")
                if len(value) > 100:
                    self.log(f"    Preview: {value[:100]}...")
                else:
                    self.log(f"    Content: {value}")
            elif isinstance(value, list):
                self.log(f"  {key}: {len(value)} items")
                if value and isinstance(value[0], str):
                    total_chars = sum(len(item) for item in value)
                    self.log(f"    Total chars: {total_chars}")
            else:
                self.log(f"  {key}: {value}")


def test_scraping(logger: DebugLogger, url: str) -> Dict[str, Any]:
    """Test Phase 1: arXiv scraping."""
    logger.section("📥 PHASE 1: TESTING ARXIV SCRAPING")
    
    try:
        logger.log(f"Scraping URL: {url}")
        scraped = scrape_arxiv(url)
        
        logger.dict_info(scraped, "Scraping Results")
        
        # Validation
        if not scraped["full_text"]:
            logger.log("❌ ERROR: No full text extracted!", "ERROR")
            return scraped
            
        logger.log("✅ Scraping successful!")
        return scraped
        
    except Exception as e:
        logger.log(f"❌ Scraping failed: {e}", "ERROR")
        import traceback
        logger.log(traceback.format_exc(), "ERROR")
        return {}


def test_parsing(logger: DebugLogger, full_text: str) -> Dict[str, str]:
    """Test Phase 2: Section parsing."""
    logger.section("🔍 PHASE 2: TESTING SECTION PARSING")
    
    try:
        logger.log(f"Input text length: {len(full_text)} chars")
        sections = parse_sections(full_text)
        
        logger.dict_info(sections, "Parsed Sections")
        
        # Check for missing sections
        expected_sections = ["abstract", "introduction", "methodology", "results", "conclusion"]
        missing = [sec for sec in expected_sections if not sections.get(sec)]
        
        if missing:
            logger.log(f"⚠️  Missing sections: {missing}", "WARNING")
        else:
            logger.log("✅ All expected sections found!")
            
        return sections
        
    except Exception as e:
        logger.log(f"❌ Parsing failed: {e}", "ERROR")
        import traceback
        logger.log(traceback.format_exc(), "ERROR")
        return {}


def test_chunking(logger: DebugLogger, sections: Dict[str, str]) -> Dict[str, List[str]]:
    """Test Phase 3: Text chunking."""
    logger.section("✂️ PHASE 3: TESTING TEXT CHUNKING")
    
    try:
        chunked = chunk_sections(sections)
        
        logger.dict_info(chunked, "Chunked Sections")
        
        # Token estimate analysis
        total_chunks = sum(len(chunks) for chunks in chunked.values())
        logger.log(f"Total chunks across all sections: {total_chunks}")
        
        # Estimate tokens (rough: 1 token ≈ 4 chars)
        for section, chunks in chunked.items():
            if chunks:
                avg_chunk_size = sum(len(chunk) for chunk in chunks) / len(chunks)
                est_tokens_per_chunk = avg_chunk_size / 4
                logger.log(f"  {section}: ~{est_tokens_per_chunk:.0f} tokens per chunk")
        
        logger.log("✅ Chunking successful!")
        return chunked
        
    except Exception as e:
        logger.log(f"❌ Chunking failed: {e}", "ERROR")
        import traceback
        logger.log(traceback.format_exc(), "ERROR")
        return {}


def test_llm(logger: DebugLogger) -> Any:
    """Test LLM initialization and basic functionality."""
    logger.section("🤖 PHASE 4: TESTING LLM INITIALIZATION")
    
    try:
        logger.log("Initializing LLM...")
        llm = get_llm()
        logger.log(f"✅ LLM initialized successfully!")
        logger.log(f"Model: {llm.model}")
        logger.log(f"Temperature: {llm.temperature}")
        
        # Test basic invocation
        logger.log("Testing basic LLM invocation...")
        test_messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Hello from Gemini!' in exactly 5 words."}
        ]
        
        start_time = time.time()
        response = llm.invoke(test_messages)
        elapsed = time.time() - start_time
        
        logger.log(f"✅ LLM invocation successful! ({elapsed:.2f}s)")
        logger.log(f"Response: {response.content}")
        
        return llm
        
    except Exception as e:
        logger.log(f"❌ LLM test failed: {e}", "ERROR")
        import traceback
        logger.log(traceback.format_exc(), "ERROR")
        return None


def test_agents(logger: DebugLogger, sections: Dict[str, str], chunked: Dict[str, List[str]]) -> Dict[str, str]:
    """Test Phase 5: Agent execution."""
    logger.section("🧠 PHASE 5: TESTING AGENT EXECUTION")
    
    try:
        logger.log("Running all agents...")
        start_time = time.time()
        
        agent_results = run_agents(sections, chunked)
        
        elapsed = time.time() - start_time
        logger.log(f"✅ All agents completed! ({elapsed:.2f}s)")
        
        logger.dict_info(agent_results, "Agent Results")
        
        # Analyze results
        for agent, result in agent_results.items():
            if result:
                logger.log(f"  {agent}: {len(result)} chars")
            else:
                logger.log(f"  {agent}: EMPTY RESULT", "WARNING")
        
        return agent_results
        
    except Exception as e:
        logger.log(f"❌ Agent execution failed: {e}", "ERROR")
        import traceback
        logger.log(traceback.format_exc(), "ERROR")
        return {}


def test_report_generation(logger: DebugLogger, title: str, url: str, sections: Dict[str, str], agent_results: Dict[str, str]) -> str:
    """Test Phase 6: Report generation."""
    logger.section("📝 PHASE 6: TESTING REPORT GENERATION")
    
    try:
        logger.log("Generating report...")
        report_md = generate_report(title, url, sections, agent_results)
        
        logger.log(f"✅ Report generated! ({len(report_md)} chars)")
        
        # Save report
        report_file = "debug_report.md"
        save_report(report_md, report_file)
        logger.log(f"✅ Report saved to: {report_file}")
        
        # Show preview
        lines = report_md.split('\n')
        logger.log(f"Report has {len(lines)} lines")
        logger.log("First 10 lines:")
        for i, line in enumerate(lines[:10]):
            logger.log(f"  {i+1:2d}: {line}")
        
        return report_md
        
    except Exception as e:
        logger.log(f"❌ Report generation failed: {e}", "ERROR")
        import traceback
        logger.log(traceback.format_exc(), "ERROR")
        return ""


def full_pipeline_test(logger: DebugLogger, url: str):
    """Run complete pipeline test."""
    logger.section("🚀 FULL PIPELINE TEST")
    
    # Phase 1: Scraping
    scraped = test_scraping(logger, url)
    if not scraped.get("full_text"):
        logger.log("❌ Cannot continue without scraped text!", "ERROR")
        return
    
    # Phase 2: Parsing
    sections = test_parsing(logger, scraped["full_text"])
    
    # Phase 3: Chunking
    chunked = test_chunking(logger, sections)
    
    # Phase 4: LLM
    llm = test_llm(logger)
    if not llm:
        logger.log("❌ Cannot continue without LLM!", "ERROR")
        return
    
    # Phase 5: Agents
    agent_results = test_agents(logger, sections, chunked)
    
    # Phase 6: Report
    report = test_report_generation(
        logger, 
        scraped.get("title", "Unknown Paper"),
        url,
        sections,
        agent_results
    )
    
    logger.section("🎉 FULL PIPELINE COMPLETE")
    logger.log("✅ All phases completed successfully!")


def main():
    """Main debugging interface."""
    parser = argparse.ArgumentParser(description="Debug tool for Agentic Research Paper Evaluator")
    parser.add_argument("--url", help="arXiv URL to test with")
    parser.add_argument("--test-scraping", action="store_true", help="Test scraping only")
    parser.add_argument("--test-parsing", action="store_true", help="Test parsing only")
    parser.add_argument("--test-chunking", action="store_true", help="Test chunking only")
    parser.add_argument("--test-llm", action="store_true", help="Test LLM only")
    parser.add_argument("--test-agents", action="store_true", help="Test agents only")
    parser.add_argument("--full-pipeline", action="store_true", help="Run full pipeline test")
    
    args = parser.parse_args()
    
    # Initialize logger
    logger = DebugLogger()
    logger.section("🔧 AGENTIC RESEARCH PAPER EVALUATOR - DEBUG MODE")
    
    # Default test URL if none provided
    test_url = args.url or "https://arxiv.org/abs/2301.00001"
    
    if args.test_scraping:
        test_scraping(logger, test_url)
    elif args.test_parsing:
        # Need some text to test parsing
        logger.log("Testing parsing with sample text...")
        sample_text = "Abstract\nThis is a test abstract.\n\nIntroduction\nThis is the introduction.\n\nMethodology\nThis describes the method.\n\nResults\nThese are the results.\n\nConclusion\nThis is the conclusion."
        test_parsing(logger, sample_text)
    elif args.test_chunking:
        # Need sections to test chunking
        logger.log("Testing chunking with sample sections...")
        sample_sections = {
            "abstract": "This is a test abstract.",
            "methodology": "This is a long methodology section. " * 100,
            "results": "These are the results. " * 100,
            "conclusion": "This is the conclusion."
        }
        test_chunking(logger, sample_sections)
    elif args.test_llm:
        test_llm(logger)
    elif args.test_agents:
        logger.log("Testing agents requires full pipeline setup...")
        logger.log("Use --full-pipeline instead")
    elif args.full_pipeline or not any([args.test_scraping, args.test_parsing, args.test_chunking, args.test_llm, args.test_agents]):
        full_pipeline_test(logger, test_url)
    
    logger.section("🏁 DEBUG SESSION COMPLETE")
    logger.log(f"Log file saved to: {logger.log_file}")


if __name__ == "__main__":
    main()
