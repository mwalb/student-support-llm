// app/types/index.ts

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  model?: string;
  isDocumentAnswer?: boolean;
}

export interface QuestionRequest {
  question: string;
  model?: string;
}

export interface AnswerResponse {
  question: string;
  answer: string;
  model_used: string;
  timestamp: string;
}

export interface HealthResponse {
  status: string;
  ollama: string;
  timestamp: string;
}

export interface ErrorResponse {
  error: string;
  detail?: string;
  timestamp: string;
}

export interface User {
  username: string;
  email: string;
  role: string;
  api_key?: string;
}

export interface FileInfo {
  name: string;
  size: number;
  type: string;
  uploadDate: Date;
}