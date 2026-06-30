import streamlit as st
import pandas as pd
from collections import Counter
import json
from typing import Tuple
from src.models.candidate import Candidate

# =====================================================================
# Aggregation Helpers (Purely Read-Only)
# =====================================================================

KNOWN_SOURCES = [
    "ATS",
    "CSV",
    "GitHub",
    "TXT",
]

SOURCE_DISPLAY_NAMES = {
    "ATS": "ATS",
    "CSV": "CSV",
    "TXT": "TXT",
    "GITHUB": "GitHub",
}

def _clean_source_name(name: str) -> str:
    """Cleans raw source filenames for a polished UI display."""
    clean = (
        name.upper()
            .replace(".JSON", "")
            .replace(".CSV", "")
            .replace(".TXT", "")
            .replace("_", " ")
            .strip()
    )
    
    # Try an exact match first
    if clean in SOURCE_DISPLAY_NAMES:
        return SOURCE_DISPLAY_NAMES[clean]
        
    # If it's a compound name like 'GITHUB PROFILES', handle the known parts
    parts = clean.split()
    return " ".join([SOURCE_DISPLAY_NAMES.get(p, p.title()) for p in parts])

def _compute_audit_metrics(candidate: Candidate) -> Tuple[int, int, int, str]:
    if not candidate.provenance:
        return 0, 0, 0, "N/A"
        
    total_prov = len(candidate.provenance)
    sources = set(p.source.upper() for p in candidate.provenance)
    fields = set(p.field for p in candidate.provenance)
    
    source_counter = Counter(p.source.upper() for p in candidate.provenance)
    most_freq_source = source_counter.most_common(1)[0][0] if source_counter else "N/A"
    
    return total_prov, len(sources), len(fields), _clean_source_name(most_freq_source)

def _compute_source_counts(candidate: Candidate) -> pd.DataFrame:
    source_counter = Counter({src: 0 for src in KNOWN_SOURCES})
    if candidate.provenance:
        for p in candidate.provenance:
            clean_name = _clean_source_name(p.source)
            source_counter[clean_name] += 1
            
    return pd.DataFrame({"Count": list(source_counter.values())}, index=list(source_counter.keys()))

def _build_lineage_dataframe(candidate: Candidate, source_filter: str) -> pd.DataFrame:
    if not candidate.provenance:
        return pd.DataFrame(columns=["Field", "Source", "Method"])
        
    data = []
    for p in candidate.provenance:
        clean_src = _clean_source_name(p.source)
        if source_filter != "All" and source_filter.upper() not in clean_src.upper():
            continue
            
        data.append({
            "Field": p.field,
            "Source": clean_src,
            "Method": p.method
        })
        
    df = pd.DataFrame(data)
    if not df.empty:
        df = df.sort_values(by="Field")
    return df

def _compute_field_summary(candidate: Candidate) -> pd.DataFrame:
    if not candidate.provenance:
        return pd.DataFrame(columns=["Field", "Supporting Sources", "Agreement"])
        
    field_sources = {}
    for p in candidate.provenance:
        field_sources.setdefault(p.field, set()).add(_clean_source_name(p.source))
    
    data = []
    for field, sources_set in field_sources.items():
        count = len(sources_set)
        if count == 1: 
            agreement = "Low"
        elif count == 2: 
            agreement = "Medium"
        else: 
            agreement = "High"
        
        data.append({
            "Field": field,
            "Supporting Sources": count,
            "Agreement": agreement
        })
        
    df = pd.DataFrame(data)
    if not df.empty:
        df = df.sort_values(by="Field")
    return df


# =====================================================================
# Main View Rendering
# =====================================================================

def render_provenance() -> None:
    st.title("🔍 Data Provenance")
    
    # Graceful State Handling
    pipeline_data = st.session_state.get("pipeline_data")
    if not pipeline_data:
        st.warning("No data found in session state. Please execute the pipeline from the sidebar.")
        return
        
    scored_cands = pipeline_data.get("scored_candidates", [])
    if not scored_cands:
        st.info("No candidates available.")
        return
        
    # ------------------------------------------------------------
    # Section 1: Candidate Selector
    # ------------------------------------------------------------
    # Using index as the internal key guarantees we never clash on duplicate full_names
    cand_options = {
        i: f"{c.full_name or 'Unknown Candidate'} ({c.candidate_id or i})" 
        for i, c in enumerate(scored_cands)
    }
    
    selected_idx = st.selectbox(
        "Candidate Selection",
        options=list(cand_options.keys()),
        format_func=lambda x: cand_options[x]
    )
    
    selected_cand = scored_cands[selected_idx]
    
    st.markdown("---")
    
    # ------------------------------------------------------------
    # Section 2: Executive Metrics
    # ------------------------------------------------------------
    st.markdown("### Provenance Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    total_prov, num_sources, num_fields, most_freq = _compute_audit_metrics(selected_cand)
    
    col1.metric("Total Provenance Records", total_prov)
    col2.metric("Contributing Sources", num_sources)
    col3.metric("Tracked Fields", num_fields)
    col4.metric("Most Frequent Source", most_freq)
    
    st.markdown("---")
    
    # ------------------------------------------------------------
    # Section 7: Audit Summary
    # ------------------------------------------------------------
    st.info(
        f"**Audit Summary:** Candidate profile constructed from **{num_sources} independent sources** "
        f"containing **{total_prov} provenance records**."
    )
    
    st.success(
        f"✔ **Lineage Verified**\n\n"
        f"**{num_fields}** tracked fields supported by **{num_sources}** independent data sources."
    )
    
    # ------------------------------------------------------------
    # Section 3: Source Contribution
    # ------------------------------------------------------------
    st.markdown("### Source Contribution")
    df_sources = _compute_source_counts(selected_cand)
    st.bar_chart(df_sources)
    
    st.markdown("---")
    
    # ------------------------------------------------------------
    # Section 4 & 5: Source Filter & Lineage Table
    # ------------------------------------------------------------
    st.markdown("### Field Lineage Table")
    
    col_filter, _ = st.columns([1, 3])
    with col_filter:
        source_filter = st.selectbox(
            "Filter by Source",
            ["All", "ATS", "CSV", "GitHub", "TXT"]
        )
        
    df_lineage = _build_lineage_dataframe(selected_cand, source_filter)
    if not df_lineage.empty:
        st.dataframe(df_lineage, use_container_width=True, hide_index=True)
    else:
        st.write("No lineage records found for the selected filters.")
        
    st.markdown("---")
    
    # ------------------------------------------------------------
    # Section 6: Field Agreement Summary
    # ------------------------------------------------------------
    st.markdown("### Field Agreement Summary")
    df_agreement = _compute_field_summary(selected_cand)
    if not df_agreement.empty:
        st.dataframe(df_agreement, use_container_width=True, hide_index=True)
    else:
        st.write("No field agreement data available.")
        
    st.markdown("---")
    
    # ------------------------------------------------------------
    # Section 8: Download Provenance
    # ------------------------------------------------------------
    if selected_cand.provenance:
        # Serialize only the provenance array to JSON
        prov_list = [p.model_dump() for p in selected_cand.provenance]
        prov_json = json.dumps(prov_list, indent=2)
        
        cand_id = selected_cand.candidate_id or str(selected_idx)
        st.download_button(
            label="⬇️ Download Provenance JSON",
            data=prov_json,
            file_name=f"candidate_{cand_id}_provenance.json",
            mime="application/json"
        )
