import re
from typing import List, Set
from src.models.candidate import Candidate, Link

class CandidateMatcher:
    """
    Deterministic Candidate Matcher for identifying if two Candidate profiles 
    represent the same person.
    
    Operates strictly post-validation and post-normalization.
    Never modifies, validates, or normalizes Candidate objects.
    """
    
    # Configurable blocklists to ignore generic/placeholder emails during matching
    GENERIC_EMAIL_PREFIXES = {
        "noreply", "no-reply", "info", "support", "admin", "test"
    }
    GENERIC_EMAILS = {
        "na@na.com"
    }

    @classmethod
    def is_same_candidate(cls, candidate1: Candidate, candidate2: Candidate) -> tuple[bool, str]:
        """
        Determines if two candidates are the same person using strict deterministic rules.
        """
        # Rule 1: Exact email match
        if cls._match_by_email(candidate1.emails, candidate2.emails):
            return True, "Exact email"
            
        # Rule 2: Exact phone match
        if cls._match_by_phone(candidate1.phones, candidate2.phones):
            return True, "Phone"
            
        # Rule 3 & 4: Normalized full name
        name1 = cls._normalize_name_for_match(candidate1.full_name)
        name2 = cls._normalize_name_for_match(candidate2.full_name)
        
        if name1 and name2 and name1 == name2:
            return True, "Fuzzy name similarity"
            
        return False, ""

    @classmethod
    def _is_generic_email(cls, email: str) -> bool:
        if not email: return True
        if email in cls.GENERIC_EMAILS: return True
        prefix = email.split('@')[0]
        if any(prefix.startswith(p) for p in cls.GENERIC_EMAIL_PREFIXES): return True
        return False

    @classmethod
    def _match_by_email(cls, emails1: List[str], emails2: List[str]) -> bool:
        if not emails1 or not emails2: return False
        valid1 = {e.strip().lower() for e in emails1 if not cls._is_generic_email(e)}
        valid2 = {e.strip().lower() for e in emails2 if not cls._is_generic_email(e)}
        return bool(valid1.intersection(valid2))

    @classmethod
    def _match_by_phone(cls, phones1: List[str], phones2: List[str]) -> bool:
        if not phones1 or not phones2: return False
        p1 = {cls._normalize_phone(p) for p in phones1 if p}
        p2 = {cls._normalize_phone(p) for p in phones2 if p}
        p1 = {p for p in p1 if p}
        p2 = {p for p in p2 if p}
        return bool(p1.intersection(p2))

    @classmethod
    def _normalize_phone(cls, phone: str) -> str:
        # Simple digits extraction for exact match
        return re.sub(r'\D', '', phone)

    @classmethod
    def _normalize_name_for_match(cls, name: str) -> str:
        if not name: return ""
        name = re.sub(r'[^\w\s]', '', name)
        name = name.lower()
        name = re.sub(r'\s+', ' ', name).strip()
        
        words = name.split()
        if len(words) > 2:
            filtered = [words[0]] + [w for w in words[1:] if len(w) > 2]
            if len(filtered) < 2:
                filtered = [words[0], words[-1]]
            name = " ".join(filtered)
        return name

    @classmethod
    def _match_by_github(cls, links1: Link, links2: Link) -> bool:
        if not links1 or not links2: return False
        g1 = links1.github
        g2 = links2.github
        if not g1 or not g2: return False
        
        g1_norm = g1.lower().strip().rstrip('/')
        g2_norm = g2.lower().strip().rstrip('/')
        return g1_norm == g2_norm
