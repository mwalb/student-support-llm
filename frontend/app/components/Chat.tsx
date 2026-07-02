'use client';

import { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { 
  Send, Loader2, Sparkles, User, Bot, AlertCircle, 
  WifiOff, Paperclip, X, FileText, LogOut, Square
} from 'lucide-react';
import { apiService } from '@/services/apiService';

// Type definitions
interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  model?: string;
  isDocumentAnswer?: boolean;
}

interface FileInfo {
  name: string;
  size: number;
  type: string;
  uploadDate: Date;
}

interface User {
  username: string;
  email: string;
  role: string;
}

// Quick questions
const QUICK_QUESTIONS = [
  { id: '1', label: '📚 Registration', question: 'How do I register for courses?' },
  { id: '2', label: '📖 Library', question: 'What services does the library offer?' },
  { id: '3', label: '📝 Exams', question: 'What are the exam rules?' },
  { id: '4', label: '💰 Fees', question: 'How do I pay university fees?' },
  { id: '5', label: '🏠 Hostel', question: 'How do I apply for hostel?' },
  { id: '6', label: '💻 ICT', question: 'How do I get ICT support?' },
];

const DOCUMENT_QUESTIONS = [
  { id: 'd1', label: '📄 Summary', question: 'Summarize the uploaded document' },
  { id: 'd2', label: '📄 Key Points', question: 'What are the key points in the document?' },
  { id: 'd3', label: '📄 Details', question: 'What are the main details in the document?' },
];

export default function Chat() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [apiKey, setApiKey] = useState<string>('');
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: '✨ Welcome to the **Student Support Assistant**! I\'m here to help you with:\n\n• 📚 Course Registration\n• 📖 Library Services  \n• 📝 Exam Rules\n• 💰 Fee Payment\n• 🏠 Hostel Applications\n• 💻 ICT Support\n\n**How can I assist you today?** 🎓',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [isBackendDown, setIsBackendDown] = useState<boolean>(false);
  const [useRAG, setUseRAG] = useState<boolean>(false);
  const [ratings, setRatings] = useState<{[key: string]: string}>({});
  const [uploadedFile, setUploadedFile] = useState<FileInfo | null>(null);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [uploadStatus, setUploadStatus] = useState<string | null>(null);
  
  const [abortController, setAbortController] = useState<AbortController | null>(null);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Load user data
  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    const storedApiKey = localStorage.getItem('apiKey');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
      setApiKey(storedApiKey || '');
    }
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const addSystemMessage = (content: string) => {
    const msg: Message = {
      id: Date.now().toString(),
      role: 'system',
      content: content,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, msg]);
  };

  const handleLogout = () => {
    localStorage.removeItem('apiKey');
    localStorage.removeItem('user');
    router.push('/login');
  };

  const stopConversation = () => {
    if (abortController) {
      abortController.abort();
      setAbortController(null);
      setIsLoading(false);
      addSystemMessage('⏹️ Generation stopped by user.');
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    const validTypes = ['.txt', '.md', '.pdf', '.docx'];
    const fileExt = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!validTypes.includes(fileExt)) {
      addSystemMessage('❌ Please upload .txt, .md, .pdf, or .docx files only.');
      return;
    }
    
    if (file.size > 5 * 1024 * 1024) {
      addSystemMessage('❌ File size must be less than 5MB.');
      return;
    }
    
    setUploadedFile({
      name: file.name,
      size: file.size,
      type: file.type,
      uploadDate: new Date()
    });
    
    setError(null);
    setIsUploading(true);
    setUploadStatus('Uploading...');
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fetch('http://localhost:8000/upload-document', {
        method: 'POST',
        body: formData,
      });
      
      if (response.ok) {
        const data = await response.json();
        setUploadStatus('✅ Uploaded successfully!');
        addSystemMessage(`📄 Document **"${data.filename}"** uploaded successfully! (${(file.size / 1024).toFixed(1)} KB)`);
        addSystemMessage('💡 You can now ask questions about this document.');
        setTimeout(() => setUploadStatus(null), 3000);
      } else {
        addSystemMessage('❌ Failed to upload document');
        setUploadedFile(null);
        setUploadStatus(null);
      }
    } catch (err) {
      addSystemMessage('❌ Error uploading document');
      setUploadedFile(null);
      setUploadStatus(null);
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const removeFile = () => {
    setUploadedFile(null);
    setUploadStatus(null);
  };

  const handleRating = async (messageId: string, rating: string) => {
    const message = messages.find(m => m.id === messageId);
    if (!message || message.role !== 'assistant') return;
    
    const messageIndex = messages.indexOf(message);
    const userQuestion = messageIndex > 0 ? messages[messageIndex - 1]?.content || '' : '';
    
    try {
      const response = await fetch('http://localhost:8000/rate-answer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: userQuestion,
          answer: message.content,
          rating: rating
        }),
      });
      
      if (response.ok) {
        setRatings(prev => ({ ...prev, [messageId]: rating }));
        addSystemMessage(`⭐ You rated this answer as "${rating}"`);
      } else {
        const error = await response.json();
        addSystemMessage(`❌ Failed to save rating: ${error.detail || 'Unknown error'}`);
      }
    } catch (err) {
      addSystemMessage('❌ Failed to save rating');
    }
  };

  // ============================================
  // SEND MESSAGE - FIXED ERROR HANDLING
  // ============================================
  const sendMessage = async (question: string, fromDocument: boolean = false) => {
    if (!question.trim()) {
      addSystemMessage('⚠️ Please enter a question first!');
      return;
    }
    
    if (isLoading) return;

    const controller = new AbortController();
    setAbortController(controller);

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: question,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    setError(null);
    setIsBackendDown(false);

    try {
      let response;
      const headers: any = { 'Content-Type': 'application/json' };
      
      if (apiKey) {
        headers['api_key'] = apiKey;
      }
      
      const requestBody = {
        question: question,
        model: 'uni-assistant'
      };
      
      let url = '';

      if (uploadedFile && fromDocument) {
        url = 'http://localhost:8000/ask-from-document';
      } else if (useRAG) {
        url = 'http://localhost:8000/ask-rag';
      } else if (apiKey) {
        url = 'http://localhost:8000/ask-protected';
      } else {
        url = 'http://localhost:8000/ask';
      }

      const res = await fetch(url, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify(requestBody),
        signal: controller.signal,
      });

      // ============================================
      // BETTER ERROR HANDLING
      // ============================================
      if (!res.ok) {
        let errorMessage = `HTTP ${res.status}`;
        try {
          const errorData = await res.json();
          if (errorData.error) {
            errorMessage = errorData.error;
          } else if (errorData.detail) {
            errorMessage = errorData.detail;
          } else {
            errorMessage = JSON.stringify(errorData);
          }
        } catch (e) {
          errorMessage = res.statusText || `HTTP ${res.status}`;
        }
        throw new Error(errorMessage);
      }

      response = await res.json();

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.answer || 'I apologize, I couldn\'t generate a response.',
        timestamp: new Date(),
        model: response.model_used || 'uni-assistant',
        isDocumentAnswer: uploadedFile && fromDocument ? true : false,
      };
      setMessages((prev) => [...prev, assistantMessage]);
      
    } catch (err: any) {
      if (err.name === 'AbortError' || err.message?.includes('aborted')) {
        return;
      }
      
      let errorMessage = 'Failed to get response.';
      
      if (err instanceof Error) {
        errorMessage = err.message;
      } else if (typeof err === 'string') {
        errorMessage = err;
      } else if (err && typeof err === 'object') {
        errorMessage = err.message || err.error || err.detail || JSON.stringify(err);
      }
      
      // Clean up common error messages
      if (errorMessage.includes('connect') || errorMessage.includes('ECONNREFUSED')) {
        setIsBackendDown(true);
        errorMessage = 'Cannot connect to backend! Please ensure the backend is running.';
      } else if (errorMessage.includes('timeout') || errorMessage.includes('timed out')) {
        errorMessage = 'Request timed out. Please try again.';
      } else if (errorMessage.includes('401') || errorMessage.includes('Unauthorized')) {
        errorMessage = 'Authentication required. Please login first.';
      } else if (errorMessage.includes('422')) {
        errorMessage = 'Invalid request. Please try again.';
      }
      
      addSystemMessage(`❌ ${errorMessage}`);
      
    } finally {
      setIsLoading(false);
      setAbortController(null);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(input, !!uploadedFile);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input, !!uploadedFile);
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="flex flex-col h-screen w-full bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <header className="bg-white/5 backdrop-blur-xl border-b border-white/10 px-6 py-3 sticky top-0 z-10">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full blur-xl opacity-50 animate-pulse"></div>
              <div className="relative bg-gradient-to-r from-blue-500 to-purple-500 p-2.5 rounded-full shadow-lg shadow-blue-500/30">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
            </div>
            <div>
              <h1 className="text-lg font-bold text-white flex items-center gap-2">
                Student Support Assistant
                <span className="text-[10px] font-normal bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded-full border border-emerald-500/30">
                  v2.0
                </span>
              </h1>
              <div className="flex items-center gap-3">
                <p className="text-xs text-slate-400 flex items-center gap-1.5">
                  <span className={`w-1.5 h-1.5 ${isBackendDown ? 'bg-red-500' : 'bg-emerald-400'} rounded-full inline-block`}></span>
                  {isBackendDown ? 'Offline' : 'Online'}
                </p>
                {user && (
                  <p className="text-xs text-slate-400 flex items-center gap-1">
                    👤 {user.username} ({user.role})
                  </p>
                )}
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <button
              onClick={() => setUseRAG(!useRAG)}
              className={`px-3 py-1 text-xs rounded-full transition-all ${
                useRAG 
                  ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30 shadow-lg shadow-amber-500/10' 
                  : 'bg-white/5 text-slate-400 border border-white/10 hover:bg-white/10'
              }`}
            >
              {useRAG ? '🧠 RAG ON' : '🧠 RAG OFF'}
            </button>
            
            <button
              onClick={handleLogout}
              className="px-3 py-1 text-xs bg-red-500/20 text-red-400 border border-red-500/30 rounded-full hover:bg-red-500/30 transition-colors flex items-center gap-1"
            >
              <LogOut className="w-3 h-3" />
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Messages - No error banner, errors show inline */}
      <div className="flex-1 overflow-y-auto px-4 py-4">
        <div className="max-w-4xl mx-auto space-y-4">
          {messages.map((message) => (
            <div key={message.id} className="animate-in fade-in slide-in-from-bottom-2 duration-300">
              <div className={`flex items-start gap-3 ${message.role === 'user' ? 'flex-row-reverse' : ''}`}>
                <div className="flex-shrink-0">
                  <div
                    className={`w-9 h-9 rounded-full flex items-center justify-center shadow-lg ${
                      message.role === 'user'
                        ? 'bg-gradient-to-br from-blue-500 to-indigo-600 shadow-blue-500/30'
                        : message.role === 'system'
                        ? 'bg-gradient-to-br from-red-500 to-rose-600 shadow-red-500/30'
                        : message.isDocumentAnswer
                        ? 'bg-gradient-to-br from-emerald-500 to-teal-600 shadow-emerald-500/30'
                        : 'bg-gradient-to-br from-amber-500 to-amber-600 shadow-amber-500/30'
                    }`}
                  >
                    {message.role === 'user' ? (
                      <User className="w-4 h-4 text-white" />
                    ) : message.role === 'system' ? (
                      isBackendDown ? <WifiOff className="w-4 h-4 text-white" /> : <AlertCircle className="w-4 h-4 text-white" />
                    ) : message.isDocumentAnswer ? (
                      <FileText className="w-4 h-4 text-white" />
                    ) : (
                      <Bot className="w-4 h-4 text-white" />
                    )}
                  </div>
                </div>

                <div className={`max-w-[80%] ${message.role === 'user' ? 'items-end' : 'items-start'}`}>
                  <div
                    className={`px-4 py-3 rounded-2xl ${
                      message.role === 'user'
                        ? 'bg-gradient-to-br from-blue-500 to-indigo-600 text-white rounded-tr-sm shadow-lg shadow-blue-500/20'
                        : message.role === 'system'
                        ? 'bg-red-500/10 border border-red-500/30 text-red-300 rounded-tl-sm'
                        : message.isDocumentAnswer
                        ? 'bg-gradient-to-br from-emerald-500/10 to-teal-500/10 border border-emerald-500/20 text-white rounded-tl-sm'
                        : 'bg-white/5 backdrop-blur-sm border border-white/10 text-white rounded-tl-sm shadow-xl shadow-slate-800/50'
                    }`}
                  >
                    <p className="text-sm whitespace-pre-wrap leading-relaxed">{message.content}</p>
                    {message.isDocumentAnswer && (
                      <div className="mt-2 flex items-center gap-1.5">
                        <span className="text-[10px] bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded-full border border-emerald-500/30">
                          📄 Document Answer
                        </span>
                      </div>
                    )}
                    {message.model && (
                      <span className="text-[10px] opacity-40 mt-1.5 block">🤖 {message.model}</span>
                    )}
                  </div>
                  
                  <div className={`text-[10px] text-slate-500 mt-1 ${message.role === 'user' ? 'text-right' : 'text-left'}`}>
                    {formatTime(message.timestamp)}
                  </div>
                </div>
              </div>

              {message.role === 'assistant' && !ratings[message.id] && (
                <div className="flex items-center gap-1 ml-12 mt-1">
                  <button
                    onClick={() => handleRating(message.id, 'Good')}
                    className="text-xs text-slate-500 hover:text-emerald-400 transition-colors px-2 py-0.5 rounded-full hover:bg-emerald-500/10"
                  >
                    👍 Good
                  </button>
                  <button
                    onClick={() => handleRating(message.id, 'Average')}
                    className="text-xs text-slate-500 hover:text-amber-400 transition-colors px-2 py-0.5 rounded-full hover:bg-amber-500/10"
                  >
                    👌 Average
                  </button>
                  <button
                    onClick={() => handleRating(message.id, 'Poor')}
                    className="text-xs text-slate-500 hover:text-red-400 transition-colors px-2 py-0.5 rounded-full hover:bg-red-500/10"
                  >
                    👎 Poor
                  </button>
                </div>
              )}
              {message.role === 'assistant' && ratings[message.id] && (
                <div className="ml-12 mt-1 text-xs text-slate-500 flex items-center gap-1">
                  <span>⭐ Rated:</span>
                  <span className={`font-medium ${
                    ratings[message.id] === 'Good' ? 'text-emerald-400' :
                    ratings[message.id] === 'Average' ? 'text-amber-400' :
                    'text-red-400'
                  }`}>
                    {ratings[message.id]}
                  </span>
                </div>
              )}
            </div>
          ))}

          {isLoading && (
            <div className="flex items-start gap-3 animate-in fade-in duration-300">
              <div className="flex-shrink-0">
                <div className="w-9 h-9 rounded-full bg-gradient-to-br from-amber-500 to-amber-600 flex items-center justify-center shadow-lg shadow-amber-500/30 animate-pulse">
                  <Loader2 className="w-4 h-4 text-white animate-spin" />
                </div>
              </div>
              <div className="bg-white/5 backdrop-blur-sm border border-white/10 px-4 py-3 rounded-2xl rounded-tl-sm shadow-xl shadow-slate-800/50">
                <div className="flex items-center gap-4">
                  <p className="text-sm text-slate-300 flex items-center gap-2">
                    <span>Thinking</span>
                    <span className="flex gap-1">
                      <span className="w-1.5 h-1.5 bg-amber-400 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                      <span className="w-1.5 h-1.5 bg-amber-400 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                      <span className="w-1.5 h-1.5 bg-amber-400 rounded-full animate-bounce"></span>
                    </span>
                  </p>
                  <button
                    onClick={stopConversation}
                    className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium bg-red-500 text-white border border-red-600 rounded-lg hover:bg-red-600 transition-colors shadow-lg shadow-red-500/30"
                  >
                    <Square className="w-3 h-3" />
                    Stop
                  </button>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Quick Questions */}
      <div className="bg-white/5 backdrop-blur-sm border-t border-white/5 px-4 py-2">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-thin scrollbar-thumb-white/10">
            {QUICK_QUESTIONS.map((q) => (
              <button
                key={q.id}
                onClick={() => sendMessage(q.question, !!uploadedFile)}
                disabled={isLoading || isBackendDown}
                className="px-3 py-1.5 text-xs font-medium bg-white/5 hover:bg-white/10 text-slate-300 hover:text-amber-400 rounded-full border border-white/10 hover:border-amber-500/50 transition-all duration-300 whitespace-nowrap disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {q.label}
              </button>
            ))}
            {uploadedFile && (
              <>
                <span className="text-slate-600 text-xs">|</span>
                {DOCUMENT_QUESTIONS.map((q) => (
                  <button
                    key={q.id}
                    onClick={() => sendMessage(q.question, true)}
                    disabled={isLoading || isBackendDown}
                    className="px-3 py-1.5 text-xs font-medium bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 rounded-full border border-emerald-500/20 hover:border-emerald-500/50 transition-all duration-300 whitespace-nowrap disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {q.label}
                  </button>
                ))}
              </>
            )}
          </div>
        </div>
      </div>

      {/* Input Area */}
      <div className="bg-white/5 backdrop-blur-sm border-t border-white/5 px-4 py-3">
        <div className="max-w-4xl mx-auto">
          {uploadStatus && (
            <div className="mb-2 text-sm text-slate-400 flex items-center gap-2">
              {isUploading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin text-amber-400" />
                  <span>{uploadStatus}</span>
                </>
              ) : (
                <span className="text-emerald-400">{uploadStatus}</span>
              )}
            </div>
          )}

          <form onSubmit={handleSubmit} className="flex gap-2">
            <div className="relative flex-1">
              <input
                ref={inputRef}
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={uploadedFile ? "Ask about the uploaded document..." : "Ask me anything about university..."}
                className="w-full px-4 py-3 bg-white/10 border border-white/10 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-transparent transition-all duration-300 pr-10"
                disabled={isLoading || isBackendDown}
              />
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 hover:bg-white/10 rounded-full transition-colors"
                disabled={isLoading || isBackendDown}
              >
                <Paperclip className={`w-4 h-4 transition-colors ${uploadedFile ? 'text-emerald-400' : 'text-slate-400 hover:text-amber-400'}`} />
              </button>
              <input
                ref={fileInputRef}
                type="file"
                accept=".txt,.md,.pdf,.docx"
                onChange={handleFileUpload}
                className="hidden"
              />
            </div>
            
            <button
              type="submit"
              disabled={!input.trim() || isLoading || isBackendDown}
              className="px-5 py-3 bg-gradient-to-r from-blue-500 to-purple-500 text-white font-medium rounded-xl hover:from-blue-600 hover:to-purple-600 transition-all duration-300 shadow-lg shadow-blue-500/30 hover:shadow-blue-500/50 hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
          
          {uploadedFile && (
            <div className="mt-1.5 flex items-center gap-2 text-xs text-slate-500">
              <FileText className="w-3 h-3 text-emerald-400" />
              <span className="text-emerald-400/70">{uploadedFile.name}</span>
              <span>•</span>
              <span>{(uploadedFile.size / 1024).toFixed(1)} KB</span>
              <button
                onClick={removeFile}
                className="text-slate-500 hover:text-red-400 transition-colors"
              >
                <X className="w-3 h-3" />
              </button>
              <span className="text-slate-600">|</span>
              <span className="text-blue-400/70">💡 Ask document-specific questions</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}