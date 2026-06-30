/**
 * Application State
 */
const AppState = {
    data: null, // Holds the output.json payload
    currentView: 'dashboard'
};

/**
 * Initialize Application
 */
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    loadData();
    
    // Listen for hash changes to trigger SPA routing
    window.addEventListener('hashchange', handleRoute);
    
    // Add global refresh for file uploads
    window.triggerGlobalRefresh = () => {
        loadData();
    };
});

/**
 * Navigation & Routing
 */
function initNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            // Hash changes automatically via href="#..."
        });
    });
}

function handleRoute() {
    // Default to dashboard if no hash is present
    const hash = window.location.hash.replace('#', '') || 'dashboard';
    
    // Update active class in sidebar
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.toggle('active', link.getAttribute('data-target') === hash);
    });
    
    AppState.currentView = hash;
    renderView();
}

/**
 * Fetch and Cache ETL Data
 */
async function loadData() {
    const statusBadge = document.getElementById('pipeline-status');
    
    try {
        const response = await fetch('/api/run');
        
        if (!response.ok) throw new Error('Failed to run pipeline API');
        
        const result = await response.json();
        
        if (result.success) {
            statusBadge.className = 'status-badge success';
            statusBadge.innerHTML = '<i class="bi bi-check-circle-fill"></i> Pipeline Complete';
            handleRoute();
        } else {
            throw new Error(result.error);
        }
    } catch (error) {
        console.error("Error loading data:", error);
        
        statusBadge.className = 'status-badge error';
        statusBadge.innerHTML = '<i class="bi bi-exclamation-triangle-fill"></i> Load Failed';
        
        document.getElementById('app-content').innerHTML = `
            <div class="card fade-in" style="text-align: center; padding: 40px;">
                <h3 style="color: var(--danger);"><i class="bi bi-exclamation-triangle"></i> Error Connecting to Backend</h3>
                <p style="color: var(--text-sec); margin-top: 12px;">
                    Ensure you are running the Flask server: <code>python server.py</code>
                </p>
                <p style="color: var(--text-sec); margin-top: 8px;">
                    Failed to fetch: <code>/api/run</code>
                </p>
            </div>
        `;
    }
}

/**
 * View Orchestrator
 */
function renderView() {
    const container = document.getElementById('app-content');
    container.innerHTML = '<div style="text-align: center; padding: 40px; color: var(--text-sec);"><i class="bi bi-arrow-repeat spin" style="font-size: 2rem;"></i> Loading...</div>'; 
    
    switch (AppState.currentView) {
        case 'dashboard':
            if (typeof renderDashboard === 'function') renderDashboard(container);
            break;
        case 'datasources':
            if (typeof renderDataSources === 'function') renderDataSources(container);
            break;
        case 'candidates':
            if (typeof renderCandidates === 'function') renderCandidates(container);
            break;
        case 'analytics':
            if (typeof renderAnalytics === 'function') renderAnalytics(container);
            break;
        case 'provenance':
            if (typeof renderProvenance === 'function') renderProvenance(container);
            break;
        case 'jsonviewer':
            if (typeof renderJsonViewer === 'function') renderJsonViewer(container);
            break;
        default:
            container.innerHTML = `<h2 class="fade-in" style="color: var(--text-sec);">404 - View Not Found</h2>`;
    }
}
