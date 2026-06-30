from typing import List, Dict, Any

from src.models.candidate import Candidate

class ProjectionLayer:
    """
    Projection Layer for the Candidate Data Transformer.
    
    Executes at the very end of the ETL pipeline.
    Converts strictly typed Candidate Pydantic models into clean, JSON-ready 
    Python dictionaries suitable for external API payloads or database injection.
    
    Responsibilities:
    - Serializes Candidate objects deterministically.
    - Optionally strips internal metadata (provenance, confidence scores).
    - Operates completely side-effect free (never mutates the input models).
    """

    @classmethod
    def project(
        cls, 
        candidate: Candidate, 
        include_provenance: bool = True, 
        include_confidence: bool = True
    ) -> Dict[str, Any]:
        """
        Projects a single Candidate model into a JSON-ready dictionary.
        
        Args:
            candidate: The fully merged and scored Candidate profile.
            include_provenance: If False, removes the global provenance array and nested skill sources.
            include_confidence: If False, removes overall_confidence and nested skill confidence scores.
            
        Returns:
            A clean Python dictionary representing the candidate.
        """
        # Utilize Pydantic's built-in deterministic serialization.
        # This operates on a copy, guaranteeing side-effect free execution.
        data = candidate.model_dump(exclude_none=True)
        
        if not include_provenance:
            data.pop("provenance", None)
            
            # Clean up nested sources in skills array
            if "skills" in data and data["skills"]:
                for skill in data["skills"]:
                    skill.pop("sources", None)
                    
        if not include_confidence:
            data.pop("overall_confidence", None)
            
            # Clean up nested confidences in skills array
            if "skills" in data and data["skills"]:
                for skill in data["skills"]:
                    skill.pop("confidence", None)
                    
        return data

    @classmethod
    def project_all(
        cls, 
        candidates: List[Candidate], 
        include_provenance: bool = True, 
        include_confidence: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Batch processes a list of Candidate models into a list of JSON-ready dictionaries.
        """
        return [
            cls.project(
                candidate=candidate,
                include_provenance=include_provenance,
                include_confidence=include_confidence
            )
            for candidate in candidates
        ]
