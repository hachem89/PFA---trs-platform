/**
 * analysis.js — TRS trend charts, metric toggles, comparison.
 */

let mainChart = null;
let compareChart = null;
let historyData = null;
let allMachinesData = null;
let activeMetrics = ['trs'];

const metricColors = { trs: '#3fb950', tdo: '#58a6ff', tp: '#a371f7', tq: '#d29922' };
const metricLabels = { trs: 'TRS', tdo: 'TDO (Availability)', tp: 'TP (Performance)', tq: 'TQ (Quality)' };

async function initAnalysis() {
    const res = await fetch('/api/usines');
    const usines = await res.json();
    const select = document.getElementById('machine-select');
    select.innerHTML = '';
    usines.forEach(u => {
        u.machines.forEach(m => {
            const opt = document.createElement('option');
            opt.value = m.id;
            opt.textContent = `${m.nom} (${u.nom})`;
            select.appendChild(opt);
        });
    });
    if (select.options.length > 0) {
        loadHistory();
        loadComparison();
    }
}

async function loadHistory() {
    const machineId = document.getElementById('machine-select').value;
    const days = document.getElementById('period-select').value;
    if (!machineId) return;
    const res = await fetch(`/api/machines/${machineId}/history?days=${days}`);
    historyData = await res.json();
    renderChart();
    renderStats();
    loadComparison();
}

function toggleMetric(btn) {
    const metric = btn.dataset.metric;
    if (activeMetrics.includes(metric)) {
        if (activeMetrics.length > 1) {
            activeMetrics = activeMetrics.filter(m => m !== metric);
            btn.classList.remove('active');
        }
    } else {
        activeMetrics.push(metric);
        btn.classList.add('active');
    }
    renderChart();
    renderStats();
}

function renderChart() {
    if (!historyData || !historyData.data.length) return;

    const labels = historyData.data.map(d => {
        const date = new Date(d.date);
        return date.toLocaleDateString('en-US', { day: '2-digit', month: 'short' });
    });

    const datasets = activeMetrics.map(metric => ({
        label: metricLabels[metric],
        data: historyData.data.map(d => d[metric]),
        borderColor: metricColors[metric],
        backgroundColor: metricColors[metric] + '15',
        fill: activeMetrics.length === 1,
        tension: 0.4, pointRadius: 3, pointHoverRadius: 6, borderWidth: 2,
    }));

    const ctx = document.getElementById('main-chart');
    if (mainChart) mainChart.destroy();

    document.getElementById('chart-title').textContent = `Evolution — ${historyData.machine_nom}`;
    document.getElementById('chart-subtitle').textContent =
        `${activeMetrics.map(m => metricLabels[m]).join(' · ')} over ${historyData.data.length} days`;

    mainChart = new Chart(ctx, {
        type: 'line',
        data: { labels, datasets },
        options: {
            responsive: true, maintainAspectRatio: false,
            interaction: { intersect: false, mode: 'index' },
            plugins: {
                legend: {
                    display: activeMetrics.length > 1,
                    labels: { color: '#8b949e', font: { size: 11 }, usePointStyle: true }
                },
                tooltip: {
                    backgroundColor: '#161b22', borderColor: '#30363d', borderWidth: 1,
                    titleColor: '#e6edf3', bodyColor: '#8b949e', padding: 12, displayColors: true,
                    callbacks: { label: (ctx) => ` ${ctx.dataset.label}: ${ctx.parsed.y}%` }
                }
            },
            scales: {
                x: { grid: { color: '#21262d', drawBorder: false }, ticks: { color: '#484f58', font: { size: 10 } } },
                y: { min: 0, max: 100, grid: { color: '#21262d', drawBorder: false }, ticks: { color: '#484f58', font: { size: 10 }, callback: v => v + '%' } }
            }
        }
    });
}

function renderStats() {
    if (!historyData || !historyData.data.length) return;
    const metric = activeMetrics[0];
    const values = historyData.data.map(d => d[metric]);
    const avg = (values.reduce((a, b) => a + b, 0) / values.length).toFixed(1);
    const max = Math.max(...values).toFixed(1);
    const min = Math.min(...values).toFixed(1);
    const trend = values.length >= 2 ? (values[values.length - 1] - values[0]).toFixed(1) : 0;

    const avgEl = document.getElementById('stat-avg');
    avgEl.textContent = avg + '%';
    avgEl.className = 'stat-value ' + (avg >= 85 ? 'c-green' : avg >= 70 ? 'c-yellow' : 'c-red');
    document.getElementById('stat-max').textContent = max + '%';
    document.getElementById('stat-min').textContent = min + '%';
    const trendEl = document.getElementById('stat-trend');
    trendEl.textContent = (trend >= 0 ? '+' : '') + trend + '%';
    trendEl.className = 'stat-value ' + (trend >= 0 ? 'c-green' : 'c-red');
}

async function loadComparison() {
    const days = document.getElementById('period-select').value;
    const res = await fetch(`/api/all-machines-history?days=${days}`);
    allMachinesData = await res.json();
    renderComparison();
}

function renderComparison() {
    if (!allMachinesData || !allMachinesData.length) return;
    const colors = ['#3fb950', '#58a6ff', '#a371f7', '#d29922', '#f85149', '#f778ba', '#79c0ff', '#56d364'];
    const allDates = new Set();
    allMachinesData.forEach(m => m.data.forEach(d => allDates.add(d.date)));
    const sortedDates = [...allDates].sort();
    const labels = sortedDates.map(d => {
        const date = new Date(d);
        return date.toLocaleDateString('en-US', { day: '2-digit', month: 'short' });
    });
    const datasets = allMachinesData.map((m, i) => {
        const dateMap = {};
        m.data.forEach(d => { dateMap[d.date] = d.trs; });
        return {
            label: `${m.machine_nom} (${m.usine_nom})`,
            data: sortedDates.map(d => dateMap[d] || null),
            borderColor: colors[i % colors.length],
            backgroundColor: 'transparent', tension: 0.4, pointRadius: 2, borderWidth: 2,
        };
    });
    const ctx = document.getElementById('compare-chart');
    if (compareChart) compareChart.destroy();
    compareChart = new Chart(ctx, {
        type: 'line', data: { labels, datasets },
        options: {
            responsive: true, maintainAspectRatio: false,
            interaction: { intersect: false, mode: 'index' },
            plugins: {
                legend: { labels: { color: '#8b949e', font: { size: 11 }, usePointStyle: true } },
                tooltip: { backgroundColor: '#161b22', borderColor: '#30363d', borderWidth: 1, titleColor: '#e6edf3', bodyColor: '#8b949e', padding: 12 }
            },
            scales: {
                x: { grid: { color: '#21262d', drawBorder: false }, ticks: { color: '#484f58', font: { size: 10 } } },
                y: { min: 0, max: 100, grid: { color: '#21262d', drawBorder: false }, ticks: { color: '#484f58', font: { size: 10 }, callback: v => v + '%' } }
            }
        }
    });
}

// Boot
initAnalysis();
