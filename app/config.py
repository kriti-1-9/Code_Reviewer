import os
from dotenv import load_dotenv

load_dotenv()

GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "")
GCP_LOCATION = os.getenv("GCP_LOCATION", "us-central1")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
FIRESTORE_COLLECTION = os.getenv("FIRESTORE_COLLECTION", "code_reviews")
API_KEY = os.getenv("API_KEY", "dev-key")