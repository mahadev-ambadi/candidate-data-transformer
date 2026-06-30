/**
 * Utility functions for formatting and data manipulation
 */
const Utils = {
    // Format a decimal confidence score to a clean percentage
    formatConfidence(score) {
        if (score == null) return "0%";
        return Math.round(score * 100) + "%";
    },

    // Get color for confidence badge based on score
    getConfidenceColor(score) {
        if (score >= 0.90) return 'var(--success)';
        if (score >= 0.70) return 'var(--warning)';
        return 'var(--danger)';
    },
    
    // Clean a source filename for display (e.g. "github_profiles.json" -> "GitHub")
    cleanSourceName(name) {
        if (!name) return "Unknown";
        const clean = name.toUpperCase()
            .replace('.JSON', '')
            .replace('.CSV', '')
            .replace('.TXT', '')
            .replace(/_/g, ' ')
            .trim();
            
        const dict = {
            "ATS": "ATS",
            "CSV": "CSV",
            "TXT": "TXT",
            "GITHUB": "GitHub",
            "GITHUB PROFILES": "GitHub"
        };
        
        // Exact match
        if (dict[clean]) return dict[clean];
        
        // Substring match
        for (const [key, value] of Object.entries(dict)) {
            if (clean.includes(key)) return value;
        }
        
        return clean.toLowerCase().replace(/\b\w/g, s => s.toUpperCase());
    },
    
    // Safely escape HTML to prevent XSS
    escapeHtml(unsafe) {
        if (!unsafe) return '';
        return unsafe
             .toString()
             .replace(/&/g, "&amp;")
             .replace(/</g, "&lt;")
             .replace(/>/g, "&gt;")
             .replace(/"/g, "&quot;")
             .replace(/'/g, "&#039;");
    }
};
