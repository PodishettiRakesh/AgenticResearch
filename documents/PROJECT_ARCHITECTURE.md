# 🏗️ AgenticResearch Project Architecture

## 📋 Overview

AgenticResearch is a modular research paper evaluation system that uses multiple AI agents to analyze academic papers for consistency, grammar, novelty, fact-checking, and potential fabrication detection.

## 🎯 Core Mission

To provide automated, comprehensive analysis of research papers using specialized AI agents, helping researchers, reviewers, and institutions assess paper quality and authenticity.

## 🏛️ Architecture Evolution

### **Previous Architecture (Monolithic)**
```
├── agents/
│   ├── crew_setup.py      # 456 lines - All agents in one file
│   ├── prompts.py         # All prompts mixed together
│   └── tools.py           # All tools mixed together
├── utils/
│   ├── llm.py             # Basic LLM utilities
│   ├── scraper.py          # Web scraping
│   ├── section_parser.py    # Text parsing
│   └── chunker.py          # Text chunking
└── main.py                 # Simple orchestration
```

**Problems:**
- ❌ Single responsibility principle violated
- ❌ Difficult to test individual components
- ❌ Hard to add new agents
- ❌ Mixed concerns in single files

### **Current Architecture (Modular)**
```
├── agents/
│   ├── base/              # Base classes and interfaces
│   │   ├── agent_base.py
│   │   └── task_base.py
│   ├── consistency/        # Consistency analysis agent
│   │   ├── agent.py
│   │   ├── tasks.py
│   │   └── tools.py
│   ├── grammar/           # Grammar analysis agent
│   │   ├── agent.py
│   │   ├── tasks.py
│   │   └── tools.py
│   ├── novelty/           # Novelty assessment agent
│   │   ├── agent.py
│   │   ├── tasks.py
│   │   └── tools.py
│   ├── factcheck/         # Fact-checking agent
│   │   ├── agent.py
│   │   ├── tasks.py
│   │   └── tools.py
│   ├── fabrication/       # Fabrication aggregator
│   │   ├── agent.py
│   │   ├── tasks.py
│   │   └── tools.py
│   ├── prompts/           # Organized by agent
│   │   ├── consistency.py
│   │   ├── grammar.py
│   │   ├── novelty.py
│   │   ├── factcheck.py
│   │   └── fabrication.py
│   └── crew_setup.py     # Simplified orchestration
├── utils/
│   ├── llm/              # LLM management
│   │   ├── llm.py
│   │   ├── llm_hybrid.py
│   │   ├── gemini_checker.py
│   │   └── ollama_checker.py
│   ├── scraping/          # Web utilities
│   │   ├── scraper.py
│   │   └── section_parser.py
│   ├── processing/        # Text processing
│   │   └── chunker.py
│   └── config/           # Configuration
│       └── settings.py
├── core/
│   ├── interfaces.py      # Abstract interfaces
│   ├── exceptions.py      # Custom exceptions
│   └── pipeline.py       # Main orchestration
└── main.py                 # Clean entry point
```

**Benefits:**
- ✅ Single responsibility principle
- ✅ Easy testing and debugging
- ✅ Simple to add new agents
- ✅ Clear separation of concerns
- ✅ Better maintainability

## 🤖 Agent System

### **Agent Specializations**

1. **Consistency Agent**
   - **Role**: Academic Consistency Reviewer
   - **Focus**: Logical gaps between methodology and results
   - **Method**: Map-Reduce analysis on text chunks

2. **Grammar Agent**
   - **Role**: Academic Language Editor
   - **Focus**: Grammar, tone, professional writing quality
   - **Method**: Single-call analysis on combined text

3. **Novelty Agent**
   - **Role**: Research Novelty Assessor
   - **Focus**: Originality and contribution significance
   - **Method**: Analysis of abstract and conclusion

4. **Fact-Check Agent**
   - **Role**: Research Fact-Checker
   - **Focus**: Verification of factual claims
   - **Method**: Map-Reduce analysis on all sections

5. **Fabrication Aggregator**
   - **Role**: Research Integrity Analyst
   - **Focus**: Synthesize all analyses into probability score
   - **Method**: Weighted scoring based on all agent outputs

### **Execution Flow**

```
1. Paper Scraping → 2. Section Parsing → 3. Text Chunking
                                                        ↓
4. Consistency Analysis → 5. Grammar Analysis → 6. Novelty Assessment
                                                        ↓
7. Fact-Check Analysis → 8. Fabrication Aggregation → 9. Report Generation
```

## 🔧 Hybrid LLM System

### **Provider Support**
- **Gemini (Cloud)**: High quality, no setup required
- **Ollama (Local)**: Free, unlimited, private

### **Switching Mechanism**
```python
# Environment variable
LLM_PROVIDER=gemini  # or ollama

# Runtime switching
from utils.llm import get_llm
llm = get_llm(provider="ollama")  # Override environment
```

### **Configuration Management**
```python
from utils.config import settings

# Access configuration
provider = settings.LLM_PROVIDER
model = settings.GEMINI_MODEL
temperature = settings.TEMPERATURE

# Validate configuration
settings.validate()
```

## 📊 Data Flow

```
arXiv URL → Scraper → Full Text → Parser → Sections
                                                    ↓
Sections → Chunker → Text Chunks → Agents
                                                    ↓
Agent Results → Aggregator → Final Scores → Report Generator → Markdown
```

## 🧪 Testing Strategy

### **Unit Tests**
- Individual agent testing
- Utility function testing
- Configuration validation

### **Integration Tests**
- End-to-end pipeline testing
- LLM provider switching
- Error handling validation

## 🔮 Future Enhancements

### **Phase 1: Immediate**
- [ ] Fix remaining import encoding issues
- [ ] Complete agent module implementations
- [ ] Add comprehensive test suite

### **Phase 2: Medium Term**
- [ ] Web UI improvements
- [ ] Batch processing capabilities
- [ ] Custom agent creation tools

### **Phase 3: Long Term**
- [ ] Machine learning integration
- [ ] Multi-language support
- [ ] Real-time collaboration features

## 🎯 Design Principles

1. **Modularity**: Each component has single responsibility
2. **Extensibility**: Easy to add new agents and tools
3. **Testability**: Components can be tested in isolation
4. **Maintainability**: Clear organization and documentation
5. **Flexibility**: Support for multiple LLM providers
6. **Robustness**: Comprehensive error handling

## 📈 Performance Considerations

### **Optimization Strategies**
- **Chunking**: Intelligent text segmentation for context management
- **Parallel Processing**: Async operations where possible
- **Caching**: Model response caching for repeated queries
- **Resource Management**: Memory and API quota optimization

### **Scalability**
- **Horizontal**: Add more agents for new analysis types
- **Vertical**: Enhance existing agent capabilities
- **Integration**: Connect with external databases and APIs

---

*This architecture enables rapid development, testing, and deployment of new analysis capabilities while maintaining system stability and performance.*
