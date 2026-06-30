import streamlit as st
import pandas as pd

def render_dashboard() -> None:
    """
    Renders the primary Dashboard view for the Candidate Data Transformer.
    Purely a presentation layer reading from st.session_state.
    """
    st.title("📊 Pipeline Dashboard")
    
    # Graceful state handling
    pipeline_data = st.session_state.get("pipeline_data")
    if not pipeline_data:
        st.warning("No data found in session state. Please execute the pipeline from the sidebar.")
        return
        
    stats = pipeline_data.get("stats", {})
    scored_cands = pipeline_data.get("scored_candidates", [])
    
    # 1. KPI Cards
    st.markdown("### Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    
    raw_count = stats.get("raw", 0)
    val_count = stats.get("validated", 0)
    merged_count = stats.get("merged", 0)
    avg_conf = sum(c.overall_confidence for c in scored_cands) / len(scored_cands) if scored_cands else 0
    
    col1.metric("Raw Candidates", raw_count)
    col2.metric("Validated", val_count)
    col3.metric("Merged", merged_count)
    col4.metric("Avg Confidence", f"{avg_conf * 100:.0f}%")
    
    st.markdown("---")
    
    st.info(
        f"💡 **Pipeline Summary**: Processed **{raw_count}** raw records ➔ "
        f"Merged into **{merged_count}** unique candidates ➔ "
        f"Achieved **{avg_conf * 100:.0f}%** average confidence."
    )
    
    st.markdown("---")
    
    # 2 & 3 Layout
    col_status, col_funnel = st.columns(2)
    
    # 2. Pipeline Execution Checklist
    with col_status:
        st.markdown("### Execution Status")
        st.success("✅ **Extraction** — Data loaded from CSV, JSON, and TXT")
        st.success("✅ **Validation** — Invalid or malformed values scrubbed")
        st.success("✅ **Normalization** — Phones, dates, and casing standardized")
        st.success("✅ **Merge Engine** — Duplicate profiles unified deterministically")
        st.success("✅ **Confidence** — Lineage-based scoring computed")
        st.success("✅ **Projection** — Output serialized for external APIs")
        
    # 3. Pipeline Statistics Funnel
    with col_funnel:
        st.markdown("### Volume Funnel")
        funnel_data = {
            "Stage": ["Raw", "Validated", "Normalized", "Merged", "Scored"],
            "Count": [
                stats.get("raw", 0),
                stats.get("validated", 0),
                stats.get("normalized", 0),
                stats.get("merged", 0),
                stats.get("scored", 0)
            ]
        }
        df_funnel = pd.DataFrame(funnel_data)
        st.bar_chart(df_funnel.set_index("Stage"))
        
    st.markdown("---")
    
    # 4. Recent Merged Candidates Preview
    st.markdown("### Recent Merged Candidates Preview")
    
    if scored_cands:
        # Take the first 5 scored candidates
        preview_cands = scored_cands[:5]
        
        table_data = []
        for c in preview_cands:
            table_data.append({
                "Name": c.full_name or "Unknown",
                "Confidence": f"{c.overall_confidence * 100:.0f}%",
                "Number of Skills": len(c.skills) if c.skills else 0,
                "Provenance Records": len(c.provenance) if c.provenance else 0
            })
            
        df_preview = pd.DataFrame(table_data)
        st.dataframe(df_preview, use_container_width=True, hide_index=True)
    else:
        st.info("No scored candidates available to display.")
