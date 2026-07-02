const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const apiService = {
  // Public ask (no auth required)
  askQuestion: async ({ question, model }: { question: string; model: string }) => {
    const response = await fetch(`${API_BASE_URL}/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, model }),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'API Error');
    }
    return response.json();
  },

  // Protected ask (requires API key)
  askProtected: async ({ question, model, apiKey }: { question: string; model: string; apiKey: string }) => {
    const response = await fetch(`${API_BASE_URL}/ask-protected`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'api_key': apiKey,
      },
      body: JSON.stringify({ question, model }),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'API Error');
    }
    return response.json();
  },

  // RAG ask
  askRAG: async ({ question, model }: { question: string; model: string }) => {
    const response = await fetch(`${API_BASE_URL}/ask-rag`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, model }),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'API Error');
    }
    return response.json();
  },
};