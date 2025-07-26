# redis_client.py
import redis
import os
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")  # e.g., redis://default:pass@host:port/0

redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
