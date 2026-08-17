import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
REGION = os.getenv("REGION", "europe")
PLATFORM = os.getenv("PLATFORM", "euw1")
DRAGON_PATH = os.getenv("DRAGON_PATH")