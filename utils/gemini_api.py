import os
import json
import re
import logging
import google.generativeai as genai
from config import Config

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class GeminiAPI:
    """Handles interactions with Google's Gemini API"""

    def __init__(self):
        """Initialize the Gemini API with configuration"""
        try:
            # Get API key from Config, which should load from environment variables
            api_key = Config.GEMINI_API_KEY

            if not api_key or api_key == "my_gemini_key" or api_key == "your-api-key-here":
                logger.error("Invalid or missing Gemini API key. Please set a valid key in your .env file.")
                raise ValueError("Invalid Gemini API key configuration")

            # Configure the Gemini client
            genai.configure(api_key=api_key)

            # Initialize the model with configuration
            self.model = genai.GenerativeModel(
                model_name=Config.GEMINI_MODEL_NAME,
                generation_config={
                    "temperature": Config.GEMINI_TEMPERATURE,
                    "top_p": Config.GEMINI_TOP_P,
                    "max_output_tokens": Config.GEMINI_MAX_TOKENS
                }
            )

            logger.info(f"Gemini API initialized with model: {Config.GEMINI_MODEL_NAME}")

        except Exception as e:
            logger.error(f"Failed to initialize Gemini API: {str(e)}")
            raise

    def analyze_resume(self, resume_text: str, job_description: str) -> dict:
        """
        Analyze a resume against a job description

        Args:
            resume_text (str): The text content of the resume
            job_description (str): The job description to match against

        Returns:
            dict: Analysis results with match scores and recommendations
        """
        # Truncate inputs if they're too long
        max_length = 30000  # Safety limit
        if len(resume_text) > max_length:
            logger.warning(f"Resume text truncated from {len(resume_text)} to {max_length} characters")
            resume_text = resume_text[:max_length] + "... [truncated]"

        if len(job_description) > max_length:
            logger.warning(f"Job description truncated from {len(job_description)} to {max_length} characters")
            job_description = job_description[:max_length] + "... [truncated]"

        prompt = f"""
You are an AI HR assistant specialized in resume screening. Analyze the resume text and job description below.

Job Description:
{job_description}

Resume:
{resume_text}

Provide a comprehensive analysis in JSON format with the following structure:
{{
    "match_score": 85,  // Overall match score from 0-100
    "skills_matched": ["Python", "TensorFlow", "Data Analysis"],  // List of matched skills
    "skills_missing": ["AWS", "Kubernetes"],  // List of required skills missing from resume
    "experience_match": true,  // Boolean indicating if experience level matches
    "education_match": true,  // Boolean indicating if education requirements match
    "key_strengths": ["Strong ML background", "3 years in similar role"],  // Key strengths relevant to the position
    "improvement_areas": ["Could benefit from cloud certification"],  // Areas for improvement
    "recommendation": "Strong candidate for interview"  // Overall recommendation
}}

Be objective and thorough in your analysis. Focus specifically on the alignment between the resume and the job requirements.
        """

        try:
            logger.info("Sending request to Gemini API for resume analysis")
            response = self.model.generate_content(prompt)

            if not hasattr(response, 'text'):
                logger.error("Invalid response format from Gemini API - missing text attribute")
                return {"error": "Invalid API response format", "status": "failed"}

            logger.info("Successfully received response from Gemini API")
            return self._safe_json_parse(response.text)

        except Exception as e:
            logger.error(f"Error during resume analysis API call: {str(e)}")
            return {"error": f"API error: {str(e)}", "status": "failed"}

    def analyze_sentiment(self, feedback_text: str) -> dict:
        """
        Analyze employee feedback text for sentiment and attrition risk

        Args:
            feedback_text (str): The employee feedback text

        Returns:
            dict: Analysis results with sentiment scores and recommendations
        """
        # Truncate input if it's too long
        max_length = 30000  # Safety limit
        if len(feedback_text) > max_length:
            logger.warning(f"Feedback text truncated from {len(feedback_text)} to {max_length} characters")
            feedback_text = feedback_text[:max_length] + "... [truncated]"

        prompt = f"""
You are an AI HR analyst specialized in sentiment analysis. Analyze the employee feedback below.

Employee Feedback:
{feedback_text}

Provide a comprehensive analysis in JSON format with the following structure:
{{
    "sentiment_score": 0.75,  // Overall sentiment from -1 (negative) to 1 (positive)
    "attrition_risk": "Low",  // Attrition risk: Low, Medium, or High
    "key_concerns": ["Work-life balance", "Limited growth opportunities"],  // Main concerns identified
    "positive_factors": ["Team collaboration", "Company culture"],  // Positive aspects mentioned
    "satisfaction_areas": {{  // Ratings from 1-10 in key satisfaction areas
        "compensation": 7,
        "work_environment": 8,
        "management": 6,
        "career_growth": 4,
        "work_life_balance": 5
    }},
    "engagement_recommendations": [  // Recommended actions to improve engagement
        "Provide more career development opportunities",
        "Address concerns about work-life balance"
    ],
    "summary": "Generally positive feedback with specific concerns about career growth."  // Brief summary
}}

Be objective and detailed in your analysis. Focus on detecting both explicit and implicit signals of satisfaction or dissatisfaction.
IMPORTANT: Always provide at least 3 engagement_recommendations, even if the feedback is very positive.
        """

        try:
            logger.info("Sending request to Gemini API for sentiment analysis")
            response = self.model.generate_content(prompt)

            if not hasattr(response, 'text'):
                logger.error("Invalid response format from Gemini API - missing text attribute")
                return {"error": "Invalid API response format", "status": "failed"}

            logger.info("Successfully received response from Gemini API")
            result = self._safe_json_parse(response.text)

            # Ensure engagement_recommendations are always present
            if "engagement_recommendations" not in result or not result["engagement_recommendations"]:
                result["engagement_recommendations"] = [
                    "Conduct regular check-ins to maintain employee satisfaction",
                    "Continue reinforcing positive aspects of workplace culture",
                    "Consider implementing a formal recognition program"
                ]

            return result

        except Exception as e:
            logger.error(f"Error during sentiment analysis API call: {str(e)}")
            return {"error": f"API error: {str(e)}", "status": "failed"}

    def _safe_json_parse(self, text):
        """
        Safely parse JSON from LLM responses, handling various edge cases

        Args:
            text (str): The text response from the API

        Returns:
            dict: Parsed JSON object or error message
        """
        if not text or not isinstance(text, str):
            logger.error(f"Invalid text input for JSON parsing: {type(text)}")
            return {"error": "Empty or invalid response text", "status": "failed"}

        # Log a sample of the response for debugging
        preview = text[:100] + ("..." if len(text) > 100 else "")
        logger.info(f"Parsing API response text (preview): {preview}")

        try:
            # First try direct JSON parsing
            return json.loads(text)
        except json.JSONDecodeError:
            # If that fails, try to extract JSON using regex
            try:
                # Look for content between curly braces (including nested braces)
                matches = re.search(r'(\{(?:[^{}]|(?:\{(?:[^{}]|(?:\{[^{}]*\}))*\}))*\})', text, re.DOTALL)
                if matches:
                    json_text = matches.group(1)
                    return json.loads(json_text)
                else:
                    # Try to find JSON-like content with markdown code block syntax
                    matches = re.search(r'```(?:json)?(.*?)```', text, re.DOTALL)
                    if matches:
                        json_text = matches.group(1).strip()
                        return json.loads(json_text)
                    else:
                        logger.error("Failed to find valid JSON structure in response")
                        return {
                            "error": "Failed to parse JSON from API response",
                            "raw_response": text.strip(),
                            "status": "failed"
                        }
            except Exception as e:
                logger.error(f"Error in JSON extraction and parsing: {str(e)}")
                return {
                    "error": f"JSON parsing error: {str(e)}",
                    "raw_response": text.strip(),
                    "status": "failed"
                }