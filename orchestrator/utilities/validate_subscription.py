def subscription_validation(
    service_name,
    next_payment_str,
    payment_type,
    till_number,
    paybill_number,
    account_number,
    amount,
    frequency,
    form_data
):

    if not service_name:
        return "service name required"

    if not next_payment_str:
        return "payment date is required"

    if payment_type == "Till Number":

        if not till_number:
            return "till number is required for this payment service"

        if paybill_number or account_number:
            return "till number payment only requires till numbers; not paybill or account numbers."

    if payment_type == "Paybill":

        if till_number:
            if till_number is None:
                till_number = ""
            return "till numbers are not applicable for the paybill payment service"

        
        if not paybill_number or not account_number:
            return "paybill and account numbers are required for the paybill payment service"

    if not amount:
        return "amount definition required"

    return None

