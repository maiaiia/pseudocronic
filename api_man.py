import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

print("Checking available Gemini models...\n")

# List all models
models = genai.list_models()

for m in models:
    # Filter to text/chat capable models
    if "generateContent" in m.supported_generation_methods:
        print(f"✅ {m.name}")
