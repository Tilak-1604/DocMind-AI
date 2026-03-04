import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
    DATABASE_URL= os.getenv("DATABASE_URL")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

settings = Settings()