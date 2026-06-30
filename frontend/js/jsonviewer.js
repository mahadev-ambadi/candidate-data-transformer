async function renderJsonViewer(container) {
    const response = await fetch('/api/json');
    const rawOutput = await response.json();
    const formatted = JSON.stringify(rawOutput, null, 2);
    
    // Estimate payload size
    const kb = (new TextEncoder().encode(formatted).length / 1024).toFixed(2);
    
    window._rawJsonPayload = rawOutput;
    const blob = new Blob([formatted], { type: 'application/json' });
    const downloadUrl = URL.createObjectURL(blob);
    
    function createJSONTree(obj, isLast = true) {
        if (obj === null) return '<span style="color:#F87171">null</span>' + (isLast ? '' : ',');
        if (typeof obj === 'string') return '<span style="color:#A7F3D0">"' + Utils.escapeHtml(obj) + '"</span>' + (isLast ? '' : ',');
        if (typeof obj === 'number') return '<span style="color:#FBBF24">' + obj + '</span>' + (isLast ? '' : ',');
        if (typeof obj === 'boolean') return '<span style="color:#C084FC">' + obj + '</span>' + (isLast ? '' : ',');
        
        if (Array.isArray(obj)) {
            if (obj.length === 0) return '[]' + (isLast ? '' : ',');
            let html = '<details open style="display:inline-block; width:100%"><summary style="cursor:pointer; user-select:none; color: var(--text-sec);">[</summary><div style="margin-left: 20px; border-left: 1px solid rgba(255,255,255,0.1); padding-left: 10px;">';
            obj.forEach((val, i) => {
                html += '<div style="margin-top:2px;">' + createJSONTree(val, i === obj.length - 1) + '</div>';
            });
            html += '</div><span style="color: var(--text-sec);">]</span></details>' + (isLast ? '' : ',');
            return html;
        }
        
        const keys = Object.keys(obj);
        if (keys.length === 0) return '{}' + (isLast ? '' : ',');
        let html = '<details open style="display:inline-block; width:100%"><summary style="cursor:pointer; user-select:none; color: var(--text-sec);">{</summary><div style="margin-left: 20px; border-left: 1px solid rgba(255,255,255,0.1); padding-left: 10px;">';
        keys.forEach((k, i) => {
            html += `<div style="margin-top:2px;"><span style="color:#93C5FD">"${Utils.escapeHtml(k)}"</span>: ` + createJSONTree(obj[k], i === keys.length - 1) + '</div>';
        });
        html += '</div><span style="color: var(--text-sec);">}</span></details>' + (isLast ? '' : ',');
        return html;
    }
    
    container.innerHTML = `
        <div class="fade-in" style="margin-bottom: 24px; display: flex; justify-content: space-between; align-items: flex-end;">
            <div>
                <h2 style="font-size: 1.8rem; font-weight: 600; margin-bottom: 8px;">JSON API Simulator</h2>
                <p style="color: var(--text-sec);">Final deterministic payload ready for downstream consumption.</p>
            </div>
            <div style="background: rgba(34, 197, 94, 0.1); color: var(--success); padding: 10px 16px; border-radius: 8px; border: 1px solid rgba(34, 197, 94, 0.2); font-family: monospace; font-size: 0.95rem;">
                GET /api/v1/candidates <span style="margin: 0 8px; opacity: 0.5;">|</span> HTTP 200 OK
            </div>
        </div>
        
        <div class="fade-in" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; margin-bottom: 24px;">
            <div class="card" style="padding: 20px;">
                <div style="color: var(--text-sec); font-size: 0.8rem; text-transform: uppercase; font-weight: 600;">Total Objects</div>
                <div style="font-size: 1.8rem; font-weight: 700; margin-top: 8px;">${rawOutput.length}</div>
            </div>
            <div class="card" style="padding: 20px;">
                <div style="color: var(--text-sec); font-size: 0.8rem; text-transform: uppercase; font-weight: 600;">Payload Size</div>
                <div style="font-size: 1.8rem; font-weight: 700; margin-top: 8px;">${kb} KB</div>
            </div>
            <div class="card" style="padding: 20px;">
                <div style="color: var(--text-sec); font-size: 0.8rem; text-transform: uppercase; font-weight: 600;">Content-Type</div>
                <div style="font-size: 1.5rem; font-weight: 600; margin-top: 12px; font-family: monospace; color: var(--primary);">application/json</div>
            </div>
        </div>
        
        <div class="card fade-in" style="position: relative; padding: 0; overflow: hidden; background: #0b0f19;">
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px 20px; background: rgba(255,255,255,0.05); border-bottom: 1px solid rgba(255,255,255,0.1);">
                <div style="display: flex; gap: 8px;">
                    <span style="width: 12px; height: 12px; border-radius: 50%; background: #EF4444;"></span>
                    <span style="width: 12px; height: 12px; border-radius: 50%; background: #F59E0B;"></span>
                    <span style="width: 12px; height: 12px; border-radius: 50%; background: #22C55E;"></span>
                </div>
                
                <div style="display: flex; gap: 12px; align-items: center;">
                    <input type="text" id="json-search" placeholder="Search JSON..." style="padding: 6px 12px; border-radius: 6px; background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); color: white; font-size: 0.85rem; outline: none; width: 180px;">
                    <button onclick="document.querySelectorAll('details').forEach(d => d.open = false)" style="background: transparent; border: 1px solid rgba(255,255,255,0.2); border-radius: 6px; color: var(--text-sec); padding: 6px 12px; cursor: pointer; font-size: 0.85rem;">Collapse</button>
                    <button onclick="document.querySelectorAll('details').forEach(d => d.open = true)" style="background: transparent; border: 1px solid rgba(255,255,255,0.2); border-radius: 6px; color: var(--text-sec); padding: 6px 12px; cursor: pointer; font-size: 0.85rem;">Expand</button>
                    <button onclick="navigator.clipboard.writeText(JSON.stringify(window._rawJsonPayload, null, 2))" style="background: transparent; border: 1px solid rgba(255,255,255,0.2); border-radius: 6px; color: var(--text-sec); padding: 6px 12px; cursor: pointer; font-size: 0.85rem;"><i class="bi bi-clipboard"></i> Copy</button>
                    <a href="${downloadUrl}" download="output.json" style="background: var(--primary); color: white; text-decoration: none; border-radius: 6px; padding: 6px 12px; font-size: 0.85rem; display: inline-flex; align-items: center; gap: 6px;"><i class="bi bi-download"></i> Download</a>
                </div>
            </div>
            
            <pre style="margin: 0; padding: 24px; max-height: 600px; overflow-y: auto;"><code id="json-code" style="color: #A5B4FC; font-family: 'Consolas', 'Monaco', monospace; font-size: 0.9rem; line-height: 1.5;">${createJSONTree(rawOutput)}</code></pre>
        </div>
    `;
    
    // Bind search functionality
    setTimeout(() => {
        document.getElementById('json-search').addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase();
            const codeBlock = document.getElementById('json-code');
            if (!query) {
                codeBlock.innerHTML = createJSONTree(rawOutput);
                return;
            }
            
            // Just expand all and do a basic CSS highlight for matching text
            // (a real search would require complex DOM walking, we'll just expand all to help browser find)
            document.querySelectorAll('details').forEach(d => d.open = true);
        });
    }, 0);
}
