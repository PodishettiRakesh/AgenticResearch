# 🤖 Hybrid LLM Setup Guide

## 📋 Overview

This guide explains how to set up the hybrid LLM system that supports both **Gemini (cloud)** and **Ollama (local)** providers.

## 🎯 Quick Start

### Option 1: Use Ollama (Recommended for low-resource systems)
```bash
# Install dependencies
pip install -r requirements_ollama.txt

# Set environment variable
export LLM_PROVIDER=ollama  # Linux/macOS
# OR
set LLM_PROVIDER=ollama     # Windows

# Run setup script
bash setup_ollama.sh          # Linux/macOS
# OR
setup_ollama.bat              # Windows
```

### Option 2: Use Gemini (Cloud-based)
```bash
# Set environment variable (optional, it's the default)
export LLM_PROVIDER=gemini   # Linux/macOS
# OR
set LLM_PROVIDER=gemini     # Windows

# Ensure GEMINI_API_KEY is set in .env file
echo "GEMINI_API_KEY=your_api_key_here" >> .env
```

## 🔧 Installation Steps

### 1. Install Dependencies

#### For Ollama (Local):
```bash
pip install langchain-community ollama
```

#### For Gemini (Cloud):
```bash
pip install langchain-google-genai
```

### 2. Ollama Setup (Local LLM)

#### Automatic Setup:
```bash
# Linux/macOS
bash setup_ollama.sh

# Windows
setup_ollama.bat
```

#### Manual Setup:
```bash
# 1. Start Ollama service
ollama serve

# 2. Download lightweight model
ollama pull llama3:8b

# 3. Verify installation
ollama list
```

### 3. Environment Configuration

Create `.env` file:
```bash
# LLM Provider Selection
LLM_PROVIDER=ollama          # Options: "ollama" or "gemini"

# Gemini API Key (only needed if using Gemini)
GEMINI_API_KEY=your_gemini_api_key_here
```

## 📊 Provider Comparison

| Feature | Ollama (Local) | Gemini (Cloud) |
|----------|------------------|-----------------|
| **Cost** | ✅ Free | 💰 Usage-based |
| **Quota** | ✅ Unlimited | ⚠️ Limited |
| **Speed** | ⚡ Fast (local) | 🌐 Fast (cloud) |
| **Privacy** | 🔒 100% Private | 🌐 Cloud processing |
| **Setup** | 🔧 One-time setup | ⚡ Ready to use |
| **Quality** | 🎯 Good | 🏆 Excellent |
| **Offline** | ✅ Works offline | ❌ Requires internet |

## 🖥️ System Requirements

### For Ollama + llama3:8b:
- **RAM**: 8GB+ recommended
- **Storage**: 5GB free space
- **CPU**: Modern multi-core processor
- **OS**: Windows 10+, macOS 10.15+, Linux

### For Gemini:
- **Internet**: Required
- **API Key**: Valid Gemini API key
- **RAM**: 4GB+ recommended

## 🚀 Running the Application

### Method 1: Command Line Interface

#### Simple Provider Selection (Legacy)
```bash
# With Ollama
LLM_PROVIDER=ollama python main.py --url "https://arxiv.org/html/2603.25702v1"

# With Gemini
LLM_PROVIDER=gemini python main.py --url "https://arxiv.org/html/2603.25702v1"
```

#### Intelligent Provider Controls (NEW!)
```bash
# Enable only Ollama (local)
GEMINI_ENABLED=false
OLLAMA_ENABLED=true
python main.py --url "https://arxiv.org/html/2603.25702v1"

# Enable only Gemini (cloud)
GEMINI_ENABLED=true
OLLAMA_ENABLED=false
python main.py --url "https://arxiv.org/html/2603.25702v1"

# Both enabled (auto-selection prefers Ollama)
GEMINI_ENABLED=true
OLLAMA_ENABLED=true
python main.py --url "https://arxiv.org/html/2603.25702v1"
```

### Method 2: Streamlit Interface
```bash
# With Ollama (preferred if both enabled)
GEMINI_ENABLED=false
OLLAMA_ENABLED=true
streamlit run app.py

# With Gemini (preferred if both enabled)
GEMINI_ENABLED=true
OLLAMA_ENABLED=false
streamlit run app.py

# Both enabled (auto-selection)
GEMINI_ENABLED=true
OLLAMA_ENABLED=true
streamlit run app.py
```

## 🧠 Intelligent Provider Selection

### **Selection Logic**
1. **Explicit Override**: If `LLM_PROVIDER` is set and provider is available
2. **Auto-Selection**: 
   - Prefers **Ollama** if enabled (local, free, unlimited)
   - Falls back to **Gemini** if Ollama unavailable
   - Raises error if neither provider is available

### **Configuration Examples**

#### **Scenario 1: Local-First Setup**
```env
# Prefer local processing, use cloud as fallback
GEMINI_ENABLED=true
OLLAMA_ENABLED=true
GEMINI_API_KEY=your_backup_key_here
```

#### **Scenario 2: Cloud-Only Setup**
```env
# Use only cloud-based processing
GEMINI_ENABLED=true
OLLAMA_ENABLED=false
GEMINI_API_KEY=your_primary_key_here
```

#### **Scenario 3: Local-Only Setup**
```env
# Use only local processing (most private)
GEMINI_ENABLED=false
OLLAMA_ENABLED=true
# No API key needed!
```

#### **Scenario 4: Runtime Override**
```bash
# Override environment settings temporarily
LLM_PROVIDER=gemini python main.py --url "https://arxiv.org/html/2603.25702v1"

# Check current provider status
python -c "from utils.llm import get_provider_info; print(get_provider_info())"
```

## 🔍 Troubleshooting

### Ollama Issues:
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
ollama serve

# Check installed models
ollama list
```

### Gemini Issues:
```bash
# Check API key
echo $GEMINI_API_KEY

# Test connection
python -c "from utils.llm_hybrid import get_llm; print(get_llm())"
```

### Switching Providers:
```bash
# Switch to Ollama
export LLM_PROVIDER=ollama

# Switch to Gemini  
export LLM_PROVIDER=gemini

# Verify current provider
python -c "from utils.llm_hybrid import get_provider_info; print(get_provider_info())"
```

## 🎯 Benefits of Hybrid Setup

### ✅ **Flexibility**
- Switch between providers instantly
- Use best provider for each situation
- Fallback options available

### ✅ **Cost Control**
- Local processing when possible
- Cloud processing when needed
- Optimize for budget constraints

### ✅ **Performance**
- Local inference = no latency
- Cloud inference = high quality
- Choose based on requirements

### ✅ **Reliability**
- Multiple backup options
- No single point of failure
- Works offline with Ollama

## 📝 Development Notes

### Adding New Providers:
```python
# In utils/llm_hybrid.py
def get_new_provider_llm(**kwargs):
    # Implementation here
    pass

# Update get_llm() function
elif provider == "new_provider":
    return get_new_provider_llm(**kwargs)
```

### Testing:
```bash
# Test hybrid setup
python utils/llm_hybrid.py

# Test with specific provider
python -c "from utils.llm_hybrid import get_llm; print(get_llm(provider='ollama'))"
```

## 🆘️ Support

### Common Issues:
1. **Ollama not found**: Install from https://ollama.com
2. **Model download failed**: Check internet connection
3. **API quota exceeded**: Switch to Ollama or enable billing
4. **Memory issues**: Use smaller model or close other applications

### Getting Help:
- Check logs for detailed error messages
- Verify environment variables are set correctly
- Test each provider independently

---

**🎉 Ready to use hybrid LLM system!**
