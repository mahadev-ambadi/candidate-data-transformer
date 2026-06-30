import streamlit as st
import hashlib

def clean_source(name: str) -> str:
    """Cleans raw source filenames for a polished UI display."""
    return (
        name.upper()
            .replace(".JSON", "")
            .replace(".CSV", "")
            .replace(".TXT", "")
            .replace("_", " ")
            .title()
    )

def render_candidates() -> None:
    """
    Renders the Candidate Explorer view.
    Provides searching, filtering, and detailed profile expansion.
    """
    st.title("👥 Candidate Explorer")
    
    # Graceful state handling
    pipeline_data = st.session_state.get("pipeline_data")
    if not pipeline_data:
        st.warning("No data found in session state. Please execute the pipeline from the sidebar.")
        return
        
    scored_candidates = pipeline_data.get("scored_candidates", [])
    if not scored_candidates:
        st.info("No candidates available.")
        return
        
    # --- UI Controls ---
    col_search, col_filter = st.columns([3, 1])
    
    with col_search:
        search_term = st.text_input("🔍 Search candidates by name, email, or skill", "")
        
    with col_filter:
        conf_filter = st.selectbox(
            "Confidence",
            ["All", "90+", "80+", "70+"]
        )
        
    st.markdown("---")
    
    # --- Filtering Logic (Presentation Layer Only) ---
    filtered_cands = []
    for c in scored_candidates:
        # 1. Confidence filter
        conf_pct = (c.overall_confidence or 0) * 100
        if conf_filter == "90+" and conf_pct < 90: continue
        if conf_filter == "80+" and conf_pct < 80: continue
        if conf_filter == "70+" and conf_pct < 70: continue
        
        # 2. Search filter
        if search_term:
            term = search_term.lower()
            name_match = c.full_name and term in c.full_name.lower()
            email_match = c.emails and any(term in str(e).lower() for e in c.emails)
            skill_match = c.skills and any(term in str(s.name).lower() for s in c.skills)
            
            if not (name_match or email_match or skill_match):
                continue
                
        filtered_cands.append(c)
        
    # --- Render Results ---
    col_vis, col_tot = st.columns(2)
    col_vis.metric("Visible Candidates", len(filtered_cands))
    col_tot.metric("Total Candidates", len(scored_candidates))
    
    if not filtered_cands:
        st.info("No candidates matched your search. Try changing filters.")
        return
        
    # Sort candidates by overall confidence (highest first)
    filtered_cands = sorted(
        filtered_cands, 
        key=lambda c: c.overall_confidence or 0.0, 
        reverse=True
    )
        
    for c in filtered_cands:
        # Use Streamlit's native container border for a 'card' aesthetic
        with st.container(border=True):
            conf_val = c.overall_confidence or 0.0
            conf_display = f"{conf_val * 100:.0f}%"
            st.subheader(c.full_name or "Unknown Candidate")
            
            # Profile Quality (Confidence Engine visual reinforcement)
            st.progress(conf_val)
            if conf_val >= 0.90:
                st.caption(f"🟢 **High Confidence** — {conf_display}")
            elif conf_val >= 0.75:
                st.caption(f"🟡 **Medium Confidence** — {conf_display}")
            else:
                st.caption(f"🔴 **Low Confidence** — {conf_display}")
                
            if c.provenance:
                sources = list(dict.fromkeys(clean_source(p.source) for p in c.provenance))
                st.caption(f"**Merged From:** {', '.join(sources)}")
            
            if c.headline:
                st.caption(f"**{c.headline}**")
                
            col_info, col_skills = st.columns([1, 1])
            
            with col_info:
                if c.emails: st.write(f"📧 {c.emails[0]}")
                if c.phones: st.write(f"📞 {c.phones[0]}")
                if c.location:
                    # Safely fallback between state and region to prevent AttributeError
                    state_or_region = getattr(c.location, "state", getattr(c.location, "region", None))
                    loc_parts = [c.location.city, state_or_region, c.location.country]
                    loc_str = ", ".join(filter(None, loc_parts))
                    st.write(f"📍 {loc_str}")
                    
            with col_skills:
                if c.skills:
                    # Sort safely, defaulting to 0 if confidence is missing, and grab top 5
                    top_skills = sorted(c.skills, key=lambda x: x.confidence or 0.0, reverse=True)[:5]
                    skill_badges = "   ".join([f":blue[{s.name}]" for s in top_skills])
                    st.write(f"🛠️ **Top Skills:**\n\n{skill_badges}")
                else:
                    st.write("🛠️ **Top Skills:** None listed")
                    
            # Download JSON
            cand_json = c.model_dump_json(exclude_none=True, indent=2)
            
            cand_id = c.candidate_id
            if not cand_id:
                cand_id = hashlib.sha256((c.full_name or "unknown").encode()).hexdigest()[:10]
                
            st.download_button(
                label="⬇️ Download JSON",
                data=cand_json,
                file_name=f"candidate_{cand_id}.json",
                mime="application/json",
                key=f"dl_{cand_id}"
            )
            
            # Detail Expander
            with st.expander("View Complete Profile"):
                tab_exp, tab_edu, tab_links, tab_prov = st.tabs([
                    "Experience", "Education", "Links", "Provenance"
                ])
                
                with tab_exp:
                    if c.experience:
                        for exp in c.experience:
                            title = exp.title or "Unknown Role"
                            company = exp.company or "Unknown Company"
                            st.markdown(f"**{title}** at **{company}**")
                            st.caption(f"{exp.start or 'Unknown'} - {exp.end or 'Present'}")
                            if exp.summary: st.write(exp.summary)
                            st.divider()
                    else:
                        st.write("No experience records found.")
                        
                with tab_edu:
                    if c.education:
                        for edu in c.education:
                            degree = edu.degree or "Unknown Degree"
                            field = edu.field or "General"
                            institution = edu.institution or "Unknown Institution"
                            st.markdown(f"**{degree}** — {field}")
                            st.caption(f"🏫 {institution}")
                            st.divider()
                    else:
                        st.write("No education records found.")
                        
                with tab_links:
                    if c.links:
                        if c.links.linkedin: st.markdown(f"💼 **LinkedIn:** [{c.links.linkedin}]({c.links.linkedin})")
                        if c.links.github: st.markdown(f"💻 **GitHub:** [{c.links.github}]({c.links.github})")
                        if c.links.portfolio: st.markdown(f"🎨 **Portfolio:** [{c.links.portfolio}]({c.links.portfolio})")
                        if c.links.other:
                            st.write("**Other Links:**")
                            for link in c.links.other:
                                st.markdown(f"- [{link}]({link})")
                    else:
                        st.write("No external links found.")
                        
                with tab_prov:
                    if c.provenance:
                        st.write(f"Profile built from **{len(c.provenance)}** distinct data extractions.")
                        prov_data = [{"Field": p.field, "Source": p.source, "Method": p.method} for p in c.provenance]
                        st.dataframe(prov_data, use_container_width=True, hide_index=True)
                    else:
                        st.write("No provenance records found.")
