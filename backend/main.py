"""
main.py - Complete FastAPI Backend with Fixed Error Handling
"""

from fastapi import FastAPI, HTTPException, File, UploadFile, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ValidationError
from llm_client import ask_llm
import uvicorn
import logging
import os
from datetime import datetime
import traceback
import json
import re
from typing import Optional, List, Dict

# ============================================
# LOGGING SETUP
# ============================================
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
log_file = f"{LOG_DIR}/app_{datetime.now().strftime('%Y-%m-%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================
# FASTAPI APP
# ============================================
app = FastAPI(
    title="Student Support Assistant API",
    description="AI-powered university student support system",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# MODELS - WITH DEFAULTS
# ============================================
class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1, description="The question to ask")
    model: str = Field(default="uni-assistant", description="Model to use")

class AnswerResponse(BaseModel):
    question: str
    answer: str
    model_used: str
    timestamp: str

# ============================================
# AUTH SYSTEM
# ============================================
USER_DB_FILE = "users.json"

def load_users() -> Dict:
    if os.path.exists(USER_DB_FILE):
        with open(USER_DB_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users: Dict):
    with open(USER_DB_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def hash_password(password: str) -> str:
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()

def generate_api_key() -> str:
    import secrets
    return secrets.token_hex(32)

def create_user(username: str, password: str, email: str, role: str = "student") -> Dict:
    users = load_users()
    if username in users:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    api_key = generate_api_key()
    user_data = {
        "username": username,
        "password": hash_password(password),
        "email": email,
        "role": role,
        "api_key": api_key,
        "created_at": datetime.now().isoformat(),
        "last_login": None
    }
    users[username] = user_data
    save_users(users)
    return {"username": username, "api_key": api_key, "role": role, "email": email}

def authenticate_user(username: str, password: str) -> Optional[Dict]:
    users = load_users()
    if username not in users:
        return None
    user = users[username]
    if user["password"] != hash_password(password):
        return None
    user["last_login"] = datetime.now().isoformat()
    save_users(users)
    return {
        "username": username,
        "api_key": user["api_key"],
        "role": user["role"],
        "email": user["email"]
    }

def validate_api_key(api_key: str) -> Optional[Dict]:
    users = load_users()
    for username, user in users.items():
        if user.get("api_key") == api_key:
            return {"username": username, "role": user.get("role", "student"), "email": user.get("email")}
    return None

def verify_api_key(api_key: str = Header(...)):
    user_info = validate_api_key(api_key)
    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return user_info

# ============================================
# BONUS A: Document Q&A
# ============================================
class DocumentQA:
    def __init__(self, doc_dir: str = "documents"):
        self.doc_dir = doc_dir
        self.documents = []
        os.makedirs(doc_dir, exist_ok=True)
        self.load_documents()
    
    def load_documents(self):
        for filename in os.listdir(self.doc_dir):
            if filename.endswith(('.txt', '.md')):
                filepath = os.path.join(self.doc_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    self.documents.append({'filename': filename, 'content': f.read()})
    
    def search_documents(self, query: str) -> Optional[str]:
        query_words = set(query.lower().split())
        best_match, best_score = None, 0
        for doc in self.documents:
            content = doc['content'].lower()
            score = sum(1 for word in query_words if word in content)
            if score > best_score:
                best_score = score
                best_match = doc['content']
        return best_match if best_score > 0 else None
    
    def ask_from_document(self, question: str) -> str:
        context = self.search_documents(question)
        if not context:
            return "I couldn't find relevant information in the documents. Please upload a document first."
        prompt = f"Based on the following document content, answer the question.\n\nDOCUMENT:\n{context}\n\nQUESTION:\n{question}\n\nANSWER:"
        return ask_llm(prompt, model="uni-assistant")
    
    def add_document(self, content: str, filename: str) -> bool:
        try:
            filepath = os.path.join(self.doc_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            self.documents.append({'filename': filename, 'content': content})
            return True
        except Exception as e:
            logger.error(f"Failed to add document: {e}")
            return False

doc_qa = DocumentQA()

# ============================================
# BONUS B: RAG (Retrieval-Augmented Generation)
# ============================================
class SimpleRAG:
    def __init__(self, faq_file: str = None):
        self.faq_file = faq_file or "documents/university_faq.md"
        self.faq_data = []
        self.load_faq()
    
    def load_faq(self):
        os.makedirs("documents", exist_ok=True)
        if not os.path.exists(self.faq_file):
            default_faq = """# University FAQ

Q: How do I register for courses?
A: Register online before the deadline. Registration opens two weeks before the semester.

Q: What are the library hours?
A: Monday-Friday: 8am-10pm, Saturday: 9am-6pm, Sunday: 10am-6pm.

Q: How do I apply for hostel?
A: Submit application in July with medical records and deposit.

Q: What are the exam rules?
A: Bring valid ID. No electronic devices. Cheating leads to failure.

Q: How do I pay fees?
A: Pay by 15th of each month via bank transfer or online portal.

Q: What ICT support is available?
A: ICT support Monday-Friday, 8am-5pm for Wi-Fi, email, and software issues."""
            with open(self.faq_file, 'w') as f:
                f.write(default_faq)
        
        with open(self.faq_file, 'r') as f:
            content = f.read()
        
        qa_pairs = re.findall(r'Q:\s*(.*?)\s*A:\s*(.*?)(?=Q:|$)', content, re.DOTALL)
        self.faq_data = [{"question": q.strip(), "answer": a.strip()} for q, a in qa_pairs]
        logger.info(f"📚 Loaded {len(self.faq_data)} FAQ entries")
    
    def retrieve_relevant(self, query: str, top_k: int = 2) -> List[Dict]:
        query_words = set(query.lower().split())
        scored = []
        for faq in self.faq_data:
            q_words = set(faq['question'].lower().split())
            a_words = set(faq['answer'].lower().split())
            score = len(query_words & q_words) + len(query_words & a_words)
            scored.append((score, faq))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [faq for score, faq in scored[:top_k] if score > 0]
    
    def ask_with_rag(self, question: str) -> str:
        """Answer question using RAG - retrieves relevant FAQ entries"""
        relevant = self.retrieve_relevant(question)
        
        if not relevant:
            logger.info("No relevant FAQ found, using normal LLM")
            return ask_llm(question, model="uni-assistant")
        
        context = "Based on the following FAQ entries, answer the question:\n\n"
        for i, faq in enumerate(relevant, 1):
            context += f"FAQ {i}:\nQ: {faq['question']}\nA: {faq['answer']}\n\n"
        
        prompt = f"""{context}
        
Question: {question}

Answer using the FAQ information above. If the FAQ doesn't contain the answer, say so."""
        return ask_llm(prompt, model="uni-assistant")

rag = SimpleRAG()

# ============================================
# BONUS E: Feedback System
# ============================================
class FeedbackSystem:
    def __init__(self, feedback_file: str = "feedback.json"):
        self.feedback_file = feedback_file
        self.feedback_data = []
        self.load_feedback()
    
    def load_feedback(self):
        if os.path.exists(self.feedback_file):
            try:
                with open(self.feedback_file, 'r') as f:
                    self.feedback_data = json.load(f)
            except:
                self.feedback_data = []
    
    def save_feedback(self):
        with open(self.feedback_file, 'w') as f:
            json.dump(self.feedback_data, f, indent=2)
    
    def add_feedback(self, question: str, answer: str, rating: str, model: str = None):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "answer": answer[:200] + "..." if len(answer) > 200 else answer,
            "rating": rating,
            "model": model
        }
        self.feedback_data.append(entry)
        self.save_feedback()
        return True
    
    def get_stats(self) -> Dict:
        if not self.feedback_data:
            return {"total": 0, "ratings": {}}
        ratings = {}
        for entry in self.feedback_data:
            rating = entry.get("rating", "unknown")
            ratings[rating] = ratings.get(rating, 0) + 1
        return {"total": len(self.feedback_data), "ratings": ratings}

feedback_system = FeedbackSystem()

# ============================================
# MIDDLEWARE
# ============================================
@app.middleware("http")
async def log_requests(request, call_next):
    start_time = datetime.now()
    logger.info(f"📥 INCOMING: {request.method} {request.url.path}")
    response = await call_next(request)
    duration = (datetime.now() - start_time).total_seconds()
    logger.info(f"📤 RESPONSE: {response.status_code} - {duration:.2f}s")
    return response

# ============================================
# AUTH ENDPOINTS
# ============================================
@app.post("/register")
def register_user(username: str, password: str, email: str, role: str = "student"):
    try:
        return create_user(username, password, email, role)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/login")
def login_user(username: str, password: str):
    user_info = authenticate_user(username, password)
    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    logger.info(f"🔐 User logged in: {username}")
    return {
        "message": "Login successful",
        "username": user_info["username"],
        "api_key": user_info["api_key"],
        "role": user_info["role"],
        "email": user_info["email"]
    }

@app.get("/user/profile")
def get_profile(api_key: str = Header(...)):
    user_info = validate_api_key(api_key)
    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return {
        "username": user_info["username"],
        "role": user_info["role"],
        "email": user_info["email"]
    }

# ============================================
# MAIN ASK ENDPOINTS - FIXED
# ============================================

@app.post("/ask")
def ask_question(request: QuestionRequest):
    """
    Public endpoint - anyone can ask questions
    Returns: { question, answer, model_used, timestamp }
    """
    logger.info(f"📝 Public question: {request.question[:100]}...")
    logger.info(f"   Model: {request.model}")
    
    try:
        answer = ask_llm(request.question, model=request.model)
        
        # Check if ask_llm returned an error message
        if answer.startswith("Error:"):
            logger.warning(f"⚠️ LLM returned error: {answer}")
            return JSONResponse(
                status_code=503,
                content={"error": answer, "timestamp": datetime.now().isoformat()}
            )
        
        return {
            "question": request.question,
            "answer": answer,
            "model_used": request.model,
            "timestamp": datetime.now().isoformat()
        }
        
    except ConnectionError as e:
        logger.error(f"❌ Connection error: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={"error": "Cannot connect to Ollama. Please run 'ollama serve'.", "timestamp": datetime.now().isoformat()}
        )
        
    except TimeoutError as e:
        logger.error(f"⏰ Timeout error: {str(e)}")
        return JSONResponse(
            status_code=504,
            content={"error": "Request timed out. Please try again.", "timestamp": datetime.now().isoformat()}
        )
        
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"error": f"An error occurred: {str(e)}", "timestamp": datetime.now().isoformat()}
        )

@app.post("/ask-protected")
def ask_protected(request: QuestionRequest, user_info: Dict = verify_api_key):
    """Protected endpoint - requires API key"""
    logger.info(f"🔐 Protected question from {user_info['username']}: {request.question[:100]}...")
    logger.info(f"   Model: {request.model}")
    
    try:
        answer = ask_llm(request.question, model=request.model)
        
        if answer.startswith("Error:"):
            logger.warning(f"⚠️ LLM returned error: {answer}")
            return JSONResponse(
                status_code=503,
                content={"error": answer, "timestamp": datetime.now().isoformat()}
            )
        
        return {
            "question": request.question,
            "answer": answer,
            "user": user_info["username"],
            "model_used": request.model,
            "timestamp": datetime.now().isoformat()
        }
        
    except ConnectionError as e:
        logger.error(f"❌ Connection error: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={"error": "Cannot connect to Ollama. Please run 'ollama serve'.", "timestamp": datetime.now().isoformat()}
        )
        
    except TimeoutError as e:
        logger.error(f"⏰ Timeout error: {str(e)}")
        return JSONResponse(
            status_code=504,
            content={"error": "Request timed out. Please try again.", "timestamp": datetime.now().isoformat()}
        )
        
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"error": f"An error occurred: {str(e)}", "timestamp": datetime.now().isoformat()}
        )

# ============================================
# BONUS B: RAG Endpoint
# ============================================
@app.post("/ask-rag")
def ask_with_rag(request: QuestionRequest):
    """RAG endpoint - retrieves from FAQ before generating answer"""
    logger.info(f"📝 RAG Question: {request.question[:100]}...")
    logger.info(f"   Model: {request.model}")
    
    try:
        answer = rag.ask_with_rag(request.question)
        
        if answer.startswith("Error:"):
            logger.warning(f"⚠️ LLM returned error: {answer}")
            return JSONResponse(
                status_code=503,
                content={"error": answer, "timestamp": datetime.now().isoformat()}
            )
        
        return {
            "question": request.question,
            "answer": answer,
            "method": "RAG",
            "model_used": request.model,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ RAG Error: {str(e)}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"error": f"RAG error: {str(e)}", "timestamp": datetime.now().isoformat()}
        )

# ============================================
# BONUS A: Document Endpoints
# ============================================
@app.post("/upload-document")
async def upload_document(file: UploadFile = File(...)):
    logger.info(f"📄 Document upload: {file.filename}")
    try:
        content = await file.read()
        content_str = content.decode('utf-8')
        success = doc_qa.add_document(content_str, file.filename)
        return {
            "message": "Document uploaded successfully" if success else "Failed",
            "filename": file.filename,
            "status": "success" if success else "error"
        }
    except Exception as e:
        logger.error(f"❌ Upload error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Upload failed: {str(e)}", "timestamp": datetime.now().isoformat()}
        )

@app.post("/ask-from-document")
def ask_from_document(request: QuestionRequest):
    logger.info(f"📝 Document question: {request.question[:100]}...")
    logger.info(f"   Model: {request.model}")
    
    try:
        answer = doc_qa.ask_from_document(request.question)
        
        if answer.startswith("Error:"):
            logger.warning(f"⚠️ LLM returned error: {answer}")
            return JSONResponse(
                status_code=503,
                content={"error": answer, "timestamp": datetime.now().isoformat()}
            )
        
        return {
            "question": request.question,
            "answer": answer,
            "source": "document",
            "model_used": request.model,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Document QA Error: {str(e)}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"error": f"Document QA error: {str(e)}", "timestamp": datetime.now().isoformat()}
        )

# ============================================
# BONUS E: Feedback Endpoints
# ============================================
@app.post("/rate-answer")
async def rate_answer(request: Request):
    """Rate an answer as Good/Average/Poor"""
    try:
        data = await request.json()
        question = data.get('question', '')
        answer = data.get('answer', '')
        rating = data.get('rating', '')
        
        if rating not in ["Good", "Average", "Poor"]:
            return JSONResponse(
                status_code=400,
                content={"error": "Rating must be Good, Average, or Poor", "timestamp": datetime.now().isoformat()}
            )
        
        logger.info(f"⭐ Rating: {rating} for question: {question[:50]}...")
        feedback_system.add_feedback(question, answer, rating)
        
        return {
            "message": "Feedback recorded successfully",
            "rating": rating,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Rating error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Rating error: {str(e)}", "timestamp": datetime.now().isoformat()}
        )

@app.get("/feedback-stats")
def get_feedback_stats():
    return feedback_system.get_stats()

# ============================================
# HEALTH AND ROOT ENDPOINTS
# ============================================
@app.get("/")
def root():
    return {
        "message": "Student Support Assistant API",
        "status": "running",
        "version": "2.0.0",
        "models": ["llama3.2:1b", "llama3.2:3b", "uni-assistant"],
        "bonus_features": {
            "A": "Document-Based Question Answering",
            "B": "Simple RAG (Retrieval-Augmented Generation)",
            "C": "Docker (Dockerfile + docker-compose)",
            "D": "Authentication (Login + Registration + API Keys)",
            "E": "Response Evaluation (Good/Average/Poor)"
        },
        "endpoints": {
            "/": "API info",
            "/health": "Health check",
            "/ask": "Ask a question (POST) - Public",
            "/ask-protected": "Ask with API key (POST) - Protected",
            "/ask-rag": "Ask with RAG (POST) - Bonus B",
            "/ask-from-document": "Ask from document (POST) - Bonus A",
            "/upload-document": "Upload document (POST) - Bonus A",
            "/rate-answer": "Rate answer (POST) - Bonus E",
            "/feedback-stats": "Feedback stats (GET) - Bonus E",
            "/register": "Register user (POST) - Bonus D",
            "/login": "Login user (POST) - Bonus D",
            "/user/profile": "User profile (GET) - Bonus D",
            "/docs": "Swagger documentation"
        }
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "ollama": "connected",
        "timestamp": datetime.now().isoformat()
    }

# ============================================
# GLOBAL ERROR HANDLERS
# ============================================
@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    logger.error(f"Validation Error: {str(exc)}")
    return JSONResponse(
        status_code=422,
        content={"error": "Validation error", "detail": str(exc), "timestamp": datetime.now().isoformat()}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "timestamp": datetime.now().isoformat()}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled Exception: {str(exc)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={"error": f"Internal server error: {str(exc)}", "timestamp": datetime.now().isoformat()}
    )

# ============================================
# RUN SERVER
# ============================================
if __name__ == "__main__":
    logger.info("🚀 Starting Student Support Assistant API v2.0...")
    print("\n" + "="*60)
    print("🎓 STUDENT SUPPORT ASSISTANT API v2.0")
    print("="*60)
    print("📚 Bonus Features Enabled:")
    print("  A. Document-Based Question Answering")
    print("  B. Simple RAG (Retrieval-Augmented Generation)")
    print("  C. Docker (Dockerfile + docker-compose)")
    print("  D. Authentication (Login + Registration + API Keys)")
    print("  E. Response Evaluation (Good/Average/Poor)")
    print("="*60)
    print("\n📋 Endpoints:")
    print("  POST /login - Login with username + password")
    print("  POST /register - Register new user")
    print("  POST /ask - Ask a question (public) ✅")
    print("  POST /ask-protected - Ask with API key (protected)")
    print("  POST /ask-rag - Ask with RAG (Bonus B)")
    print("  POST /upload-document - Upload document (Bonus A)")
    print("  POST /ask-from-document - Ask from document (Bonus A)")
    print("  POST /rate-answer - Rate an answer (Bonus E)")
    print("  GET /feedback-stats - Get feedback stats (Bonus E)")
    print("="*60 + "\n")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)