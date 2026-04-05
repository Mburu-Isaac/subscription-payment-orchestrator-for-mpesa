from flask_login import login_user
from flask import redirect, url_for, flash

def log_in_user(user_object):
    user_logged_in = login_user(user=user_object)

    if user_logged_in:
        return redirect(
            url_for(
                "main.index_page"
            )
        )

    else:
        return None


def authenticaticate_otp(result, user):
    
    otp_forwarding = result[0]

    if otp_forwarding["success"]:
        flash(otp_forwarding.get("message"), "success")
        return redirect(
            url_for(
                "auth.otp_verification",
                slug=user.slug,
                otp_type=result[1]
            )
        )

    else:
        flash(otp_forwarding.get("error"), "error")
        return redirect(
            url_for(
                "auth.signup"
            )
        )