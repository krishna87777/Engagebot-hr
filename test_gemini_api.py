# test_gemini_api.py
import os
from dotenv import load_dotenv
import google.generativeai as genai
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")  # Note: Using GEMINI_API_KEY from your config


def test_api_connection():
    try:
        # Configure the Gemini API
        genai.configure(api_key=api_key)

        # List available models first (helpful for debugging)
        models = genai.list_models()
        model_names = [model.name for model in models]
        print("Available models:", model_names)

        # Use the correct model name format from your Config
        # The issue is likely in the model name format - removing "models/" prefix
        model_name = "gemini-1.5-flash-latest"  # Using from your config but without "models/" prefix

        model = genai.GenerativeModel(model_name)

        # Test with a simple prompt
        response = model.generate_content("Say hello")

        print("API Connection Successful!")
        print(f"Response: {response.text}")
        return True

    except Exception as e:
        print(f"API Connection Failed: {str(e)}")
        return False


if __name__ == "__main__":
    test_api_connection()