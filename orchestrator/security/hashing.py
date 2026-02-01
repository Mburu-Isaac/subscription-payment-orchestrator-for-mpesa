from hashlib import sha256
from argon2 import PasswordHasher
from dotenv import load_dotenv
import os

load_dotenv()

ph = PasswordHasher(
  time_cost=int(os.getenv("TIME_COST")),
  memory_cost=int(os.getenv("MEMORY_COST"))*1024,
  parallelism=int(os.getenv("PARALLELISM"))
)

def hash_email(email: str) -> str:
    return sha256(email.strip().lower().encode()).hexdigest()