import os
from crewai import LLM
from dotenv import load_dotenv

load_dotenv(r'D:\vector_databse\.env')

try:
    llm = LLM(
        model="gemini/gemini-1.5-flash",
        api_key=os.getenv("GOOGLE_API_KEY"),
    )
    print("LLM init success")
except Exception as e:
    print(f"Error: {e}")
