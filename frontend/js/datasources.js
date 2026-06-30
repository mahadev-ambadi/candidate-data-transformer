async function renderDataSources(container) {
    container.innerHTML = `
        <div class="fade-in" style="margin-bottom: 24px;">
            <h2 style="font-size: 1.8rem; font-weight: 600; margin-bottom: 8px;">Data Sources</h2>
            <p style="color: var(--text-sec);">Upload extraction files to run the deterministic ETL pipeline.</p>
        </div>
        
        <div class="fade-in" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 24px; margin-bottom: 32px;">
            <!-- ATS JSON -->
            <div class="card" style="display: flex; flex-direction: column;">
                <h3 style="font-size: 1.1rem; margin-bottom: 8px;"><i class="bi bi-filetype-json" style="color: #2563EB;"></i> ATS JSON</h3>
                <p style="color: var(--text-sec); font-size: 0.85rem; margin-bottom: 16px;">Expected: ats.json</p>
                <div style="margin-top: auto;">
                    <input type="file" id="file-ats" accept=".json" style="display: none;" onchange="handleFileSelect('file-ats', 'ats-status', 'ats.json')">
                    <button class="upload-btn" onclick="document.getElementById('file-ats').click()" style="width: 100%; padding: 10px; background: rgba(255,255,255,0.05); border: 1px solid var(--border); color: var(--text-main); border-radius: 6px; cursor: pointer;">
                        Choose File
                    </button>
                    <div id="ats-status" style="margin-top: 8px; font-size: 0.8rem; color: var(--text-sec); text-align: center;">Waiting...</div>
                </div>
            </div>
            
            <!-- Recruiter CSV -->
            <div class="card" style="display: flex; flex-direction: column;">
                <h3 style="font-size: 1.1rem; margin-bottom: 8px;"><i class="bi bi-filetype-csv" style="color: #22C55E;"></i> Recruiter CSV</h3>
                <p style="color: var(--text-sec); font-size: 0.85rem; margin-bottom: 16px;">Expected: recruiter.csv</p>
                <div style="margin-top: auto;">
                    <input type="file" id="file-csv" accept=".csv" style="display: none;" onchange="handleFileSelect('file-csv', 'csv-status', 'recruiter.csv')">
                    <button class="upload-btn" onclick="document.getElementById('file-csv').click()" style="width: 100%; padding: 10px; background: rgba(255,255,255,0.05); border: 1px solid var(--border); color: var(--text-main); border-radius: 6px; cursor: pointer;">
                        Choose File
                    </button>
                    <div id="csv-status" style="margin-top: 8px; font-size: 0.8rem; color: var(--text-sec); text-align: center;">Waiting...</div>
                </div>
            </div>
            
            <!-- GitHub JSON -->
            <div class="card" style="display: flex; flex-direction: column;">
                <h3 style="font-size: 1.1rem; margin-bottom: 8px;"><i class="bi bi-github" style="color: #A78BFA;"></i> GitHub Profiles</h3>
                <p style="color: var(--text-sec); font-size: 0.85rem; margin-bottom: 16px;">Expected: github_profiles.json</p>
                <div style="margin-top: auto;">
                    <input type="file" id="file-gh" accept=".json" style="display: none;" onchange="handleFileSelect('file-gh', 'gh-status', 'github_profiles.json')">
                    <button class="upload-btn" onclick="document.getElementById('file-gh').click()" style="width: 100%; padding: 10px; background: rgba(255,255,255,0.05); border: 1px solid var(--border); color: var(--text-main); border-radius: 6px; cursor: pointer;">
                        Choose File
                    </button>
                    <div id="gh-status" style="margin-top: 8px; font-size: 0.8rem; color: var(--text-sec); text-align: center;">Waiting...</div>
                </div>
            </div>
            
            <!-- Recruiter Notes -->
            <div class="card" style="display: flex; flex-direction: column;">
                <h3 style="font-size: 1.1rem; margin-bottom: 8px;"><i class="bi bi-filetype-txt" style="color: #F59E0B;"></i> Recruiter Notes</h3>
                <p style="color: var(--text-sec); font-size: 0.85rem; margin-bottom: 16px;">Expected: recruiter_notes.txt</p>
                <div style="margin-top: auto;">
                    <input type="file" id="file-txt" accept=".txt" style="display: none;" onchange="handleFileSelect('file-txt', 'txt-status', 'recruiter_notes.txt')">
                    <button class="upload-btn" onclick="document.getElementById('file-txt').click()" style="width: 100%; padding: 10px; background: rgba(255,255,255,0.05); border: 1px solid var(--border); color: var(--text-main); border-radius: 6px; cursor: pointer;">
                        Choose File
                    </button>
                    <div id="txt-status" style="margin-top: 8px; font-size: 0.8rem; color: var(--text-sec); text-align: center;">Waiting...</div>
                </div>
            </div>
        </div>
        
        <div class="fade-in card" style="text-align: center; padding: 40px 20px;">
            <button id="run-etl-btn" disabled onclick="runEtlPipeline()" style="padding: 16px 40px; font-size: 1.2rem; font-weight: 600; background: var(--primary); color: white; border: none; border-radius: 8px; cursor: not-allowed; opacity: 0.5; transition: all 0.3s; display: inline-flex; align-items: center; gap: 12px; box-shadow: 0 4px 12px rgba(37,99,235,0.3);">
                <i class="bi bi-play-fill"></i> Run ETL Pipeline
            </button>
            
            <div id="etl-error" style="margin-top: 16px; color: var(--danger); font-size: 0.9rem; display: none;"></div>
            
            <div id="etl-progress-container" style="display: none; margin-top: 24px; max-width: 400px; margin-left: auto; margin-right: auto; text-align: left;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 0.9rem; color: var(--text-sec);">
                    <span id="etl-progress-text">Initializing...</span>
                </div>
                <div style="width: 100%; height: 8px; background: rgba(255,255,255,0.1); border-radius: 4px; overflow: hidden;">
                    <div id="etl-progress-bar" style="width: 0%; height: 100%; background: var(--primary); transition: width 0.3s ease;"></div>
                </div>
            </div>
        </div>
    `;
    
    // Add hover styles for active button
    setTimeout(() => {
        checkAllFilesUploaded();
    }, 0);
}

// Global functions for inline handlers
window.handleFileSelect = function(inputId, statusId, expectedName) {
    const fileInput = document.getElementById(inputId);
    const statusDiv = document.getElementById(statusId);
    
    if (fileInput.files.length > 0) {
        const file = fileInput.files[0];
        statusDiv.innerHTML = `<span style="color: var(--success);"><i class="bi bi-check-circle"></i> Uploaded: ${file.name}</span>`;
    } else {
        statusDiv.innerHTML = 'Waiting...';
    }
    
    checkAllFilesUploaded();
};

window.checkAllFilesUploaded = function() {
    const hasAts = document.getElementById('file-ats')?.files.length > 0;
    const hasCsv = document.getElementById('file-csv')?.files.length > 0;
    const hasGh = document.getElementById('file-gh')?.files.length > 0;
    const hasTxt = document.getElementById('file-txt')?.files.length > 0;
    
    const btn = document.getElementById('run-etl-btn');
    if (btn) {
        if (hasAts && hasCsv && hasGh && hasTxt) {
            btn.disabled = false;
            btn.style.opacity = '1';
            btn.style.cursor = 'pointer';
        } else {
            btn.disabled = true;
            btn.style.opacity = '0.5';
            btn.style.cursor = 'not-allowed';
        }
    }
};

window.runEtlPipeline = async function() {
    const btn = document.getElementById('run-etl-btn');
    const errorDiv = document.getElementById('etl-error');
    const progCont = document.getElementById('etl-progress-container');
    const progText = document.getElementById('etl-progress-text');
    const progBar = document.getElementById('etl-progress-bar');
    
    btn.disabled = true;
    btn.style.opacity = '0.5';
    errorDiv.style.display = 'none';
    progCont.style.display = 'block';
    
    const formData = new FormData();
    formData.append('ats.json', document.getElementById('file-ats').files[0]);
    formData.append('recruiter.csv', document.getElementById('file-csv').files[0]);
    formData.append('github_profiles.json', document.getElementById('file-gh').files[0]);
    formData.append('recruiter_notes.txt', document.getElementById('file-txt').files[0]);
    
    // Simulate UI progress steps
    const steps = [
        { msg: "Uploading...", pct: 20, time: 500 },
        { msg: "Validating...", pct: 40, time: 600 },
        { msg: "Running Pipeline...", pct: 70, time: 800 },
        { msg: "Merging...", pct: 90, time: 500 }
    ];
    
    let stepPromise = Promise.resolve();
    steps.forEach(step => {
        stepPromise = stepPromise.then(() => new Promise(res => {
            setTimeout(() => {
                progText.innerText = step.msg;
                progBar.style.width = step.pct + '%';
                res();
            }, step.time);
        }));
    });
    
    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        await stepPromise; // Wait for the visual progress to finish at least
        
        if (result.success) {
            progText.innerText = "Completed!";
            progBar.style.width = '100%';
            progBar.style.background = 'var(--success)';
            
            setTimeout(() => {
                // Redirect to dashboard to see results
                window.location.hash = '#dashboard';
                if (window.triggerGlobalRefresh) {
                    window.triggerGlobalRefresh();
                }
            }, 1000);
        } else {
            throw new Error(result.error || "Unknown error occurred");
        }
    } catch (e) {
        progCont.style.display = 'none';
        errorDiv.innerText = e.message;
        errorDiv.style.display = 'block';
        btn.disabled = false;
        btn.style.opacity = '1';
    }
};
