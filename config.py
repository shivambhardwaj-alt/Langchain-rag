import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "ai_knowledge_studio")



LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")  
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))
GROQ_API_KEY = os.getenv("GROQ_API_KEY")  