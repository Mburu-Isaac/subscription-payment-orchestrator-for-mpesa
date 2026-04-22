from email.message import EmailMessage
from dotenv import load_dotenv
import smtplib
import os


load_dotenv()

def send_company_email(
    to_email,
    subject,
    body,
    company_name,
    html_body=None
):

    try:

        company_email = os.getenv("COMPANY_EMAIL")

        msg = EmailMessage()
        msg["From"] = f"{company_name} <{company_email}>" 
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.set_content(body)

        if html_body:
            msg.add_alternative(html_body, subtype="html")
    

        with smtplib.SMTP("smtp.gmail.com", port=int(os.getenv("SMTP_PORT"))) as connection:
            connection.starttls()
            connection.login(
                user=company_email,
                password=os.getenv("SMTP_EMAIL_PASSWORD")
            )
            connection.send_message(msg)

        return True

    except smtplib.SMTPAuthenticationError:
        print("SMTP authentication failed.")
        return False

    except smtplib.SMTPConnectError:
        print("Could not connect to SMTP server")
        return False

    except Exception as error:
        print(f"Email forwarding failed: {error}")
        return False


