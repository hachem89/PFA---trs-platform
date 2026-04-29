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
        showToast('Profile updated');
        document.getElementById('display-name').textContent = data.prenom + ' ' + data.nom;
        document.getElementById('display-entreprise').textContent = data.entreprise || '—';
        document.getElementById('display-secteur').textContent = data.secteur || '—';
        document.getElementById('avatar-initials').textContent =
            (data.prenom[0] || '') + (data.nom[0] || '');

        const indicator = document.getElementById('info-saved');
        indicator.classList.add('show');
        setTimeout(() => indicator.classList.remove('show'), 3000);
    } else {
        showToast('Error updating profile', 'error');
    }
}

async function changePassword() {
    const currentPwd = document.getElementById('current-password').value;
    const newPwd = document.getElementById('new-password').value;
    const confirmPwd = document.getElementById('confirm-password').value;

    if (!currentPwd || !newPwd) {
        showToast('Please fill all fields', 'error');
        return;
    }
    if (newPwd.length < 8) {
        showToast('New password must be at least 8 characters', 'error');
        return;
    }
    if (newPwd !== confirmPwd) {
        showToast('Passwords do not match', 'error');
        return;
    }

    const res = await fetch('/api/profile', {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ current_password: currentPwd, new_password: newPwd })
    });

    if (res.ok) {
        showToast('Password updated');
        document.getElementById('current-password').value = '';
        document.getElementById('new-password').value = '';
        document.getElementById('confirm-password').value = '';
        const indicator = document.getElementById('pwd-saved');
        indicator.classList.add('show');
        setTimeout(() => indicator.classList.remove('show'), 3000);
    } else {
        const err = await res.json();
        showToast(err.error || 'Error', 'error');
    }
}
