/**
 * Reusable Chart.js wrappers customized for the Dark Theme
 */
const Charts = {
    // Global defaults for dark theme
    initDefaults() {
        if (!window.Chart) return;
        Chart.defaults.color = '#CBD5E1'; // var(--text-sec)
        Chart.defaults.font.family = "'Inter', -apple-system, sans-serif";
        if (Chart.defaults.plugins && Chart.defaults.plugins.legend) {
            Chart.defaults.plugins.legend.labels.color = '#CBD5E1';
        }
    },

    // Render a Bar Chart
    renderBarChart(canvasId, label, labels, data, color = '#2563EB') {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;
        
        return new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: label,
                    data: data,
                    backgroundColor: color,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: '#334155' } // var(--border)
                    },
                    x: {
                        grid: { display: false }
                    }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    },

    // Render a Doughnut Chart
    renderDoughnutChart(canvasId, labels, data, colors) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;
        
        return new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: colors,
                    borderWidth: 0,
                    hoverOffset: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '70%',
                plugins: {
                    legend: { position: 'bottom' }
                }
            }
        });
    }
};

// Initialize Chart defaults on load
Charts.initDefaults();
