import re

def normalize_name(name: str) -> str:
    """
    Normalizes a candidate's name by stripping excess whitespace and applying title casing.
    Returns the original value if it is empty.
    """
    if not name:
        return name
        
    # Replace multiple consecutive spaces with a single space and strip ends
    cleaned_name = re.sub(r'\s+', ' ', str(name)).strip()
    
    return cleaned_name.title()
