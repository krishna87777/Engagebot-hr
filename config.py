import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask settings
    DEBUG = True
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret")
    PORT = int(os.getenv("PORT", 5000))

    # Gemini 1.5 Flash API
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    # Remove "models/" prefix as the library adds this automatically
    GEMINI_MODEL_NAME = 'gemini-1.5-flash-latest'  # Changed from 'models/gemini-1.5-flash-latest'

    # Usage limits for free tier (adjust if needed)
    GEMINI_MAX_TOKENS = 1024  # Free tier often limits this
    GEMINI_TEMPERATURE = 0.7  # Controls randomness
    GEMINI_TOP_P = 1.0        # Sampling parameter

    # Uploads
    UPLOAD_FOLDER = os.path.join('static', 'uploads')  # Fixed path to match app.py
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))  # 16MB
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}