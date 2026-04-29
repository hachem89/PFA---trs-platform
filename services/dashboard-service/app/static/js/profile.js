/**
 * profile.js — Personal info update and password change.
 */

async function saveProfile() {
    const data = {
        prenom: document.getElementById('edit-prenom').value,
        nom: document.getElementById('edit-nom').value,
        telephone: document.getElementById('edit-telephone').value,
        entreprise: document.getElementById('edit-entreprise').value,
        secteur: document.getElementById('edit-secteur').value,
    };

    const res = await fetch('/api/profile', {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    });

    if (res.ok) {
        showToast('Profil mis à jour');
        document.getElementById('display-name').textContent = data.prenom + ' ' + data.nom;
        document.getElementById('display-entreprise').textContent = data.entreprise || '—';
        document.getElementById('display-secteur').textContent = data.secteur || '—';
        document.getElementById('avatar-initials').textContent =
            (data.prenom[0] || '') + (data.nom[0] || '');

        const indicator = document.getElementById('info-saved');
        indicator.classList.add('show');
        setTimeout(() => indicator.classList.remove('show'), 3000);
    } else {
        showToast('Erreur lors de la mise à jour', 'error');
    }
}

async function changePassword() {
    const currentPwd = document.getElementById('current-password').value;
    const newPwd = document.getElementById('new-password').value;
    const confirmPwd = document.getElementById('confirm-password').value;

    if (!currentPwd || !newPwd) {
        showToast('Veuillez remplir tous les champs', 'error');
        return;
    }
    if (newPwd.length < 8) {
        showToast('Le nouveau mot de passe doit avoir au moins 8 caractères', 'error');
        return;
    }
    if (newPwd !== confirmPwd) {
        showToast('Les mots de passe ne correspondent pas', 'error');
        return;
    }

    const res = await fetch('/api/profile', {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ current_password: currentPwd, new_password: newPwd })
    });

    if (res.ok) {
        showToast('Mot de passe mis à jour');
        document.getElementById('current-password').value = '';
        document.getElementById('new-password').value = '';
        document.getElementById('confirm-password').value = '';
        const indicator = document.getElementById('pwd-saved');
        indicator.classList.add('show');
        setTimeout(() => indicator.classList.remove('show'), 3000);
    } else {
        const err = await res.json();
        showToast(err.error || 'Erreur', 'error');
    }
}
