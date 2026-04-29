/**
 * machine.js — Detailed machine view logic, fetches machine data and node-red mock data
 */

let charts = {};

async function loadMachineDetails() {
    try {
        const res = await fetch(`/api/machines/${MACHINE_ID}/details`);
        if (!res.ok) {
            console.error('Error fetching machine details');
            return;
        }
        const data = await res.json();
        
        // Hide loader, show content
        document.getElementById('loader').style.display = 'none';
        document.getElementById('machine-content').style.display = 'block';

        populateUI(data);
        renderGauges(data);
    } catch (e) {
        console.error('Failed to load machine details:', e);
    }
}

function getColor(val) {
    if (val >= 85) return '#3fb950'; // Green
    if (val >= 70) return '#d29922'; // Yellow
    return '#f85149'; // Red
}

function populateUI(m) {
    // Header
    document.getElementById('m-nom').textContent = m.nom;
    document.getElementById('m-usine').textContent = m.usine_nom;

    // Status Badge
    const statusBadge = document.getElementById('m-status-badge');
    const statusDot = document.getElementById('m-status-dot');
    document.getElementById('m-status-text').textContent = m.status.toUpperCase();
    
    statusBadge.className = 'badge ' + (m.status === 'online' ? 'badge-green' : 'badge-red') + ' badge-live';
    statusDot.className = 'status-dot ' + (m.status === 'online' ? 'online' : 'offline');

    // Production Data (Mock from Node-RED)
    const mock = m.mock_live_data;
    document.getElementById('m-pieces-ok').textContent = mock.pieces_ok;
    document.getElementById('m-pieces-rebus').textContent = mock.pieces_rebus;
    document.getElementById('m-cycle-time').innerHTML = `${mock.cycle_time} <span style="font-size: 13px; color: var(--text-secondary);">s/part</span>`;
    document.getElementById('m-cadence').innerHTML = `${m.cadence_theorique} <span style="font-size: 13px; color: var(--text-secondary);">parts/min</span>`;
    
    // IoT environment
    document.getElementById('m-temp').innerHTML = `${mock.temperature} <span style="font-size: 13px; color: var(--text-secondary);">°C</span>`;
    document.getElementById('m-vib').innerHTML = `${mock.vibration} <span style="font-size: 13px; color: var(--text-secondary);">mm/s</span>`;

    const sensorBadge = document.getElementById('m-sensor-health');
    sensorBadge.textContent = mock.sensor_health;
    sensorBadge.className = 'badge ' + (mock.sensor_health === 'Optimal' ? 'badge-green' : 'badge-red');
}

function renderGauges(m) {
    updateOrCreateGauge('gauge-trs', m.trs, 'm-trs-val', null);
    updateOrCreateGauge('gauge-tdo', m.tdo, 'm-tdo-val', null);
    updateOrCreateGauge('gauge-tp', m.tp, 'm-tp-val', null);
    updateOrCreateGauge('gauge-tq', m.tq, 'm-tq-val', null);
}

function updateOrCreateGauge(canvasId, value, valueId, badgeId) {
    document.getElementById(valueId).textContent = value + '%';
    document.getElementById(valueId).style.color = getColor(value);
    
    if (badgeId) {
        const badge = document.getElementById(badgeId);
        badge.textContent = value >= 85 ? 'Optimal' : value >= 70 ? 'Warning' : 'Critical';
        badge.className = 'badge ' + (value >= 85 ? 'badge-green' : value >= 70 ? 'badge-yellow' : 'badge-red');
    }

    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    const color = getColor(value);

    if (charts[canvasId]) {
        // Update existing chart smoothly
        charts[canvasId].data.datasets[0].data = [value, 100 - value];
        charts[canvasId].data.datasets[0].backgroundColor[0] = color;
        charts[canvasId].update();
    } else {
        // Create new chart
        charts[canvasId] = new Chart(ctx, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [value, 100 - value],
                    backgroundColor: [color, '#21262d'],
                    borderWidth: 0, circumference: 180, rotation: 270,
                }]
            },
            options: {
                responsive: true, maintainAspectRatio: false, cutout: '75%',
                plugins: { legend: { display: false }, tooltip: { enabled: false } },
            }
        });
    }
}

// Initial pull
loadMachineDetails();

// Refresh every 30 seconds
setInterval(loadMachineDetails, 30000);
