import re
from dateutil.parser import parse as parse_date

def normalize_date(date_str: str) -> str:
    """
    Normalizes a date string to YYYY-MM format.
    Explicitly preserves purely 4-digit years (YYYY).
    Returns the original string if parsing fails.
    """
    if not date_str:
        return date_str
        
    date_str_clean = str(date_str).strip()
    
    # If it's exactly a 4-digit year, preserve it without adding a month
    if re.match(r'^\d{4}$', date_str_clean):
        return date_str_clean
        
    try:
        parsed = parse_date(date_str_clean, fuzzy=False)
        return parsed.strftime("%Y-%m")
    except (ValueError, TypeError, OverflowError):
        pass
        
    return date_str_clean
