async function renderProvenance(container) {
    const response = await fetch('/api/provenance');
    const scored = await response.json();
    
    container.innerHTML = `
        <div class="fade-in" style="margin-bottom: 24px;">
            <h2 style="font-size: 1.8rem; font-weight: 600; margin-bottom: 8px;">Provenance Lineage</h2>
            <p style="color: var(--text-sec);">Audit trail tracking data origin and field-level consensus.</p>
        </div>
        
        <div class="fade-in card" style="margin-bottom: 24px;">
            <label style="display: block; margin-bottom: 12px; color: var(--text-sec); font-weight: 500;">Select a Candidate to View Lineage:</label>
            <select id="prov-select" style="width: 100%; padding: 12px 16px; border-radius: 8px; border: 1px solid var(--border); background: var(--bg-main); color: var(--text-main); font-family: inherit; font-size: 1rem; outline: none; cursor: pointer;">
                <option value="">-- Choose a profile --</option>
                ${scored.map((c, i) => `<option value="${i}">${Utils.escapeHtml(c.full_name || c.candidate_id)}</option>`).join('')}
            </select>
        </div>
        
        <div id="prov-content" class="fade-in">
            <div style="text-align: center; padding: 60px; color: var(--text-sec); border: 1px dashed var(--border); border-radius: 12px; background: rgba(0,0,0,0.2);">
                <i class="bi bi-diagram-3" style="font-size: 2.5rem; margin-bottom: 16px; display: block; color: var(--border);"></i>
                <p style="font-size: 1.1rem;">Select a candidate above to view their data lineage.</p>
            </div>
        </div>
    `;
    
    document.getElementById('prov-select').addEventListener('change', (e) => {
        const idx = e.target.value;
        const content = document.getElementById('prov-content');
        if (idx === "") {
            content.innerHTML = `
                <div style="text-align: center; padding: 60px; color: var(--text-sec); border: 1px dashed var(--border); border-radius: 12px; background: rgba(0,0,0,0.2);">
                    <i class="bi bi-diagram-3" style="font-size: 2.5rem; margin-bottom: 16px; display: block; color: var(--border);"></i>
                    <p style="font-size: 1.1rem;">Select a candidate above to view their data lineage.</p>
                </div>
            `;
            return;
        }
        
        const c = scored[idx];
        renderCandidateProvenance(content, c);
    });
}

function renderCandidateProvenance(container, c) {
    const prov = c.provenance || [];
    if (prov.length === 0) {
        container.innerHTML = `<div class="card" style="animation: fadeIn 0.3s ease;"><p style="color: var(--warning);"><i class="bi bi-exclamation-triangle"></i> No provenance metadata found for this candidate.</p></div>`;
        return;
    }
    
    // Group provenance by field
    const grouped = {};
    prov.forEach(p => {
        if (!grouped[p.field]) grouped[p.field] = [];
        grouped[p.field].push(p);
    });
    
    let tableRows = Object.keys(grouped).map(field => {
        const records = grouped[field];
        const winningSource = records[0].source;
        const mergeMethod = records[0].method;
        const availableSources = [...new Set(records.map(r => Utils.cleanSourceName(r.source)))].join(', ');
        
        return `
            <tr style="border-bottom: 1px solid var(--border); transition: var(--trans-fast);">
                <td style="padding: 16px; font-family: monospace; color: var(--text-sec);">${Utils.escapeHtml(field)}</td>
                <td style="padding: 16px;">
                    <span style="background: rgba(37,99,235,0.1); color: var(--primary); padding: 4px 10px; border-radius: 999px; font-size: 0.8rem; font-weight: 500; border: 1px solid rgba(37,99,235,0.2);">
                        ${Utils.escapeHtml(Utils.cleanSourceName(winningSource))}
                    </span>
                </td>
                <td style="padding: 16px; color: var(--text-sec);">${Utils.escapeHtml(mergeMethod)}</td>
                <td style="padding: 16px; color: var(--text-sec); font-size: 0.9rem;">${Utils.escapeHtml(availableSources)}</td>
            </tr>
        `;
    }).join('');
    
    container.innerHTML = `
        <div class="card" style="animation: fadeIn 0.3s ease;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
                <h3 style="font-size: 1.2rem;">Data Origin Lineage</h3>
                <span style="color: var(--text-sec); font-size: 0.9rem; background: rgba(34,197,94,0.1); color: var(--success); padding: 4px 10px; border-radius: 6px;"><i class="bi bi-shield-check"></i> Fully Auditable</span>
            </div>
            
            <div style="overflow-x: auto;">
                <table style="width: 100%; border-collapse: collapse; text-align: left;">
                    <thead>
                        <tr style="background: rgba(0,0,0,0.2); border-bottom: 1px solid var(--border); font-size: 0.85rem; text-transform: uppercase; color: var(--text-sec);">
                            <th style="padding: 16px;">Field</th>
                            <th style="padding: 16px;">Winning Source</th>
                            <th style="padding: 16px;">Merge Method</th>
                            <th style="padding: 16px;">Available Sources</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${tableRows}
                    </tbody>
                </table>
            </div>
        </div>
    `;
}
