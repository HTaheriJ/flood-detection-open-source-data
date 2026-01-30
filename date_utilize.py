import datetime

def get_date_ranges(event_date_str, post_lag, days_before_start=30, days_before_end=1):
    """
    Compute post-flood and reference date ranges from a flood event date.

    Args:
        event_date_str (str): Flood event date in 'YYYY-MM-DD' format.
        post_lag (int): Number of days after the flood to include in post-flood analysis.
        days_before_start (int, optional): Start of reference period (days before event). Default is 30.
        days_before_end (int, optional): End of reference period (days before event). Default is 1.

    Returns:
        (str, str, str, str): post_start_date, post_end_date, ref_start_date, ref_end_date
    """

    def parse(date_str):
        return datetime.datetime.strptime(date_str, '%Y-%m-%d')

    def format(date_obj):
        return date_obj.strftime('%Y-%m-%d')

    event_date = parse(event_date_str)

    # Post-flood range
    post_start_date = format(event_date + datetime.timedelta(days=1))
    post_end_date = format(event_date + datetime.timedelta(days=post_lag))

    # Reference range
    ref_start_date = format(event_date - datetime.timedelta(days=days_before_start))
    ref_end_date = format(event_date - datetime.timedelta(days=days_before_end))

    return post_start_date, post_end_date, ref_start_date, ref_end_date
