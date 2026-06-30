import streamlit as st
import json
from typing import List, Dict, Any

# =====================================================================
# Aggregation & Read-Only Helpers
# =====================================================================

def _compute_payload_size(data: Any) -> float:
    try:
        raw_bytes = json.dumps(data).encode('utf-8')
        return len(raw_bytes) / 1024.0
    except Exception:
        return 0.0

def _compute_average_fields(dataset: List[Dict[str, Any]]) -> float:
    if not dataset:
        return 0.0
    total_fields = sum(len(d) for d in dataset)
    return total_fields / len(dataset)

def _strip_metadata(dataset: List[Dict[str, Any]], show_prov: bool, show_conf: bool) -> List[Dict[str, Any]]:
    clean_data = []
    
    for c in dataset:
        # Fast top-level dictionary comprehension to avoid deepcopy overhead
        stripped_c = {k: v for k, v in c.items()}
        
        if not show_prov:
            stripped_c.pop("provenance", None)
            
        if not show_conf:
            stripped_c.pop("overall_confidence", None)
            # Strip confidence metadata from nested skills
            if "skills" in stripped_c and isinstance(stripped_c["skills"], list):
                clean_skills = []
                for skill in stripped_c["skills"]:
                    if isinstance(skill, dict):
                        clean_skill = {sk: sv for sk, sv in skill.items()}
                        clean_skill.pop("confidence", None)
                        clean_skill.pop("sources", None)
                        clean_skills.append(clean_skill)
                    else:
                        clean_skills.append(skill)
                stripped_c["skills"] = clean_skills
                
        clean_data.append(stripped_c)
        
    return clean_data

def _filter_json_text(dataset: List[Dict[str, Any]], search_term: str) -> List[Dict[str, Any]]:
    if not search_term:
        return dataset
        
    search_term = search_term.lower()
    filtered = []
    for c in dataset:
        # Object-level serialization for accurate and safe substring matching
        try:
            c_str = json.dumps(c).lower()
            if search_term in c_str:
                filtered.append(c)
        except Exception:
            pass
            
    return filtered


# =====================================================================
# Main View Rendering
# =====================================================================

def render_json_viewer() -> None:
    st.title("📄 JSON Output Viewer")
    
    # Graceful state handling
    pipeline_data = st.session_state.get("pipeline_data")
    if not pipeline_data:
        st.warning("No data found in session state. Please execute the pipeline from the sidebar.")
        return
        
    projected_output = pipeline_data.get("projected_output", [])
    if not projected_output:
        st.info("No projected output available.")
        return
        
    # ------------------------------------------------------------
    # Section: Projection Summary
    # ------------------------------------------------------------
    st.success(
        "**Projection Layer Complete**\n\n"
        "✔ Validated\n"
        "✔ Normalized\n"
        "✔ Merged\n"
        "✔ Confidence Scored\n"
        "✔ API Ready"
    )
    
    st.markdown("---")
    
    # ------------------------------------------------------------
    # Section: View Mode & Controls
    # ------------------------------------------------------------
    col_view, col_toggles = st.columns([1, 1])
    
    with col_view:
        view_mode = st.radio("View Mode", ["Entire Dataset", "Single Candidate"])
        
        selected_cand = None
        if view_mode == "Single Candidate":
            # Using index guarantees no crashes on identical full_names
            cand_options = {
                i: f"{c.get('full_name') or 'Unknown Candidate'} ({c.get('candidate_id') or i})" 
                for i, c in enumerate(projected_output)
            }
            selected_idx = st.selectbox(
                "Select Candidate",
                options=list(cand_options.keys()),
                format_func=lambda x: cand_options[x]
            )
            selected_cand = projected_output[selected_idx]
            
    with col_toggles:
        st.markdown("**Metadata Options**")
        show_prov = st.checkbox("Show Provenance", value=True)
        show_conf = st.checkbox("Show Confidence", value=True)
        
        search_term = st.text_input("🔍 Search JSON", "")
        
    # ------------------------------------------------------------
    # Section: Data Prep (Stateless)
    # ------------------------------------------------------------
    # Isolate working dataset based on user mode
    working_dataset = projected_output if view_mode == "Entire Dataset" else [selected_cand]
    
    # Strip metadata safely using fast comprehensions
    clean_dataset = _strip_metadata(working_dataset, show_prov, show_conf)
    
    # Apply safe object-level substring filtering
    display_dataset = _filter_json_text(clean_dataset, search_term)
    
    # Determine what actually gets passed to Streamlit
    if view_mode == "Single Candidate" and display_dataset:
        display_json = display_dataset[0]
    elif view_mode == "Single Candidate" and not display_dataset:
        display_json = {}
    else:
        display_json = display_dataset
        
    # ------------------------------------------------------------
    # Section: Dataset Summary (KPIs)
    # ------------------------------------------------------------
    st.markdown("### Payload Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    num_records = len(display_dataset)
    num_objects = num_records if view_mode == "Entire Dataset" else (1 if display_json else 0)
    payload_kb = _compute_payload_size(display_json)
    avg_fields = _compute_average_fields(display_dataset)
    
    col1.metric("Candidate Records", num_records)
    col2.metric("JSON Objects", num_objects)
    col3.metric("Payload Size (KB)", f"{payload_kb:.2f} KB")
    col4.metric("Avg Fields / Profile", f"{avg_fields:.1f}")
    
    st.markdown("---")
    
    # ------------------------------------------------------------
    # Section: API Preview
    # ------------------------------------------------------------
    st.markdown("### API Preview")
    st.code(
        "GET /api/v1/candidates\nHTTP/1.1 200 OK\nContent-Type: application/json", 
        language="http"
    )
    
    # ------------------------------------------------------------
    # Section: JSON Display
    # ------------------------------------------------------------
    if display_json:
        tab_interactive, tab_raw = st.tabs(["Interactive JSON", "Raw JSON"])
        
        with tab_interactive:
            # expanded=False protects against browser freezes on large JSON payloads
            st.json(display_json, expanded=False)
            
        with tab_raw:
            raw_str = json.dumps(display_json, indent=2)
            st.code(raw_str, language="json")
            
        # ------------------------------------------------------------
        # Section: Download
        # ------------------------------------------------------------
        st.markdown("---")
        dl_filename = "candidate_dataset.json"
        if view_mode == "Single Candidate":
            cid = selected_cand.get("candidate_id", "export")
            dl_filename = f"candidate_{cid}.json"
            
        st.download_button(
            label="⬇️ Download Output",
            data=raw_str,
            file_name=dl_filename,
            mime="application/json",
            use_container_width=True
        )
    else:
        st.info("No data matches the current filters or search query.")
