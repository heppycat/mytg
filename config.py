from dotenv import load_dotenv
import os

load_dotenv()

API_ID: int = int(os.environ["API_ID"])
API_HASH: str = os.environ["API_HASH"]
SESSION_STRING: str = os.environ.get("SESSION_STRING", "")
