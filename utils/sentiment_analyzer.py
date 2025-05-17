import re
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from collections import Counter
from utils.gemini_api import GeminiAPI

# Try to download NLTK data if not already present
try:
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')
    nltk.download('punkt')


class SentimentAnalyzer:
    """Class to handle employee sentiment analysis logic"""

    def __init__(self):
        """Initialize the sentiment analyzer with required components"""
        # Initialize our own Gemini API instance
        self.gemini_api = GeminiAPI()
        # Initialize NLTK's sentiment analyzer for backup/comparison
        self.nltk_sia = SentimentIntensityAnalyzer()

    def _extract_keywords(self, text, num_keywords=5):
        """Extract most frequent meaningful words as keywords"""
        # Simple stopwords list (can be expanded)
        stopwords = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves',
                     'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him',
                     'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its',
                     'itself', 'they', 'them', 'their', 'theirs', 'themselves',
                     'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those',
                     'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have',
                     'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an',
                     'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while',
                     'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between',
                     'into', 'through', 'during', 'before', 'after', 'above', 'below',
                     'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over',
                     'under', 'again', 'further', 'then', 'once', 'here', 'there',
                     'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each',
                     'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor',
                     'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very',
                     's', 't', 'can', 'will', 'just', 'don', 'should', 'now']

        # Clean text and tokenize
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())

        # Remove stopwords
        filtered_words = [word for word in words if word not in stopwords]

        # Count word frequencies
        freq = Counter(filtered_words)

        # Return top keywords
        return [word for word, count in freq.most_common(num_keywords)]

    def analyze(self, feedback_text):
        """
        Analyze employee feedback for sentiment and attrition risk

        Args:
            feedback_text (str): The employee feedback text

        Returns:
            dict: Analysis results
        """
        try:
            # Use the Gemini API for sentiment analysis
            results = self.gemini_api.analyze_sentiment(feedback_text)

            # Calculate backup sentiment score using NLTK
            nltk_scores = self.nltk_sia.polarity_scores(feedback_text)
            nltk_compound = nltk_scores['compound']

            # Extract keywords as a backup/enhancement
            keywords = self._extract_keywords(feedback_text)

            # Check if Gemini API returned proper results
            if isinstance(results, dict) and ('error' in results or 'sentiment_score' not in results):
                # Use NLTK as fallback
                sentiment_score = nltk_compound
                results = {
                    'sentiment_score': sentiment_score,
                    'attrition_risk': 'Medium',  # Default value
                    'key_concerns': keywords,
                    'positive_factors': [],
                    'engagement_recommendations': [
                        'Consider conducting a follow-up interview to gather more specific feedback.',
                        'Implement regular check-ins to maintain communication channels.',
                        'Review team dynamics and management practices.'
                    ]
                }
            elif not isinstance(results, dict):
                # If results is not a dictionary, create one
                sentiment_score = nltk_compound
                results = {
                    'sentiment_score': sentiment_score,
                    'attrition_risk': 'Medium',
                    'key_concerns': keywords,
                    'positive_factors': [],
                    'sentiment_analysis': results,  # Include the original analysis as a field
                    'engagement_recommendations': [
                        'Consider conducting a follow-up interview to gather more specific feedback.',
                        'Implement regular check-ins to maintain communication channels.',
                        'Review team dynamics and management practices.'
                    ]
                }
            else:
                sentiment_score = results.get('sentiment_score', nltk_compound)

            # Add interpretations of the sentiment score
            if sentiment_score >= 0.7:
                results['interpretation'] = 'Very Positive'
            elif sentiment_score >= 0.3:
                results['interpretation'] = 'Positive'
            elif sentiment_score >= -0.3:
                results['interpretation'] = 'Neutral'
            elif sentiment_score >= -0.7:
                results['interpretation'] = 'Negative'
            else:
                results['interpretation'] = 'Very Negative'

            # Ensure key_concerns and positive_factors exist
            if 'key_concerns' not in results:
                results['key_concerns'] = keywords
            if 'positive_factors' not in results:
                results['positive_factors'] = []

            # Ensure engagement_recommendations exist
            if 'engagement_recommendations' not in results or not results['engagement_recommendations']:
                # Default recommendations based on sentiment
                if sentiment_score >= 0.3:
                    results['engagement_recommendations'] = [
                        "Continue reinforcing positive workplace culture",
                        "Consider implementing a formal recognition program",
                        "Maintain current management practices that are working well"
                    ]
                elif sentiment_score >= -0.3:
                    results['engagement_recommendations'] = [
                        "Schedule regular feedback sessions to address potential concerns",
                        "Evaluate team communication processes for improvement opportunities",
                        "Consider workplace satisfaction surveys to identify specific areas for enhancement"
                    ]
                else:
                    results['engagement_recommendations'] = [
                        "Conduct one-on-one meetings to address specific concerns",
                        "Review management practices and team dynamics",
                        "Develop an action plan to address identified issues",
                        "Consider implementing additional support resources"
                    ]

            # Format recommendations for display
            results['recommendations'] = "\n• " + "\n• ".join(results['engagement_recommendations'])

            # Add text analysis metadata
            results["text_length"] = len(feedback_text)
            results["word_count"] = len(feedback_text.split())
            results["nltk_sentiment"] = nltk_compound
            results["keywords"] = keywords

            return results

        except Exception as e:
            # Provide default values in case of error
            return {
                "error": str(e),
                "status": "failed",
                "sentiment_score": 0,
                "interpretation": "Error",
                "attrition_risk": "Medium",
                "key_concerns": [],
                "positive_factors": [],
                "engagement_recommendations": [
                    "Error analyzing feedback. Please try again.",
                    "Consider conducting a manual review of this feedback.",
                    "Check system configuration if errors persist."
                ],
                "recommendations": "• Error analyzing feedback. Please try again.\n• Consider conducting a manual review of this feedback.\n• Check system configuration if errors persist.",
                "suggestion": "Please try again with different text or check if the Gemini API is functioning correctly."
            }