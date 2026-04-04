from flask_login import login_user
from flask import redirect, url_for

def log_in_user(user_object):
    login_user(user=user_object)
    return redirect(
        url_for(
            "main.index_page"
        )
    )