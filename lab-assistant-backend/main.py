# main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os
import io
import re
import json
from dotenv import load_dotenv

# Force load from the same directory as main.py
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
print(f"DEBUG: Attempting to load .env from: {env_path}")

if os.path.exists(env_path):
    print(f"DEBUG: File exists: True")
    # debug file size
    size = os.path.getsize(env_path)
    print(f"DEBUG: File size: {size} bytes")
    if size == 0:
        print("DEBUG: File is EMPTY. Did you save it?")
    else:
        # PEEK at the content without printing the whole key
        with open(env_path, 'r') as f:
            content = f.read().strip()
            print(f"DEBUG: Raw content preview: {content[:15]}...")
else:
    print(f"DEBUG: File exists: False")

load_dotenv(env_path)

# Verify key immediately
key_debug = os.getenv("GOOGLE_API_KEY")
if key_debug:
    print(f"DEBUG: GOOGLE_API_KEY found: {key_debug[:5]}...{key_debug[-5:]}")
else:
    print("DEBUG: GOOGLE_API_KEY NOT found after load_dotenv")

# PDF / DOCX libs
import PyPDF2
from docx import Document

# Attempt both Google SDKs
genai_old = None
GenAIClient = None

try:
    import google.generativeai as genai_old  # Old SDK
except:
    genai_old = None

try:
    from google.genai import Client as GenAIClient  # New SDK
except:
    GenAIClient = None


app = FastAPI()

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- API KEY ----------------
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    print("❌ GOOGLE_API_KEY not set in environment!")
    print('Set it using:  $env:GOOGLE_API_KEY="YOUR_KEY"')
    # Continue running — /generate will return an error.


# ---------------- MODEL SETUP ----------------
MODEL_NAME = "gemini-2.0-flash"   # FREE TIER MODEL

model_helper = {
    "mode": None,    # 'new' or 'old'
    "client": None,
    "model_name": MODEL_NAME
}


# NEW SDK
if API_KEY and GenAIClient:
    try:
        client = GenAIClient(api_key=API_KEY)
        model_helper["client"] = client
        model_helper["mode"] = "new"
        print("✅ Using NEW google.genai Client()")
    except Exception as e:
        print("⚠️ New SDK initialization failed:", e)

# OLD SDK (fallback)
if API_KEY and model_helper["mode"] is None and genai_old:
    try:
        genai_old.configure(api_key=API_KEY)
        model_helper["client"] = genai_old.GenerativeModel(MODEL_NAME)
        model_helper["mode"] = "old"
        print("⚠️ Using OLD google.generativeai fallback")
    except Exception as e:
        print("⚠️ Old SDK initialization failed:", e)

# If no SDK works
if model_helper["mode"] is None:
    print("❌ No Gemini SDK initialized. Install: pip install google-genai")
    print("❌ /generate will not work.")


# ---------------- Pydantic Models ----------------
class GenerateRequest(BaseModel):
    experiment_text: str


class GenerateResponse(BaseModel):
    procedure: str
    theory: str
    safety: str


class ExperimentInfo(BaseModel):
    id: int
    title: str
    preview: str
    text: str


class UploadResponse(BaseModel):
    experiments: List[ExperimentInfo]


# ---------------- File Parsing ----------------
def extract_text_from_pdf(file_bytes: bytes):
    reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
    return "\n".join([p.extract_text() or "" for p in reader.pages])


def extract_text_from_docx(file_bytes: bytes):
    doc = Document(io.BytesIO(file_bytes))
    return "\n".join(p.text for p in doc.paragraphs)


def extract_text(filename: str, file_bytes: bytes):
    name = filename.lower()
    if name.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    if name.endswith(".docx"):
        return extract_text_from_docx(file_bytes)
    return file_bytes.decode("utf-8", errors="ignore")


def parse_experiments(text: str):
    pattern = re.compile(
        r"(Experiment\s*\d+|Exp\s*\d+|EXPERIMENT\s*\d+|Practical\s*\d+|\n\d+\.\s+[A-Za-z].+)",
        re.IGNORECASE,
    )
    matches = list(pattern.finditer(text))

    experiments = []
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        title = m.group().strip()
        body = text[start:end].strip()
        experiments.append((title, body))

    return experiments


# ---------------- LLM CALL ----------------
def call_llm(experiment_text: str):

    if not API_KEY:
        raise HTTPException(status_code=500, detail="GOOGLE_API_KEY not set.")

    if model_helper["client"] is None:
        raise HTTPException(status_code=500, detail="Gemini client not initialized.")

    prompt = f"""
Extract procedure, theory, and safety from the experiment below.
Return JSON only:

\"\"\"
{experiment_text}
\"\"\"

JSON format:
{{
  "procedure": "...",
  "theory": "...",
  "safety": "..."
}}
"""

    try:
        # --------------- NEW SDK ---------------
        if model_helper["mode"] == "new":
            resp = model_helper["client"].models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )
            raw = resp.text

        # --------------- OLD SDK ---------------
        else:
            resp = model_helper["client"].generate_content(prompt)
            raw = resp.text

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini API error: {e}")

    # Extract JSON
    start = raw.find("{")
    end = raw.rfind("}")

    if start == -1 or end == -1:
        return GenerateResponse(
            procedure=raw,
            theory="Model did not return JSON.",
            safety="Model did not return JSON."
        )

    try:
        data = json.loads(raw[start:end + 1])
        return GenerateResponse(
            procedure=data.get("procedure", ""),
            theory=data.get("theory", ""),
            safety=data.get("safety", "")
        )
    except:
        return GenerateResponse(
            procedure=raw,
            theory="Malformed JSON.",
            safety="Malformed JSON."
        )


# ---------------- API Endpoints ----------------
@app.post("/upload-file", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()
    text = extract_text(file.filename, content)
    exps = parse_experiments(text)

    if not exps:
        raise HTTPException(status_code=400, detail="No experiments found.")

    return UploadResponse(
        experiments=[
            ExperimentInfo(
                id=i,
                title=title,
                preview=body[:300].replace("\n", " "),
                text=body
            )
            for i, (title, body) in enumerate(exps)
        ]
    )


@app.post("/generate", response_model=GenerateResponse)
async def generate(req: GenerateRequest):
    if not req.experiment_text.strip():
        raise HTTPException(status_code=400, detail="Experiment text empty.")
    return call_llm(req.experiment_text)
