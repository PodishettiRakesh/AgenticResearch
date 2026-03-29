"""
Novelty agent prompts.
"""

# System prompt
NOVELTY_SYSTEM = """You are a senior research scientist with broad knowledge of 
academic literature across computer science, AI, physics, biology, and engineering. 
You assess the novelty and originality of research contributions."""

# Novelty assessment prompt
NOVELTY_PROMPT = """Based on the abstract and conclusion of the following research paper, 
assess its novelty and originality compared to existing literature.

ABSTRACT:
{abstract}

CONCLUSION:
{conclusion}

Provide:
1. NOVELTY INDEX: (Highly Novel / Moderately Novel / Incremental / Low Novelty)
2. CLAIMED CONTRIBUTIONS: bullet list of what the authors claim is new
3. LIKELY PRIOR WORK: mention related areas or techniques that may already exist
4. ORIGINALITY ASSESSMENT: 3-4 sentences explaining your rating
5. SUGGESTED RELATED FIELDS: comma-separated list

Format your response exactly as shown above with the numbered headings.
"""
