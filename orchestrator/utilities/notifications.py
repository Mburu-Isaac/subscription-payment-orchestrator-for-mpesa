from email.message import EmailMessage
import smtplib

from dotenv import load_dotenv
import os

load_dotenv()

def send_verification_email(otp,email):

    company_email = os.getenv("COMPANY_EMAIL")

    msg = EmailMessage()
    msg["From"] = f"Company Name <{company_email}>"
    msg["To"] = email
    msg["Subject"] = "OTP Verification"
    msg.set_content(
        f"""
            Dear Customer, 
            please use the following one time password to verify your email address:
            OTP: {otp}
            if you did not request the OTP please ignore this email.
        """
    )


    with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
        connection.starttls()
        connection.login(user=company_email, password=os.getenv("SMTP_EMAIL_PASSWORD"))
        connection.send_message(msg)

    return True

