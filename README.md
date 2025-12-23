# 🧪 Lab Manual Assistant

An AI-powered **Lab Manual Conversational Assistant** designed to help students understand laboratory experiments by uploading lab manual PDFs and interacting with them using natural language.

The system uses a **Retrieval-Augmented Generation (RAG)** approach with **local embeddings and a local LLM (Ollama)** to ensure accurate, context-grounded answers **without relying on paid cloud APIs**.

---

## 🚀 Features

- 📄 **Multi-PDF Support**: Upload one or multiple Lab Manuals simultaneously.
- 🔬 **Experiment Extraction**: Automatically identifies Title, Aim, Apparatus, and Theory.
- 📋 **Procedure Generation**: Creates step-by-step, record-ready instructions.
- 🎤 **Exam Prep**: Generates Viva-voce and exam-oriented questions.
- 📝 **Lab Notes**: Summarizes key concepts, observations, precautions, and formulas.
- 💬 **Contextual Chat**: Ask specific questions strictly grounded in the manual content.
- ⚡ **100% Offline**: Privacy-focused AI processing using Ollama (no API keys required).

---

## 🧠 System Architecture

The workflow follows a standard Retrieval-Augmented Generation pipeline:



1. **Extraction**: Text is pulled from PDFs using PyPDF2.
2. **Chunking**: Text is split into segments for precise retrieval.
3. **Embeddings**: Vectorization via HuggingFace (MiniLM) running locally.
4. **Vector Store**: Chunks are stored in FAISS for similarity search.
5. **Retrieval**: Finds the most relevant segments based on user queries.
6. **Inference**: Ollama (Phi-3 Mini) processes the context to generate a response.

---

## 🛠 Tech Stack

| Component | Technology |
| :--- | :--- |
| **Frontend** | Streamlit |
| **LLM** | Ollama (phi3:mini) |
| **Embeddings** | HuggingFace (Local) |
| **Vector DB** | FAISS |
| **RAG Framework** | LangChain |
| **PDF Engine** | PyPDF2 |

---

## 📦 Installation & Setup

### 1️⃣ Clone the Repository
- git https://github.com/rxxkie-git/capabl-labmanual.git
cd capabl-labmanual

### 2️⃣ Create Virtual Environment
# Create the environment
- python -m venv .venv

# Activate on Windows:
- .venv\Scripts\activate   

# Activate on Mac/Linux:
- source .venv/bin/activate

### 3️⃣ Install Dependencies
- pip install -r requirements.txt

### 4️⃣ Setup Ollama
1. Download and install from ollama.com.
2. Pull the required model:
ollama pull phi3:mini

---

## ▶️ Running the Application

- streamlit run app.py
Open your browser to http://localhost:8501.

---

## 🧪 How to Use

1. **Upload**: Drop your Lab Manual PDFs into the sidebar.
2. **Process**: Click "Process Lab Manual" to vectorize the content.
3. **Analyze**: 
   - Click Extract Experiments for a quick overview.
   - Click Generate Viva Questions for exam prep.
4. **Chat**: Use the chatbox for custom queries like "Explain the precautions for the titration experiment."

---

## 🔒 Privacy & Safety
- **Local Processing**: No document content ever leaves your machine.
- **No Cloud API**: Eliminates data leak risks associated with external LLM providers.
- **Academic Integrity**: Designed as a study aid to assist in understanding, not replacing, lab work.

---

## 📌 Future Enhancements
- [ ] Diagram Support: Multi-modal capabilities to explain circuit diagrams or flowcharts.
- [ ] Marks-Based Length: Toggle answers for 2M, 5M, or 10M mark questions.
- [ ] Navigation: Easy experiment-wise jump links in the UI.

---

### ✅ Summary
Lab Manual Assistant demonstrates how AI can be used responsibly in education by combining document retrieval with local reasoning, providing a free and private solution for science and engineering students.
