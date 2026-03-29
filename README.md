# 🔬 AgenticResearch: AI-Powered Research Paper Analysis

A **modular multi-agent AI system** that autonomously analyzes research papers for consistency, grammar, novelty, fact-checking, and potential fabrication detection.

## 🎯 Mission

To provide comprehensive, automated analysis of academic papers using specialized AI agents, helping researchers, reviewers, and institutions assess paper quality and authenticity.

## 🏗️ System Architecture

### **Core Components**
```
├── agents/           # Specialized AI agents
│   ├── consistency/  # Methodology vs results analysis
│   ├── grammar/      # Language quality evaluation  
│   ├── novelty/      # Originality assessment
│   ├── factcheck/    # Claim verification
│   └── fabrication/  # Result synthesis & scoring
├── utils/           # Infrastructure utilities
│   ├── llm/         # Hybrid LLM management
│   ├── scraping/    # Web content extraction
│   └── processing/  # Text chunking & parsing
└── core/            # System orchestration
    ├── pipeline.py  # Main execution flow
    └── interfaces.py # Abstract contracts
```

### **Data Flow Pipeline**
```
arXiv URL → HTML Scraper → Section Parser → Text Chunker
                                                    ↓
Specialized Agents (Consistency, Grammar, Novelty, Fact-Check)
                                                    ↓
Fabrication Agent → Aggregated Scores → Markdown Report
```

### **System Architecture Diagram**
```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           AGENTIC RESEARCH PIPELINE                            │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   arXiv     │───▶│   HTML      │───▶│   Section   │───▶│    Text     │
│     URL     │    │   Scraper   │    │   Parser    │    │   Chunker   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                            │
                                                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           HYBRID LLM SYSTEM                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐              ┌─────────────┐                              │
│  │   Gemini    │◀─────────────▶│   Ollama    │                              │
│  │  (Cloud)    │   Provider    │  (Local)    │                              │
│  └─────────────┘   Switching    └─────────────┘                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                                            │
                                                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SEQUENTIAL AGENT PIPELINE                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Consistency │───▶│   Grammar   │───▶│   Novelty   │───▶│ Fact-Check  │
│   Agent     │    │   Agent     │    │   Agent     │    │   Agent     │
│ (Map-Reduce)│    │ (Single)    │    │ (Single)    │    │ (Map-Reduce)│
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                            │
                                                            ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│Fabrication  │───▶│   Report    │───▶│   Streamlit │
│   Agent     │    │  Generator  │    │   Web UI    │
│ (Aggregator)│    │ (Markdown)  │    │ (Interface) │
└─────────────┘    └─────────────┘    └─────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                              SYSTEM COMPONENTS                                  │
│  • Configuration Management (.env settings)                                     │
│  • Error Handling & Logging (Graceful degradation)                             │
│  • Token Management (Chunking & Map-Reduce)                                    │
│  • Observability (Pipeline tracking & monitoring)                              │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### **Sequential Pipeline Design**
- **Deterministic Execution**: Agents run in controlled sequence for reproducible results
- **Simplicity First**: Clear dependency chain eliminates race conditions and debugging complexity
- **Controlled Flow**: Each agent builds upon previous analysis, ensuring logical progression
- **Easy Debugging**: Linear execution makes failure isolation straightforward

## 🔄 Sequential Multi-Agent Design

### **Why Sequential Pipeline?**
- **Deterministic Results**: Each analysis builds on previous outputs, ensuring consistent evaluation
- **Controlled Complexity**: Eliminates race conditions and coordination overhead
- **Debuggable Architecture**: Linear execution makes failure isolation straightforward
- **Resource Efficiency**: Optimizes LLM token usage through staged processing

### **Execution Benefits**
- **Simplicity**: No complex agent coordination or consensus mechanisms
- **Reliability**: Single point of failure per stage, easier error handling
- **Maintainability**: Clear separation of concerns with defined interfaces
- **Scalability**: Individual agents can be optimized independently

## 🤖 Hybrid LLM System

### **Provider Support**
- **Gemini (Cloud)**: High quality, no setup required
- **Ollama (Local)**: Free, unlimited, private

### **Switching**
```bash
# Environment-based
LLM_PROVIDER=gemini python main.py --url "https://arxiv.org/html/2603.25702v1"

# Runtime override  
python -c "from utils.llm import get_llm; llm = get_llm(provider='ollama')"
```

## 🚀 Quick Start

### **Option 1: Gemini (Cloud)**
```bash
# Set API key in .env
echo "GEMINI_API_KEY=your_key_here" >> .env

# Run analysis
python main.py --url "https://arxiv.org/html/2603.25702v1"
```

### **Option 2: Ollama (Local)**
```bash
# Install and start Ollama
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve
ollama pull llama3:8b

# Run with local models
LLM_PROVIDER=ollama python main.py --url "https://arxiv.org/html/2603.25702v1"
```

### **Option 3: Web Interface**
```bash
streamlit run app.py
```

## 📊 Analysis Pipeline

```python
# Complete Flow
1. 📥 Paper Scraping → arXiv URL → Full text
2. 🔍 Section Parsing → Full text → Structured sections  
3. ✂️ Text Chunking → Sections → Context-optimized chunks
4. 🤖 Agent Analysis → Chunks → Specialized evaluations
5. 📊 Result Synthesis → Agent outputs → Fabrication probability
6. 📄 Report Generation → Results → Structured Markdown
```

## 🎯 Key Features

### **Agent Capabilities**
- **Consistency Analysis**: Logical gaps between methodology and results
- **Grammar Evaluation**: Professional tone and language quality
- **Novelty Assessment**: Originality and contribution significance  
- **Fact-Checking**: Verification of claims and citations
- **Fabrication Detection**: Probabilistic scoring of authenticity

### **Technical Features**
- **Modular Architecture**: Easy to extend and maintain
- **Hybrid LLM Support**: Cloud and local model options
- **Intelligent Chunking**: Context window optimization
- **Configuration Management**: Environment-based settings
- **Error Handling**: Graceful degradation and recovery
- **Comprehensive Logging**: Debug and monitoring support

## 🎯 Key Design Decisions

### **HTML over PDF Parsing**
- **Why**: arXiv provides structured HTML with semantic section headers
- **Benefit**: Reliable section extraction without OCR complexity
- **Fallback**: Automatic PDF parsing when HTML unavailable

### **Map-Reduce for Long Sections**
- **Problem**: Methodology/results sections exceed 16k token limits
- **Solution**: Chunk analysis → partial results → synthesis
- **Result**: Each LLM call stays under 4k tokens, ensuring reliability

### **No Embeddings/Vector Database**
- **Rationale**: Research papers require deep reasoning, not similarity matching
- **Advantage**: Eliminates embedding drift and maintenance overhead
- **Trade-off**: Higher compute cost but more accurate analysis

### **Image Handling via Captions**
- **Approach**: Extract figure captions and table descriptions
- **Reasoning**: LLMs can't process images directly
- **Benefit**: Preserves context without vision model dependencies

## �️ Edge Case Handling

### **Robust Section Parsing**
- **Keyword-Based Detection**: Uses academic section headers (Abstract, Introduction, Methodology, Results, Conclusion)
- **Non-Standard Handling**: Graceful fallback for papers with unconventional structures
- **Missing Section Recovery**: Falls back to full-text analysis when standard sections absent
- **Future Enhancement**: LLM-based semantic section classification for improved detection

### **Long Document Processing**
- **Chunk-wise Analysis**: Large methodology sections broken into analyzable segments
- **Context Preservation**: Overlapping chunks maintain semantic continuity
- **Progressive Synthesis**: Results aggregated incrementally to build complete picture
- **Quality Assurance**: Cross-chunk consistency checks during aggregation phase

### **Missing HTML Content**
- **Primary**: Attempt HTML parsing from arXiv
- **Fallback 1**: Parse PDF if available
- **Fallback 2**: Use abstract-only analysis with limited scope
- **Graceful Degradation**: Always provide meaningful output

### **Image & Figure Processing**
- **Caption Extraction**: Parses figure captions and table descriptions for context
- **Surrounding Text**: Includes preceding/following paragraphs for semantic understanding
- **Limitation**: No visual analysis - relies on textual descriptions only
- **Future Scope**: Integration with multimodal models for direct image analysis

## 🤖 Agent Orchestration Strategy

### **Modular Independence**
- **Design**: Each agent operates independently with clear interfaces
- **Benefits**: Easy testing, maintenance, and individual optimization
- **Communication**: Structured data contracts between agents

### **Execution Flow**
```
1. Consistency Agent → Analyzes methodology vs results logic
2. Grammar Agent → Evaluates language quality and tone  
3. Novelty Agent → Assesses originality and contribution
4. Fact-Check Agent → Verifies claims and citations
5. Fabrication Agent → Synthesizes all outputs into final score
```

### **Fabrication Score Computation**
- **Weighted Signal Aggregation**: Combines multiple risk indicators with calibrated weights
- **Key Signals**:
  - Logical inconsistencies (Consistency Agent): 40% weight
  - Unsupported claims (Fact-Check Agent): 25% weight  
  - Contradictory statements (Cross-agent analysis): 20% weight
  - Language anomalies (Grammar Agent): 15% weight
- **Confidence Scoring**: Probability percentage based on signal strength and consensus
- **Risk Calibration**: Thresholds tuned for academic paper evaluation patterns

### **Error Propagation**
- **Isolation**: Agent failures don't cascade to other agents
- **Fallback**: Missing agent outputs are handled gracefully
- **Logging**: Comprehensive error tracking for debugging

## � Why Multi-Agent Approach

### **Separation of Concerns**
- **Specialized Expertise**: Each agent focuses on specific evaluation dimension
- **Domain Optimization**: Prompts and logic tuned for particular analysis types
- **Quality Enhancement**: Specialized agents outperform general-purpose LLM calls

### **Modular Extensibility**
- **Easy Enhancement**: New evaluation dimensions can be added without affecting existing agents
- **Independent Testing**: Each agent can be validated and improved separately
- **Flexible Orchestration**: Pipeline can be reconfigured for different use cases

### **Better Evaluation Quality**
- **Focused Analysis**: Agents avoid context switching between different evaluation types
- **Deeper Insights**: Specialized prompts extract more nuanced information
- **Consistent Scoring**: Standardized evaluation criteria within each domain

## ��️ System Design Philosophy

### **Simplicity Over Over-Engineering**
- **Principle**: Minimal components, maximum functionality
- **Implementation**: Direct LLM calls without complex middleware
- **Benefit**: Reduced maintenance, easier debugging, faster iteration

### **Reasoning Over Retrieval**
- **Approach**: Deep analytical reasoning vs. similarity search
- **Rationale**: Research paper evaluation requires critical thinking
- **Result**: More nuanced and accurate assessments

### **Explainability First**
- **Design**: Every decision point is traceable
- **Output**: Detailed reasoning for each agent's conclusion
- **Value**: Users understand WHY a paper received its score

### **Scalability by Design**
- **Architecture**: Modular agents enable horizontal scaling
- **Resources**: Efficient token usage for cost optimization
- **Future**: Easy addition of new analysis dimensions

## 🔧 Development Status

### **✅ Completed**
- [x] Modular architecture refactoring
- [x] Hybrid LLM integration (Gemini + Ollama)
- [x] Agent separation and specialization
- [x] Configuration management system
- [x] Pipeline orchestration
- [x] Web interface (Streamlit)

### **🔄 Current Focus**
- [ ] Comprehensive test suite
- [ ] Performance optimization
- [ ] Batch processing capabilities

## 📁 Project Structure

```
AgenticResearch/
├── agents/                 # AI agents and orchestration
│   ├── base/              # Base classes and interfaces
│   ├── consistency/        # Consistency analysis
│   ├── grammar/           # Grammar analysis
│   ├── novelty/           # Novelty assessment
│   ├── factcheck/         # Fact-checking
│   ├── fabrication/       # Fabrication aggregation
│   ├── prompts/           # Agent prompts
│   └── crew_setup.py     # CrewAI orchestration
├── utils/                 # Utility functions
│   ├── llm/              # LLM management
│   ├── scraping/          # Web scraping
│   ├── processing/        # Text processing
│   └── config/           # Configuration
├── core/                  # Core system components
│   ├── interfaces.py      # Abstract interfaces
│   ├── exceptions.py      # Custom exceptions
│   └── pipeline.py       # Main pipeline
├── reports/               # Report generation
├── tests/                 # Test suite
├── main.py                # CLI entry point
├── app.py                 # Web interface
└── README.md              # This file
```

## 🔍 Detailed Architecture

```python
# Data Flow
arXiv URL → Scraper → Full Text → Parser → Sections
                                                    ↓
Sections → Chunker → Text Chunks → Agents
                                                    ↓  
Agent Results → Aggregator → Final Scores → Report Generator → Markdown

# Agent Dependencies
Consistency → Grammar → Novelty → Fact-Check → Fabrication
    (context passing between agents)
```

## 📈 Performance Characteristics

### **Processing Metrics**
- **Analysis Time**: 2-5 minutes per paper (varies by length)
- **Memory Usage**: <2GB for typical academic papers
- **Token Efficiency**: Optimized chunking minimizes API calls
- **Concurrent Processing**: Agents operate in parallel where possible

### **Scalability Design**
- **Horizontal Scaling**: Modular agents enable distributed deployment
- **Vertical Scaling**: Enhanced analysis capabilities through agent specialization
- **Resource Optimization**: Intelligent chunking respects token limits
- **Integration Ready**: Clean interfaces for external system connections

## � Observability & Reliability

### **Pipeline Visibility**
- **Stage Tracking**: Each agent execution logged with timing and token usage
- **Progress Monitoring**: Real-time status updates for long-running analyses
- **Result Validation**: Consistency checks between agent outputs

### **Failure Handling**
- **Graceful Degradation**: System continues analysis even if individual agents fail
- **Fallback Mechanisms**: Alternative strategies when primary approaches fail
- **Error Recovery**: Automatic retries with exponential backoff for API failures
- **Comprehensive Logging**: Detailed error tracking for debugging and monitoring

## �️ Development

### **Setup**
```bash
# Clone and setup
git clone <repository>
cd AgenticResearch
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements_ollama.txt  # For Ollama support

# Configure
cp .env.example .env
# Edit .env with your API keys
```

### **Testing**
```bash
# Test individual components
python test_imports.py              # Import validation
python utils/llm/gemini_checker.py  # LLM testing
python utils/llm/ollama_checker.py   # Ollama testing

# Run full pipeline
python main.py --url "https://arxiv.org/html/2603.25702v1"
```

## 📚 Documentation

### **📁 Comprehensive Documentation**
- **[documents/](documents/)**: Complete documentation collection
  - **[PROJECT_ARCHITECTURE.md](documents/PROJECT_ARCHITECTURE.md)**: Detailed technical architecture
  - **[INTERVIEW_PREP.md](documents/INTERVIEW_PREP.md)**: Interview preparation guide
  - **[CHALLENGE_SOLUTION_LOG.md](documents/CHALLENGE_SOLUTION_LOG.md)**: Development history and solutions
  - **[RESTRUCTURING_SUMMARY.md](documents/RESTRUCTURING_SUMMARY.md)**: Project transformation summary

### **🔧 Setup Guides**
- **[HYBRID_LLM_SETUP.md](HYBRID_LLM_SETUP.md)**: LLM configuration guide
- **[setup_ollama.bat](setup_ollama.bat)**: Automated Ollama setup script

---

## 🚀 Future Improvements

### **Enhanced Section Detection**
- **LLM-Based Classification**: Use semantic understanding for non-standard section formats
- **Multi-Language Support**: Extend beyond English academic papers
- **Adaptive Parsing**: Learn section patterns from different academic fields

### **Advanced Fact-Checking**
- **Web Integration**: Real-time claim verification against academic databases
- **Citation Validation**: Cross-reference claims with cited papers
- **Knowledge Base Integration**: Domain-specific fact repositories

### **Improved Scoring Models**
- **Machine Learning Enhancement**: Train calibration models on verified datasets
- **Domain-Specific Tuning**: Different scoring weights for various academic fields
- **Confidence Intervals**: Statistical uncertainty quantification for scores

### **Performance Optimization**
- **Parallel Processing**: Concurrent agent execution where dependencies allow
- **Caching Layer**: Memoize repeated analyses across similar papers
- **Batch Operations**: Process multiple papers efficiently in production

### **Multimodal Capabilities**
- **Image Analysis**: Direct processing of figures and charts
- **Table Extraction**: Structured data extraction from complex tables
- **Formula Analysis**: Mathematical expression evaluation and verification

## 🙏 Acknowledgments

- **CrewAI**: Agent orchestration framework
- **Google**: Gemini API for language understanding
- **Ollama**: Local model serving capabilities
- **arXiv**: Open access to research papers

---

*Built with ❤️ for the research community*

---

## 🤖 Agent Roles

| Agent | Input | Strategy | Output |
|-------|-------|----------|--------|
| **Consistency Agent** | Methodology + Results chunks | Map-Reduce | Consistency Score (0–100) |
| **Grammar Agent** | Abstract + Introduction | Single call | Grammar Rating (High/Medium/Low) |
| **Novelty Agent** | Abstract + Conclusion | Single call | Novelty Index (qualitative) |
| **Fact-Check Agent** | All section chunks | Map-Reduce | Verified / Unverified / Suspicious claims |
| **Fabrication Aggregator** | All agent outputs | Single call | Fabrication Probability % + Recommendation |

---

## 🔄 Map-Reduce Explanation

For long sections (methodology, results), a single LLM call would exceed the **16k token limit**. We solve this with a **Map-Reduce** pattern:

1. **Map** — Each chunk is sent to the LLM independently. The LLM analyses only that chunk and returns a partial analysis.
2. **Reduce** — All partial analyses are concatenated and sent in a single final call. The LLM synthesises them into one coherent score/report.

This keeps every individual LLM call well under **4 000 tokens** (chunk ~1 200 tokens + prompt ~800 tokens + response ~2 000 tokens).

---

## 📁 Project Structure

```
AgenticResearch/
│
├── app.py                  # Streamlit UI
├── main.py                 # CLI orchestrator / pipeline runner
│
├── agents/
│   ├── __init__.py
│   ├── crew_setup.py       # Agent definitions + Map-Reduce logic
│   └── prompts.py          # All LLM prompts (centralised)
│
├── utils/
│   ├── __init__.py
│   ├── scraper.py          # arXiv HTML scraper with fallback
│   ├── section_parser.py   # Keyword-based section splitter
│   ├── chunker.py          # Overlapping text chunker
│   └── llm.py              # Gemini LLM initialiser
│
├── report/
│   ├── __init__.py
│   └── generator.py        # Markdown report builder
│
├── .env                    # API keys (not committed to git)
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup & Installation

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd AgenticResearch
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your API key

Edit the `.env` file and add your **Google Gemini API key**:

```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

> 🔑 Get a free Gemini API key at: https://aistudio.google.com/app/apikey

---

## 🚀 Running the App

### Option A — Streamlit UI (recommended)

```bash
streamlit run app.py
```

Then open your browser at `http://localhost:8501`, paste an arXiv URL, and click **Evaluate**.

### Option B — CLI

```bash
python main.py --url https://arxiv.org/abs/2301.00001
python main.py --url https://arxiv.org/abs/2301.00001 --output my_report.md
```

---

## 📊 Report Structure

The generated `judgement_report.md` contains:

| Section | Description |
|---------|-------------|
| **Executive Summary** | 3–4 sentence overview + PASS/FAIL recommendation |
| **Score Dashboard** | All metrics in a table |
| **Consistency Analysis** | Methodology vs. results cross-check |
| **Grammar & Language** | Tone, syntax, clarity rating |
| **Novelty Assessment** | Originality compared to known literature |
| **Fact-Check Log** | Verified / Unverified / Suspicious claims |
| **Fabrication Risk** | Probability % + Risk Level |
| **Sections Summary** | Character counts per parsed section |

---

## 🛡️ Token & Chunking Strategy

### **Why Chunking is Required**
- **Token Limits**: LLM context windows capped at 16k tokens (Gemini 1.5 Flash)
- **Methodology Sections**: Often exceed limits with detailed experimental procedures
- **Results Sections**: Can be lengthy with extensive data and analysis
- **Context Preservation**: Chunking ensures no information loss while respecting limits

### **Map-Reduce Implementation**
- **Map Phase**: Each chunk (~1,200 tokens) analyzed independently with consistent prompts
- **Reduce Phase**: Partial analyses synthesized into coherent evaluation
- **Overlap Strategy**: 400-character overlap preserves context across chunk boundaries
- **Token Budgeting**: Each call stays under 4k tokens (chunk + prompt + response buffer)

### **Scalability Benefits**
- **Predictable Performance**: Consistent token usage enables reliable cost estimation
- **Parallel Processing**: Chunks can be processed concurrently when beneficial
- **Memory Efficiency**: Prevents context window overflow and memory issues

---

## ⚠️ Limitations

- Relies on arXiv's HTML rendering — very new papers may only have the abstract available.
- Novelty assessment is based on the LLM's training knowledge, not a live literature search.
- Fact-checking is LLM-based (knowledge cutoff applies); it cannot browse the web.
- Free-tier Gemini has rate limits — very long papers may take 2–4 minutes.

---

## 🧰 Tech Stack

| Component | Technology |
|-----------|-----------|
| Agent Framework | CrewAI |
| LLM | Google Gemini 1.5 Flash |
| LLM Integration | LangChain Google GenAI |
| Web Scraping | BeautifulSoup4 + Requests |
| UI | Streamlit |
| Environment | python-dotenv |

---

*Agentic Research Paper Evaluator — Assignment submission.*
