"""
Output Formatter - Formats answers for display
"""

import json
import re
from typing import Dict, Any, Optional

class OutputFormatter:
    """Format answers for different output types"""
    
    def __init__(self):
        self.json_patterns = [
            r'\{.*\}',
            r'\[.*\]',
            r'```json.*```',
        ]
    
    def format_answer(self, answer: str, field_name: str = "") -> Dict[str, Any]:
        """
        Format answer based on content
        
        Returns:
            Dict with formatted answer and metadata
        """
        result = {
            'text': answer,
            'is_json': self._is_json(answer),
            'should_display_table': False,
            'table_data': None
        }
        
        if result['is_json']:
            # Try to parse as table
            table_data = self._json_to_table(answer)
            if table_data:
                result['should_display_table'] = True
                result['table_data'] = table_data
                result['text'] = self._json_to_text(answer)
        
        return result
    
    def _is_json(self, text: str) -> bool:
        """Check if text is JSON"""
        text = text.strip()
        for pattern in self.json_patterns:
            if re.match(pattern, text, re.DOTALL):
                return True
        
        try:
            json.loads(text.replace('```json', '').replace('```', ''))
            return True
        except:
            return False
    
    def _json_to_table(self, json_str: str) -> Optional[Dict]:
        """Convert JSON to table structure"""
        try:
            # Clean JSON string
            cleaned = json_str.replace('```json', '').replace('```', '').strip()
            data = json.loads(cleaned)
            
            if isinstance(data, dict):
                # Check if it's already in table format
                if 'columns' in data and 'data' in data:
                    return {
                        'headers': data['columns'],
                        'rows': [[str(row.get(col, '')) for col in data['columns']] 
                                for row in data['data']]
                    }
                
                # Convert simple dict to table
                return {
                    'headers': ['Field', 'Value'],
                    'rows': [[k, str(v)] for k, v in data.items() 
                            if not isinstance(v, (dict, list))]
                }
            
            elif isinstance(data, list) and data:
                if isinstance(data[0], dict):
                    # List of objects
                    headers = list(data[0].keys())
                    return {
                        'headers': headers,
                        'rows': [[str(item.get(h, '')) for h in headers] 
                                for item in data]
                    }
                else:
                    # Simple list
                    return {
                        'headers': ['#', 'Item'],
                        'rows': [[i+1, str(item)] for i, item in enumerate(data)]
                    }
            
            return None
            
        except:
            return None
    
    def _json_to_text(self, json_str: str) -> str:
        """Convert JSON to readable text"""
        try:
            cleaned = json_str.replace('```json', '').replace('```', '').strip()
            data = json.loads(cleaned)
            
            if isinstance(data, dict):
                items = [f"{k}: {v}" for k, v in data.items() 
                        if not isinstance(v, (dict, list))]
                return "; ".join(items)
            
            elif isinstance(data, list):
                items = [str(item) for item in data[:5]]
                if len(data) > 5:
                    items.append(f"... and {len(data)-5} more")
                return ", ".join(items)
            
            return str(data)
            
        except:
            return json_str

# Global instance
_formatter = None

def get_formatter() -> OutputFormatter:
    """Get formatter instance"""
    global _formatter
    if _formatter is None:
        _formatter = OutputFormatter()
    return _formatter