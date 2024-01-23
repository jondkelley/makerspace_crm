import re

# from helpers.datehelper import validate_date_time_format

def validate_date_time_format(date_time_str):
    # Example usage
    # event_dt = '2024-01-22 15:30:00'
    # if validate_date_time_format(event_dt):
    #     print("Format is correct.")
    # else:
    #     print("Format is incorrect.")
    pattern = r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$'
    if re.match(pattern, date_time_str):
        return True
    else:
        return False
