import json
from typing import List
from pathlib import Path

from src.adapters.base_adapter import BaseAdapter
from src.models.candidate import Candidate, Location, Experience, Provenance

class ATSAdapter(BaseAdapter):
    """
    Adapter for reading candidate data from ATS JSON files and mapping to canonical model.
    """
    
    def load(self, file_path: Path) -> List[Candidate]:
        """
        Reads an ATS JSON file containing candidates and maps them to Candidate models.
        """
        candidates = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            for item in data:
                name = item.get("candidateName") or item.get("full_name")
                mail = item.get("mail") or item.get("email")
                mobile = item.get("mobile") or item.get("phone")
                org = item.get("organization")
                designation = item.get("designation")
                city = item.get("city") or item.get("location")
                
                if not name:
                    continue
                    
                emails = [mail] if mail else []
                phones = [mobile] if mobile else []
                
                location = None
                if city:
                    location = Location(city=city)
                    
                experience = []
                # Fallback to experience array if direct org/designation not found
                if org or designation:
                    experience.append(Experience(company=org, title=designation))
                elif "experience" in item and isinstance(item["experience"], list):
                    for exp in item["experience"]:
                        company = exp.get("company")
                        title = exp.get("title")
                        if company or title:
                            experience.append(Experience(company=company, title=title))
                            org = company if not org else org
                            designation = title if not designation else designation
                    
                # Setup basic field provenance tracking
                provenance_records = []
                fields_to_track = [
                    (name, "full_name"),
                    (mail, "emails"),
                    (mobile, "phones"),
                    (org or designation, "experience"),
                    (city, "location"),
                ]
                
                for val, field_name in fields_to_track:
                    if val:
                        provenance_records.append(
                            Provenance(field=field_name, source="ats.json", method="direct_mapping")
                        )
                    
                candidate = Candidate(
                    full_name=str(name) if name else None,
                    emails=emails,
                    phones=phones,
                    location=location,
                    experience=experience,
                    provenance=provenance_records
                )
                candidates.append(candidate)
        except Exception as e:
            # TODO: Replace print with logger
            print(f"Error loading ATS JSON file {file_path}: {e}")
            
        return candidates
