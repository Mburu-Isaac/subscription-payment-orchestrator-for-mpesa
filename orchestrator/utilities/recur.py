from dateutil.relativedelta import relativedelta

def recur(base_date, frequency):
    if frequency == "Annually":
        return base_date + relativedelta(year=1)
    elif frequency == "Biannually":
        return base_date + relativedelta(months=6)
    elif frequency == "Monthly":
        return base_date + relativedelta(months=1)
    elif frequency == "Weekly":
        return base_date + relativedelta(weeks=1)
    elif frequency == "Daily":
        return base_date + relativedelta(days=1)