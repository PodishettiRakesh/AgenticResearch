"""
Prompts module for all agents.
"""

# Import all prompt modules
from .consistency import (
    CONSISTENCY_SYSTEM,
    CONSISTENCY_CHUNK_PROMPT,
    CONSISTENCY_REDUCE_PROMPT
)
from .grammar import (
    GRAMMAR_SYSTEM,
    GRAMMAR_PROMPT
)
from .novelty import (
    NOVELTY_SYSTEM,
    NOVELTY_PROMPT
)
from .factcheck import (
    FACTCHECK_SYSTEM,
    FACTCHECK_CHUNK_PROMPT,
    FACTCHECK_REDUCE_PROMPT
)
from .fabrication import (
    FABRICATION_PROMPT
)

__all__ = [
    # Consistency prompts
    'CONSISTENCY_SYSTEM',
    'CONSISTENCY_CHUNK_PROMPT',
    'CONSISTENCY_REDUCE_PROMPT',
    
    # Grammar prompts
    'GRAMMAR_SYSTEM',
    'GRAMMAR_PROMPT',
    
    # Novelty prompts
    'NOVELTY_SYSTEM',
    'NOVELTY_PROMPT',
    
    # Fact-check prompts
    'FACTCHECK_SYSTEM',
    'FACTCHECK_CHUNK_PROMPT',
    'FACTCHECK_REDUCE_PROMPT',
    
    # Fabrication prompts
    'FABRICATION_PROMPT'
]
