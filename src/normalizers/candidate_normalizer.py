import copy
import pycountry
from typing import Optional

from src.models.candidate import Candidate
from src.normalizers.name import normalize_name
from src.normalizers.phone import normalize_phone
from src.normalizers.date import normalize_date
from src.normalizers.skills import normalize_skill

class CandidateNormalizer:
    """
    Production-quality CandidateNormalizer class.
    
    Responsible for applying deterministic normalization across an entire Candidate object.
    It delegates field-specific normalization to independent modules (name, phone, date, skills) 
    and handles complex nested normalizations (location, experience, education, emails).
    
    This class is strictly side-effect free: it creates and returns a deep copy of the 
    Candidate object without mutating the original.
    """

    @classmethod
    def normalize(cls, candidate: Candidate) -> Candidate:
        """
        Receives a canonical Candidate object and returns a fully normalized copy.
        """
        # Create a deep copy to ensure the operation is side-effect free
        norm_candidate = copy.deepcopy(candidate)
        
        # 1. Normalize Name
        if norm_candidate.full_name:
            norm_candidate.full_name = normalize_name(norm_candidate.full_name)
            
        # 2. Normalize Emails
        if norm_candidate.emails:
            norm_candidate.emails = [
                str(e).strip().lower() for e in norm_candidate.emails if e
            ]
            
        # 3. Normalize Phones
        if norm_candidate.phones:
            norm_candidate.phones = [
                normalize_phone(p) for p in norm_candidate.phones if p
            ]
            
        # 4. Normalize Skills
        if norm_candidate.skills:
            for skill in norm_candidate.skills:
                skill.name = normalize_skill(skill.name)
                
        # 5. Normalize Location
        if norm_candidate.location:
            loc = norm_candidate.location
            if loc.city:
                loc.city = loc.city.strip().title()
            if loc.region:
                loc.region = loc.region.strip().title()
            if loc.country:
                country_clean = loc.country.strip()
                try:
                    # Attempt to resolve the country name/code to standard ISO-3166 alpha-2
                    country_obj = pycountry.countries.lookup(country_clean)
                    loc.country = country_obj.alpha_2
                except LookupError:
                    # Deterministic fallback if pycountry cannot resolve it
                    loc.country = country_clean.upper()
                    
        # 6. Normalize Experience Dates
        if norm_candidate.experience:
            for exp in norm_candidate.experience:
                if exp.start:
                    exp.start = normalize_date(exp.start)
                if exp.end:
                    exp.end = normalize_date(exp.end)
                    
        # 7. Normalize Education Dates
        if norm_candidate.education:
            for edu in norm_candidate.education:
                if edu.start:
                    edu.start = normalize_date(edu.start)
                if edu.end:
                    edu.end = normalize_date(edu.end)
                    
        return norm_candidate
