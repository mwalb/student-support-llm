import requests
import json
import logging

# Setup logger
logger = logging.getLogger(__name__)

OLLAMA_URL = "http://localhost:11434/api/generate"

def ask_llm(question, model="uni-assistant"):
    """
    Send a question to Ollama and get a response.
    
    Parameters:
    - question: str - the question to ask
    - model: str - model name (default: uni-assistant)
    
    Returns:
    - str: the AI's response
    """
    payload = {
        "model": model,
        "prompt": question,
        "stream": False,
        "options": {
            "temperature": 0.3,
            "num_predict": 500
        }
    }
    
    # Log the request
    logger.info(f"📤 Ollama request - Model: {model}")
    
    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        data = response.json()
        answer = data.get("response", "No response generated.")
        
        logger.info(f"📥 Ollama response - Length: {len(answer)} chars")
        return answer
        
    except requests.exceptions.ConnectionError as e:
        error_msg = "❌ Error: Cannot connect to Ollama. Please run 'ollama serve'."
        logger.error(f"ConnectionError: {str(e)}")
        return error_msg
        
    except requests.exceptions.Timeout as e:
        error_msg = "❌ Error: Request timed out. Please try again."
        logger.error(f"Timeout: {str(e)}")
        return error_msg
        
    except requests.exceptions.RequestException as e:
        error_msg = f"❌ Error: {str(e)}"
        logger.error(f"RequestException: {str(e)}")
        return error_msg