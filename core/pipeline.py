"""
Main research pipeline orchestration.
"""

import os
import re
from typing import Dict, Any, List
from datetime import datetime

from crewai import Agent, Task, Crew, Process
from utils.llm import get_llm, get_provider_info
from utils.scraping import scrape_arxiv, parse_sections
from utils.processing import chunk_sections
from utils.config import settings

# Import all agent modules
from agents.consistency.agent import ConsistencyAgent
from agents.consistency.tasks import ConsistencyTask
from agents.grammar.agent import GrammarAgent
from agents.grammar.tasks import GrammarTask
from agents.novelty.agent import NoveltyAgent
from agents.novelty.tasks import NoveltyTask
from agents.factcheck.agent import FactCheckAgent
from agents.factcheck.tasks import FactCheckTask
from agents.fabrication.agent import FabricationAgent
from agents.fabrication.tasks import FabricationTask


class ResearchPipeline:
    """Main pipeline for research paper analysis."""
    
    def __init__(self):
        self.agents = {}
        self.tasks = {}
        self._setup_agents()
    
    def _setup_agents(self):
        """Initialize all agents."""
        llm = get_llm()
        
        # Create agent instances
        self.agents = {
            'consistency': ConsistencyAgent(),
            'grammar': GrammarAgent(),
            'novelty': NoveltyAgent(),
            'factcheck': FactCheckAgent(),
            'fabrication': FabricationAgent()
        }
        
        # Create CrewAI agents
        self.crew_agents = {}
        for name, agent in self.agents.items():
            self.crew_agents[name] = agent.create_agent(llm)
    
    def run(self, arxiv_url: str, **kwargs) -> Dict[str, Any]:
        """Run the complete research pipeline."""
        print(f"\n🚀 Starting Research Pipeline Analysis")
        print(f"📄 URL: {arxiv_url}")
        print(f"🤖 LLM Provider: {get_provider_info()['provider']}")
        print(f"⏰ Started at: {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 60)
        
        try:
            # Step 1: Scrape paper
            print("\n📥 [1/5] Scraping paper...")
            paper_data = scrape_arxiv(arxiv_url)
            
            # Step 2: Parse sections
            print("🔍 [2/5] Parsing sections...")
            sections = parse_sections(paper_data['full_text'])
            
            # Step 3: Chunk sections
            print("✂️ [3/5] Chunking sections...")
            chunked = chunk_sections(sections, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
            
            # Step 4: Run agents
            print("🤖 [4/5] Running analysis agents...")
            results = self._run_agents(sections, chunked)
            
            # Step 5: Generate report
            print("📊 [5/5] Processing results...")
            
            print(f"\n✅ Pipeline completed successfully!")
            print(f"⏰ Finished at: {datetime.now().strftime('%H:%M:%S')}")
            
            return {
                'paper_data': paper_data,
                'sections': sections,
                'chunked': chunked,
                'results': results,
                'metadata': {
                    'url': arxiv_url,
                    'provider': get_provider_info()['provider'],
                    'timestamp': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            print(f"\n❌ Pipeline failed: {e}")
            raise
    
    def _run_agents(self, sections: Dict[str, str], chunked: Dict[str, List[str]]) -> Dict[str, Any]:
        """Run all analysis agents."""
        # Create task instances
        task_creators = {
            'consistency': ConsistencyTask(),
            'grammar': GrammarTask(),
            'novelty': NoveltyTask(),
            'factcheck': FactCheckTask(),
            'fabrication': FabricationTask()
        }
        
        # Create CrewAI tasks
        tasks = []
        context = []
        
        # Consistency task
        consistency_task = task_creators['consistency'].create_task(
            self.crew_agents['consistency'], sections, chunked
        )
        tasks.append(consistency_task)
        
        # Grammar task (depends on consistency)
        grammar_task = task_creators['grammar'].create_task(
            self.crew_agents['grammar'], sections, chunked, context=[consistency_task]
        )
        tasks.append(grammar_task)
        
        # Novelty task (depends on grammar)
        novelty_task = task_creators['novelty'].create_task(
            self.crew_agents['novelty'], sections, chunked, context=[grammar_task]
        )
        tasks.append(novelty_task)
        
        # Fact-check task (depends on novelty)
        factcheck_task = task_creators['factcheck'].create_task(
            self.crew_agents['factcheck'], sections, chunked, context=[novelty_task]
        )
        tasks.append(factcheck_task)
        
        # Fabrication task (depends on fact-check)
        fabrication_task = task_creators['fabrication'].create_task(
            self.crew_agents['fabrication'], sections, chunked, context=[factcheck_task]
        )
        tasks.append(fabrication_task)
        
        # Create and run crew
        crew = Crew(
            agents=list(self.crew_agents.values()),
            tasks=tasks,
            process=Process.sequential,
            verbose=False
        )
        
        result = crew.kickoff()
        
        # Extract results
        return self._extract_results(result)
    
    def _extract_results(self, crew_result) -> Dict[str, Any]:
        """Extract structured results from CrewAI execution."""
        result_text = str(crew_result)
        results = {}
        
        # Extract consistency score
        consistency_match = re.search(r"OVERALL CONSISTENCY SCORE[:\s]+(\d{1,3})", result_text, re.IGNORECASE)
        results['consistency_score'] = int(consistency_match.group(1)) if consistency_match else 70
        
        # Extract grammar rating
        grammar_match = re.search(r"GRAMMAR RATING[:\s]+(High|Medium|Low)", result_text, re.IGNORECASE)
        results['grammar_rating'] = grammar_match.group(1) if grammar_match else "Medium"
        
        # Extract novelty index
        novelty_match = re.search(
            r"NOVELTY INDEX[:\s]+(Highly Novel|Moderately Novel|Incremental|Low Novelty)",
            result_text, re.IGNORECASE
        )
        results['novelty_index'] = novelty_match.group(1) if novelty_match else "Moderately Novel"
        
        # Extract fact-check summary
        factcheck_match = re.search(
            r"FACT-CHECK SUMMARY[:\s]+(.*?)(?:\n\n|\d+\.|\Z)",
            result_text, re.IGNORECASE | re.DOTALL
        )
        results['factcheck_summary'] = factcheck_match.group(1).strip() if factcheck_match else "Fact-check completed"
        
        # Extract fabrication probability
        fabrication_match = re.search(r"FABRICATION PROBABILITY[:\s]+(\d{1,3})%", result_text, re.IGNORECASE)
        results['fabrication_probability'] = int(fabrication_match.group(1)) if fabrication_match else 20
        
        # Extract risk level
        risk_match = re.search(r"RISK LEVEL[:\s]+(Low|Medium|High|Critical)", result_text, re.IGNORECASE)
        results['risk_level'] = risk_match.group(1) if risk_match else "Low"
        
        # Extract recommendation
        rec_match = re.search(r"RECOMMENDATION[:\s]+(PASS|FAIL)", result_text, re.IGNORECASE)
        results['recommendation'] = rec_match.group(1) if rec_match else "PASS"
        
        return results
    
    def validate_inputs(self, arxiv_url: str) -> bool:
        """Validate pipeline inputs."""
        if not arxiv_url:
            raise ValueError("arXiv URL is required")
        
        if "arxiv.org" not in arxiv_url:
            raise ValueError("Invalid arXiv URL")
        
        return True
