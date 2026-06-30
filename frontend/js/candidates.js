let _allCandidates = [];

async function renderCandidates(container) {
    const response = await fetch('/api/candidates');
    const data = await response.json();
    _allCandidates = data || [];
    
    container.innerHTML = `
        <div class="fade-in" style="margin-bottom: 24px;">
            <h2 style="font-size: 1.8rem; font-weight: 600; margin-bottom: 8px;">Candidate Explorer</h2>
            <p style="color: var(--text-sec);">Search and filter unified profiles.</p>
        </div>
        
        <!-- Controls -->
        <div class="fade-in card" style="display: flex; gap: 16px; margin-bottom: 24px; padding: 16px; align-items: center;">
            <div style="flex: 1;">
                <input type="text" id="cand-search" placeholder="Search by name, headline, or skill..." 
                       style="width: 100%; padding: 12px 16px; border-radius: 8px; border: 1px solid var(--border); background: var(--bg-main); color: var(--text-main); font-family: inherit; font-size: 0.95rem; outline: none;">
            </div>
            <div>
                <select id="cand-filter" style="padding: 12px 16px; border-radius: 8px; border: 1px solid var(--border); background: var(--bg-main); color: var(--text-main); font-family: inherit; font-size: 0.95rem; outline: none; cursor: pointer;">
                    <option value="all">All Confidence</option>
                    <option value="90">90% +</option>
                    <option value="80">80% +</option>
                    <option value="70">70% +</option>
                </select>
            </div>
        </div>
        
        <div style="margin-bottom: 16px; color: var(--text-sec); font-size: 0.9rem; font-weight: 500;" id="cand-count">
            Showing ${_allCandidates.length} candidates
        </div>
        
        <!-- Grid -->
        <div id="cand-grid" class="fade-in" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 24px; margin-bottom: 40px;">
        </div>
    `;
    
    // Bind listeners
    document.getElementById('cand-search').addEventListener('input', updateCandidateGrid);
    document.getElementById('cand-filter').addEventListener('change', updateCandidateGrid);
    
    // Initial Render
    updateCandidateGrid();
}

function updateCandidateGrid() {
    const search = document.getElementById('cand-search').value.toLowerCase();
    const filterVal = document.getElementById('cand-filter').value;
    const grid = document.getElementById('cand-grid');
    const countDiv = document.getElementById('cand-count');
    
    let filtered = _allCandidates;
    
    // Filter by Confidence
    if (filterVal !== 'all') {
        const threshold = parseFloat(filterVal) / 100;
        filtered = filtered.filter(c => (c.overall_confidence || 0) >= threshold);
    }
    
    // Filter by Search
    if (search) {
        filtered = filtered.filter(c => {
            const name = (c.full_name || '').toLowerCase();
            const headline = (c.headline || '').toLowerCase();
            const email = (c.email || '').toLowerCase();
            const skills = (c.skills || []).map(s => typeof s === 'string' ? s.toLowerCase() : s.name.toLowerCase()).join(' ');
            return name.includes(search) || headline.includes(search) || email.includes(search) || skills.includes(search);
        });
    }
    
    // Render Grid
    grid.innerHTML = '';
    
    if (filtered.length === 0) {
        grid.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; padding: 60px; color: var(--text-sec); border: 1px dashed var(--border); border-radius: 12px; background: rgba(0,0,0,0.2);">
                <i class="bi bi-search" style="font-size: 2.5rem; margin-bottom: 16px; display: block; color: var(--border);"></i>
                <p style="font-size: 1.1rem;">No candidates matched your search criteria.</p>
                <p style="font-size: 0.9rem; margin-top: 8px;">Try adjusting your filters.</p>
            </div>
        `;
    } else {
        filtered.forEach((c) => {
            grid.appendChild(createCandidateCard(c));
        });
    }
    
    countDiv.innerText = `Showing ${filtered.length} candidates`;
}

function createCandidateCard(c) {
    const card = document.createElement('div');
    card.className = 'card';
    card.style.display = 'flex';
    card.style.flexDirection = 'column';
    
    const name = Utils.escapeHtml(c.full_name || 'Unknown Candidate');
    const headline = Utils.escapeHtml(c.headline || 'No Headline Provided');
    const email = c.emails && c.emails.length > 0 ? Utils.escapeHtml(c.emails[0]) : 'N/A';
    const phone = c.phones && c.phones.length > 0 ? Utils.escapeHtml(c.phones[0]) : 'N/A';
    
    let expStr = 'No Experience Listed';
    if (c.experience && c.experience.length > 0) {
        const exp = c.experience[0];
        expStr = Utils.escapeHtml((exp.title || 'Role') + ' at ' + (exp.company || 'Company'));
    }
    
    // Location Safe Extraction
    const locParts = [];
    if (c.location) {
        if (c.location.city) locParts.push(c.location.city);
        if (c.location.state) locParts.push(c.location.state);
        else if (c.location.region) locParts.push(c.location.region);
        if (c.location.country) locParts.push(c.location.country);
    }
    const locStr = locParts.length > 0 ? Utils.escapeHtml(locParts.join(', ')) : 'Unknown Location';
    
    // Top 5 Skills
    let skillsHtml = '<span style="color: var(--text-sec); font-size: 0.85rem;">No skills found</span>';
    if (c.skills && c.skills.length > 0) {
        skillsHtml = c.skills.slice(0, 5).map(s => {
            const sn = typeof s === 'string' ? s : s.name;
            return `<span style="background: rgba(37,99,235,0.1); color: var(--primary); padding: 4px 10px; border-radius: 999px; font-size: 0.75rem; margin-right: 6px; margin-bottom: 8px; display: inline-block; font-weight: 500; border: 1px solid rgba(37,99,235,0.2);">${Utils.escapeHtml(sn)}</span>`;
        }).join('');
    }
    
    // Confidence Processing
    const confScore = c.overall_confidence || 0;
    const confColor = Utils.getConfidenceColor(confScore);
    const confText = Utils.formatConfidence(confScore);
    
    card.innerHTML = `
        <div style="flex: 1;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
                <h3 style="font-size: 1.25rem; font-weight: 600; color: var(--text-main);">${name}</h3>
                <span style="color: ${confColor}; font-weight: 700; background: rgba(0,0,0,0.2); padding: 4px 10px; border-radius: 6px; font-size: 0.85rem;">${confText}</span>
            </div>
            
            <p style="color: var(--text-sec); font-size: 0.95rem; margin-bottom: 16px; font-weight: 500;">
                <i class="bi bi-briefcase" style="margin-right: 6px;"></i> ${headline}
            </p>
            
            <div style="margin-bottom: 20px; font-size: 0.85rem; color: var(--text-sec); display: flex; flex-direction: column; gap: 6px;">
                <div><i class="bi bi-geo-alt" style="margin-right: 8px;"></i> ${locStr}</div>
                <div><i class="bi bi-envelope" style="margin-right: 8px;"></i> ${email}</div>
                <div><i class="bi bi-telephone" style="margin-right: 8px;"></i> ${phone}</div>
                <div><i class="bi bi-building" style="margin-right: 8px;"></i> ${expStr}</div>
            </div>
            
            <div style="margin-bottom: 24px;">
                <div style="font-size: 0.75rem; text-transform: uppercase; color: var(--text-sec); font-weight: 600; margin-bottom: 8px;">Top Skills</div>
                <div>${skillsHtml}</div>
            </div>
        </div>
        
        <button class="view-btn" style="width: 100%; padding: 12px; border-radius: 8px; border: 1px solid var(--border); background: var(--bg-main); color: var(--text-main); font-weight: 500; cursor: pointer; transition: all 0.2s; box-shadow: 0 1px 2px rgba(0,0,0,0.1);">
            <i class="bi bi-person-lines-fill" style="margin-right: 6px;"></i> View Complete Profile
        </button>
    `;
    
    // Add Hover Event Listener to Button
    const btn = card.querySelector('.view-btn');
    btn.addEventListener('mouseenter', () => {
        btn.style.backgroundColor = 'var(--bg-card)';
        btn.style.borderColor = 'var(--primary)';
        btn.style.color = 'var(--primary)';
    });
    btn.addEventListener('mouseleave', () => {
        btn.style.backgroundColor = 'var(--bg-main)';
        btn.style.borderColor = 'var(--border)';
        btn.style.color = 'var(--text-main)';
    });
    
    btn.addEventListener('click', () => openCandidateModal(c));
    return card;
}

function openCandidateModal(c) {
    const modal = document.getElementById('global-modal');
    const body = document.getElementById('modal-body');
    
    const name = Utils.escapeHtml(c.full_name || 'Unknown Candidate');
    
    // ----------------------------------------------------
    // Experience Section
    // ----------------------------------------------------
    let expHtml = '<p style="color: var(--text-sec); font-style: italic;">No experience history available.</p>';
    if (c.experience && c.experience.length > 0) {
        expHtml = c.experience.map(e => `
            <div style="margin-bottom: 20px; padding-bottom: 20px; border-bottom: 1px solid var(--border);">
                <h4 style="font-size: 1.1rem; color: var(--text-main); margin-bottom: 6px;">${Utils.escapeHtml(e.title || 'Unknown Role')}</h4>
                <div style="color: var(--primary); font-size: 0.95rem; margin-bottom: 12px; font-weight: 500;">
                    <i class="bi bi-building" style="margin-right: 4px;"></i> ${Utils.escapeHtml(e.company || 'Unknown Company')} 
                    <span style="color: var(--text-sec); margin: 0 8px;">|</span> 
                    <i class="bi bi-calendar3" style="margin-right: 4px;"></i> ${Utils.escapeHtml(e.start_date || '?')} - ${Utils.escapeHtml(e.end_date || 'Present')}
                </div>
                ${e.description ? `<p style="font-size: 0.9rem; color: var(--text-sec); line-height: 1.6;">${Utils.escapeHtml(e.description)}</p>` : ''}
            </div>
        `).join('');
    }
    
    // ----------------------------------------------------
    // Education Section
    // ----------------------------------------------------
    let eduHtml = '<p style="color: var(--text-sec); font-style: italic;">No education history available.</p>';
    if (c.education && c.education.length > 0) {
        eduHtml = c.education.map(e => `
            <div style="margin-bottom: 16px;">
                <h4 style="font-size: 1rem; color: var(--text-main); margin-bottom: 4px;">${Utils.escapeHtml(e.degree || 'Unknown Degree')}</h4>
                <div style="color: var(--text-sec); font-size: 0.9rem;">
                    <i class="bi bi-bank" style="margin-right: 4px;"></i> ${Utils.escapeHtml(e.institution || 'Unknown Institution')}
                </div>
            </div>
        `).join('');
    }
    
    // ----------------------------------------------------
    // Download Blob Setup
    // ----------------------------------------------------
    const rawJson = JSON.stringify(c, null, 2);
    const dataBlob = new Blob([rawJson], { type: 'application/json' });
    const downloadUrl = URL.createObjectURL(dataBlob);
    
    // ----------------------------------------------------
    // Render Modal Content
    // ----------------------------------------------------
    body.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 20px; margin-bottom: 24px;">
            <div>
                <h2 style="font-size: 1.6rem; margin-bottom: 6px;">${name}</h2>
                <div style="color: var(--text-sec); font-size: 0.9rem;"><i class="bi bi-fingerprint"></i> ID: ${Utils.escapeHtml(c.candidate_id || 'N/A')}</div>
            </div>
            <a href="${downloadUrl}" download="candidate_${c.candidate_id || 'export'}.json" style="padding: 10px 20px; background: var(--primary); color: white; text-decoration: none; border-radius: 8px; font-size: 0.95rem; font-weight: 500; transition: var(--trans-fast); box-shadow: 0 2px 4px rgba(37,99,235,0.3);">
                <i class="bi bi-download" style="margin-right: 6px;"></i> Export JSON
            </a>
        </div>
        
        <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 40px;">
            <!-- Main Column -->
            <div>
                <h3 style="font-size: 1.2rem; margin-bottom: 20px; color: var(--primary); font-weight: 600;">Experience</h3>
                ${expHtml}
            </div>
            
            <!-- Sidebar Column -->
            <div style="display: flex; flex-direction: column; gap: 32px;">
                <div>
                    <h3 style="font-size: 1.2rem; margin-bottom: 16px; color: var(--primary); font-weight: 600;">Education</h3>
                    ${eduHtml}
                </div>
                
                <div>
                    <h3 style="font-size: 1.2rem; margin-bottom: 16px; color: var(--primary); font-weight: 600;">Links</h3>
                    ${(c.links && c.links.github) ? `<a href="${Utils.escapeHtml(c.links.github)}" target="_blank" style="color: var(--text-main); text-decoration: none; display: flex; align-items: center; gap: 8px; font-size: 0.9rem; margin-bottom: 12px; padding: 12px; border: 1px solid var(--border); border-radius: 8px; background: var(--bg-main);"><i class="bi bi-github" style="font-size: 1.2rem;"></i> GitHub Profile</a>` : ''}
                    ${(c.links && c.links.linkedin) ? `<a href="${Utils.escapeHtml(c.links.linkedin)}" target="_blank" style="color: var(--text-main); text-decoration: none; display: flex; align-items: center; gap: 8px; font-size: 0.9rem; margin-bottom: 12px; padding: 12px; border: 1px solid var(--border); border-radius: 8px; background: var(--bg-main);"><i class="bi bi-linkedin" style="font-size: 1.2rem; color: #0A66C2;"></i> LinkedIn Profile</a>` : ''}
                    ${(!c.links || (!c.links.github && !c.links.linkedin)) ? '<p style="color: var(--text-sec); font-style: italic;">No links provided.</p>' : ''}
                </div>
            </div>
        </div>
    `;
    
    // Add hover effect to export button
    const expBtn = body.querySelector('a[download]');
    if (expBtn) {
        expBtn.addEventListener('mouseenter', () => expBtn.style.backgroundColor = 'var(--primary-hover)');
        expBtn.addEventListener('mouseleave', () => expBtn.style.backgroundColor = 'var(--primary)');
    }
    
    modal.classList.add('active');
}
