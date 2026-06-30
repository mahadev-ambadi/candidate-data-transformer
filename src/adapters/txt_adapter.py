import re
from typing import List, Optional
from pathlib import Path

from src.adapters.base_adapter import BaseAdapter
from src.models.candidate import Candidate, Provenance, Skill

class TXTAdapter(BaseAdapter):
    """
    Adapter for reading candidate data from unstructured text files (e.g., recruiter notes).
    Uses deterministic techniques like regex and keyword matching.
    """
    
    KNOWN_SKILLS = [
        "python", "java", "javascript", "react", "django", "sql", 
        "docker", "tensorflow", "machine learning", "kubernetes", 
        "c++", "go", "ruby", "aws", "azure", "gcp"
    ]

    EMAIL_REGEX = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
    # Simple regex for phone numbers (e.g., +91 9876543210, (123) 456-7890)
    PHONE_REGEX = re.compile(r'\+?\d[\d\s\-\(\)]{7,}\d')
    
    def load(self, file_path: Path) -> List[Candidate]:
        """
        Reads a TXT file containing recruiter notes and maps the extracted entities 
        into Candidate models. Supports multiple candidates separated by '---'.
        """
        candidates = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Split candidates if there are multiple blocks separated by '---'
            blocks = content.split("---")
            for block in blocks:
                block = block.strip()
                if not block:
                    continue
                
                candidate = self._parse_block(block, file_path.name)
                candidates.append(candidate)
                
        except Exception as e:
            # TODO: Replace print with logger
            print(f"Error loading TXT file {file_path}: {e}")
            
        return candidates

    def _parse_block(self, text: str, source_file: str) -> Candidate:
        """Parses a single block of text representing one candidate."""
        name = self._extract_name(text)
        emails = self._extract_emails(text)
        phones = self._extract_phones(text)
        skills = self._extract_skills(text, source_file)
        headline = self._extract_headline(text)
        
        provenance_records = []
        if name:
            provenance_records.append(Provenance(field="full_name", source=source_file, method="regex"))
        if emails:
            provenance_records.append(Provenance(field="emails", source=source_file, method="regex"))
        if phones:
            provenance_records.append(Provenance(field="phones", source=source_file, method="regex"))
        if skills:
            provenance_records.append(Provenance(field="skills", source=source_file, method="keyword_matching"))
        if headline:
            provenance_records.append(Provenance(field="headline", source=source_file, method="heuristic"))
            
        return Candidate(
            full_name=name,
            emails=emails,
            phones=phones,
            skills=skills,
            headline=headline,
            provenance=provenance_records
        )

    def _extract_name(self, text: str) -> Optional[str]:
        """Extracts the candidate's name typically prefixed by 'Candidate:'."""
        match = re.search(r'(?i)Candidate:\s*([^\n]+)', text)
        if match:
            return match.group(1).strip()
        return None

    def _extract_emails(self, text: str) -> List[str]:
        """Extracts unique email addresses using regex."""
        return list(set(self.EMAIL_REGEX.findall(text)))

    def _extract_phones(self, text: str) -> List[str]:
        """Extracts unique phone numbers using regex."""
        raw_matches = self.PHONE_REGEX.findall(text)
        valid_phones = []
        for p in raw_matches:
            # Ignore sequences that are too short to be phone numbers when spaces/dashes are removed
            digits = re.sub(r'\D', '', p)
            if len(digits) >= 10:
                valid_phones.append(p.strip())
        return list(set(valid_phones))

    def _extract_skills(self, text: str, source_file: str) -> List[Skill]:
        """Detects skills based on a predefined list of keywords."""
        found_skills = []
        text_lower = text.lower()
        
        for skill_key in self.KNOWN_SKILLS:
            escaped_skill = re.escape(skill_key)
            # Use word boundaries to avoid partial matches (e.g., 'go' in 'good')
            if re.search(rf'\b{escaped_skill}\b', text_lower):
                formatted_skill = skill_key.title()
                # Fix casing for specific acronyms
                if skill_key == "c++": formatted_skill = "C++"
                if skill_key == "sql": formatted_skill = "SQL"
                if skill_key == "aws": formatted_skill = "AWS"
                if skill_key == "gcp": formatted_skill = "GCP"
                if skill_key == "javascript": formatted_skill = "JavaScript"
                if skill_key == "machine learning": formatted_skill = "Machine Learning"
                
                found_skills.append(Skill(name=formatted_skill, sources=[source_file]))
                
        return found_skills

    def _extract_headline(self, text: str) -> Optional[str]:
        """Extracts the first non-empty sentence as the headline, skipping the 'Candidate: Name' line."""
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.lower().startswith('candidate:'):
                continue
            
            # The first substantial line encountered is treated as the headline.
            return line
        return None
