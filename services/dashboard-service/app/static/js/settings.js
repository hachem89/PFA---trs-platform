/**
 * settings.js — CRUD for usines and machines.
 */

async function loadSettings() {
    const res = await fetch('/api/usines');
    const usines = await res.json();
    renderUsines(usines);
}

function renderUsines(usines) {
    const container = document.getElementById('usines-list');
    if (usines.length === 0) {
        container.innerHTML = `
            <div class="card" style="text-align:center;padding:48px;">
                <div style="font-size:48px;margin-bottom:16px;opacity:0.5;">🏭</div>
                <h3 style="font-size:16px;margin-bottom:8px;">Aucune usine configurée</h3>
                <p style="font-size:13px;color:var(--text-secondary);margin-bottom:16px;">
                    Commencez par ajouter votre première usine
                </p>
                <button class="btn btn-primary" onclick="openUsineModal()">+ Ajouter une usine</button>
            </div>`;
        return;
    }

    container.innerHTML = usines.map(u => `
        <div class="usine-block">
            <div class="usine-block-header" onclick="this.parentElement.querySelector('.usine-block-body').style.display = this.parentElement.querySelector('.usine-block-body').style.display === 'none' ? 'block' : 'none'">
                <div class="usine-block-title">
                    <span style="font-size:20px;">🏭</span>
                    <div>
                        <div class="usine-block-name">${u.nom}</div>
                        <div class="usine-block-info">📍 ${u.ville || '—'}, ${u.pays || '—'} · ${u.machines_count} machines · ${u.postes} poste(s)</div>
                    </div>
                </div>
                <div class="usine-block-actions" onclick="event.stopPropagation()">
                    <button class="btn btn-secondary btn-sm" onclick="openUsineModal(${u.id}, '${escHtml(u.nom)}', '${escHtml(u.ville||'')}', '${escHtml(u.pays||'Tunisie')}', ${u.postes}, ${u.tr})">✏️ Modifier</button>
                    <button class="btn btn-danger btn-sm" onclick="confirmDelete('usine', ${u.id}, '${escHtml(u.nom)}')">🗑️</button>
                </div>
            </div>
            <div class="usine-block-body">
                ${u.machines.length > 0 ? `
                <div class="machines-table-wrap">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Machine</th><th>Cadence</th><th>TRS</th>
                                <th>Status</th><th>Capteurs</th><th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${u.machines.map(m => `
                            <tr>
                                <td style="font-weight:500;">${m.nom}</td>
                                <td>${m.cadence_theorique} pcs/min</td>
                                <td>
                                    <span class="${m.trs >= 85 ? 'c-green' : m.trs >= 70 ? 'c-yellow' : 'c-red'}" style="font-family:'Space Mono',monospace;font-weight:700;">
                                        ${m.trs}%
                                    </span>
                                </td>
                                <td><span class="status-dot ${m.status}"></span> ${m.status}</td>
                                <td style="font-size:11px;color:var(--text-secondary);">
                                    ${m.capteur_vitesse} · ${m.capteur_pieces}
                                </td>
                                <td>
                                    <div class="actions">
                                        <button class="btn btn-secondary btn-sm btn-icon" onclick="openMachineModal(${u.id}, ${m.id}, '${escHtml(m.nom)}', ${m.cadence_theorique}, ${m.seuil_vibration}, ${m.seuil_piece_cm}, ${m.delai_mesures}, '${m.capteur_vitesse}', '${m.capteur_pieces}', '${m.capteur_dispo}', '${m.capteur_qualite}')">✏️</button>
                                        <button class="btn btn-danger btn-sm btn-icon" onclick="confirmDelete('machine', ${m.id}, '${escHtml(m.nom)}')">🗑️</button>
                                    </div>
                                </td>
                            </tr>`).join('')}
                        </tbody>
                    </table>
                </div>` : `
                <div class="empty-machines"><p>Aucune machine dans cette usine</p></div>`}
                <div class="add-machine-row">
                    <button class="btn btn-secondary btn-sm" onclick="openMachineModal(${u.id})">+ Ajouter une machine</button>
                </div>
            </div>
        </div>
    `).join('');
}

function escHtml(str) {
    return String(str).replace(/'/g, "\\'").replace(/"/g, '&quot;');
}

// ── Usine Modal ──

function openUsineModal(id, nom, ville, pays, postes, tr) {
    document.getElementById('usine-edit-id').value = id || '';
    document.getElementById('usine-nom').value = nom || '';
    document.getElementById('usine-ville').value = ville || '';
    document.getElementById('usine-pays').value = pays || 'Tunisie';
    document.getElementById('usine-postes').value = postes || 1;
    document.getElementById('usine-tr').value = tr || 8;
    document.getElementById('usine-modal-title').textContent = id ? "Modifier l'usine" : 'Ajouter une usine';
    document.getElementById('usine-modal').classList.add('active');
}
function closeUsineModal() { document.getElementById('usine-modal').classList.remove('active'); }

async function saveUsine() {
    const id = document.getElementById('usine-edit-id').value;
    const data = {
        nom: document.getElementById('usine-nom').value,
        ville: document.getElementById('usine-ville').value,
        pays: document.getElementById('usine-pays').value,
        postes: parseInt(document.getElementById('usine-postes').value),
        tr: parseInt(document.getElementById('usine-tr').value),
    };
    if (!data.nom) { showToast('Le nom est obligatoire', 'error'); return; }
    const url = id ? `/api/usines/${id}` : '/api/usines';
    const method = id ? 'PUT' : 'POST';
    await fetch(url, { method, headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) });
    closeUsineModal();
    showToast(id ? 'Usine modifiée' : 'Usine ajoutée');
    loadSettings();
}

// ── Machine Modal ──

function openMachineModal(usineId, machineId, nom, cadence, seuilV, seuilP, delai, cv, cp, cd, cq) {
    document.getElementById('machine-usine-id').value = usineId || '';
    document.getElementById('machine-edit-id').value = machineId || '';
    document.getElementById('machine-nom').value = nom || '';
    document.getElementById('machine-cadence').value = cadence || '';
    document.getElementById('machine-seuil-vibration').value = seuilV || '';
    document.getElementById('machine-seuil-piece-cm').value = seuilP || '';
    document.getElementById('machine-delai').value = delai || '';
    document.getElementById('machine-capteur-vitesse').value = cv || 'simulation';
    document.getElementById('machine-capteur-pieces').value = cp || 'simulation';
    document.getElementById('machine-capteur-dispo').value = cd || 'simulation';
    document.getElementById('machine-capteur-qualite').value = cq || 'simulation';
    document.getElementById('machine-modal-title').textContent = machineId ? 'Modifier la machine' : 'Ajouter une machine';
    document.getElementById('machine-modal').classList.add('active');
}
function closeMachineModal() { document.getElementById('machine-modal').classList.remove('active'); }

async function saveMachine() {
    const machineId = document.getElementById('machine-edit-id').value;
    const usineId = document.getElementById('machine-usine-id').value;
    const data = {
        nom: document.getElementById('machine-nom').value,
        cadence_theorique: parseFloat(document.getElementById('machine-cadence').value) || 50,
        seuil_vibration: parseFloat(document.getElementById('machine-seuil-vibration').value) || 0.0,
        seuil_piece_cm: parseFloat(document.getElementById('machine-seuil-piece-cm').value) || 0.0,
        delai_mesures: parseInt(document.getElementById('machine-delai').value) || 60,
        capteur_vitesse: document.getElementById('machine-capteur-vitesse').value,
        capteur_pieces: document.getElementById('machine-capteur-pieces').value,
        capteur_dispo: document.getElementById('machine-capteur-dispo').value,
        capteur_qualite: document.getElementById('machine-capteur-qualite').value,
    };
    if (!data.nom) { showToast('Le nom est obligatoire', 'error'); return; }
    let url, method;
    if (machineId) { url = `/api/machines/${machineId}`; method = 'PUT'; }
    else { url = `/api/usines/${usineId}/machines`; method = 'POST'; }
    await fetch(url, { method, headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) });
    closeMachineModal();
    showToast(machineId ? 'Machine modifiée' : 'Machine ajoutée');
    loadSettings();
}

// ── Confirm Delete ──

let deleteTarget = {};
function confirmDelete(type, id, name) {
    deleteTarget = { type, id };
    document.getElementById('confirm-message').textContent =
        `Êtes-vous sûr de vouloir supprimer "${name}" ? Cette action est irréversible.`;
    document.getElementById('confirm-btn').onclick = executeDelete;
    document.getElementById('confirm-modal').classList.add('active');
}
function closeConfirm() { document.getElementById('confirm-modal').classList.remove('active'); }

async function executeDelete() {
    const url = deleteTarget.type === 'usine'
        ? `/api/usines/${deleteTarget.id}`
        : `/api/machines/${deleteTarget.id}`;
    await fetch(url, { method: 'DELETE' });
    closeConfirm();
    showToast('Supprimé avec succès');
    loadSettings();
}

// Boot
loadSettings();
