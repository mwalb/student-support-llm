"""
feedback.py - Response Evaluation (Bonus E)
Users can rate answers as Good/Average/Poor.
"""

import os
import json
from datetime import datetime
from typing import Dict

class FeedbackSystem:
    def __init__(self, feedback_file: str = "feedback.json"):
        self.feedback_file = feedback_file
        self.feedback_data = []
        self.load_feedback()
    
    def load_feedback(self):
        """Load existing feedback from file"""
        if os.path.exists(self.feedback_file):
            try:
                with open(self.feedback_file, 'r') as f:
                    self.feedback_data = json.load(f)
            except:
                self.feedback_data = []
    
    def save_feedback(self):
        """Save feedback to file"""
        with open(self.feedback_file, 'w') as f:
            json.dump(self.feedback_data, f, indent=2)
    
    def add_feedback(self, question: str, answer: str, rating: str, model: str = None):
        """Add new feedback entry"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "answer": answer[:200] + "..." if len(answer) > 200 else answer,
            "rating": rating,
            "model": model
        }
        self.feedback_data.append(entry)
        self.save_feedback()
        return True
    
    def get_stats(self) -> Dict:
        """Get feedback statistics"""
        if not self.feedback_data:
            return {"total": 0, "ratings": {}}
        
        ratings = {}
        for entry in self.feedback_data:
            rating = entry.get("rating", "unknown")
            ratings[rating] = ratings.get(rating, 0) + 1
        
        return {
            "total": len(self.feedback_data),
            "ratings": ratings
        }

# Global instance
feedback_system = FeedbackSystem()
