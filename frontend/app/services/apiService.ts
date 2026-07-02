// app/services/apiService.ts

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface AskQuestionResponse {
  question: string;
  answer: string;
  model_used: string;
  timestamp: string;
}

export interface ErrorResponse {
  error: string;
  detail?: string;
  timestamp: string;
}

export const apiService = {
  // Public ask (no auth required)
  askQuestion: async ({ question, model }: { question: string; model: string }) => {
    try {
      const response = await fetch(`${API_BASE_URL}/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, model }),
      });

      const data = await response.json();

      // Check if response is an error
      if (!response.ok || data.error) {
        throw new Error(data.error || data.detail || `HTTP ${response.status}`);
      }

      return data;
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Failed to get response from server');
    }
  },

  // Protected ask (requires API key)
  askProtected: async ({ question, model, apiKey }: { question: string; model: string; apiKey: string }) => {
    try {
      const response = await fetch(`${API_BASE_URL}/ask-protected`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'api_key': apiKey,
        },
        body: JSON.stringify({ question, model }),
      });

      const data = await response.json();

      if (!response.ok || data.error) {
        throw new Error(data.error || data.detail || `HTTP ${response.status}`);
      }

      return data;
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Failed to get response from server');
    }
  },

  // RAG ask
  askRAG: async ({ question, model }: { question: string; model: string }) => {
    try {
      const response = await fetch(`${API_BASE_URL}/ask-rag`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, model }),
      });

      const data = await response.json();

      if (!response.ok || data.error) {
        throw new Error(data.error || data.detail || `HTTP ${response.status}`);
      }

      return data;
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Failed to get response from server');
    }
  },

  // Document ask
  askFromDocument: async ({ question, model, apiKey }: { question: string; model: string; apiKey?: string }) => {
    try {
      const headers: any = { 'Content-Type': 'application/json' };
      if (apiKey) {
        headers['api_key'] = apiKey;
      }

      const response = await fetch(`${API_BASE_URL}/ask-from-document`, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({ question, model }),
      });

      const data = await response.json();

      if (!response.ok || data.error) {
        throw new Error(data.error || data.detail || `HTTP ${response.status}`);
      }

      return data;
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Failed to get response from server');
    }
  },
};