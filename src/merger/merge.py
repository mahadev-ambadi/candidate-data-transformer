import copy
from typing import List

from src.models.candidate import Candidate
from src.merger.matcher import CandidateMatcher
from src.merger.field_merger import FieldMerger

class MergeEngine:
    """
    Orchestration engine for merging Candidate profiles.
    
    Strictly coordinates the CandidateMatcher and FieldMerger components to combine 
    a raw list of candidates into a unified, deduplicated list.
    
    This class is purely an orchestrator:
    - Never mutates the input list.
    - Operates completely side-effect free.
    - Defers all validation, normalization, and confidence scoring.
    - Has zero knowledge of upstream source formats (CSV, ATS, GitHub, etc.).
    """

    @classmethod
    def merge_candidates(cls, candidates: List[Candidate]) -> List[Candidate]:
        """
        Takes an unmerged list of Candidate objects and reduces it to a unified list.
        """
        def get_priority(candidate: Candidate) -> int:
            sources = [p.source.lower() for p in candidate.provenance]
            if any('ats' in s for s in sources): return 1
            if any('github' in s for s in sources): return 2
            if any('txt' in s for s in sources): return 3
            if any('csv' in s for s in sources): return 4
            return 5
            
        sorted_candidates = sorted(candidates, key=get_priority)
        merged_candidates: List[Candidate] = []
        
        for incoming in sorted_candidates:
            match_found = False
            
            # Compare the incoming candidate against every existing merged candidate
            for i, existing in enumerate(merged_candidates):
                is_match, reason = CandidateMatcher.is_same_candidate(existing, incoming)
                if is_match:
                    print("Matched:")
                    print(f"{existing.full_name or existing.candidate_id}")
                    print("<->")
                    print(f"{incoming.full_name or incoming.candidate_id}\n")
                    print("Merge reason:")
                    print(f"{reason}\n")
                    # Merge the profiles and replace the element in place
                    merged_candidates[i] = FieldMerger.merge(existing, incoming)
                    match_found = True
                    break
                    
            if not match_found:
                # If no match is found, append a deepcopy to ensure strict isolation
                merged_candidates.append(copy.deepcopy(incoming))
                
        return merged_candidates
