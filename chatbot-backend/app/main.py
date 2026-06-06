# app/main.py
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.search import SemanticSearch
from app.llm import generate_answer
from app.logger import log_conversation

app = FastAPI(title="IT FAQ Chatbot API", version="1.0.0")

# CORS — cho phép frontend (Streamlit / React) gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Khởi tạo 1 lần khi server start — không load lại mỗi request
searcher = SemanticSearch(kb_path="knowledge_base.json")


# --- Schema ---
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    answer: str
    category: str | None
    score: float | None
    escalated: bool


# --- Endpoints ---
@app.get("/api/health")
def health_check():
    return {"status": "ok", "kb_size": len(searcher.kb)}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, background_tasks: BackgroundTasks):
    user_msg = request.message.strip()

    # Bước 1: Semantic Search
    results = searcher.find(user_msg)

    # Bước 2: Generate answer
    answer = generate_answer(user_msg, results)

    # Bước 3: Log — chạy nền, không chặn response
    background_tasks.add_task(log_conversation, user_msg, answer, results)

    # Bước 4: Build response
    if results:
        top = results[0]
        return ChatResponse(
            answer=answer,
            category=top["item"]["category"],
            score=top["score"],
            escalated=False
        )
    else:
        return ChatResponse(
            answer=answer,
            category=None,
            score=None,
            escalated=True
        )