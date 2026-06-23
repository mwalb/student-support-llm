import requests
import json

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
    
    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        data = response.json()
        return data.get("response", "No response generated.")
    except requests.exceptions.ConnectionError:
        return "Error: Cannot connect to Ollama. Please run 'ollama serve' in another terminal."
    except requests.exceptions.Timeout:
        return "Error: Request timed out. Please try again."
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"
