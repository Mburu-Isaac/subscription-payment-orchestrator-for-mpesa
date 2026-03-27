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

def generate_subscription_fingerprint(
  user_id,
  service_name,
  payment_type,
  account_number,
  paybill_number,
  till_number
):
  payment_target = account_number or paybill_number or till_number

  identity = f"{user_id}:{service_name}:{payment_type}:{payment_target}"
  fingerprint = sha256(identity.encode()).hexdigest()

  return fingerprint


def generate_service_fingerprint():
  pass

