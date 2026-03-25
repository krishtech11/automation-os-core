"""
Advanced Natural Language Intent Parser (Week 5)
Uses sklearn TF-IDF + regex patterns for better entity extraction
"""
import re
from typing import Dict, Tuple, Optional, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import logging

logger = logging.getLogger(__name__)


class AdvancedIntentParser:
    """
    Enhanced intent parser with TF-IDF classification and entity extraction
    """
    
    def __init__(self):
        # Training data for TF-IDF classifier
        self.training_data = {
            'NEWS_DIGEST': [
                'send me news', 'tech news email', 'latest headlines',
                'daily news digest', 'breaking news', 'news update',
                'mujhe news bhejo', 'khabar bhejo', 'samachar email karo',
                'tech updates', 'business news', 'sports news'
            ],
            'FILE_CLEANUP': [
                'clean downloads folder', 'organize files', 'rename pdfs',
                'folder cleanup', 'sort documents', 'arrange files',
                'downloads ko clean karo', 'files organize karo', 'pdf rename',
                'folder ko arrange karo', 'desktop cleanup', 'file management'
            ],
            'INVOICE_SYNC': [
                'gmail invoices', 'sync bills', 'save receipts',
                'invoice backup', 'gmail to drive', 'email attachments',
                'invoices save karo', 'bills backup', 'gmail se documents'
            ]
        }
        
        # Initialize TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),  # unigrams + bigrams
            max_features=100,
            lowercase=True
        )
        
        # Train the vectorizer
        all_samples = []
        self.labels = []
        for workflow_type, samples in self.training_data.items():
            all_samples.extend(samples)
            self.labels.extend([workflow_type] * len(samples))
        
        self.tfidf_matrix = self.vectorizer.fit_transform(all_samples)
        
        logger.info("Advanced Intent Parser initialized with TF-IDF classifier")
    
    def classify_intent(self, text: str) -> Tuple[str, float]:
        """
        Classify intent using TF-IDF similarity
        Returns: (workflow_type, confidence)
        """
        # Transform input text
        text_vector = self.vectorizer.transform([text.lower()])
        
        # Calculate cosine similarity with all training samples
        similarities = cosine_similarity(text_vector, self.tfidf_matrix)[0]
        
        # Get best match
        best_idx = np.argmax(similarities)
        confidence = similarities[best_idx]
        workflow_type = self.labels[best_idx]
        
        # Fallback to MANUAL if confidence too low
        if confidence < 0.15:
            return 'MANUAL', confidence
        
        logger.info(f"Classified as {workflow_type} (confidence: {confidence:.2f})")
        return workflow_type, confidence
    
    def extract_email(self, text: str) -> Optional[str]:
        """Extract email address from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, text)
        return match.group(0) if match else None
    
    def extract_numbers(self, text: str) -> List[int]:
        """Extract all numbers from text"""
        return [int(n) for n in re.findall(r'\b\d+\b', text)]
    
    def extract_time(self, text: str) -> Optional[Dict[str, int]]:
        """
        Extract time from text (e.g., "6 PM", "9:30 AM", "18:00")
        Returns: {'hour': int, 'minute': int}
        """
        # 12-hour format: 6 PM, 9:30 AM
        match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm|AM|PM)', text)
        if match:
            hour = int(match.group(1))
            minute = int(match.group(2)) if match.group(2) else 0
            meridiem = match.group(3).lower()
            
            if meridiem == 'pm' and hour != 12:
                hour += 12
            elif meridiem == 'am' and hour == 12:
                hour = 0
            
            return {'hour': hour, 'minute': minute}
        
        # 24-hour format: 18:00, 9:30
        match = re.search(r'(\d{1,2}):(\d{2})', text)
        if match:
            return {'hour': int(match.group(1)), 'minute': int(match.group(2))}
        
        return None
    
    def extract_schedule(self, text: str):
        if not text:
            return 'manual', None

        t = text.lower().strip()

        # --- DAILY ---
        if "daily" in t or "everyday" in t or "every day" in t:
            return "daily", {'hour': 9, 'minute': 0}

        # --- HOURLY ---
        if "every hour" in t or "hourly" in t:
            return "every_hour", None

        # --- MINUTE ---
        if "every minute" in t:
            return "every_minute", None

        # --- WEEKLY ---
        days = [
            "monday", "tuesday", "wednesday",
            "thursday", "friday", "saturday", "sunday"
        ]

        for day in days:
            if f"every {day}" in t or day in t:
                return f"every_{day}", {'hour': 9, 'minute': 0}

        return 'manual', None
    
    def extract_category(self, text: str) -> str:
        """Extract news category"""
        text_lower = text.lower()
        
        if 'tech' in text_lower or 'technology' in text_lower:
            return 'technology'
        elif 'business' in text_lower or 'finance' in text_lower:
            return 'business'
        elif 'sports' in text_lower or 'khel' in text_lower:
            return 'sports'
        elif 'entertainment' in text_lower or 'bollywood' in text_lower:
            return 'entertainment'
        elif 'health' in text_lower:
            return 'health'
        elif 'science' in text_lower:
            return 'science'
        else:
            return 'technology'  # default
    
    def extract_country(self, text: str) -> str:
        """Extract country preference"""
        text_lower = text.lower()
        
        if 'india' in text_lower or 'indian' in text_lower or 'bharat' in text_lower:
            return 'in'
        elif 'us' in text_lower or 'america' in text_lower or 'usa' in text_lower:
            return 'us'
        elif 'uk' in text_lower or 'britain' in text_lower:
            return 'gb'
        elif 'canada' in text_lower:
            return 'ca'
        else:
            return 'in'  # default
    
    def extract_folder(self, text: str) -> str:
        """Extract folder name"""
        text_lower = text.lower()
        
        if 'download' in text_lower:
            return 'Downloads'
        elif 'document' in text_lower:
            return 'Documents'
        elif 'desktop' in text_lower:
            return 'Desktop'
        elif 'picture' in text_lower or 'image' in text_lower or 'photo' in text_lower:
            return 'Pictures'
        else:
            return 'Downloads'  # default
    
    def extract_file_pattern(self, text: str) -> str:
        """Extract file pattern"""
        text_lower = text.lower()
        
        if 'pdf' in text_lower:
            return '*.pdf'
        elif 'image' in text_lower or 'photo' in text_lower or 'picture' in text_lower:
            return '*.jpg,*.png,*.jpeg,*.gif'
        elif 'video' in text_lower:
            return '*.mp4,*.avi,*.mkv,*.mov'
        elif 'document' in text_lower or 'doc' in text_lower:
            return '*.doc,*.docx,*.txt,*.xlsx'
        else:
            return '*'  # all files
    
    def build_config(self, workflow_type: str, text: str) -> Dict:
        """Build workflow config based on type"""
        config = {}
        
        if workflow_type == 'NEWS_DIGEST':
            email = self.extract_email(text)
            numbers = self.extract_numbers(text)
            
            config['email'] = email or 'demo@uaos.com'
            config['category'] = self.extract_category(text)
            config['country'] = self.extract_country(text)
            config['limit'] = numbers[0] if numbers and numbers[0] <= 50 else 10
        
        elif workflow_type == 'FILE_CLEANUP':
            config['folder'] = self.extract_folder(text)
            config['file_pattern'] = self.extract_file_pattern(text)
            
            # Detect action
            if 'organize' in text.lower():
                config['action'] = 'organize'
                config['organize_by_type'] = True
            elif 'rename' in text.lower():
                config['action'] = 'rename'
                config['rename_pattern'] = 'date_title'
            else:
                config['action'] = 'both'
                config['rename_pattern'] = 'date_title'
        
        elif workflow_type == 'INVOICE_SYNC':
            config['gmail_filter'] = 'invoice OR receipt OR bill'
            config['drive_folder'] = 'Invoices'
        
        return config
    
    def parse(self, raw_text: str) -> Tuple[str, Dict, str, float]:
        """
        Main parsing function
        Returns: (workflow_type, config, schedule, confidence)
        """
        # Classify intent
        workflow_type, confidence = self.classify_intent(raw_text)
        
        # Extract schedule
        schedule_str, time_info = self.extract_schedule(raw_text)
        
        # Build config
        config = self.build_config(workflow_type, raw_text)
        
        # Add time info to config if available
        if time_info:
            config['time_info'] = time_info
        
        logger.info(f"Parsed: {workflow_type} | Schedule: {schedule_str} | Confidence: {confidence:.2f}")
        
        return workflow_type, config, schedule_str, confidence
    
    def get_workflow_description(self, workflow_type: str, config: Dict) -> str:
        """
        Generate human-readable description of what the workflow will do
        """
        if workflow_type == 'NEWS_DIGEST':
            category = config.get('category', 'technology')
            limit = config.get('limit', 10)
            email = config.get('email', 'user')
            return f"Send top {limit} {category} news to {email}"
        
        elif workflow_type == 'FILE_CLEANUP':
            folder = config.get('folder', 'Downloads')
            pattern = config.get('file_pattern', '*')
            return f"Organize {pattern} files in {folder} folder"
        
        elif workflow_type == 'INVOICE_SYNC':
            return "Sync invoices from Gmail to Google Drive"
        
        else:
            return "Manual workflow (no automation)"


# Singleton instance
advanced_parser = AdvancedIntentParser()


def parse_task_intent_v2(raw_text: str) -> Tuple[str, Dict, str, float]:
    """
    Helper function to use advanced parser
    """
    return advanced_parser.parse(raw_text)
