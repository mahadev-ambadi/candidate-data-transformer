async function renderAnalytics(container) {
    const response = await fetch('/api/analytics');
    const data = await response.json();
    const stats = data.stats || {};
    const scored = data.scored_candidates || [];
    
    // Calculate Math
    const duplicateReduction = stats.raw > 0 ? 
        ((stats.raw - stats.merged) / stats.raw * 100).toFixed(1) : 0;
        
    let totalSkills = 0;
    scored.forEach(c => totalSkills += (c.skills ? c.skills.length : 0));
    const avgSkills = scored.length > 0 ? (totalSkills / scored.length).toFixed(1) : 0;
    
    // Calculate Merge Enrichment Metrics
    let beforeMergeSkills = 0;
    let beforeCount = 0;
    const rawCands = data.raw_candidates || [];
    rawCands.forEach(c => {
        if (c.skills) beforeMergeSkills += c.skills.length;
        beforeCount++;
    });
    const avgSkillsBefore = beforeCount > 0 ? (beforeMergeSkills / beforeCount).toFixed(1) : 0;
    
    container.innerHTML = `
        <div class="fade-in" style="margin-bottom: 24px;">
            <h2 style="font-size: 1.8rem; font-weight: 600; margin-bottom: 8px;">Advanced Analytics</h2>
            <p style="color: var(--text-sec);">Deep dive into deduplication efficiency and data quality enrichment.</p>
        </div>
        
        <!-- KPI Cards -->
        <div class="fade-in" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 24px; margin-bottom: 32px;">
            <div class="card" style="border-left: 4px solid var(--success);">
                <div style="color: var(--text-sec); font-size: 0.85rem; font-weight: 600; text-transform: uppercase;">Duplicate Reduction</div>
                <div style="font-size: 2.2rem; font-weight: 700; color: var(--success); margin-top: 8px;">${duplicateReduction}%</div>
                <div style="color: var(--text-sec); font-size: 0.85rem; margin-top: 8px;">Compressed from ${stats.raw} to ${stats.merged} profiles</div>
            </div>
            
            <div class="card" style="border-left: 4px solid var(--warning);">
                <div style="color: var(--text-sec); font-size: 0.85rem; font-weight: 600; text-transform: uppercase;">Merge Enrichment (Skills)</div>
                <div style="display: flex; align-items: center; gap: 16px; margin-top: 8px;">
                    <div style="font-size: 1.5rem; font-weight: 600; color: var(--text-sec); text-decoration: line-through;">${avgSkillsBefore}</div>
                    <i class="bi bi-arrow-right" style="font-size: 1.5rem; color: var(--primary);"></i>
                    <div style="font-size: 2.2rem; font-weight: 700; color: var(--warning);">${avgSkills}</div>
                </div>
                <div style="color: var(--text-sec); font-size: 0.85rem; margin-top: 8px;">Avg skills per profile (Before vs After)</div>
            </div>
        </div>
        
        <!-- Charts Grid -->
        <div class="fade-in" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 24px;">
            <div class="card" style="display: flex; flex-direction: column;">
                <h3 style="font-size: 1.1rem; margin-bottom: 20px;">Top Extracted Skills</h3>
                <div style="position: relative; flex: 1; min-height: 300px;">
                    <canvas id="analyticsSkillsChart"></canvas>
                </div>
            </div>
            
            <div class="card" style="display: flex; flex-direction: column;">
                <h3 style="font-size: 1.1rem; margin-bottom: 20px;">Confidence Distribution</h3>
                <div style="position: relative; flex: 1; min-height: 300px;">
                    <canvas id="analyticsConfChart"></canvas>
                </div>
            </div>
        </div>
    `;
    
    // Render Charts
    setTimeout(() => {
        // Skills Bar Chart
        const skillCounts = {};
        scored.forEach(c => {
            if (c.skills) {
                c.skills.forEach(s => {
                    const sn = typeof s === 'string' ? s : s.name;
                    skillCounts[sn] = (skillCounts[sn] || 0) + 1;
                });
            }
        });
        
        const sortedSkills = Object.entries(skillCounts)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 10);
            
        Charts.renderBarChart('analyticsSkillsChart', 'Candidates with Skill', 
            sortedSkills.map(s => s[0]), 
            sortedSkills.map(s => s[1]),
            '#8B5CF6'
        );
        
        // Confidence Distribution Doughnut
        const buckets = {"90-100%": 0, "80-89%": 0, "70-79%": 0, "<70%": 0};
        scored.forEach(c => {
            const conf = c.overall_confidence || 0;
            if (conf >= 0.9) buckets["90-100%"]++;
            else if (conf >= 0.8) buckets["80-89%"]++;
            else if (conf >= 0.7) buckets["70-79%"]++;
            else buckets["<70%"]++;
        });
        
        Charts.renderDoughnutChart('analyticsConfChart', 
            Object.keys(buckets), 
            Object.values(buckets), 
            ['#22C55E', '#2563EB', '#F59E0B', '#EF4444']
        );
    }, 0);
}
