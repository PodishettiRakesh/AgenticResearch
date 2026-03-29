"""
Fabrication aggregator agent prompts.
"""

# Aggregation prompt
FABRICATION_PROMPT = """Based on the following evaluation results from four specialised 
agents, calculate a Fabrication Probability score and provide an executive summary.

CONSISTENCY SCORE: {consistency_score}/100
GRAMMAR RATING: {grammar_rating}
NOVELTY INDEX: {novelty_index}
FACT-CHECK SUMMARY: {factcheck_summary}

Calculate:
1. FABRICATION PROBABILITY: (0-100%, where 0% = definitely authentic, 100% = likely fabricated)
2. RISK LEVEL: (Low / Medium / High / Critical)
3. EXECUTIVE SUMMARY: 3-4 sentences
4. RECOMMENDATION: PASS or FAIL with one-sentence justification

Use this scoring logic as a guide:
- Consistency < 60 → adds 25% fabrication risk
- Grammar = Low → adds 10% fabrication risk  
- Novelty = Low → adds 15% fabrication risk
- Suspicious claims present → adds 20% fabrication risk
- Start from 0% and cap at 95%

Format your response exactly as shown above with the numbered headings.
"""
