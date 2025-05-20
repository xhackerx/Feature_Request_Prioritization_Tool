from transformers import pipeline
import numpy as np
from collections import defaultdict
import re

class SentimentAnalyzer:
    def __init__(self):
        self.analyzer = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english"
        )
        self.aspect_keywords = {
            'usability': ['easy', 'intuitive', 'difficult', 'confusing', 'user-friendly'],
            'performance': ['fast', 'slow', 'responsive', 'laggy', 'efficient'],
            'reliability': ['stable', 'crash', 'bug', 'reliable', 'consistent'],
            'features': ['feature', 'functionality', 'capability', 'option', 'tool']
        }
    
    def analyze_feedback(self, feedback_text):
        """Analyze sentiment of a single feedback text"""
        # Clean text
        cleaned_text = self._preprocess_text(feedback_text)
        
        # Get overall sentiment
        sentiment_result = self.analyzer(cleaned_text)[0]
        
        # Analyze aspects
        aspect_sentiments = self._analyze_aspects(cleaned_text)
        
        return {
            'overall_sentiment': sentiment_result['label'],
            'confidence': sentiment_result['score'],
            'aspects': aspect_sentiments,
            'text': feedback_text,
            'key_phrases': self._extract_key_phrases(cleaned_text)
        }
    
    def batch_analyze(self, feedback_list):
        """Analyze multiple feedback items"""
        results = []
        for feedback in feedback_list:
            results.append(self.analyze_feedback(feedback))
        return results
    
    def _preprocess_text(self, text):
        """Clean and prepare text for analysis"""
        # Convert to lowercase
        text = text.lower()
        # Remove special characters
        text = re.sub(r'[^\w\s]', ' ', text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text
    
    def _analyze_aspects(self, text):
        """Analyze sentiment for different aspects of the feedback"""
        aspect_results = {}
        
        for aspect, keywords in self.aspect_keywords.items():
            # Find sentences containing aspect keywords
            relevant_text = ''
            for keyword in keywords:
                if keyword in text:
                    # Get surrounding context
                    pattern = f'.{{0,50}}{keyword}.{{0,50}}'
                    matches = re.finditer(pattern, text)
                    relevant_text += ' '.join([m.group() for m in matches])
            
            if relevant_text:
                sentiment = self.analyzer(relevant_text)[0]
                aspect_results[aspect] = {
                    'sentiment': sentiment['label'],
                    'confidence': sentiment['score']
                }
        
        return aspect_results
    
    def _extract_key_phrases(self, text, min_words=2, max_words=5):
        """Extract important phrases from the feedback"""
        # Simple key phrase extraction based on word combinations
        words = text.split()
        phrases = []
        
        for i in range(len(words)):
            for j in range(min_words, max_words + 1):
                if i + j <= len(words):
                    phrase = ' '.join(words[i:i+j])
                    phrases.append(phrase)
        
        # Filter and score phrases
        scored_phrases = []
        for phrase in set(phrases):
            score = self._score_phrase(phrase)
            if score > 0.3:  # Threshold for significance
                scored_phrases.append({
                    'phrase': phrase,
                    'score': score
                })
        
        return sorted(scored_phrases, key=lambda x: x['score'], reverse=True)[:5]
    
    def _score_phrase(self, phrase):
        """Score a phrase based on its potential importance"""
        # Simple scoring based on word significance
        words = phrase.split()
        score = 0
        
        # Bonus for phrases with aspect keywords
        for aspect_words in self.aspect_keywords.values():
            if any(word in phrase for word in aspect_words):
                score += 0.3
        
        # Bonus for proper length
        if 2 <= len(words) <= 4:
            score += 0.2
        
        return score