import copy
from typing import List, Dict, Any, Optional

from src.models.candidate import Candidate, Provenance, Skill

class ConfidenceEngine:
    """
    Deterministic Confidence Engine for the Candidate Data Transformer.
    
    Computes confidence scores purely mathematically based on provenance data, 
    source reliability, agreement, and completeness.
    
    Strictly post-merger operations. Completely side-effect free.
    Does not validate, normalize, or use AI.
    """
    
    # Configurable source weights
    SOURCE_WEIGHTS: Dict[str, float] = {
        "ats": 1.00,
        "csv": 0.95,
        "github": 0.90,
        "txt": 0.75,
        "heuristic": 0.50
    }
    DEFAULT_SOURCE_WEIGHT = 0.50
    
    FIELD_WEIGHTS = {
        "source": 0.50,
        "agreement": 0.30,
        "completeness": 0.20
    }
    
    OVERALL_WEIGHTS = {
        "field": 0.80,
        "profile": 0.20
    }
    
    CORE_FIELDS = [
        "full_name",
        "headline",
        "years_experience",
        "location",
        "emails",
        "phones",
        "experience",
        "education",
        "links"
    ]

    @classmethod
    def score(cls, candidate: Candidate) -> Candidate:
        """
        Computes the overall confidence score for the candidate and updates 
        individual skill confidences if applicable.
        Returns a scored deepcopy of the Candidate.
        """
        scored = copy.deepcopy(candidate)
        
        field_confidences = []
        
        # 1. Compute confidence for standard fields based on provenance
        for field_name in cls.CORE_FIELDS:
            value = getattr(scored, field_name, None)
            if value:
                conf = cls._compute_field_confidence(field_name, value, scored.provenance)
                field_confidences.append(conf)

        # 2. Compute individual skill confidences using their nested sources
        if scored.skills:
            for skill in scored.skills:
                skill_conf = cls._compute_skill_confidence(skill)
                # Assign back to the skill object as per schema
                skill.confidence = round(skill_conf, 2)
                field_confidences.append(skill_conf)
                
        # 3. Compute Profile Completeness
        profile_completeness = cls._get_profile_completeness(scored)
        
        # 4. Calculate Overall Confidence
        if field_confidences:
            mean_field_conf = sum(field_confidences) / len(field_confidences)
            overall = (cls.OVERALL_WEIGHTS["field"] * mean_field_conf) + (cls.OVERALL_WEIGHTS["profile"] * profile_completeness)
        else:
            overall = 0.0
            
        scored.overall_confidence = round(overall, 2)
        
        return scored

    @classmethod
    def _compute_field_confidence(cls, field_name: str, value: Any, provenance: List[Provenance]) -> float:
        """Applies the field confidence formula for a generic field using Candidate provenance."""
        field_provs = [p for p in provenance if p.field == field_name]
        sources = [p.source for p in field_provs]
        
        rel = cls._get_source_reliability(sources)
        agr = cls._get_agreement(len(sources))
        comp = cls._get_field_completeness(value)
        
        return (cls.FIELD_WEIGHTS["source"] * rel) + (cls.FIELD_WEIGHTS["agreement"] * agr) + (cls.FIELD_WEIGHTS["completeness"] * comp)

    @classmethod
    def _compute_skill_confidence(cls, skill: Skill) -> float:
        """Applies the field confidence formula for a specific Skill using its nested sources."""
        sources = skill.sources or []
        
        rel = cls._get_source_reliability(sources)
        agr = cls._get_agreement(len(sources))
        comp = 1.0  # If the skill exists, it's structurally complete (just a name)
        
        return (cls.FIELD_WEIGHTS["source"] * rel) + (cls.FIELD_WEIGHTS["agreement"] * agr) + (cls.FIELD_WEIGHTS["completeness"] * comp)

    @classmethod
    def _get_source_reliability(cls, sources: List[str]) -> float:
        """Returns the maximum source weight among the provided sources."""
        if not sources:
            return cls.DEFAULT_SOURCE_WEIGHT
            
        weights = []
        for src in sources:
            src_lower = str(src).lower()
            weight = cls.DEFAULT_SOURCE_WEIGHT
            
            # Simple substring matching for source identification (e.g., 'ats.json' -> 'ats')
            for key, val in cls.SOURCE_WEIGHTS.items():
                if key in src_lower:
                    weight = val
                    break
            weights.append(weight)
            
        return max(weights)

    @classmethod
    def _get_agreement(cls, source_count: int) -> float:
        """
        Derives agreement strictly from the number of provenance sources.
        
        One source -> Moderate confidence
        Two sources -> Strong confidence
        Three+ -> Maximum agreement
        """
        if source_count <= 1:
            return 0.60
        if source_count == 2:
            return 0.80
        return 1.00

    @classmethod
    def _get_field_completeness(cls, value: Any) -> float:
        """
        Computes completeness based on the complexity of the field.
        Scalars and simple lists are 1.0 if populated.
        Objects (Location, Links, Experience) are scored by populated attributes.
        """
        if not value:
            return 0.0
            
        if isinstance(value, list):
            # If it's a list (like experience), average the completeness of its items
            if not value: return 0.0
            if hasattr(value[0], '__dict__'):
                scores = [cls._get_object_completeness(item) for item in value]
                return sum(scores) / len(scores)
            return 1.0
            
        if hasattr(value, '__dict__'):
            return cls._get_object_completeness(value)
            
        return 1.0

    @classmethod
    def _get_object_completeness(cls, obj: Any) -> float:
        """Calculates what fraction of a Pydantic model's attributes are populated."""
        if not hasattr(obj, "model_dump"):
            return 1.0
            
        data = obj.model_dump(exclude_none=False)
        if not data:
            return 1.0
            
        populated = sum(1 for v in data.values() if v not in (None, [], {}))
        return populated / len(data)

    @classmethod
    def _get_profile_completeness(cls, candidate: Candidate) -> float:
        """Computes global profile completeness (populated core fields / total core fields)."""
        total = len(cls.CORE_FIELDS) + 1  # +1 for skills
        populated = sum(1 for field in cls.CORE_FIELDS if getattr(candidate, field, None))
        
        if candidate.skills:
            populated += 1
            
        return populated / total
