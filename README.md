# 🔬 Agentic Research Paper Evaluator

A **multi-agent AI system** that autonomously scrapes an arXiv paper and produces a comprehensive **Judgement Report** — going far beyond simple summarisation to perform a full peer-review simulation.

Built with **CrewAI** + **Google Gemini 1.5 Flash** (free-tier).

---

## 🏗️ Architecture

```
arXiv URL
    │
    ▼
┌─────────────┐
│   Scraper   │  BeautifulSoup — HTML full-text → fallback to abstract
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ Section Parser  │  Keyword-based heading detection
│  abstract       │  → methodology → results → conclusion
└──────┬──────────┘
       │
       ▼
┌──────────────┐
│   Chunker    │  4 800-char chunks (~1 200 tokens) with 400-char overlap
└──────┬───────┘
       │
       ├──────────────────────────────────────────────────┐
       ▼                                                  ▼
┌──────────────────┐  ┌──────────────┐  ┌─────────────┐  ┌──────────────────┐
│ Consistency Agent│  │ Grammar Agent│  │ Novelty Agent│  │ Fact-Check Agent │
│  (Map-Reduce)    │  │ (single call)│  │ (single call)│  │  (Map-Reduce)    │
└──────────────────┘  └──────────────┘  └─────────────┘  └──────────────────┘
       │                    │                  │                   │
       └────────────────────┴──────────────────┴───────────────────┘
                                       │
                                       ▼
                          ┌────────────────────────┐
                          │  Fabrication Aggregator │
                          │  (single call)          │
                          └────────────┬───────────┘
                                       │
                                       ▼
                          ┌────────────────────────┐
                          │   Judgement Report .md  │
                          └────────────────────────┘
```

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

## 🛡️ Token Handling

- **Hard limit per call:** ~4 000 tokens input (well under the 16k limit)
- **Chunk size:** 4 800 characters ≈ 1 200 tokens
- **Overlap:** 400 characters to preserve context across chunk boundaries
- **Max chunks per agent:** 6 (to avoid rate-limit exhaustion on free tier)
- **Abstract:** Never chunked — kept whole (capped at 3 000 chars)

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
