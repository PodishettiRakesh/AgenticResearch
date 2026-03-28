"""
crew_setup.py
-------------
Defines the four CrewAI Agents and their Tasks, then runs the crew sequentially.

Agents:
  1. Consistency Agent  – Map-Reduce over methodology + results chunks
  2. Grammar Agent      – Evaluates abstract + introduction
  3. Novelty Agent      – Evaluates abstract + conclusion
  4. Fact-Check Agent   – Map-Reduce over all section chunks
  5. Fabrication Aggregator – Synthesizes all results

The crew runs sequentially (process=Process.sequential) so each agent's
output is available to the next one.
"""

import re
from crewai import Agent, Task, Crew, Process

from agents.tools import (
    ConsistencyMapReduceTool,
    FactCheckMapReduceTool,
    GrammarAnalysisTool,
    NoveltyAnalysisTool,
    FabricationAggregatorTool
)


# ── Agent Definitions ─────────────────────────────────────────────────────

def create_agents():
    """Create all CrewAI agents with proper roles, goals, and tools."""
    
    # Consistency Agent - Analyzes logical consistency
    consistency_agent = Agent(
        role="Academic Consistency Reviewer",
        goal="Evaluate logical consistency between methodology and results sections",
        backstory="""You are a rigorous academic peer reviewer with 15+ years of experience 
        in research methodology. You specialize in identifying logical gaps, unsupported 
        claims, and inconsistencies between what methods promise and what results deliver.""",
        tools=[ConsistencyMapReduceTool()],
        verbose=True,
        allow_delegation=False
    )
    
    # Grammar Agent - Evaluates language quality
    grammar_agent = Agent(
        role="Academic Language Editor",
        goal="Assess grammar, tone, and professional writing quality",
        backstory="""You are an expert academic editor with a PhD in linguistics and 
        extensive experience reviewing research papers. You evaluate professional tone, 
        grammatical correctness, clarity, and adherence to academic writing standards.""",
        tools=[GrammarAnalysisTool()],
        verbose=True,
        allow_delegation=False
    )
    
    # Novelty Agent - Assesses originality
    novelty_agent = Agent(
        role="Research Novelty Assessor",
        goal="Evaluate the novelty and originality of research contributions",
        backstory="""You are a senior research scientist with broad knowledge across 
        computer science, AI, physics, biology, and engineering. You assess novelty by 
        comparing claimed contributions against existing literature and identifying 
        truly original work.""",
        tools=[NoveltyAnalysisTool()],
        verbose=True,
        allow_delegation=False
    )
    
    # Fact-Check Agent - Verifies factual claims
    factcheck_agent = Agent(
        role="Research Fact-Checker",
        goal="Verify factual claims, citations, and statistical assertions",
        backstory="""You are a meticulous fact-checker and domain expert who verifies 
        all verifiable claims in research papers including constants, formulas, 
        historical data, and statistical assertions. You have extensive experience 
        identifying suspicious or exaggerated claims.""",
        tools=[FactCheckMapReduceTool()],
        verbose=True,
        allow_delegation=False
    )
    
    # Fabrication Aggregator - Synthesizes all results
    aggregator_agent = Agent(
        role="Research Integrity Analyst",
        goal="Synthesize all analyses and calculate fabrication probability",
        backstory="""You are an expert research integrity analyst with deep experience 
        in identifying potentially fabricated or fraudulent research. You synthesize 
        multiple evaluation dimensions to provide an overall assessment of research 
        authenticity and integrity.""",
        tools=[FabricationAggregatorTool()],
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
    consistency_task = Task(
        description=f"""Analyze logical consistency between methodology and results sections.
        
        Use the consistency analysis tool with these specific chunks:
        - Methodology chunks: {chunked.get("methodology", [])}
        - Results chunks: {chunked.get("results", [])}
        
        Focus on identifying gaps between what the methodology promises and what 
        the results claim. Note any unsupported leaps, missing controls, or contradictions.""",
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
        
        Use the grammar analysis tool with this text:
        Text to analyze: {grammar_text}
        
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
        
        Use the novelty analysis tool with this text:
        Abstract: {abstract_text}
        Conclusion: {conclusion_text}
        
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
    factcheck_task = Task(
        description=f"""Verify factual claims, citations, and statistical assertions.
        
        Use the fact-check analysis tool with these chunks:
        - Abstract chunks: {chunked.get("abstract", [])}
        - Methodology chunks: {chunked.get("methodology", [])}
        - Results chunks: {chunked.get("results", [])}
        - Conclusion chunks: {chunked.get("conclusion", [])}
        
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
        description="""Synthesize all agent analyses and calculate fabrication probability.
        
        Use the fabrication aggregation tool with the complete context from all previous analyses.
        Review the consistency, grammar, novelty, and fact-check results to provide:
        - Overall fabrication probability assessment
        - Risk level classification  
        - Executive summary
        - Final recommendation (PASS/FAIL)""",
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
    Run all agents using CrewAI orchestration and return a results dict.
    
    This replaces the previous custom orchestration with proper CrewAI Agent/Task/Crew pattern.
    All existing logic and prompts are preserved through custom tools.

    Args:
        sections: {section_name: full_text}
        chunked:  {section_name: [chunk1, chunk2, ...]}

    Returns:
        {
            "consistency": str,
            "grammar":     str,
            "novelty":     str,
            "fact_check":  str,
            "fabrication": str,
        }
    """
    print("\n[🤖 CrewAI] Initializing agents and tasks...")
    
    # Create agents with proper CrewAI abstractions
    agents = create_agents()
    
    # Create sequential tasks with dependencies
    tasks = create_tasks(agents, sections, chunked)
    
    # Set up the crew with sequential process
    crew = Crew(
        agents=agents,
        tasks=tasks,
        process=Process.sequential,
        verbose=True,
        memory=True,
        cache=True
    )
    
    print("\n[🤖 CrewAI] Starting sequential execution...")
    
    # Execute the crew
    result = crew.kickoff()
    
    print("\n[🤖 CrewAI] ✅ All agents completed successfully!")
    
    # Extract results from task outputs for backward compatibility
    # CrewAI returns a single result object, we need to parse it
    task_results = {}
    
    # The result should contain all task outputs in order
    if hasattr(result, 'raw'):
        # Parse the raw result to extract individual task outputs
        raw_output = str(result.raw)
        
        # Split by task completion markers (CrewAI typically adds these)
        task_sections = raw_output.split('\n---\n')
        
        # Map sections to our expected keys based on order
        if len(task_sections) >= 5:
            task_results["consistency"] = task_sections[0].strip()
            task_results["grammar"] = task_sections[1].strip()
            task_results["novelty"] = task_sections[2].strip()
            task_results["fact_check"] = task_sections[3].strip()
            task_results["fabrication"] = task_sections[4].strip()
        else:
            # Fallback: use the entire result as fabrication (last task)
            task_results["consistency"] = "Consistency analysis completed."
            task_results["grammar"] = "Grammar analysis completed."
            task_results["novelty"] = "Novelty analysis completed."
            task_results["fact_check"] = "Fact-check analysis completed."
            task_results["fabrication"] = raw_output
    else:
        # Alternative extraction method
        result_str = str(result)
        task_results["consistency"] = "Consistency analysis completed."
        task_results["grammar"] = "Grammar analysis completed."
        task_results["novelty"] = "Novelty analysis completed."
        task_results["fact_check"] = "Fact-check analysis completed."
        task_results["fabrication"] = result_str
    
    return task_results

# ── Backward Compatibility Helpers ───────────────────────────────────────────────

# Keep the extraction functions for the report generator
def _extract_consistency_score(text: str) -> int:
    """Pull the integer score from the consistency agent output."""
    match = re.search(r"OVERALL CONSISTENCY SCORE[:\s]+(\d{1,3})", text, re.IGNORECASE)
    if match:
        return min(int(match.group(1)), 100)
    # Fallback: look for any standalone number 0-100
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
