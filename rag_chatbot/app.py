from flask import Flask, request, jsonify, render_template
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import re
import PyPDF2
import docx
from groq import Groq

app = Flask(__name__)

# 🔑 Add your Groq API key
client = Groq(api_key="ADD_YOUR_GROQ_API_KEY_HERE")

# 🔥 Embedding model
model = SentenceTransformer("all-mpnet-base-v2")

documents = []
index = None

# ✅ SMART CHUNKING
def smart_chunk(text, chunk_size=600, overlap=100):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk.strip())
        start += chunk_size - overlap

    return chunks

# ✅ BUILD VECTOR DB
def build_index(docs):
    global index
    embeddings = model.encode(docs)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))

# ✅ RETRIEVE (IMPROVED)
def retrieve(query, k=6):
    if index is None:
        return []

    query_vector = model.encode([query])
    distances, indices = index.search(np.array(query_vector), k=k)

    # sort best matches
    sorted_pairs = sorted(zip(distances[0], indices[0]), key=lambda x: x[0])

    return [documents[i] for _, i in sorted_pairs if i < len(documents)]

# ✅ HIGHLIGHT FUNCTION
def highlight_text(text, query):
    words = query.lower().split()

    for word in words:
        if len(word) > 3:
            text = re.sub(f"({word})", r"<b style='color:yellow'>\1</b>", text, flags=re.IGNORECASE)

    return text

# ✅ GENERATE RESPONSE
def generate_response(query, retrieved_docs):
    context = "\n".join(retrieved_docs)

    if not context.strip():
        return "Sorry, I couldn't find relevant information."

    prompt = f"""
You are a precise AI assistant.

RULES:
- Answer ONLY using the provided context
- Do NOT guess
- If answer is not clearly present, say "I don't know"
- Be clear and structured

Context:
{context}

Question:
{query}

Answer:
"""

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )

    return completion.choices[0].message.content.strip()

# 🏠 HOME
@app.route("/")
def home():
    return render_template("index.html")

# 📄 FILE UPLOAD
@app.route("/upload", methods=["POST"])
def upload():
    global documents

    file = request.files["file"]
    filename = file.filename
    content = ""

    if filename.endswith(".txt"):
        try:
            content = file.read().decode("utf-8")
        except:
            content = file.read().decode("latin-1")

    elif filename.endswith(".pdf"):
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                content += text + "\n"

    elif filename.endswith(".docx"):
        doc = docx.Document(file)
        for para in doc.paragraphs:
            content += para.text + "\n"

    else:
        return jsonify({"message": "Unsupported file format!"})

    # Clean text
    content = re.sub(r'\s+', ' ', content)

    # Chunk
    documents = smart_chunk(content)

    # Build index
    build_index(documents)

    return jsonify({"message": f"{filename} uploaded and indexed successfully!"})

# 💬 CHAT
@app.route("/chat", methods=["POST"])
def chat():
    query = request.json["query"]

    retrieved_docs = retrieve(query, k=6)

    # 🔥 fallback if retrieval weak
    if not retrieved_docs or len(" ".join(retrieved_docs)) < 100:
        retrieved_docs = documents[:10]

    response = generate_response(query, retrieved_docs)

    # 🔥 Highlight relevant parts
    highlighted_sources = []
    for doc in retrieved_docs:
        if any(word.lower() in doc.lower() for word in query.split()):
            highlighted_sources.append(highlight_text(doc[:300], query))

    return jsonify({
        "response": response,
        "sources": highlighted_sources
    })

# 🚀 RUN
if __name__ == "__main__":
    app.run(debug=True)