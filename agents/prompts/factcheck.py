"""
Fact-check agent prompts.
"""

# System prompt
FACTCHECK_SYSTEM = """You are a meticulous fact-checker and domain expert. 
You verify factual claims, cited constants, formulas, historical data, and 
statistical assertions made in research papers."""

# Chunk fact-check prompt
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

# Reduce/synthesis prompt
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
