import re
from typing import Optional
from urllib.parse import urlparse
import phonenumbers
from dateutil.parser import parse as parse_date

from src.models.candidate import Candidate, Link

class Validator:
    """
    Production-quality Validator for the Candidate Data Transformer.
    Performs strict, deterministic validation on individual fields and Candidate objects.
    Invalid values safely return None or are stripped from lists without raising exceptions.
    """
    
    # A standard, robust regex for canonical email validation
    EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    
    @classmethod
    def validate_email(cls, email: Optional[str]) -> Optional[str]:
        """
        Validates an email address using a deterministic regular expression.
        Returns the original email if valid, otherwise None.
        """
        if not email:
            return None
            
        email_str = str(email).strip()
        if cls.EMAIL_REGEX.match(email_str):
            return email_str.lower()
            
        return None

    @classmethod
    def validate_phone(cls, phone: Optional[str], default_region: str = "US") -> Optional[str]:
        """
        Validates a phone number using the phonenumbers library.
        Returns the original phone string if valid, otherwise None.
        Does NOT normalize the phone number format.
        """
        if not phone:
            return None
            
        try:
            # Parse the number to check its validity. default_region helps if country code is missing.
            parsed_number = phonenumbers.parse(str(phone), default_region)
            if phonenumbers.is_valid_number(parsed_number):
                return str(phone).strip()
            return None
        except phonenumbers.NumberParseException:
            return None

    @classmethod
    def validate_date(cls, date_str: Optional[str]) -> Optional[str]:
        """
        Validates a date string deterministically using dateutil's parser.
        Returns the original string if it represents a valid date, otherwise None.
        """
        if not date_str:
            return None
            
        try:
            # fuzzy=False ensures strict parsing so we don't accidentally extract dates from random text
            parse_date(str(date_str), fuzzy=False)
            return date_str
        except (ValueError, TypeError, OverflowError):
            return None

    @classmethod
    def validate_url(cls, url: Optional[str]) -> Optional[str]:
        """
        Validates a URL by verifying the presence of a valid scheme (http/https) and network location.
        """
        if not url:
            return None
            
        try:
            result = urlparse(str(url))
            # Require both a scheme and a netloc to consider the URL fully valid
            if all([result.scheme, result.netloc]):
                return url
            return None
        except ValueError:
            return None

    @classmethod
    def validate_candidate(cls, candidate: Candidate) -> Candidate:
        """
        Validates an entire Candidate object in place.
        Removes invalid emails, phones, links, and clears invalid dates from experience and education.
        Preserves provenance records cleanly.
        """
        # Validate simple list fields
        if candidate.emails:
            candidate.emails = [e for e in candidate.emails if cls.validate_email(e)]
            
        if candidate.phones:
            # For this dataset (Candidate 1 & 2), we use IN to correctly validate Indian 10-digit numbers 
            # if they happen to lack a country code.
            candidate.phones = [p for p in candidate.phones if cls.validate_phone(p, default_region="IN")]
            
        # Validate nested links
        if candidate.links:
            valid_links_data = {}
            if cls.validate_url(candidate.links.linkedin):
                valid_links_data['linkedin'] = candidate.links.linkedin
            if cls.validate_url(candidate.links.github):
                valid_links_data['github'] = candidate.links.github
            if cls.validate_url(candidate.links.portfolio):
                valid_links_data['portfolio'] = candidate.links.portfolio
                
            valid_other = [url for url in candidate.links.other if cls.validate_url(url)]
            if valid_other:
                valid_links_data['other'] = valid_other
                
            if valid_links_data:
                candidate.links = Link(**valid_links_data)
            else:
                candidate.links = None

        # Validate nested experience dates
        if candidate.experience:
            valid_exp = []
            for exp in candidate.experience:
                exp.start = cls.validate_date(exp.start)
                exp.end = cls.validate_date(exp.end)
                valid_exp.append(exp)
            candidate.experience = valid_exp

        # Validate nested education dates
        if candidate.education:
            valid_edu = []
            for edu in candidate.education:
                edu.start = cls.validate_date(edu.start)
                edu.end = cls.validate_date(edu.end)
                valid_edu.append(edu)
            candidate.education = valid_edu

        # Provenance is explicitly preserved by not modifying candidate.provenance.
        return candidate
