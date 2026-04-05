from .slugify_utils import slugify_object
from .email.templates import otp_email
from datetime import timedelta


def handle_otp_forwarding(
    user,
    otp_type,
    email
):

    otp_type_slug = slugify_object(otp_type)

    result = otp_email(
        user=user,
        otp_type=otp_type_slug,
        email=email,
        ttl=timedelta(minutes=5)
    )


    return result, otp_type_slug