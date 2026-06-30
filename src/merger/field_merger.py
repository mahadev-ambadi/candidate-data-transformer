import copy
from typing import List, Optional, TypeVar, Any

from src.models.candidate import Candidate, Skill, Experience, Education, Link, Provenance

T = TypeVar('T')

class FieldMerger:
    """
    Deterministic Field Merger for the Candidate Data Transformer.
    Operates strictly after validation, normalization, and matching.
    
    Responsibilities:
    - Safely combines fields from two matching Candidate profiles.
    - Resolves conflicts deterministically.
    - Preserves all provenance records.
    - Remains entirely side-effect free by creating a new Candidate object.
    """

    @classmethod
    def merge(cls, primary: Candidate, secondary: Candidate) -> Candidate:
        """
        Merges two Candidate objects into a new, unified Candidate profile.
        'primary' is treated as the higher-priority source for scalar conflict resolution.
        """
        # Create a deep copy to guarantee side-effect free operation
        merged = copy.deepcopy(primary)
        
        merged.candidate_id = cls.merge_scalar(primary.candidate_id, secondary.candidate_id)
        merged.full_name = cls.merge_scalar(primary.full_name, secondary.full_name)
        merged.headline = cls.merge_scalar(primary.headline, secondary.headline)
        merged.years_experience = cls.merge_scalar(primary.years_experience, secondary.years_experience)
        
        # Location is merged by picking the most complete location object or merging sub-fields
        if not merged.location and secondary.location:
            merged.location = copy.deepcopy(secondary.location)
        elif merged.location and secondary.location:
            merged.location.city = cls.merge_scalar(primary.location.city, secondary.location.city)
            merged.location.region = cls.merge_scalar(primary.location.region, secondary.location.region)
            merged.location.country = cls.merge_scalar(primary.location.country, secondary.location.country)
            
        merged.emails = cls.merge_list(primary.emails, secondary.emails)
        merged.phones = cls.merge_list(primary.phones, secondary.phones)
        merged.skills = cls.merge_skills(primary.skills, secondary.skills)
        merged.experience = cls.merge_experience(primary.experience, secondary.experience)
        merged.education = cls.merge_education(primary.education, secondary.education)
        merged.links = cls.merge_links(primary.links, secondary.links)
        merged.provenance = cls.merge_provenance(primary.provenance, secondary.provenance)
        
        return merged

    @classmethod
    def merge_scalar(cls, val1: Any, val2: Any) -> Any:
        """
        Merges a scalar value deterministically.
        Priority:
        1. Agreement (both are identical)
        2. Primary Source (val1 is preferred)
        3. Fallback (return whichever is not None)
        
        # TODO: 
        # Future versions will use metadata timestamps 
        # for freshness-based conflict resolution.
        """
        if val1 == val2:
            return val1
        if val1 and not val2:
            return val1
        if not val1 and val2:
            return val2
            
        # Conflict: Both exist but differ. 
        # Deterministic fallback: prefer the primary source (val1).
        return val1

    @staticmethod
    def _normalize_key(value: Optional[str]) -> str:
        """Helper to normalize string keys for deduplication."""
        if not value:
            return ""
        
        value = str(value).lower()
        value = "".join(c for c in value if c.isalnum() or c.isspace())
        return " ".join(value.split())

    @classmethod
    def merge_list(cls, list1: Optional[List[T]], list2: Optional[List[T]]) -> List[T]:
        """
        Merges two simple lists by performing a Union -> Deduplicate -> Sort.
        Returns a deterministic ordered list.
        """
        l1 = list1 or []
        l2 = list2 or []
        
        # Deduplicate while preserving order deterministically without unsafe sorting
        return list(dict.fromkeys(l1 + l2))

    @classmethod
    def merge_skills(cls, skills1: Optional[List[Skill]], skills2: Optional[List[Skill]]) -> List[Skill]:
        """
        Merges lists of Skill objects by normalized skill name.
        Combines sources from duplicate skills.
        """
        s1 = skills1 or []
        s2 = skills2 or []
        
        merged_skills_map = {}
        
        for skill in s1 + s2:
            key = str(skill.name).strip().lower()
            if key not in merged_skills_map:
                merged_skills_map[key] = copy.deepcopy(skill)
            else:
                # Merge sources, deduplicate, and sort deterministically
                existing_skill = merged_skills_map[key]
                combined_sources = set(existing_skill.sources).union(set(skill.sources))
                existing_skill.sources = sorted(list(combined_sources))
                
                # Take highest confidence if available
                if skill.confidence > existing_skill.confidence:
                    existing_skill.confidence = skill.confidence
                    
        # Return sorted by skill name to ensure determinism
        return sorted(list(merged_skills_map.values()), key=lambda x: x.name)

    @classmethod
    def merge_experience(cls, exp1: Optional[List[Experience]], exp2: Optional[List[Experience]]) -> List[Experience]:
        """
        Merges Experience objects. Deduplicates strictly by (company + title + start).
        Merges safe missing values (e.g., if one has end_date and the other does not).
        """
        e1 = exp1 or []
        e2 = exp2 or []
        
        merged_exp_map = {}
        
        for exp in e1 + e2:
            # Deterministic composite key. 
            company = cls._normalize_key(exp.company)
            import re
            company = re.sub(r'\b(pvt\s*ltd|limited|inc|llc|corp|corporation)\b\.?', '', company).strip()
            title = cls._normalize_key(exp.title)
            start = str(exp.start).strip() if exp.start else ""
            
            key = f"{company}::{title}::{start}"
            
            matched_key = None
            for existing_key in merged_exp_map.keys():
                ext_comp, ext_title, ext_start = existing_key.split("::")
                if ext_title == title and ext_start == start:
                    if ext_comp.startswith(company) or company.startswith(ext_comp):
                        matched_key = existing_key
                        break
            
            if not matched_key:
                merged_exp_map[key] = copy.deepcopy(exp)
            else:
                # Deduplicate and fill safe missing values
                existing_exp = merged_exp_map[matched_key]
                
                # TODO:
                # Future versions should merge dataclass/model fields
                # generically based on completeness rather than
                # field-by-field assignments.
                if not existing_exp.end and exp.end:
                    existing_exp.end = exp.end
                if not existing_exp.summary and exp.summary:
                    existing_exp.summary = exp.summary
                    
        # Sort by start date (descending), then company name
        return sorted(list(merged_exp_map.values()), key=lambda x: (x.start or "", x.company or ""), reverse=True)

    @classmethod
    def merge_education(cls, edu1: Optional[List[Education]], edu2: Optional[List[Education]]) -> List[Education]:
        """
        Merges Education objects. Deduplicates by (institution + degree).
        Merges safe missing values.
        """
        e1 = edu1 or []
        e2 = edu2 or []
        
        merged_edu_map = {}
        
        for edu in e1 + e2:
            institution = cls._normalize_key(edu.institution)
            degree = cls._normalize_key(edu.degree)
            
            key = f"{institution}::{degree}"
            
            if key not in merged_edu_map:
                merged_edu_map[key] = copy.deepcopy(edu)
            else:
                existing_edu = merged_edu_map[key]
                
                # TODO:
                # Future versions should merge dataclass/model fields
                # generically based on completeness rather than
                # field-by-field assignments.
                if not existing_edu.start and edu.start:
                    existing_edu.start = edu.start
                if not existing_edu.end and edu.end:
                    existing_edu.end = edu.end
                if not existing_edu.field and edu.field:
                    existing_edu.field = edu.field
                    
        # Sort by start date descending
        return sorted(list(merged_edu_map.values()), key=lambda x: (x.start or ""), reverse=True)

    @classmethod
    def merge_links(cls, links1: Optional[Link], links2: Optional[Link]) -> Optional[Link]:
        """
        Merges primary link fields and deduplicates the "other" URLs.
        """
        if not links1 and not links2:
            return None
        if links1 and not links2:
            return copy.deepcopy(links1)
        if not links1 and links2:
            return copy.deepcopy(links2)
            
        merged_links = Link()
        merged_links.linkedin = cls.merge_scalar(links1.linkedin, links2.linkedin)
        merged_links.github = cls.merge_scalar(links1.github, links2.github)
        merged_links.portfolio = cls.merge_scalar(links1.portfolio, links2.portfolio)
        
        merged_links.other = cls.merge_list(links1.other, links2.other)
        return merged_links

    @classmethod
    def merge_provenance(cls, prov1: Optional[List[Provenance]], prov2: Optional[List[Provenance]]) -> List[Provenance]:
        """
        Unions and strictly deduplicates provenance records so lineage arrays do not bloat unnecessarily.
        """
        p1 = prov1 or []
        p2 = prov2 or []
        
        prov_map = {}
        for prov in p1 + p2:
            # Create a unique footprint for the provenance record
            key = f"{prov.field}::{prov.source}::{prov.method}"
            if key not in prov_map:
                prov_map[key] = copy.deepcopy(prov)
                
        # Return sorted deterministically by field then source
        return sorted(list(prov_map.values()), key=lambda x: (x.field, x.source))
