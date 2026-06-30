import pandas as pd
from typing import List
from pathlib import Path

from src.adapters.base_adapter import BaseAdapter
from src.models.candidate import Candidate, Location, Experience, Provenance

class CSVAdapter(BaseAdapter):
    """
    Adapter for reading candidate data from CSV files and mapping to canonical model.
    """
    
    def load(self, file_path: Path) -> List[Candidate]:
        """
        Reads a CSV file containing recruiter candidates and maps them to Candidate models.
        """
        candidates = []
        try:
            df = pd.read_csv(file_path)
            # Replace NaNs with None for easier Pydantic mapping
            df = df.where(pd.notnull(df), None)
            
            for _, row in df.iterrows():
                candidate_id = row.get("candidate_id")
                name = row.get("full_name")
                if pd.isna(name):
                    name = row.get("name")
                
                if not name or pd.isna(name):
                    continue
                    
                email = row.get("email")
                phone = row.get("phone")
                company = row.get("company")
                title = row.get("title")
                location_str = row.get("location")
                if pd.notna(phone):
                    if isinstance(phone, float) and phone.is_integer():
                        phone = str(int(phone))
                    else:
                        phone = str(phone)
                else:
                    phone = None
                    
                emails = [str(email)] if email else []
                phones = [phone] if phone else []
                
                location = None
                if location_str:
                    location = Location(city=location_str)
                    
                experience = []
                if company or title:
                    experience.append(Experience(company=company, title=title))
                
                # Setup basic field provenance tracking
                provenance_records = []
                fields_to_track = [
                    (name, "full_name"),
                    (email, "emails"),
                    (phone, "phones"),
                    (company or title, "experience"),
                    (location_str, "location"),
                ]
                
                for val, field_name in fields_to_track:
                    if val:
                        provenance_records.append(
                            Provenance(field=field_name, source="recruiter.csv", method="direct_mapping")
                        )
                    
                candidate = Candidate(
                    candidate_id=str(candidate_id) if candidate_id else None,
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
            print(f"Error loading CSV file {file_path}: {e}")
            
        return candidates
