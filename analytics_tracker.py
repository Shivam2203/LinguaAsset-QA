"""
Analytics Tracker - Tracks usage and performance metrics
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

class AnalyticsTracker:
    """Track system usage analytics"""
    
    def __init__(self, analytics_file: str = "analytics.json"):
        self.analytics_file = analytics_file
        self.session_start = datetime.now()
        self.data = self._load_data()
    
    def _load_data(self) -> Dict:
        """Load existing analytics"""
        if os.path.exists(self.analytics_file):
            try:
                with open(self.analytics_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return self._init_data()
        return self._init_data()
    
    def _init_data(self) -> Dict:
        """Initialize analytics structure"""
        return {
            'sessions': [],
            'total_questions': 0,
            'languages_used': {},
            'first_run': datetime.now().isoformat()
        }
    
    def track_qa(self, question: str, answer: str, language: str = 'en'):
        """Track a Q&A interaction"""
        self.data['total_questions'] += 1
        self.data['languages_used'][language] = self.data['languages_used'].get(language, 0) + 1
        
    def track_document_fill(self, filename: str, questions_filled: int):
        """Track document filling"""
        if 'documents' not in self.data:
            self.data['documents'] = []
        self.data['documents'].append({
            'filename': filename,
            'questions': questions_filled,
            'timestamp': datetime.now().isoformat()
        })
    
    def save(self):
        """Save analytics to file"""
        with open(self.analytics_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2)

# Global instance
_analytics = None

def get_analytics() -> AnalyticsTracker:
    """Get analytics instance"""
    global _analytics
    if _analytics is None:
        _analytics = AnalyticsTracker()
    return _analytics