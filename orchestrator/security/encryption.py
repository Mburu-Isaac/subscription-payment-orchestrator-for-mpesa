from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os

load_dotenv()

fernet = Fernet(os.getenv("CONTACT_ENCRYPTION_KEY"))

def encrypt_contact(phone_number: str) -> bytes:
    return fernet.encrypt(phone_number.encode())

def decrypt_contact(encrypted_number: bytes) -> str:
    return fernet.decrypt(encrypted_number).decode()