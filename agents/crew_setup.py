"""
crew_setup_v2.py
-------------
Simplified CrewAI integration that uses existing logic directly in tasks.
This avoids tool complexity while still leveraging CrewAI orchestration.
"""

import os
import re
import sys
from datetime import datetime
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from crewai import Agent, Task, Crew, Process

from utils.llm import get_llm, get_provider_info
from agents.prompts import (
    CONSISTENCY_SYSTEM, CONSISTENCY_CHUNK_PROMPT, CONSISTENCY_REDUCE_PROMPT,
    GRAMMAR_SYSTEM, GRAMMAR_PROMPT,
    NOVELTY_SYSTEM, NOVELTY_PROMPT,
    FACTCHECK_SYSTEM, FACTCHECK_CHUNK_PROMPT, FACTCHECK_REDUCE_PROMPT,
    FABRICATION_PROMPT,
)


# ── API Call Logging Wrapper ────────────────────────────────────────────
def log_api_call(agent_name: str, prompt_type: str, input_length: int):
    """Log each API call for debugging purposes."""
    print(f"[API_CALL] 🤖 {agent_name} - {prompt_type}")
    print(f"[API_CALL] 📝 Input length: {input_length} chars")
    print(f"[API_CALL] ⏰ Time: {datetime.now().strftime('%H:%M:%S')}")
    print("-" * 40)


# ── Helper Functions (Preserved from original) ─────────────────────────────────

def _map_reduce(llm, system_prompt: str, chunk_prompt_tpl: str,
                reduce_prompt_tpl: str, chunks: list[str]) -> str:
    """Run a map step (one LLM call per chunk) then a reduce step (one final call)."""
    if not chunks:
        return "No content available for analysis."

    # MAP
    chunk_analyses = []
    for i, chunk in enumerate(chunks):
        prompt = chunk_prompt_tpl.format(chunk=chunk)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]
        response = llm.invoke(messages)
        analysis = response.content if hasattr(response, "content") else str(response)
        chunk_analyses.append(f"--- Chunk {i+1} ---\n{analysis}")

    # REDUCE
    combined = "\n\n".join(chunk_analyses)
    reduce_prompt = reduce_prompt_tpl.format(analyses=combined)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": reduce_prompt},
    ]
    response = llm.invoke(messages)
    return response.content if hasattr(response, "content") else str(response)


def _single_call(llm, system_prompt: str, user_prompt: str) -> str:
    """Single LLM call (no chunking needed)."""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    response = llm.invoke(messages)
    return response.content if hasattr(response, "content") else str(response)


# ── Agent Definitions ─────────────────────────────────────────────────────

def create_agents():
    """Create all agents with appropriate LLM provider."""
    
    # Display current provider information
    provider_info = get_provider_info()
    print(f"\n[LLM Provider] {provider_info['active_provider'].upper()} ({provider_info['type']})")
    print(f"[LLM Model] {provider_info['model']}")
    print(f"[LLM Selection] {provider_info['selection_method']}")
    print(f"[Gemini Available] {provider_info['gemini_enabled']}")
    print(f"[Ollama Available] {provider_info['ollama_enabled']}")
    
    # Get LLM instance based on environment
    llm = get_llm()
    
    # Consistency Agent
    consistency_agent = Agent(
        role="Academic Consistency Reviewer",
        goal="Evaluate logical consistency between methodology and results sections",
        backstory="""You are a rigorous academic peer reviewer with 15+ years of experience 
        in research methodology. You specialize in identifying logical gaps, unsupported 
        claims, and inconsistencies between what methods promise and what results deliver.""",
        llm=llm,
        verbose=True,
        allow_delegation=False
    )
    
    # Grammar Agent
    grammar_agent = Agent(
        role="Academic Language Editor",
        goal="Assess grammar, tone, and professional writing quality",
        backstory="""You are an expert academic editor with a PhD in linguistics and 
        extensive experience reviewing research papers. You evaluate professional tone, 
        grammatical correctness, clarity, and adherence to academic writing standards.""",
        llm=llm,
        verbose=True,
        allow_delegation=False
    )
    
    # Novelty Agent
    novelty_agent = Agent(
        role="Research Novelty Assessor",
        goal="Evaluate the novelty and originality of research contributions",
        backstory="""You are a senior research scientist with broad knowledge across 
        computer science, AI, physics, biology, and engineering. You assess novelty by 
        comparing claimed contributions against existing literature and identifying 
        truly original work.""",
        llm=llm,
        verbose=True,
        allow_delegation=False
    )
    
    # Fact-Check Agent
    factcheck_agent = Agent(
        role="Research Fact-Checker",
        goal="Verify factual claims, citations, and statistical assertions",
        backstory="""You are a meticulous fact-checker and domain expert who verifies 
        all verifiable claims in research papers including constants, formulas, 
        historical data, and statistical assertions. You have extensive experience 
        identifying suspicious or exaggerated claims.""",
        llm=llm,
        verbose=True,
        allow_delegation=False
    )
    
    # Fabrication Aggregator
    aggregator_agent = Agent(
        role="Research Integrity Analyst",
        goal="Synthesize all analyses and calculate fabrication probability",
        backstory="""You are an expert research integrity analyst with deep experience 
        in identifying potentially fabricated or fraudulent research. You synthesize 
        multiple evaluation dimensions to provide an overall assessment of research 
        authenticity and integrity.""",
        llm=llm,
        verbose=True,
        allow_delegation=False
    )
    
    return [
        consistency_agent,
        grammar_agent, 
        novelty_agent,
        factcheck_agent,
        aggregator_agent
    ]


# ── Task Definitions ─────────────────────────────────────────────────────

def create_tasks(agents: list, sections: dict, chunked: dict):
    """Create sequential tasks for all agents with proper dependencies."""
    
    consistency_agent, grammar_agent, novelty_agent, factcheck_agent, aggregator_agent = agents
    
    # Task 1: Consistency Analysis
    consistency_chunks = (chunked.get("methodology", []) + chunked.get("results", []))[:6]
    consistency_task = Task(
        description=f"""Analyze logical consistency between methodology and results sections.
        
        You must perform a Map-Reduce analysis on these chunks:
        - Methodology chunks: {chunked.get("methodology", [])}
        - Results chunks: {chunked.get("results", [])}
        
        Use this exact process:
        1. MAP: For each chunk, use this prompt: "{CONSISTENCY_CHUNK_PROMPT}"
        2. REDUCE: Combine all analyses and use this prompt: "{CONSISTENCY_REDUCE_PROMPT}"
        3. System prompt: "{CONSISTENCY_SYSTEM}"
        
        Focus on identifying gaps between what the methodology promises and what 
        the results claim. Provide a detailed consistency analysis.""",
        expected_output="""A detailed consistency analysis including:
        1. OVERALL CONSISTENCY SCORE: (integer 0-100)
        2. MAJOR INCONSISTENCIES: bullet list
        3. MINOR ISSUES: bullet list
        4. SUMMARY: 2-3 sentences""",
        agent=consistency_agent,
        async_execution=False
    )
    
    # Task 2: Grammar Analysis
    grammar_text = (sections.get("abstract", "") + "\n\n" + sections.get("introduction", ""))[:4000]
    grammar_task = Task(
        description=f"""Evaluate grammar, language quality, and professional academic tone.
        
        You must analyze this text using this exact prompt:
        Text to analyze: {grammar_text}
        
        Use this prompt template: "{GRAMMAR_PROMPT}"
        System prompt: "{GRAMMAR_SYSTEM}"
        
        Analyze for grammatical correctness, professional academic tone, clarity, and adherence to academic writing standards.""",
        expected_output="""A comprehensive grammar evaluation including:
        1. GRAMMAR RATING: (High / Medium / Low)
        2. TONE ASSESSMENT: (Professional / Acceptable / Informal)
        3. NOTABLE ISSUES: bullet list (max 10)
        4. POSITIVE ASPECTS: bullet list (max 5)
        5. OVERALL LANGUAGE SUMMARY: 2-3 sentences""",
        agent=grammar_agent,
        async_execution=False,
        context=[consistency_task]
    )
    
    # Task 3: Novelty Assessment
    abstract_text = sections.get("abstract", "Not available")[:2000]
    conclusion_text = sections.get("conclusion", "Not available")[:2000]
    novelty_task = Task(
        description=f"""Assess the novelty and originality of research contributions.
        
        You must analyze these texts using this exact prompt:
        Abstract: {abstract_text}
        Conclusion: {conclusion_text}
        
        Use this prompt template: "{NOVELTY_PROMPT}"
        System prompt: "{NOVELTY_SYSTEM}"
        
        Evaluate originality compared to existing literature, significance of contributions, and potential impact.""",
        expected_output="""A thorough novelty assessment including:
        1. NOVELTY INDEX: (Highly Novel / Moderately Novel / Incremental / Low Novelty)
        2. CLAIMED CONTRIBUTIONS: bullet list
        3. LIKELY PRIOR WORK: mention related areas
        4. ORIGINALITY ASSESSMENT: 3-4 sentences
        5. SUGGESTED RELATED FIELDS: comma-separated list""",
        agent=novelty_agent,
        async_execution=False,
        context=[grammar_task]
    )
    
    # Task 4: Fact-Check Analysis
    all_chunks = []
    for sec in ["abstract", "methodology", "results", "conclusion"]:
        all_chunks.extend(chunked.get(sec, []))
    all_chunks = all_chunks[:6]
    factcheck_task = Task(
        description=f"""Verify factual claims, citations, and statistical assertions.
        
        You must perform a Map-Reduce analysis on these chunks:
        - All sections chunks: {all_chunks}
        
        Use this exact process:
        1. MAP: For each chunk, use this prompt: "{FACTCHECK_CHUNK_PROMPT}"
        2. REDUCE: Combine all analyses and use this prompt: "{FACTCHECK_REDUCE_PROMPT}"
        3. System prompt: "{FACTCHECK_SYSTEM}"
        
        Examine for constants, formulas, historical facts, statistical assertions, and citations.""",
        expected_output="""A comprehensive fact-check log including:
        1. VERIFIED CLAIMS: bullet list
        2. UNVERIFIED CLAIMS: bullet list
        3. SUSPICIOUS CLAIMS: bullet list
        4. FACT-CHECK SUMMARY: 2-3 sentences""",
        agent=factcheck_agent,
        async_execution=False,
        context=[novelty_task]
    )
    
    # Task 5: Fabrication Aggregation
    aggregation_task = Task(
        description=f"""Synthesize all agent analyses and calculate fabrication probability.
        
        You must aggregate all previous results and calculate fabrication probability.
        
        Use this exact prompt template: "{FABRICATION_PROMPT}"
        
        Extract these values from the previous analyses:
        - Consistency score (from consistency analysis)
        - Grammar rating (from grammar analysis)  
        - Novelty index (from novelty analysis)
        - Fact-check summary (from fact-check analysis)
        
        Provide overall fabrication probability assessment, risk level, executive summary, and final recommendation.""",
        expected_output="""A final integrity assessment including:
        1. FABRICATION PROBABILITY: (0-100%)
        2. RISK LEVEL: (Low / Medium / High / Critical)
        3. EXECUTIVE SUMMARY: 3-4 sentences
        4. RECOMMENDATION: PASS or FAIL with justification""",
        agent=aggregator_agent,
        async_execution=False,
        context=[factcheck_task]
    )
    
    return [
        consistency_task,
        grammar_task,
        novelty_task,
        factcheck_task,
        aggregation_task
    ]


# ── CrewAI Orchestration ───────────────────────────────────────────────────

def run_agents(sections: dict, chunked: dict) -> dict:
    """
    Run the full CrewAI pipeline with proper result extraction.
    
    This implementation uses CrewAI as the ONLY execution engine.
    All LLM calls happen through CrewAI tools and agents.
    """
    print("\n[CrewAI] Initializing agents and tasks...")
    agents = create_agents()
    tasks = create_tasks(agents, sections, chunked)
    
    print("\n[CrewAI] Starting sequential execution...")
    print(f"[DEBUG] Consistency chunks: {len(chunked.get('methodology', []) + chunked.get('results', []))}")
    print(f"[DEBUG] Methodology content preview: {chunked.get('methodology', [''])[0][:200] if chunked.get('methodology') else 'None'}")
    print(f"[DEBUG] Results content preview: {chunked.get('results', [''])[0][:200] if chunked.get('results') else 'None'}")
    
    crew = Crew(
        agents=agents,
        tasks=tasks,
        process=Process.sequential,
        verbose=False,  # Disable verbose logging to prevent Unicode encoding errors
    )
    
    result = crew.kickoff()
    
    print("\n[CrewAI] All agents completed successfully!")
    print(f"[DEBUG] Raw result type: {type(result)}")
    print(f"[DEBUG] Raw result preview: {str(result)[:500]}...")
    
    # Extract results from CrewAI execution
    # The result should contain outputs from all tasks in order
    task_results = extract_crew_results(result)
    
    print(f"[DEBUG] Consistency agent completed!")
    print(f"[DEBUG] Consistency score: {task_results.get('consistency', 'N/A')}")
    
    # Break here to check consistency agent output before continuing
    import sys
    print("\n" + "="*50)
    print("🎯 CONSISTENCY AGENT ANALYSIS COMPLETE!")
    print(f"📊 Consistency Score: {task_results.get('consistency', 'N/A')}")
    print("="*50)
    print("⏸️ Execution paused. Press Ctrl+C to continue with other agents or check logs.")
    print("⏸️ Or modify run_agents() to remove this break point.")
    
    return task_results


def extract_crew_results(crew_result) -> dict:
    """
    Extract structured results from CrewAI execution.
    
    Args:
        crew_result: The result object returned by crew.kickoff()
        
    Returns:
        Dictionary with keys: consistency, grammar, novelty, fact_check, fabrication
    """
    # Convert CrewAI result to string if needed
    if hasattr(crew_result, 'raw'):
        result_text = crew_result.raw
    elif hasattr(crew_result, 'result'):
        result_text = crew_result.result
    else:
        result_text = str(crew_result)
    
    # Parse the combined result to extract individual task outputs
    # CrewAI typically returns results separated by task completion markers
    results = {}
    
    # Split by task completion patterns and extract individual results
    task_patterns = [
        (r"OVERALL CONSISTENCY SCORE.*?(?=1\.|2\.|3\.|4\.|5\.|$)", "consistency"),
        (r"GRAMMAR RATING.*?(?=1\.|2\.|3\.|4\.|5\.|$)", "grammar"),
        (r"NOVELTY INDEX.*?(?=1\.|2\.|3\.|4\.|5\.|$)", "novelty"),
        (r"VERIFIED CLAIMS.*?(?=1\.|2\.|3\.|4\.|5\.|$)", "fact_check"),
        (r"FABRICATION PROBABILITY.*?(?=1\.|2\.|3\.|4\.|5\.|$)", "fabrication")
    ]
    
    # Extract each task result
    for pattern, key in task_patterns:
        match = re.search(pattern, result_text, re.DOTALL | re.IGNORECASE)
        if match:
            # Extract a reasonable chunk around the match
            start = max(0, match.start() - 100)
            end = min(len(result_text), match.end() + 500)
            results[key] = result_text[start:end].strip()
        else:
            # Fallback: try to find the key in the text
            if key.upper() in result_text.upper():
                # Find the section and extract surrounding content
                pass  # Placeholder for future implementation
    
    # Extract other scores similarly
    grammar_match = re.search(r'GRAMMAR SCORE:\s*(\d+)', result_text, re.IGNORECASE)
    grammar_score = grammar_match.group(1) if grammar_match else "0"
    
    novelty_match = re.search(r'NOVELTY SCORE:\s*(\d+)', result_text, re.IGNORECASE)
    novelty_score = novelty_match.group(1) if novelty_match else "0"
    
    factcheck_match = re.search(r'FACT-CHECK SCORE:\s*(\d+)', result_text, re.IGNORECASE)
    factcheck_score = factcheck_match.group(1) if factcheck_match else "0"
    
    fabrication_match = re.search(r'FABRICATION SCORE:\s*(\d+)', result_text, re.IGNORECASE)
    fabrication_score = fabrication_match.group(1) if fabrication_match else "0"
    
    final_results = {
        "consistency": consistency_score,
        "grammar": grammar_score,
        "novelty": novelty_score,
        "fact_check": factcheck_score,
        "fabrication": fabrication_score,
    }
    
    print("[DEBUG] Final extracted results:", final_results)
    return final_results


# ── Backward Compatibility Helpers ───────────────────────────────────────────────

def _extract_consistency_score(text: str) -> int:
    """Pull the integer score from the consistency agent output."""
    match = re.search(r"OVERALL CONSISTENCY SCORE[:\s]+(\d{1,3})", text, re.IGNORECASE)
    if match:
        return min(int(match.group(1)), 100)
    match = re.search(r"\b([0-9]{1,3})\b", text)
    return int(match.group(1)) if match else 70


def _extract_grammar_rating(text: str) -> str:
    """Pull High/Medium/Low from grammar agent output."""
    match = re.search(r"GRAMMAR RATING[:\s]+(High|Medium|Low)", text, re.IGNORECASE)
    return match.group(1).capitalize() if match else "Medium"


def _extract_novelty_index(text: str) -> str:
    """Pull the novelty label from novelty agent output."""
    match = re.search(
        r"NOVELTY INDEX[:\s]+(Highly Novel|Moderately Novel|Incremental|Low Novelty)",
        text, re.IGNORECASE,
    )
    return match.group(1) if match else "Moderately Novel"


def _extract_factcheck_summary(text: str) -> str:
    """Pull the fact-check summary paragraph."""
    match = re.search(
        r"FACT-CHECK SUMMARY[:\s]+(.*?)(?:\n\n|\Z)", text, re.IGNORECASE | re.DOTALL
    )
    return match.group(1).strip() if match else text[:500]
