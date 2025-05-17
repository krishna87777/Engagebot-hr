from flask import Flask, render_template, request, jsonify
import os
from utils.resume_processor import ResumeProcessor
from utils.sentiment_analyzer import SentimentAnalyzer
from config import Config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

app = Flask(__name__)
app.config.from_object(Config)

# Initialize services
# No need to pass parameters as they handle their own initialization
resume_processor = ResumeProcessor()
sentiment_analyzer = SentimentAnalyzer()

# Ensure upload directory exists with correct path from config
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    """Render the home page"""
    return render_template('index.html')


@app.route('/resume-screening')
def resume_screening():
    """Render the resume screening page"""
    return render_template('resume_screening.html')


@app.route('/sentiment-analysis')
def sentiment_analysis():
    """Render the sentiment analysis page"""
    return render_template('sentiment_analysis.html')


@app.route('/api/screen-resume', methods=['POST'])
def screen_resume():
    """API endpoint to screen resume against job requirements"""
    if 'resume' not in request.files:
        return jsonify({'error': 'No resume file provided'}), 400

    resume_file = request.files['resume']
    job_description = request.form.get('job_description', '')

    if resume_file.filename == '':
        return jsonify({'error': 'No resume file selected'}), 400

    if not job_description:
        return jsonify({'error': 'Job description is required'}), 400

    # Check if the file extension is allowed
    file_ext = os.path.splitext(resume_file.filename)[1].lower()
    if file_ext[1:] not in Config.ALLOWED_EXTENSIONS:
        return jsonify({'error': f'File type {file_ext} not allowed. Please upload PDF, DOCX, TXT, or common image files.'}), 400

    try:
        # Process the resume
        app.logger.info(f"Processing resume: {resume_file.filename}")
        results = resume_processor.process(resume_file, job_description)
        if results and 'error' in results:
            app.logger.error(f"Resume processing returned error: {results['error']}")
            return jsonify(results), 500
        return jsonify(results)
    except Exception as e:
        app.logger.error(f"Resume processing error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/analyze-sentiment', methods=['POST'])
def analyze_sentiment():
    """API endpoint to analyze employee feedback and sentiment"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON data provided'}), 400

    feedback = data.get('feedback', '')

    if not feedback:
        return jsonify({'error': 'Employee feedback is required'}), 400

    try:
        # Analyze the sentiment
        app.logger.info("Processing sentiment analysis request")
        results = sentiment_analyzer.analyze(feedback)
        if results and 'error' in results:
            app.logger.error(f"Sentiment analysis returned error: {results['error']}")
            return jsonify(results), 500
        return jsonify(results)
    except Exception as e:
        app.logger.error(f"Sentiment analysis error: {str(e)}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Ensure the static folders exist
    for folder in ['uploads', 'results']:
        os.makedirs(os.path.join('static', folder), exist_ok=True)

    app.logger.info(f"Starting Flask application on port {Config.PORT}")
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=Config.PORT)