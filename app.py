import streamlit as st
from pathlib import Path

# Local application imports
from main import run_pipeline

from pages.dashboard import render_dashboard
from pages.candidates import render_candidates
from pages.analytics import render_analytics
from pages.provenance import render_provenance
from pages.json_viewer import render_json_viewer

PIPELINE_KEY = "pipeline_data"

def load_css(css_path: Path) -> None:
    """
    Safely loads an external CSS file for custom styling.
    """
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning(f"CSS file not found at {css_path}")

def main() -> None:
    """
    Main Streamlit application entry point.
    Responsible exclusively for layout, routing, and state management.
    Business logic remains strictly in the backend pipeline.
    """
    st.set_page_config(
        page_title="Candidate Data Transformer",
        page_icon="🔄",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 1. Load custom CSS
    base_dir = Path(__file__).parent
    css_path = base_dir / "assets" / "styles.css"
    load_css(css_path)
    
    # 2. Sidebar Navigation & Execution Controls
    st.sidebar.title("Candidate Data Transformer")
    st.sidebar.markdown("────────────────")
    st.sidebar.subheader("Pipeline")
    
    if st.sidebar.button("▶ Run Pipeline", type="primary", use_container_width=True):
        with st.spinner("Executing extraction, merging, and scoring..."):
            try:
                # 3. Execute backend orchestrator and store in session state
                pipeline_data = run_pipeline()
                st.session_state[PIPELINE_KEY] = pipeline_data
                st.sidebar.success("Pipeline executed successfully!")
            except Exception as e:
                st.sidebar.error(f"Pipeline execution failed: {e}")
                
    # 4. Handle Header and pre-execution state
    st.title("Candidate Data Transformer")
    st.caption("Multi-Source Candidate Intelligence Platform")
    
    if PIPELINE_KEY not in st.session_state:
        st.markdown(
            """
            ### Welcome to the ETL Dashboard!
            
            The backend pipeline is ready to process your raw HR data. 
            
            Click the **▶ Run Pipeline** button in the sidebar to begin:
            * Extracting from CSV, ATS JSON, GitHub, and Text Notes
            * Validating and Normalizing data
            * Deterministically Merging candidate profiles
            * Scoring profile confidence using provenance footprints
            """
        )
        return
    else:
        # Success Metrics immediately after running
        stats = st.session_state[PIPELINE_KEY].get("stats", {})
        scored_cands = st.session_state[PIPELINE_KEY].get("scored_candidates", [])
        avg_conf = sum(c.overall_confidence for c in scored_cands) / len(scored_cands) if scored_cands else 0
        
        st.success("✔ Pipeline Complete")
        col1, col2, col3 = st.columns(3)
        col1.metric("Raw Records", stats.get("raw", 0))
        col2.metric("Merged", stats.get("merged", 0))
        col3.metric("Average Confidence", f"{avg_conf * 100:.0f}%")
        st.markdown("---")
        
    # 5. Routing (Post-execution)
    st.sidebar.subheader("Navigation")
    page = st.sidebar.radio(
        "Select a view:",
        ["Dashboard", "Candidates", "Analytics", "Provenance", "JSON Viewer"],
        key="selected_page"
    )
    
    st.sidebar.markdown("────────────────")
    st.sidebar.subheader("Downloads")
    # Placeholders for future downloads
    
    st.sidebar.markdown("────────────────")
    st.sidebar.subheader("About")
    st.sidebar.info("Deterministic ETL Pipeline\nv1.0.0")
    
    # 6. Modular Page Routing
    if page == "Dashboard":
        render_dashboard()
        
    elif page == "Candidates":
        render_candidates()
        
    elif page == "Analytics":
        render_analytics()
        
    elif page == "Provenance":
        render_provenance()
        
    elif page == "JSON Viewer":
        render_json_viewer()

if __name__ == "__main__":
    main()
