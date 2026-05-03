/**
 * dashboard.js — KPI rendering, gauge charts, usine filter.
 */

let dashboardData = null;
let activeFilter = 'all';

async function loadDashboard() {
    try {
        const res = await fetch('/api/dashboard-data');
        dashboardData = await res.json();
        renderKPIs();
        renderFilters();
        renderGauges();
    } catch (e) {
        console.error('Dashboard load error:', e);
    }
}

function renderKPIs() {
    const k = dashboardData.kpis;
    const trsEl = document.getElementById('kpi-trs');
    trsEl.textContent = k.trs_moyen + '%';
    trsEl.className = 'kpi-value ' + (k.trs_moyen >= 85 ? 'c-green' : k.trs_moyen >= 70 ? 'c-yellow' : 'c-red');

    document.getElementById('kpi-usines').textContent = k.usines_count;
    document.getElementById('kpi-machines').textContent = k.machines_count;

    const alertEl = document.getElementById('kpi-alerts');
    alertEl.textContent = k.alerts;
    if (k.alerts === 0) {
        alertEl.className = 'kpi-value c-green';
        alertEl.textContent = '0 ✓';
    }
}

function renderFilters() {
    const container = document.getElementById('usine-filter');
    let html = `<button class="usine-chip active" onclick="filterUsine('all')">Toutes</button>`;
    dashboardData.usines.forEach(u => {
        html += `<button class="usine-chip" onclick="filterUsine('${u.id}')">${u.nom}</button>`;
    });
    container.innerHTML = html;
}

function filterUsine(id) {
    activeFilter = id;
    document.querySelectorAll('.usine-chip').forEach(c => c.classList.remove('active'));
    event.target.classList.add('active');
    renderGauges();
}

function renderGauges() {
    const grid = document.getElementById('gauges-grid');
    let machines = [];

    dashboardData.usines.forEach(u => {
        u.machines.forEach(m => {
            if (activeFilter === 'all' || activeFilter === u.id) {
                machines.push({...m, usine_nom: u.nom});
            }
        });
    });

    if (machines.length === 0) {
        grid.innerHTML = `
            <div class="empty-state" style="grid-column: 1/-1;">
                <div class="empty-icon">🏭</div>
                <h3>Aucune machine</h3>
                <p>Ajoutez des usines et machines dans les paramètres</p>
                <a href="/settings" class="btn btn-primary">⚙️ Configurer</a>
            </div>`;
        return;
    }

    grid.innerHTML = machines.map((m, idx) => {
        const trsClass = m.trs >= 85 ? 'badge-green' : m.trs >= 70 ? 'badge-yellow' : 'badge-red';
        return `
        <a href="/machine/${m.id}" class="machine-gauge-card" style="display:block; text-decoration:none; color:inherit;">
            <div class="machine-gauge-header">
                <div>
                    <div class="machine-gauge-name">${m.nom}</div>
                    <div class="machine-gauge-usine">📍 ${m.usine_nom}</div>
                </div>
                <div style="display:flex;align-items:center;gap:8px;">
                    <span class="badge ${trsClass}">${m.trs >= 85 ? 'Optimal' : m.trs >= 70 ? 'Attention' : 'Critique'}</span>
                    <span class="status-dot ${m.status}"></span>
                </div>
            </div>
            <div class="main-gauge">
                <canvas id="g-trs-${idx}" width="160" height="90"></canvas>
                <div class="main-gauge-value" style="color:${getColor(m.trs)}">${m.trs}%</div>
                <div class="main-gauge-label">TRS</div>
            </div>
            <div class="sub-gauges-row">
                <div class="mini-gauge">
                    <canvas id="g-tdo-${idx}" width="70" height="42"></canvas>
                    <div class="mini-gauge-value" style="color:${getColor(m.tdo)}">${m.tdo}%</div>
                    <div class="mini-gauge-label">TDO</div>
                </div>
                <div class="mini-gauge">
                    <canvas id="g-tp-${idx}" width="70" height="42"></canvas>
                    <div class="mini-gauge-value" style="color:${getColor(m.tp)}">${m.tp}%</div>
                    <div class="mini-gauge-label">TP</div>
                </div>
                <div class="mini-gauge">
                    <canvas id="g-tq-${idx}" width="70" height="42"></canvas>
                    <div class="mini-gauge-value" style="color:${getColor(m.tq)}">${m.tq}%</div>
                    <div class="mini-gauge-label">TQ</div>
                </div>
            </div>
        </a>`;
    }).join('');

    // Render gauges after DOM update
    setTimeout(() => {
        machines.forEach((m, idx) => {
            createBigGauge(`g-trs-${idx}`, m.trs);
            createMiniGauge(`g-tdo-${idx}`, m.tdo);
            createMiniGauge(`g-tp-${idx}`, m.tp);
            createMiniGauge(`g-tq-${idx}`, m.tq);
        });
    }, 50);
}

function getColor(val) {
    if (val >= 85) return '#3fb950';
    if (val >= 70) return '#d29922';
    return '#f85149';
}

// --- Gauge Enhancements Plugin ---
const gaugePlugin = {
    id: 'gaugePlugin',
    afterDatasetsDraw(chart, args, options) {
        const { ctx, data, chartArea: { top, bottom, left, right, width, height } } = chart;
        ctx.save();

        const xCenter = chart.getDatasetMeta(0).data[0].x;
        const yCenter = chart.getDatasetMeta(0).data[0].y;
        const outerRadius = chart.getDatasetMeta(0).data[0].outerRadius;
        const innerRadius = chart.getDatasetMeta(0).data[0].innerRadius;
        const value = data.datasets[0].data[0];

        // 1. Draw graduation ticks (0, 25, 50, 75, 100)
        const ticks = [0, 25, 50, 75, 100];
        ctx.strokeStyle = '#8b949e';
        ctx.lineWidth = 2;

        ticks.forEach(t => {
            const angle = Math.PI + (t / 100) * Math.PI;
            const startX = xCenter + Math.cos(angle) * (innerRadius);
            const startY = yCenter + Math.sin(angle) * (innerRadius);
            const endX = xCenter + Math.cos(angle) * (innerRadius + 8);
            const endY = yCenter + Math.sin(angle) * (innerRadius + 8);

            ctx.beginPath();
            ctx.moveTo(startX, startY);
            ctx.lineTo(endX, endY);
            ctx.stroke();
        });

        // 2. Draw Needle
        const needleAngle = Math.PI + (value / 100) * Math.PI;
        ctx.strokeStyle = '#c9d1d9';
        ctx.lineWidth = 3;
        ctx.lineCap = 'round';

        ctx.beginPath();
        ctx.moveTo(xCenter, yCenter);
        ctx.lineTo(xCenter + Math.cos(needleAngle) * (innerRadius + 5), yCenter + Math.sin(needleAngle) * (innerRadius + 5));
        ctx.stroke();

        // 3. Draw Needle Base
        ctx.fillStyle = '#c9d1d9';
        ctx.beginPath();
        ctx.arc(xCenter, yCenter, 5, 0, Math.PI * 2);
        ctx.fill();

        ctx.restore();
    }
};

// Register plugin globally
Chart.register(gaugePlugin);

function createBigGauge(id, value) {
    const ctx = document.getElementById(id);
    if (!ctx) return;
    const color = getColor(value);
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [value, 100 - value],
                backgroundColor: [color, '#21262d'],
                borderWidth: 0, circumference: 180, rotation: 270,
            }]
        },
        options: {
            responsive: false, maintainAspectRatio: false, cutout: '70%',
            layout: { padding: { bottom: 10 } },
            plugins: { legend: { display: false }, tooltip: { enabled: false } },
        }
    });
}

function createMiniGauge(id, value) {
    const ctx = document.getElementById(id);
    if (!ctx) return;
    const color = getColor(value);
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [value, 100 - value],
                backgroundColor: [color, '#21262d'],
                borderWidth: 0, circumference: 180, rotation: 270,
            }]
        },
        options: {
            responsive: false, maintainAspectRatio: false, cutout: '72%',
            layout: { padding: { bottom: 5 } },
            plugins: { legend: { display: false }, tooltip: { enabled: false } },
        }
    });
}

// Boot
loadDashboard();

// Refresh data every 30 seconds
setInterval(loadDashboard, 30000);
