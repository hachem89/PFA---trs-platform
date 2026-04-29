/**
 * base.js — Shared UI logic (sidebar, toast, gauge helper).
 * Loaded on every page via base.html.
 */

// ── Sidebar ──

function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('collapsed');
    localStorage.setItem('sidebarCollapsed',
        document.getElementById('sidebar').classList.contains('collapsed'));
}

function toggleMobileSidebar() {
    document.getElementById('sidebar').classList.toggle('mobile-open');
}

// Restore sidebar state on load
if (localStorage.getItem('sidebarCollapsed') === 'true') {
    document.getElementById('sidebar').classList.add('collapsed');
}

// Close mobile sidebar on outside click
document.addEventListener('click', (e) => {
    const sidebar = document.getElementById('sidebar');
    if (window.innerWidth <= 768 && sidebar.classList.contains('mobile-open')
        && !sidebar.contains(e.target) && !e.target.classList.contains('mobile-toggle')) {
        sidebar.classList.remove('mobile-open');
    }
});


// ── Toast Notifications ──

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    const icon = type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️';
    toast.innerHTML = `<span>${icon}</span> ${message}`;
    toast.className = 'toast show';
    setTimeout(() => { toast.className = 'toast'; }, 3000);
}


// ── Gauge Chart Helper ──

function createGauge(canvasId, value, label) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    let color;
    if (value >= 85) color = '#3fb950';
    else if (value >= 70) color = '#d29922';
    else color = '#f85149';

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [value, 100 - value],
                backgroundColor: [color, '#21262d'],
                borderWidth: 0,
                circumference: 180,
                rotation: 270,
            }]
        },
        options: {
            responsive: false,
            maintainAspectRatio: false,
            cutout: '75%',
            plugins: { legend: { display: false }, tooltip: { enabled: false } },
        }
    });
}
