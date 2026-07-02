"""
rag.py - Simple RAG System (Bonus B)
Retrieves relevant sections from FAQ before sending prompt to LLM.
"""

import json
import os
from typing import List, Dict
from llm_client import ask_llm

class SimpleRAG:
    def __init__(self, faq_file: str = None):
        self.faq_file = faq_file or "documents/university_faq.md"
        self.faq_data = []
        self.load_faq()
    
    def load_faq(self):
        """Load FAQ data from file"""
        if not os.path.exists(self.faq_file):
            # Create default FAQ
            default_faq = """
# University FAQ

Q: How do I register for courses?
A: Register online before the deadline. Registration opens two weeks before the semester.

Q: What are the library hours?
A: Monday-Friday: 8am-10pm, Saturday: 9am-6pm, Sunday: 10am-6pm.

Q: How do I apply for hostel?
A: Submit application in July with medical records and deposit.

Q: What are the exam rules?
A: Bring valid ID. No electronic devices. Cheating leads to failure.

Q: How do I pay fees?
A: Pay by 15th of each month via bank transfer or online portal.
"""
            with open(self.faq_file, 'w') as f:
                f.write(default_faq)
        
        # Parse FAQ
        with open(self.faq_file, 'r') as f:
            content = f.read()
        
        # Simple parsing for Q&A pairs
        import re
        qa_pairs = re.findall(r'Q:\s*(.*?)\s*A:\s*(.*?)(?=Q:|$)', content, re.DOTALL)
        self.faq_data = [{"question": q.strip(), "answer": a.strip()} for q, a in qa_pairs]
    
    def retrieve_relevant(self, query: str, top_k: int = 2) -> List[Dict]:
        """Retrieve most relevant FAQ entries"""
        query_words = set(query.lower().split())
        scored = []
        
        for faq in self.faq_data:
            q_words = set(faq['question'].lower().split())
            a_words = set(faq['answer'].lower().split())
            score = len(query_words & q_words) + len(query_words & a_words)
            scored.append((score, faq))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        return [faq for score, faq in scored[:top_k] if score > 0]
    
    def ask_with_rag(self, question: str) -> str:
        """Answer question with RAG"""
        # Retrieve relevant FAQ entries
        relevant = self.retrieve_relevant(question)
        
        if not relevant:
            # No relevant FAQ, use normal LLM
            return ask_llm(question, model="uni-assistant")
        
        # Build context
        context = "Based on the following FAQ entries, answer the question:\n\n"
        for i, faq in enumerate(relevant, 1):
            context += f"FAQ {i}:\nQ: {faq['question']}\nA: {faq['answer']}\n\n"
        
        prompt = f"""{context}
        
Question: {question}

Answer using the FAQ information above. If the FAQ doesn't contain the answer, say so.
"""
        
        return ask_llm(prompt, model="uni-assistant")

# Global instance
rag = SimpleRAG()
