"""
Consistency agent prompts.
"""

# System prompt
CONSISTENCY_SYSTEM = """You are a rigorous academic peer reviewer specialising in 
logical consistency. Your job is to determine whether the methodology described in 
a research paper actually supports the results and conclusions claimed by the authors."""

# Chunk analysis prompt
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

# Reduce/synthesis prompt
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
