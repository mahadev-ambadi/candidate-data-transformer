import phonenumbers

def normalize_phone(phone: str, default_region: str = "IN") -> str:
    """
    Normalizes a phone number to E.164 format (e.g., +14155552671).
    Returns the original string if parsing or formatting fails, preserving data safety.
    """
    if not phone:
        return phone
        
    try:
        parsed = phonenumbers.parse(str(phone), default_region)
        if phonenumbers.is_valid_number(parsed):
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except phonenumbers.NumberParseException:
        pass
        
    return str(phone).strip()
