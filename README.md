# 🚀 Smart RAG Chatbot

An intelligent Retrieval-Augmented Generation (RAG) chatbot that can understand and answer questions from uploaded documents.

--> Use Case
Upload any document and ask questions in natural language — the system retrieves relevant content and generates accurate answers.

--> 🔥 Features
- 📄 Supports PDF, DOCX, TXT
- 🧠 Semantic Search using Sentence Transformers
- ⚡ Fast retrieval with FAISS
- 🤖 LLM-powered answers using Groq
- 📌 Source highlighting for transparency
- 💬 Interactive chat UI
- 📊 Confidence indicator

--> 🛠 Tech Stack
- Python (Flask)
- FAISS (Vector Search)
- Sentence Transformers (Embeddings)
- Groq API (LLM)
- HTML/CSS/JS (Frontend)

--> How to Run

```bash
pip install -r requirements.txt
python app.py

## 🔑 Groq API Key Setup

This project uses Groq LLM for generating responses.

### Steps to get your API key:

1. Go to: https://console.groq.com/keys  
2. Sign in / create an account  
3. Click **Create API Key**  
4. Copy the key  

### Add the API key:

Option 1 — Directly in code (for testing):

```python
client = Groq(api_key="your_api_key_here")

Option 2 — Using environment variable (recommended):
</> Bash
set GROQ_API_KEY=your_api_key_here

Then update code:
'''python
import os
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
