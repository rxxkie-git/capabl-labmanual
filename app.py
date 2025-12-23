import streamlit as st
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter

import os
import io
import ollama

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from datetime import datetime


# =======================
# Embeddings (LOCAL)
# =======================
@st.cache_resource
def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


# =======================
# Session State
# =======================
def init_session_state():
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'generated_content' not in st.session_state:
        st.session_state.generated_content = {}


# =======================
# PDF Processing
# =======================
def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        reader = PdfReader(pdf)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    return text


def get_text_chunks(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=10000,
        chunk_overlap=1000
    )
    return splitter.split_text(text)


def get_vector_store(text_chunks):
    embeddings = get_embeddings()
    db = FAISS.from_texts(text_chunks, embedding=embeddings)
    db.save_local("faiss_index")
    return True


# =======================
# Prompt Template
# =======================
def get_prompt_template():
    template = """
You are a Lab Manual Assistant.

Answer strictly using the provided lab manual context.
If the answer is not present, say:
"Not available in the lab manual context."

Context:
{context}

Question:
{question}

Answer:
"""
    return PromptTemplate(
        template=template,
        input_variables=["context", "question"]
    )


# =======================
# Ollama Call (LLM ONLY)
# =======================
def ollama_answer(prompt: str) -> str:
    response = ollama.chat(
        model="phi3:mini",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response["message"]["content"]


# =======================
# Features
# =======================
def summarize_pdf():
    embeddings = get_embeddings()
    db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)

    docs = db.similarity_search(
        "list all experiments with aim apparatus theory description",
        k=10
    )

    context = "\n\n".join(d.page_content for d in docs)

    prompt = f"""
From the following lab manual content, extract all experiments.
For each experiment include:
- Experiment title
- Aim
- Apparatus
- Brief theory overview

{context}
"""

    answer = ollama_answer(prompt)
    st.session_state.generated_content["summary"] = answer
    st.write(answer)


def generate_questions():
    embeddings = get_embeddings()
    db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)

    docs = db.similarity_search(
        "experimental procedure steps",
        k=8
    )

    context = "\n\n".join(d.page_content for d in docs)

    prompt = f"""
Generate clear step-by-step experimental procedures
suitable for writing in a lab record.

{context}
"""

    answer = ollama_answer(prompt)
    st.session_state.generated_content["questions"] = answer
    st.write(answer)


def generate_mcqs():
    embeddings = get_embeddings()
    db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)

    docs = db.similarity_search(
        "important definitions principles viva questions",
        k=6
    )

    context = "\n\n".join(d.page_content for d in docs)

    prompt = f"""
Generate 5–7 viva or exam-oriented questions
based on the following lab manual content.

{context}
"""

    answer = ollama_answer(prompt)
    st.session_state.generated_content["mcqs"] = answer
    st.write(answer)


def generate_notes():
    embeddings = get_embeddings()
    db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)

    docs = db.similarity_search(
        "key concepts formulas observations precautions",
        k=8
    )

    context = "\n\n".join(d.page_content for d in docs)

    prompt = f"""
Create structured lab notes including:
- Key concepts
- Important formulas
- Observations
- Precautions

{context}
"""

    answer = ollama_answer(prompt)
    st.session_state.generated_content["notes"] = answer
    st.write(answer)


def user_input(question):
    embeddings = get_embeddings()
    db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)

    docs = db.similarity_search(question)
    context = "\n\n".join(d.page_content for d in docs)

    prompt_template = get_prompt_template()
    final_prompt = prompt_template.format(
        context=context,
        question=question
    )

    answer = ollama_answer(final_prompt)
    st.write(answer)


# =======================
# Streamlit UI
# =======================
def main():
    st.set_page_config(
        page_title="Lab Manual Assistant",
        page_icon="🧪",
        layout="wide"
    )

    init_session_state()

    st.markdown("<h1 style='text-align:center'>🧪 Lab Manual Assistant</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align:center'>Offline AI Assistant for Laboratory Experiments</p>",
        unsafe_allow_html=True
    )

    st.markdown("### 🧠 Laboratory Features")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.button("🔬 Extract Experiments", on_click=summarize_pdf)
    with col2:
        st.button("📋 Generate Procedure", on_click=generate_questions)
    with col3:
        st.button("🎤 Generate Viva Questions", on_click=generate_mcqs)
    with col4:
        st.button("📝 Generate Lab Notes", on_click=generate_notes)

    st.markdown("### 💬 Ask Questions About the Lab Manual")
    question = st.text_input("Enter your question")
    if question:
        user_input(question)

    with st.sidebar:
        st.markdown("## 📁 Lab Manual Upload")
        pdf_docs = st.file_uploader(
            "Upload Lab Manual PDFs",
            accept_multiple_files=True,
            type=["pdf"]
        )

        if st.button("⚙️ Process Lab Manual"):
            if not pdf_docs:
                st.error("Please upload at least one PDF")
            else:
                raw_text = get_pdf_text(pdf_docs)
                chunks = get_text_chunks(raw_text)
                get_vector_store(chunks)
                st.success("Lab manual processed successfully!")


if __name__ == "__main__":
    main()



