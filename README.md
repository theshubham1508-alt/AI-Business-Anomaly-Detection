Anomaly Intelligence

AI-Powered Business Anomaly Detection & Intelligence Platform

Live Demo Python Flask GitHub

Live Demo: https://ai-business-anomaly-detection.onrender.com

Table of Contents
Overview
Objectives
Key Features
Technology Stack
Machine Learning Methodology
Results
Project Structure
Installation & Local Setup
Environment Variables
Deployment
Testing
Limitations
Future Enhancements
Author
Overview

Anomaly Intelligence is a web-based business analytics platform that analyzes business datasets, detects unusual patterns and transactions, generates interactive visualizations, and produces AI-driven business insights.

It combines Python-based data analytics, machine learning (Isolation Forest), a Flask web application, interactive dashboards, and Google Gemini AI in a single, centralized interface.

Objectives
Identify unusual business transactions and patterns.
Clean and preprocess raw business datasets.
Perform Exploratory Data Analysis (EDA).
Detect anomalies using the Isolation Forest algorithm.
Provide interactive analytics dashboards.
Generate AI-powered business summaries with Google Gemini.
Export downloadable analytical reports.
Key Features
Module	Description
Overview Dashboard	Business performance overview, key metrics, and anomaly insights.
Dataset Explorer	Upload CSV files; inspect records, numeric/categorical features, missing values, and duplicates.
Data Cleaning	Automated preprocessing, missing-value and duplicate handling, cleaned dataset generation.
EDA Dashboard	Statistical analysis, business performance analysis, and interactive charts.
ML Anomaly Detection	Isolation Forest–based identification and classification of unusual transactions.
Gemini AI Intelligence	AI-generated summaries, evidence-based findings, and business recommendations.
Reports Center	Download cleaned data, anomaly reports, summaries, PDF reports, and visualizations.
Email Integration	Report delivery via Gmail SMTP with environment-based credentials.

Available report formats: Cleaned Dataset (CSV) · Anomalies Report (CSV) · Analysis Summary (TXT) · Analysis Report (PDF) · Generated Visualizations

Note: Gemini features require a valid GEMINI_API_KEY and available Google AI API quota. Email delivery requires valid SMTP credentials.

Technology Stack
Category	Technologies
Language	Python
Backend	Flask, Gunicorn
Data Processing	Pandas, NumPy
Machine Learning	Scikit-learn (Isolation Forest)
Visualization	Matplotlib, Seaborn, Plotly
Frontend	HTML, CSS, JavaScript
AI Integration	Google Gemini API
Email	Gmail SMTP
Deployment	Render
Version Control	Git & GitHub
Machine Learning Methodology

Anomalies are detected using Isolation Forest, an unsupervised algorithm that isolates records whose characteristics differ significantly from the rest of the dataset.

Parameter	Value
Estimators	100
Contamination	0.02
Random State	42
Jobs	-1 (all cores)

Output labels: 1 = Normal, -1 = Anomaly

Results
Superstore Dataset
Metric	Result
Total Records	9,994
Anomalies Detected	200
Total Sales	$2,297,200.86
Total Profit	$286,397.02
Average Sales	$229.86
Average Profit	$28.66
Web Application Validation

A separate dataset was uploaded to validate the end-to-end workflow.

Metric	Result
Total Records	505
Features	11
Missing Values	0
Duplicate Rows	0
Flagged Anomalies	11

Results vary with the selected dataset and analysis configuration.

Project Structure
text
AI-Business-Anomaly-Detection/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── data/
│   ├── raw/
│   └── processed/
├── src/
│   ├── main.py
│   ├── data_loader.py
│   ├── data_cleaning.py
│   ├── eda.py
│   ├── visualization.py
│   ├── anomaly_detection.py
│   ├── ai_summary.py
│   ├── gemini_summary.py
│   └── email_alert.py
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── dashboard.html
│   └── error.html
├── static/
│   ├── css/app.css
│   └── js/app.js
├── reports/
└── tests/
    └── test_web_app.py
Installation & Local Setup

Prerequisites: Python 3.12+ and Git.

bash
# 1. Clone the repository
git clone https://github.com/theshubham1508-alt/AI-Business-Anomaly-Detection.git
cd AI-Business-Anomaly-Detection

# 2. Create a virtual environment
python -m venv venv

# 3. Activate it (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the application
python app.py

Open http://127.0.0.1:5000 in your browser.

Environment Variables

Create a local .env file in the project root:

env
GEMINI_API_KEY=your_gemini_api_key

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_gmail_app_password

Security: Never commit your .env file, API keys, or passwords to GitHub. On Render, configure secrets under the service's Environment Variables settings.

Deployment

The application is deployed on Render and auto-deploys from the main branch.

Setting	Value
Platform	Render
Service Type	Web Service
Runtime	Python 3
Branch	main
Build Command	pip install -r requirements.txt
Start Command	gunicorn app:app
Plan	Free

Production URL: https://ai-business-anomaly-detection.onrender.com

Render Free services may sleep after inactivity (cold starts), and files stored on the instance's temporary filesystem may not persist across restarts or redeployments.

Testing

Run the automated test suite:

bash
python -m pytest tests/ -v

Manual testing has also covered CSV upload, dataset exploration, data analysis, anomaly detection, report generation and download, dashboard navigation, and cloud deployment.

Limitations
Gemini AI depends on Google API availability and quota.
Email delivery requires valid Gmail SMTP credentials.
Render Free Plan may cause cold starts.
Uploaded files are temporary and may not survive restarts.
Large datasets may exceed the memory of the free instance.
Future Enhancements
Persistent cloud storage.
Advanced anomaly detection models.
Expanded AI-powered business recommendations.
Real-time anomaly monitoring.
Support for additional dataset formats.
Advanced reporting and analytics.
Improved cloud infrastructure.
Author

Shubham Kumar B.Tech (Data Science) | Python | Data Analytics | Machine Learning | AI

GitHub: theshubham1508-alt

If you find this project useful, consider giving the repository a ⭐ on GitHub.
