import os
from dotenv import load_dotenv
from google import genai

# Base Directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")

# Load .env
load_dotenv(ENV_PATH)

API_KEY = os.getenv("GEMINI_API_KEY")

print("API KEY FOUND:", API_KEY is not None)

# Gemini Client
client = genai.Client(api_key=API_KEY)


def generate_ai_summary(summary):

    if not API_KEY:
        print("\nGemini API Key not found.")
        return summary

    prompt = f"""
You are a Business Data Analyst.

Below is a business report:

{summary}

Generate a professional business insight.

Include:
1. Overall Business Performance
2. Sales Analysis
3. Profit Analysis
4. Anomaly Impact
5. Recommendations

Keep it under 200 words.
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt,
        )

        ai_summary = response.text

        print("\n========== GEMINI AI SUMMARY ==========\n")
        print(ai_summary)

        os.makedirs("reports", exist_ok=True)

        with open(
            "reports/ai_summary.txt",
            "w",
            encoding="utf-8"
        ) as f:
            f.write(ai_summary)

        print("\nAI Summary Saved Successfully!")

        return ai_summary

    except Exception as e:

        print("\nGemini Error:", e)
        return summary
