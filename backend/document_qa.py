"""
document_qa.py - Document-Based Question Answering (Bonus A)
Allows users to upload .txt or .md files and ask questions from them.
"""

import os
import re
from typing import List, Dict, Optional
from llm_client import ask_llm

class DocumentQA:
    def __init__(self, doc_dir: str = "documents"):
        self.doc_dir = doc_dir
        self.documents = []
        self.load_documents()
    
    def load_documents(self):
        """Load all .txt and .md files from documents directory"""
        if not os.path.exists(self.doc_dir):
            os.makedirs(self.doc_dir)
            return
        
        for filename in os.listdir(self.doc_dir):
            if filename.endswith(('.txt', '.md')):
                filepath = os.path.join(self.doc_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.documents.append({
                        'filename': filename,
                        'content': content
                    })
    
    def search_documents(self, query: str) -> str:
        """Search for relevant content in documents"""
        if not self.documents:
            return None
        
        # Simple keyword matching
        query_words = set(query.lower().split())
        best_match = None
        best_score = 0
        
        for doc in self.documents:
            content = doc['content'].lower()
            score = sum(1 for word in query_words if word in content)
            if score > best_score:
                best_score = score
                best_match = doc['content']
        
        if best_score > 0:
            return best_match
        return None
    
    def ask_from_document(self, question: str) -> str:
        """Answer a question using document context"""
        # Search for relevant content
        context = self.search_documents(question)
        
        if not context:
            return "I couldn't find relevant information in the documents. Please upload a document first."
        
        # Use LLM to answer based on context
        prompt = f"""
        Based on the following document content, answer the question.
        If the answer is not in the document, say "I don't have information about that."
        
        DOCUMENT CONTENT:
        {context}
        
        QUESTION:
        {question}
        
        ANSWER:
        """
        
        return ask_llm(prompt, model="uni-assistant")
    
    def add_document(self, content: str, filename: str) -> bool:
        """Add a new document"""
        try:
            filepath = os.path.join(self.doc_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            self.documents.append({
                'filename': filename,
                'content': content
            })
            return True
        except Exception as e:
            return False

# Global instance
doc_qa = DocumentQA()
