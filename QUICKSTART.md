# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: (Optional) Setup Ollama for LLM

If you want to use the full LLM-powered features:

1. **Download Ollama**: https://ollama.ai
2. **Install and run Ollama**
3. **Pull models**:
   ```bash
   ollama pull llama2
   ollama pull codellama
   ```

**Note**: The system works without Ollama but will use fallback templates.

### Step 3: Run the Application

**Option A: Using the run script** (Easiest)
```bash
python run.py
```

**Option B: Direct Streamlit command**
```bash
streamlit run frontend/app.py
```

### Step 4: Use the Application

1. **Open browser** at `http://localhost:8501`
2. **Upload documents** from `support_docs/` folder
3. **Upload or paste** `checkout.html` content
4. **Build Knowledge Base**
5. **Generate Test Cases**
6. **Generate Selenium Scripts**

## 📁 Project Files

- `checkout.html` - Target web application
- `support_docs/` - Support documentation
- `backend/` - FastAPI backend (optional)
- `frontend/app.py` - Streamlit UI (main application)

## 🎯 Example Workflow

1. **Knowledge Base Tab**:
   - Upload `support_docs/product_specs.md`
   - Upload `support_docs/ui_ux_guide.txt`
   - Upload `support_docs/api_endpoints.json`
   - Upload `checkout.html`
   - Click "Build Knowledge Base"

2. **Test Cases Tab**:
   - Enter: "Generate test cases for discount code feature"
   - Click "Generate Test Cases"
   - Review generated test cases
   - Select one for script generation

3. **Script Generation Tab**:
   - Click "Generate Selenium Script"
   - Review generated code
   - Download script

## ⚡ Troubleshooting

**Issue**: Module not found
```bash
# Make sure you're in the project root
cd OceanAI
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

**Issue**: Ollama not found
- The system will use fallback templates
- Install Ollama for better results

**Issue**: Port already in use
```bash
# Use different port
streamlit run frontend/app.py --server.port 8502
```

## 📚 Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore the generated test cases
- Run the generated Selenium scripts
- Customize for your own projects

---

**Happy Testing! 🎉**

