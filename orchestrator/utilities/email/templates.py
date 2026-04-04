from .service import send_company_email
from orchestrator.utilities.otps import generate_otp
from orchestrator.models import OTP
from orchestrator.extensions import db
from werkzeug.security import generate_password_hash
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

# combine sign up verification email with an OTP

def otp_email(
    user,
    otp_type,
    email,
    ttl
):

    # purpose: verify the user's identity or email for a specific action
    # use case 1: Email verification on signup
    # use case 2: Two-factor authentication - authentication during login 
                    # after login, server sends OTP 
                        #  user enters OTP
                            # if correct, access granted
    # use case 3: Transaction verification
                    # OTP confirms a sensitive action - payment, password change
                        # password change request/ payment triggered -> OTP generated -> email sent
                            # -> user sends OTP -> if OTP entered is correct
                                # -> direct to password change/ authorize transaction


    otp = generate_otp()

    expires_at = datetime.now(timezone.utc) + ttl

    # Kenyan timezone
    kenyan_expiry = expires_at.astimezone(ZoneInfo("Africa/Nairobi"))

    otp_record = OTP(
        user_id=user.id,
        hashed_otp=generate_password_hash(otp),
        otp_type=otp_type,
        expires_at=expires_at,
        attempts_left=3
    )

    try:
        db.session.add(otp_record)
        db.session.commit()


        message = f"""
                        Dear Customer, 
                        please use the following one time password to verify your email address:
                        OTP: {otp}
                        if you did not request the OTP please ignore this email.
                    """

        html_body = f"""
                    <html>
                        <body>
                            <p> Dear Customer, </p>
                            <p> Please use the following one time password to verify your email address: </p>

                            <h2> OTP: {otp} </h2> # add css styling

                            <p>

                                This OTP code will expire at <strong> { kenyan_expiry.strftime("%H:%M EAT") } </strong>

                            </p>

                            <p> if you did not request the OTP please ignore this email. </p>

                            <p> 
                                Regards, 
                                <br>
                                ETERNITY 
                            </p>
                    </body>
                    </html>
        """

        send_company_email(
            to_email=email,
            subject="OTP Verification",  # work with token type
            body=message,
            html_body=html_body
        )

        return {
            "success":True,
            "otp":otp,
            "message":"OTP sent successfully"
        }

    except Exception as error:
        db.session.rollback()
        return {
            "success":False,
            "error": str(error)
        }



# verify OTP -> if OTP matches -> move on to email verification -> after both, verify user

def verification_email(
    email,
    user
):
    # purpose: confirm that the email address belongs to the user and is valid 
    # flow:
        # user signs up -> submits email -> server generates unique verification code 
            # -> function sends verification link containing the token ->
                # user clicks the link -> server verifies the token -> marks email as confirmed 

    pass


def password_reset_email(email, reset_token):
    # purpose: allow the user to reset their password securely
    # flow:
        # user clicks "forgot password" -> server generates a reset token - JWT 
            # -> server sends a link with the token -> user clicks the link 
                # -> server verifies token -> direct to password reset - user sets new password

    # reset time - provide reset at 

    reset_link = f"https://yourdomain.com/account-recovery?token={reset_token}"

    subject = "Password Reset Request"

    message = f"""
        Dear Customer,

        You requested a password reset.

        Please use the following link to reset your password:

        {reset_link}

        This link will expire in 30 minutes.

        if you did not request this password reset, please ignore this email.

        Regards,
        ETERNITY
    
    """

    html_body = f"""

        <html>
            <body>

                <p>Dear Customer,</p>

                <p>You requested a password reset.</p>

                <p>Click the button below to reset your password:</p>

                <p>   
                    <a href="{reset_link}"
                       style="background-color:#4CAF50;
                            color:white;
                            padding:12px 20px;
                            text-decoration:none;
                            border-radius:5px;">
                        Reset Password
                    </a>
                </p>

                <p> This link expires at <strong> "time the link will expired". </strong> </p>

                <p>If you did not request this password reset, please ignore this email.</p>

                <p>
                    Regards,
                    <br>
                    ETERNITY
                </p>
            </body>
        </html>
    """

    return send_company_email(
        to_email=email,
        subject=subject,
        body=message,
        html_body=html_body
    )






























# email_service.py
    # send_email()

# email/
    # otp_email()
    # verification_email()
    # password_reset_email()


