"""
prompts.py
----------
All system/task prompts for the four specialised agents.
Keeping prompts in one place makes them easy to tune without touching agent logic.
"""

# ── Consistency Agent ──────────────────────────────────────────────────────────
CONSISTENCY_SYSTEM = """You are a rigorous academic peer reviewer specialising in 
logical consistency. Your job is to determine whether the methodology described in 
a research paper actually supports the results and conclusions claimed by the authors."""

CONSISTENCY_CHUNK_PROMPT = """Analyse the following excerpt from a research paper for 
logical consistency. Identify any gaps between what the methodology promises and what 
the results claim. Note any unsupported leaps, missing controls, or contradictions.

EXCERPT:
{chunk}

Respond with:
- KEY CLAIMS found in this excerpt
- POTENTIAL INCONSISTENCIES (if any)
- CONSISTENCY NOTES
"""

CONSISTENCY_REDUCE_PROMPT = """You have received chunk-level consistency analyses of a 
research paper. Synthesise them into a final consistency evaluation.

CHUNK ANALYSES:
{analyses}

Provide:
1. OVERALL CONSISTENCY SCORE: (integer 0-100, where 100 = perfectly consistent)
2. MAJOR INCONSISTENCIES: bullet list
3. MINOR ISSUES: bullet list
4. SUMMARY: 2-3 sentences

Format your response exactly as shown above with the numbered headings.
"""

# ── Grammar Agent ──────────────────────────────────────────────────────────────
GRAMMAR_SYSTEM = """You are an expert academic editor with a PhD in linguistics. 
You evaluate research papers for professional tone, grammatical correctness, 
clarity, and adherence to academic writing standards."""

GRAMMAR_PROMPT = """Evaluate the following text from a research paper for grammar, 
language quality, and professional academic tone.

TEXT:
{text}

Provide:
1. GRAMMAR RATING: (High / Medium / Low)
2. TONE ASSESSMENT: (Professional / Acceptable / Informal)
3. NOTABLE ISSUES: bullet list of specific problems (max 10)
4. POSITIVE ASPECTS: bullet list (max 5)
5. OVERALL LANGUAGE SUMMARY: 2-3 sentences

Format your response exactly as shown above with the numbered headings.
"""

# ── Novelty Agent ─────────────────────────────────────────────────────────────
NOVELTY_SYSTEM = """You are a senior research scientist with broad knowledge of 
academic literature across computer science, AI, physics, biology, and engineering. 
You assess the novelty and originality of research contributions."""

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

# ── Fact-Check Agent ──────────────────────────────────────────────────────────
FACTCHECK_SYSTEM = """You are a meticulous fact-checker and domain expert. 
You verify factual claims, cited constants, formulas, historical data, and 
statistical assertions made in research papers."""

FACTCHECK_CHUNK_PROMPT = """Examine the following research paper excerpt and identify 
all verifiable factual claims (constants, formulas, statistics, historical facts, 
citations, benchmark numbers).

EXCERPT:
{chunk}

For each claim found, assess:
- CLAIM: (exact quote or paraphrase)
- STATUS: VERIFIED / UNVERIFIED / SUSPICIOUS
- REASON: brief explanation

List all claims found. If no verifiable claims exist in this excerpt, say "No verifiable claims found."
"""

FACTCHECK_REDUCE_PROMPT = """You have received fact-check analyses from multiple excerpts 
of a research paper. Compile a final fact-check log.

CHUNK FACT-CHECKS:
{analyses}

Provide:
1. VERIFIED CLAIMS: bullet list
2. UNVERIFIED CLAIMS: bullet list  
3. SUSPICIOUS CLAIMS: bullet list (claims that appear incorrect or exaggerated)
4. FACT-CHECK SUMMARY: 2-3 sentences with overall assessment

Format your response exactly as shown above with the numbered headings.
"""

# ── Aggregator / Fabrication Score ────────────────────────────────────────────
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
