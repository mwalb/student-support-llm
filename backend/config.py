# backend/config.py

import os
import logging
from datetime import datetime

# ============================================
# OLLAMA CONFIGURATION
# ============================================
OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "uni-assistant"
REQUEST_TIMEOUT = 60

# ============================================
# LOGGING CONFIGURATION
# ============================================
LOG_DIR = "logs"
LOG_FILE = f"{LOG_DIR}/app.log"

# Create logs directory if it doesn't exist
os.makedirs(LOG_DIR, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

def get_logger(name):
    """Get a logger instance"""
    return logging.getLogger(name)

# ============================================
# MODEL OPTIONS
# ============================================
MODEL_OPTIONS = {
    "temperature": 0.3,
    "num_predict": 500
}