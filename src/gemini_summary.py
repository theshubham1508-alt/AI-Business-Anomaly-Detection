import os
from dotenv import load_dotenv
from google import genai

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")

REPORTS_FOLDER = os.path.join(BASE_DIR, "reports")

load_dotenv(ENV_PATH)

API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY) if API_KEY else None


def generate_ai_summary(summary, dataset_name="dataset", strict=False):

    if not API_KEY or client is None:
        if strict:
            raise RuntimeError("GEMINI_API_KEY is not configured.")
        print("Gemini API Key not found.")
        return summary

    prompt = f"""
You are an expert Data Scientist and Business Analyst.

Analyze this dataset report:

{summary}

Instructions:
- Understand the actual dataset columns.
- Do not assume specific columns.
- Do not invent information.
- Explain anomaly findings.
- Mention data quality issues where visible.

Include:
1. Dataset Overview
2. Important Insights
3. Numerical and Categorical Analysis
4. Anomaly Findings
5. Potential Risks
6. Recommendations
7. Conclusion

Keep the report under 300 words.
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt
        )

        ai_summary = response.text

        if not ai_summary:
            if strict:
                raise RuntimeError("Gemini returned an empty summary.")
            return summary

        print("\n========== GEMINI AI SUMMARY ==========")
        print(ai_summary)

        dataset_folder = os.path.join(
            REPORTS_FOLDER, dataset_name
        )

        os.makedirs(dataset_folder, exist_ok=True)

        ai_summary_file = os.path.join(
            dataset_folder, "ai_summary.txt"
        )

        with open(
            ai_summary_file,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(ai_summary)

        print("\nAI Summary Saved Successfully!")
        print(f"Location: {ai_summary_file}")

        return ai_summary

    except Exception as e:

        print("\nGemini Error:", e)
        if strict:
            raise RuntimeError(f"Gemini summary generation failed: {e}") from e
        return summary