import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "ai_knowledge_studio")



llm_1 = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature= 0.3,
)

llm_2 = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.7,
)

llm_3 = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.5,
)

llm_4 = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.2,
) 
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))
GROQ_API_KEY = os.getenv("GROQ_API_KEY")  