export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  model?: string;
}

export interface QuestionRequest {
  question: string;
  model?: string;
}

export interface AnswerResponse {
  question: string;
  answer: string;
  model_used: string;
}

export interface HealthResponse {
  status: string;
  ollama: string;
}