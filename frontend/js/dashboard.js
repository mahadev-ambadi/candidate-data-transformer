/**
 * Renders the Executive Dashboard view
 */
async function renderDashboard(container) {
    const response = await fetch('/api/dashboard');
    const data = await response.json();
    const stats = data.stats || {};
    const scored = data.scored_candidates || [];
    
    // Calculate Average Confidence and Metrics
    let totalConf = 0;
    const uniqueSources = new Set();
    scored.forEach(c => {
        totalConf += (c.overall_confidence || 0);
        if (c.provenance) {
            c.provenance.forEach(p => uniqueSources.add(Utils.cleanSourceName(p.source)));
        }
    });
    const avgConf = scored.length > 0 ? (totalConf / scored.length) : 0;
    const dupRed = stats.raw > 0 ? ((stats.raw - stats.merged) / stats.raw * 100).toFixed(1) : 0;
    
    // HTML Layout
    container.innerHTML = `
        <div class="fade-in" style="margin-bottom: 24px;">
            <h2 style="font-size: 1.8rem; font-weight: 600; margin-bottom: 8px;">Executive Dashboard</h2>
            <p style="color: var(--text-sec);">High-level overview of the ETL pipeline execution.</p>
        </div>
        
        <!-- KPI Cards Grid -->
        <div class="fade-in" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 24px; margin-bottom: 32px;">
            <div class="card">
                <div style="color: var(--text-sec); font-size: 0.85rem; font-weight: 600; text-transform: uppercase;">Raw Records</div>
                <div style="font-size: 2.2rem; font-weight: 700; color: var(--primary); margin-top: 8px;">${stats.raw || 0}</div>
            </div>
            <div class="card">
                <div style="color: var(--text-sec); font-size: 0.85rem; font-weight: 600; text-transform: uppercase;">Validated</div>
                <div style="font-size: 2.2rem; font-weight: 700; color: var(--primary); margin-top: 8px;">${stats.validated || 0}</div>
            </div>
            <div class="card">
                <div style="color: var(--text-sec); font-size: 0.85rem; font-weight: 600; text-transform: uppercase;">Merged Profiles</div>
                <div style="font-size: 2.2rem; font-weight: 700; color: var(--primary); margin-top: 8px;">${stats.merged || 0}</div>
            </div>
            <div class="card">
                <div style="color: var(--text-sec); font-size: 0.85rem; font-weight: 600; text-transform: uppercase;">Merged Duplicates</div>
                <div style="font-size: 2.2rem; font-weight: 700; color: #F59E0B; margin-top: 8px;">${(stats.raw || 0) - (stats.merged || 0)}</div>
            </div>
            <div class="card">
                <div style="color: var(--text-sec); font-size: 0.85rem; font-weight: 600; text-transform: uppercase;">Avg Confidence</div>
                <div style="font-size: 2.2rem; font-weight: 700; color: ${Utils.getConfidenceColor(avgConf)}; margin-top: 8px;">${Utils.formatConfidence(avgConf)}</div>
            </div>
        </div>
        
        <!-- Main Content Area -->
        <div class="fade-in" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 24px;">
            <!-- Funnel Chart -->
            <div class="card" style="display: flex; flex-direction: column;">
                <h3 style="font-size: 1.1rem; margin-bottom: 20px;">Pipeline Funnel</h3>
                <div style="flex: 1; display: flex; flex-direction: column; justify-content: center; align-items: center; gap: 10px;">
                    <div style="background: rgba(37,99,235,1); color: white; padding: 12px; width: 100%; text-align: center; border-radius: 8px; font-weight: 500;">Raw: ${stats.raw || 0}</div>
                    <i class="bi bi-arrow-down" style="color: var(--text-sec); font-size: 1.2rem;"></i>
                    <div style="background: rgba(37,99,235,0.8); color: white; padding: 12px; width: 85%; text-align: center; border-radius: 8px; font-weight: 500;">Validated: ${stats.validated || 0}</div>
                    <i class="bi bi-arrow-down" style="color: var(--text-sec); font-size: 1.2rem;"></i>
                    <div style="background: rgba(37,99,235,0.6); color: white; padding: 12px; width: 70%; text-align: center; border-radius: 8px; font-weight: 500;">Normalized: ${stats.normalized || 0}</div>
                    <i class="bi bi-arrow-down" style="color: var(--text-sec); font-size: 1.2rem;"></i>
                    <div style="background: rgba(34,197,94,0.9); color: white; padding: 12px; width: 55%; text-align: center; border-radius: 8px; font-weight: 500;">Merged: ${stats.merged || 0}</div>
                </div>
            </div>
            
            <!-- Summary Banner & Source Chart -->
            <div style="display: flex; flex-direction: column; gap: 24px;">
                <div class="card" style="background: linear-gradient(135deg, rgba(37,99,235,0.1), rgba(15,23,42,0)); border-left: 4px solid var(--primary);">
                    <h3 style="font-size: 1.1rem; margin-bottom: 12px;"><i class="bi bi-info-circle"></i> Pipeline Summary</h3>
                    <ul style="color: var(--text-sec); font-size: 0.95rem; line-height: 1.6; list-style-type: none; padding: 0;">
                        <li>• <strong style="color: var(--text-main);">${stats.raw || 0}</strong> Raw records processed</li>
                        <li>• <strong style="color: var(--text-main);">${uniqueSources.size}</strong> Number of data sources</li>
                        <li>• <strong style="color: var(--text-main);">${stats.merged || 0}</strong> Unified candidate profiles created</li>
                        <li>• <strong style="color: var(--text-main);">${(stats.raw || 0) - (stats.merged || 0)}</strong> Duplicate records merged</li>
                        <li>• <strong style="color: var(--text-main);">${dupRed}%</strong> Duplicate reduction percentage</li>
                        <li>• <strong style="color: var(--text-main);">${Utils.formatConfidence(avgConf)}</strong> Average confidence score</li>
                    </ul>
                </div>
                
                <div class="card" style="flex: 1; display: flex; flex-direction: column;">
                    <h3 style="font-size: 1.1rem; margin-bottom: 20px;">Source Distribution</h3>
                    <div style="position: relative; flex: 1; min-height: 200px;">
                        <canvas id="dashboardSourceChart"></canvas>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Recent Candidates Table -->
        <div class="card fade-in" style="margin-top: 24px;">
            <h3 style="font-size: 1.1rem; margin-bottom: 20px;">Top Candidates Preview</h3>
            <div style="overflow-x: auto;">
                <table style="width: 100%; border-collapse: collapse; text-align: left;">
                    <thead>
                        <tr style="border-bottom: 1px solid var(--border); color: var(--text-sec); font-size: 0.85rem;">
                            <th style="padding: 12px 16px;">Name</th>
                            <th style="padding: 12px 16px;">Headline</th>
                            <th style="padding: 12px 16px;">Top Skills</th>
                            <th style="padding: 12px 16px;">Confidence</th>
                        </tr>
                    </thead>
                    <tbody id="dashboard-candidates-body">
                        ${generateTableRows(scored.slice(0, 5))}
                    </tbody>
                </table>
            </div>
        </div>
    `;
    
    // Render Charts after DOM injection
    setTimeout(() => {
        // Calculate sources for Doughnut
        const sources = {};
        scored.forEach(c => {
            if (c.provenance) {
                c.provenance.forEach(p => {
                    const src = Utils.cleanSourceName(p.source);
                    sources[src] = (sources[src] || 0) + 1;
                });
            }
        });
        
        const sourceLabels = Object.keys(sources);
        const sourceData = Object.values(sources);
        const colors = ['#2563EB', '#22C55E', '#F59E0B', '#EF4444', '#8B5CF6'];
        
        if (sourceLabels.length > 0) {
            Charts.renderDoughnutChart('dashboardSourceChart', sourceLabels, sourceData, colors);
        }
    }, 0);
}

function generateTableRows(candidates) {
    if (!candidates || candidates.length === 0) {
        return `<tr><td colspan="4" style="padding: 16px; text-align: center; color: var(--text-sec);">No candidates found.</td></tr>`;
    }
    
    return candidates.map(c => {
        const name = Utils.escapeHtml(c.full_name || 'Unknown');
        const headline = Utils.escapeHtml(c.headline || 'N/A');
        
        // Map top 3 skills
        let skillsHtml = '';
        if (c.skills && c.skills.length > 0) {
            skillsHtml = c.skills.slice(0, 3).map(s => {
                const skillName = typeof s === 'string' ? s : s.name;
                return `<span style="background: rgba(37,99,235,0.1); color: var(--primary); padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; margin-right: 6px; white-space: nowrap;">${Utils.escapeHtml(skillName)}</span>`;
            }).join('');
        } else {
            skillsHtml = '<span style="color: var(--text-sec); font-size: 0.85rem;">None</span>';
        }
        
        const confColor = Utils.getConfidenceColor(c.overall_confidence);
        const confText = Utils.formatConfidence(c.overall_confidence);
        
        return `
            <tr style="border-bottom: 1px solid var(--border); transition: var(--trans-fast);">
                <td style="padding: 16px; font-weight: 500;">${name}</td>
                <td style="padding: 16px; color: var(--text-sec); font-size: 0.9rem;">${headline}</td>
                <td style="padding: 16px;">${skillsHtml}</td>
                <td style="padding: 16px;">
                    <span style="color: ${confColor}; font-weight: 600; background: rgba(0,0,0,0.2); padding: 4px 8px; border-radius: 4px;">${confText}</span>
                </td>
            </tr>
        `;
    }).join('');
}
