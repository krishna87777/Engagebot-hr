# EngageBot-HR: Resume Analyzer & Employee Sentiment Analysis

EngageBot-HR is a comprehensive HR assistance tool that offers two primary functionalities:

* **Resume Screening**: Analyzes resumes against job descriptions to identify matching skills and qualifications.
* **Employee Sentiment Analysis**: Evaluates employee feedback to measure sentiment and identify attrition risks.

---

## Features

### Resume Screening Module

* Extract text from multiple file formats (PDF, DOCX, TXT, images)
* Advanced OCR capabilities using EasyOCR
* AI-powered analysis using Google's Gemini API
* Skill matching against job descriptions
* Match scoring and candidate recommendations

### Employee Sentiment Analysis

* Analysis of feedback text using Gemini API and NLTK
* Sentiment scoring and interpretation
* Attrition risk assessment
* Key concern identification
* Customized engagement recommendations

---

## Technology Stack

* **Backend**: Python, Flask
* **Frontend**: HTML, CSS, JavaScript
* **AI/ML**: Google Gemini API, NLTK
* **Text Processing**: PyMuPDF, PyPDF2, python-docx, EasyOCR
* **Containerization**: Docker

---

## Project Structure

```
EngageBot-HR/
├── static/
│   ├── css/
│   │   ├── animation.css
│   │   ├── sentiment-analysis.css
│   │   └── style.css
│   ├── images/
│   │   ├── background.jpg
│   │   ├── icons/
│   │   └── logo.png
│   ├── js/
│   │   ├── main.js
│   │   ├── resume-screening.js
│   │   └── sentiment-analysis.js
│   ├── results/
│   └── uploads/
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── resume_screening.html
│   └── sentiment_analysis.html
├── utils/
│   ├── __init__.py
│   ├── gemini_api.py
│   ├── resume_processor.py
│   └── sentiment_analyzer.py
├── .dockerignore
├── .env
├── .gitignore
├── app.py
├── config.py
├── Dockerfile
├── requirements.txt
└── test_gemini_api.py
```

---

## Installation & Setup

### Prerequisites

* Python 3.8+
* Google Gemini API key

### Local Installation

```bash
git clone https://github.com/krishna87777/Engagebot-hr
cd EngageBot-HR

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install -r requirements.txt
```

Create a `.env` file with the following variables:

```
GEMINI_API_KEY=your_gemini_api_key
FLASK_ENV=development
DEBUG=True
PORT=5000
```

Run the application:

```bash
python app.py
```

Access the application at [http://localhost:5000](http://localhost:5000)

---

## Docker Deployment

### Build the Docker image

```bash
docker build -t engagebot-hr .
```

### Run the container

```bash
docker run -p 5000:5000 -e GEMINI_API_KEY=your_gemini_api_key engagebot-hr
```

---

## Azure Deployment

### Push to Azure Container Registry

```bash
az login
az acr login --name youracrname

docker tag engagebot-hr youracrname.azurecr.io/engagebot-hr:latest
docker push youracrname.azurecr.io/engagebot-hr:latest
```

### Deploy to Azure Container Instances

```bash
az container create \
    --resource-group YourResourceGroup \
    --name engagebot-hr-container \
    --image youracrname.azurecr.io/engagebot-hr:latest \
    --cpu 1 \
    --memory 1.5 \
    --registry-login-server youracrname.azurecr.io \
    --registry-username youracrname \
    --registry-password yourpassword \
    --dns-name-label engagebot-hr \
    --ports 80 \
    --environment-variables GEMINI_API_KEY=your_gemini_api_key
```

---

## Usage

### Resume Screening

1. Navigate to the **Resume Screening** page.
2. Upload a resume file (PDF, DOCX, TXT, or image).
3. Enter or paste the job description.
4. Click **Analyze Resume**.
5. View results including skills match, missing skills, and recommendations.

### Sentiment Analysis

1. Navigate to the **Sentiment Analysis** page.
2. Enter employee feedback text.
3. Click **Analyze Sentiment**.
4. View sentiment score, attrition risk, key concerns, and recommended actions.

---

## API Endpoints

* `POST /api/screen-resume`: Screen resume against job requirements
* `POST /api/analyze-sentiment`: Analyze employee feedback sentiment

---

## Acknowledgements

* [Google Gemini API](https://ai.google.dev/)
* [EasyOCR](https://github.com/JaidedAI/EasyOCR)
* [NLTK](https://www.nltk.org/)
