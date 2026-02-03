def standardize_contact(phone_number):
    if phone_number.startswith("0"):
        return "254" + phone_number[1:]
    return phone_number