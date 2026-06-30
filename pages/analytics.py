import streamlit as st
import pandas as pd
from collections import Counter
from typing import List

# =====================================================================
# Aggregation Helpers (Purely Read-Only)
# =====================================================================

def _compute_duplicate_reduction(normalized_count: int, merged_count: int) -> float:
    if normalized_count == 0:
        return 0.0
    return ((normalized_count - merged_count) / normalized_count) * 100

def _compute_average_skills(candidates: List) -> float:
    if not candidates:
        return 0.0
    total_skills = sum(len(c.skills) for c in candidates if c.skills)
    return total_skills / len(candidates)

def _compute_average_confidence(candidates: List) -> float:
    if not candidates:
        return 0.0
    total_conf = sum((c.overall_confidence or 0.0) for c in candidates)
    return total_conf / len(candidates)

def _count_unique_sources(candidates: List) -> int:
    sources = set()
    for c in candidates:
        if c.provenance:
            for p in c.provenance:
                sources.add(p.source.upper())
    return len(sources)

def _compute_confidence_distribution(candidates: List) -> pd.DataFrame:
    dist = {"High (>=90%)": 0, "Medium (75-89%)": 0, "Low (<75%)": 0}
    for c in candidates:
        conf = (c.overall_confidence or 0.0) * 100
        if conf >= 90:
            dist["High (>=90%)"] += 1
        elif conf >= 75:
            dist["Medium (75-89%)"] += 1
        else:
            dist["Low (<75%)"] += 1
    return pd.DataFrame({"Count": list(dist.values())}, index=list(dist.keys()))

def _compute_top_skills(candidates: List, top_n: int = 10) -> pd.DataFrame:
    SPECIAL = {
        "Sql": "SQL",
        "Aws": "AWS",
        "Gcp": "GCP",
        "Api": "API",
        "Hr": "HR"
    }
    skill_counter = Counter()
    for c in candidates:
        if c.skills:
            for s in c.skills:
                norm_name = s.name.strip().title()
                norm_name = SPECIAL.get(norm_name, norm_name)
                skill_counter[norm_name] += 1
                
    if not skill_counter:
        return pd.DataFrame({"Count": []})
        
    top_skills = dict(skill_counter.most_common(top_n))
    return pd.DataFrame({"Count": list(top_skills.values())}, index=list(top_skills.keys()))

def _compute_source_contribution(candidates: List) -> pd.DataFrame:
    # Pre-seed counter to guarantee known sources appear even if zero
    source_counter = Counter({"ATS": 0, "CSV": 0, "GitHub": 0, "TXT": 0})
    for c in candidates:
        if c.provenance:
            for p in c.provenance:
                src = p.source.upper()
                if "ATS" in src: 
                    source_counter["ATS"] += 1
                elif "CSV" in src: 
                    source_counter["CSV"] += 1
                elif "GITHUB" in src: 
                    source_counter["GitHub"] += 1
                elif "TXT" in src: 
                    source_counter["TXT"] += 1
                else: 
                    # Handle any unexpected sources dynamically
                    source_counter[p.source.title()] += 1
                
    return pd.DataFrame({"Count": list(source_counter.values())}, index=list(source_counter.keys()))

def _compute_average_provenance(candidates: List) -> float:
    if not candidates:
        return 0.0
    total = sum(len(c.provenance) for c in candidates if c.provenance)
    return total / len(candidates)


# =====================================================================
# Main View Rendering
# =====================================================================

def render_analytics() -> None:
    st.title("📈 Data Analytics")
    
    # Graceful State Handling
    pipeline_data = st.session_state.get("pipeline_data")
    if not pipeline_data:
        st.warning("No data found in session state. Please execute the pipeline from the sidebar.")
        return
        
    stats = pipeline_data.get("stats", {})
    normalized_cands = pipeline_data.get("normalized_candidates", [])
    merged_cands = pipeline_data.get("merged_candidates", [])
    scored_cands = pipeline_data.get("scored_candidates", [])
    
    norm_count = stats.get("normalized", len(normalized_cands))
    merged_count = stats.get("merged", len(merged_cands))
    
    # ------------------------------------------------------------
    # Section 1: KPI Cards
    # ------------------------------------------------------------
    st.markdown("### Executive Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    dup_reduction = _compute_duplicate_reduction(norm_count, merged_count)
    avg_skills = _compute_average_skills(merged_cands)
    avg_conf = _compute_average_confidence(scored_cands)
    num_sources = _count_unique_sources(scored_cands)
    
    col1.metric("Duplicate Reduction", f"{dup_reduction:.1f}%")
    col2.metric("Avg Skills/Candidate", f"{avg_skills:.1f}")
    col3.metric("Average Confidence", f"{avg_conf * 100:.0f}%")
    col4.metric("Data Sources", num_sources)
    
    st.markdown("---")
    
    # ------------------------------------------------------------
    # Section 2 & 3: Funnel and Confidence Distribution
    # ------------------------------------------------------------
    col_funnel, col_conf = st.columns(2)
    
    with col_funnel:
        st.markdown("#### Pipeline Funnel")
        
        raw_count = stats.get("raw", 0)
        
        funnel_data = {
            "Stage": ["Raw", "Validated", "Normalized", "Merged", "Scored"],
            "Count": [
                raw_count,
                stats.get("validated", 0),
                stats.get("normalized", 0),
                merged_count,
                stats.get("scored", 0)
            ]
        }
        df_funnel = pd.DataFrame(funnel_data).set_index("Stage")
        st.bar_chart(df_funnel)
        
        retention = (merged_count / raw_count * 100) if raw_count > 0 else 0.0
        st.caption(f"**Retention:** {retention:.0f}% of raw records retained as unique profiles.")
        
    with col_conf:
        st.markdown("#### Confidence Distribution")
        df_conf = _compute_confidence_distribution(scored_cands)
        st.bar_chart(df_conf)
        
    st.markdown("---")
    
    # ------------------------------------------------------------
    # Section 4 & 5: Top Skills and Source Contribution
    # ------------------------------------------------------------
    col_skills, col_sources = st.columns(2)
    
    with col_skills:
        st.markdown("#### Top 10 Extracted Skills")
        df_skills = _compute_top_skills(merged_cands)
        if not df_skills.empty:
            st.bar_chart(df_skills)
        else:
            st.info("No skills data available to display.")
            
    with col_sources:
        st.markdown("#### Source Contribution")
        df_sources = _compute_source_contribution(merged_cands)
        st.bar_chart(df_sources)
        
    st.markdown("---")
    
    # ------------------------------------------------------------
    # Section 6: Merge Enrichment (Business Value)
    # ------------------------------------------------------------
    st.markdown("### Merge Enrichment Impact")
    st.caption("Demonstrating the value of the Merge Engine in creating richer candidate profiles.")
    
    avg_skills_before = _compute_average_skills(normalized_cands)
    avg_skills_after = avg_skills  # already computed off merged_cands
    
    col_before, col_arrow, col_after, _ = st.columns([2, 1, 2, 3])
    col_before.metric("Avg Skills (Before Merge)", f"{avg_skills_before:.1f}")
    col_arrow.markdown("<h2 style='text-align: center; margin-top: 10px;'>➔</h2>", unsafe_allow_html=True)
    col_after.metric("Avg Skills (After Merge)", f"{avg_skills_after:.1f}")
    
    st.markdown("---")
    
    # ------------------------------------------------------------
    # Section 7: Candidate Quality Summary
    # ------------------------------------------------------------
    st.markdown("### Candidate Quality Summary")
    
    if scored_cands:
        max_conf = max(c.overall_confidence or 0.0 for c in scored_cands)
        min_conf = min(c.overall_confidence or 0.0 for c in scored_cands)
        avg_prov = _compute_average_provenance(scored_cands)
        
        quality_data = [{
            "Highest Confidence": f"{max_conf * 100:.0f}%",
            "Lowest Confidence": f"{min_conf * 100:.0f}%",
            "Average Confidence": f"{avg_conf * 100:.0f}%",
            "Average Skills": f"{avg_skills:.1f}",
            "Avg Provenance Records": f"{avg_prov:.1f}"
        }]
        st.dataframe(pd.DataFrame(quality_data), use_container_width=True, hide_index=True)
    else:
        st.info("No scored candidates available for quality summary.")
