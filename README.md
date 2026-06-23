# 🎓 Student Support Assistant

An AI-powered university student support chatbot built with **Ollama**, **FastAPI**, and **Next.js**.

## ✨ Features

- 🤖 Local LLM integration (Ollama + Llama 3.2)
- 🎨 Modern, responsive chat interface
- 📚 University-specific knowledge base
- 🔒 Privacy-focused (all data stays local)
- ⚡ Fast response times

## 📋 Prerequisites

| Requirement | Version |
|-------------|---------|
| Python | 3.10+ |
| Node.js | 18+ |
| Ollama | Latest |
| RAM | 8GB+ (16GB+ recommended) |
| Disk Space | 10GB+ |

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/mwalb/student-support-llm.git
cd student-support-llm
# Linux/Mac
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# Download from: https://ollama.com/download
ollama pull llama3.2:1b
ollama create uni-assistant -f backend/Modelfile
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cd ../frontend
npm install
# Terminal 1: Ollama
ollama serve

# Terminal 2: Backend
cd backend
source venv/bin/activate
python main.py

# Terminal 3: Frontend
cd frontend
npm run dev
http://localhost:3000
#PROJECT STRUCTURE
student-support-llm/
├── backend/
│   ├── llm_client.py      # Ollama connection
│   ├── main.py            # FastAPI server
│   ├── Modelfile          # Custom model config
│   ├── test_llm.py        # LLM test file
│   └── requirements.txt   # Python dependencies
├── frontend/
│   ├── app/
│   │   ├── components/
│   │   │   └── Chat.tsx
│   │   ├── services/
│   │   │   └── apiService.ts
│   │   ├── types/
│   │   │   └── index.ts
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── public/
│   ├── package.json
│   └── tsconfig.json
└── README.md
