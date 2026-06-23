from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from llm_client import ask_llm
import uvicorn

# Create FastAPI app
app = FastAPI(
    title="Student Support Assistant API",
    description="AI-powered university student support system",
    version="1.0.0"
)

# Enable CORS (so frontend can talk to backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (for development)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class QuestionRequest(BaseModel):
    question: str
    model: str = "uni-assistant"

# Response model
class AnswerResponse(BaseModel):
    question: str
    answer: str
    model_used: str

# Root endpoint
@app.get("/")
def root():
    return {
        "message": "Student Support Assistant API",
        "status": "running",
        "models": ["llama3.2:1b", "uni-assistant"],
        "endpoints": {
            "/": "API info",
            "/health": "Health check",
            "/ask": "Ask a question (POST)"
        }
    }

# Health check
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "ollama": "connected"
    }

# Ask endpoint
@app.post("/ask", response_model=AnswerResponse)
def ask_question(request: QuestionRequest):
    """
    Send a question to the AI assistant.
    """
    try:
        answer = ask_llm(request.question, model=request.model)
        
        return AnswerResponse(
            question=request.question,
            answer=answer,
            model_used=request.model
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the server
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
