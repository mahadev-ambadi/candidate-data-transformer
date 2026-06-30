import logging
import json
from pathlib import Path
from typing import Dict, Any

from src.adapters.csv_adapter import CSVAdapter
from src.adapters.ats_adapter import ATSAdapter
from src.adapters.github_adapter import GitHubAdapter
from src.adapters.txt_adapter import TXTAdapter
from src.validation.validator import Validator
from src.normalizers.candidate_normalizer import CandidateNormalizer
from src.merger.merge import MergeEngine
from src.confidence.confidence_engine import ConfidenceEngine
from src.projection.projection import ProjectionLayer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("CandidateTransformer")

def run_pipeline(data_dir: str = None) -> Dict[str, Any]:
    """
    Main orchestration function for the Candidate Data Transformer ETL pipeline.
    Executes extraction, validation, normalization, merging, scoring, and projection.
    """
    # 1. Path Setup
    base_dir = Path(__file__).parent
    
    if data_dir:
        input_dir = Path(data_dir)
        if not input_dir.is_absolute():
            input_dir = base_dir / data_dir
    else:
        # Gracefully handle potential path structures (root vs nested in 'data')
        input_dir = base_dir / "data" / "sample_data"
        if not input_dir.exists():
            input_dir = base_dir / "sample_data"
        
    output_dir = base_dir / "data" / "output"
    if not output_dir.parent.exists():
        output_dir = base_dir / "output"
        
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("Initializing adapters...")
    try:
        csv_adapter = CSVAdapter()
        ats_adapter = ATSAdapter()
        gh_adapter = GitHubAdapter()
        txt_adapter = TXTAdapter()
    except Exception as e:
        logger.error(f"Failed to initialize adapters: {e}")
        raise

    # 2 & 3. Load and Combine Candidates
    raw_candidates = []
    logger.info("Extracting raw candidate data...")
    try:
        ats_recs = ats_adapter.load(input_dir / "ats.json")
        csv_recs = csv_adapter.load(input_dir / "recruiter.csv")
        gh_recs = gh_adapter.load(input_dir / "github_profiles.json")
        txt_recs = txt_adapter.load(input_dir / "recruiter_notes.txt")
        
        print(f"Loaded ATS: {len(ats_recs)} records")
        print(f"Loaded Recruiter CSV: {len(csv_recs)} records")
        print(f"Loaded GitHub Profiles: {len(gh_recs)} records")
        print(f"Loaded Recruiter Notes: {len(txt_recs)} records")
        
        raw_candidates.extend(ats_recs)
        raw_candidates.extend(csv_recs)
        raw_candidates.extend(gh_recs)
        raw_candidates.extend(txt_recs)
    except Exception as e:
        logger.error(f"Failed during data extraction: {e}")
        raise
        
    logger.info(f"Extracted {len(raw_candidates)} total raw candidate records.")

    # 4. Validate
    logger.info("Executing Validation Layer...")
    validated_candidates = []
    for cand in raw_candidates:
        try:
            valid_cand = Validator.validate_candidate(cand)
            if valid_cand:
                validated_candidates.append(valid_cand)
        except Exception as e:
            logger.warning("Validation failed for %s: %s", cand.full_name or cand.candidate_id, e)

    # 5. Normalize
    logger.info("Executing Normalization Layer...")
    normalized_candidates = []
    for cand in validated_candidates:
        try:
            norm_cand = CandidateNormalizer.normalize(cand)
            normalized_candidates.append(norm_cand)
        except Exception as e:
            logger.warning("Normalization failed for %s: %s", cand.full_name or cand.candidate_id, e)
            
    print(f"\nNormalized candidates: {len(normalized_candidates)}\n")

    # 6. Merge
    logger.info("Executing Merge Engine...")
    try:
        merged_candidates = MergeEngine.merge_candidates(normalized_candidates)
    except Exception as e:
        logger.error(f"Merge Engine failed: {e}")
        raise
        
    print(f"\nMerged candidates: {len(merged_candidates)}\n")
    logger.info(f"Reduced to {len(merged_candidates)} unique candidates after merge.")

    # 7. Compute Confidence
    logger.info("Executing Confidence Engine...")
    scored_candidates = []
    for cand in merged_candidates:
        try:
            scored_cand = ConfidenceEngine.score(cand)
            scored_candidates.append(scored_cand)
        except Exception as e:
            logger.warning("Confidence scoring failed for %s: %s", cand.full_name or cand.candidate_id, e)

    scored_candidates.sort(key=lambda x: x.overall_confidence or 0.0, reverse=True)

    # 8. Project
    logger.info("Executing Projection Layer...")
    try:
        projected_output = ProjectionLayer.project_all(
            scored_candidates,
            include_provenance=True,
            include_confidence=True
        )
    except Exception as e:
        logger.error(f"Projection failed: {e}")
        raise

    # 9. Save
    output_file = output_dir / "output.json"
    logger.info(f"Saving finalized output to {output_file}")
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(projected_output, f, indent=4)
    except Exception as e:
        logger.error(f"Failed to write output JSON to disk: {e}")
        raise

    logger.info("Pipeline execution completed successfully.")

    # 10. Return metrics and payload
    stats = {
        "raw": len(raw_candidates),
        "validated": len(validated_candidates),
        "normalized": len(normalized_candidates),
        "merged": len(merged_candidates),
        "scored": len(scored_candidates)
    }
    
    dup_reduction = 0.0
    if len(normalized_candidates) > 0:
        dup_reduction = ((len(normalized_candidates) - len(merged_candidates)) / len(normalized_candidates)) * 100
        
    avg_conf = 0.0
    if len(scored_candidates) > 0:
        avg_conf = sum(c.overall_confidence for c in scored_candidates if c.overall_confidence) / len(scored_candidates)
        
    avg_skills_before = 0.0
    if len(normalized_candidates) > 0:
        avg_skills_before = sum(len(c.skills or []) for c in normalized_candidates) / len(normalized_candidates)
        
    avg_skills_after = 0.0
    if len(merged_candidates) > 0:
        avg_skills_after = sum(len(c.skills or []) for c in merged_candidates) / len(merged_candidates)

    print("\n--- PIPELINE METRICS ---")
    print(f"Raw Records: {len(raw_candidates)}")
    print(f"Validated: {len(validated_candidates)}")
    print(f"Normalized: {len(normalized_candidates)}")
    print(f"Merged: {len(merged_candidates)}")
    print(f"Scored: {len(scored_candidates)}")
    print(f"Projected: {len(projected_output)}")
    print(f"Duplicate Reduction %: {dup_reduction:.2f}%")
    print(f"Average Confidence: {avg_conf:.2f}")
    print(f"Average Skills Before Merge: {avg_skills_before:.2f}")
    print(f"Average Skills After Merge: {avg_skills_after:.2f}")
    print("------------------------\n")
    
    logger.info("Pipeline Statistics: %s", stats)

    return {
        "stats": stats,
        "raw_candidates": raw_candidates,
        "validated_candidates": validated_candidates,
        "normalized_candidates": normalized_candidates,
        "merged_candidates": merged_candidates,
        "scored_candidates": scored_candidates,
        "projected_output": projected_output
    }

if __name__ == "__main__":
    run_pipeline()
