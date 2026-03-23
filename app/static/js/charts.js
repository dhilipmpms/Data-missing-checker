/**
 * charts.js
 * ----------
 * Renders Chart.js charts on the report dashboard page.
 * Reads data from the `reportData` global variable injected by report.html.
 *
 * Charts:
 *   1. Missing Values Bar Chart
 *   2. Data Types Doughnut Chart
 */

(function () {
    'use strict';

    // Guard: only run if Chart.js is loaded and reportData is available
    if (typeof Chart === 'undefined' || typeof reportData === 'undefined') return;

    // ── Shared Chart Defaults ────────────────────────────────────────────────
    Chart.defaults.color = '#94a3b8';
    Chart.defaults.borderColor = 'rgba(255,255,255,0.06)';

    /* ════════════════════════════════════════════════
       Chart 1: Missing Values per Column (Bar)
    ════════════════════════════════════════════════ */
    const missingCtx = document.getElementById('missingChart');
    if (missingCtx) {
        const columns = Object.keys(reportData.missingValues);
        const counts = columns.map(c => reportData.missingValues[c].count);
        const percents = columns.map(c => reportData.missingValues[c].percentage);

        // Color bars: green if 0 missing, amber if low, red if high
        const barColors = percents.map(p => {
            if (p === 0) return 'rgba(16, 185, 129, 0.6)';
            if (p <= 5) return 'rgba(245, 158, 11, 0.7)';
            if (p <= 20) return 'rgba(249, 115, 22, 0.7)';
            return 'rgba(239, 68, 68, 0.7)';
        });

        new Chart(missingCtx, {
            type: 'bar',
            data: {
                labels: columns,
                datasets: [{
                    label: 'Missing Values',
                    data: counts,
                    backgroundColor: barColors,
                    borderColor: barColors.map(c => c.replace('0.7', '1').replace('0.6', '1')),
                    borderWidth: 1,
                    borderRadius: 4,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => {
                                const col = columns[ctx.dataIndex];
                                const pct = percents[ctx.dataIndex];
                                return ` ${ctx.raw} missing (${pct}%)`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: { color: 'rgba(255,255,255,0.05)' },
                        ticks: { maxRotation: 35, font: { size: 11 } }
                    },
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(255,255,255,0.05)' },
                        ticks: { precision: 0, font: { size: 11 } }
                    }
                }
            }
        });
    }

    /* ════════════════════════════════════════════════
       Chart 2: Data Types Doughnut
    ════════════════════════════════════════════════ */
    const typeCtx = document.getElementById('typeChart');
    if (typeCtx) {
        // Aggregate dtype counts
        const typeCounts = {};
        Object.values(reportData.dataTypes).forEach(dtype => {
            // Simplify type names for readability
            let label = dtype;
            if (dtype.startsWith('int')) label = 'Integer';
            if (dtype.startsWith('float')) label = 'Float';
            if (dtype === 'object') label = 'Text/Object';
            if (dtype.startsWith('bool')) label = 'Boolean';
            if (dtype.startsWith('date')) label = 'DateTime';
            typeCounts[label] = (typeCounts[label] || 0) + 1;
        });

        const typeLabels = Object.keys(typeCounts);
        const typeData = Object.values(typeCounts);
        const palette = [
            '#3b82f6', '#8b5cf6', '#10b981',
            '#f59e0b', '#ef4444', '#06b6d4', '#ec4899'
        ];

        new Chart(typeCtx, {
            type: 'doughnut',
            data: {
                labels: typeLabels,
                datasets: [{
                    data: typeData,
                    backgroundColor: palette.slice(0, typeLabels.length).map(c => c + 'cc'),
                    borderColor: palette.slice(0, typeLabels.length),
                    borderWidth: 2,
                    hoverOffset: 6,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { padding: 14, font: { size: 12 }, boxWidth: 14 }
                    },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => ` ${ctx.label}: ${ctx.raw} column(s)`
                        }
                    }
                },
                cutout: '62%',
            }
        });
    }

})();
