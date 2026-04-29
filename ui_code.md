# UI Source Code (HTML & CSS)

This document contains the complete source code for all templates and stylesheets in the project.

---

## HTML Templates

### `templates/analysis.html`
**Path:** `c:\Users\user\Desktop\pfa backend\trs_digitalisation\templates\analysis.html`

```html
{% extends "base.html" %}
{% block title %}Analyse TRS{% endblock %}
{% block page_title %}Analyse & Tendances{% endblock %}

{% block extra_head %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/analysis.css') }}">
{% endblock %}

{% block content %}
<!-- Controls -->
<div class="analysis-controls">
    <div class="control-group">
        <span class="control-label">Machine :</span>
        <select class="control-select" id="machine-select" onchange="loadHistory()">
            <option value="">Chargement...</option>
        </select>
    </div>
    <div class="control-group">
        <span class="control-label">Période :</span>
        <select class="control-select" id="period-select" onchange="loadHistory()">
            <option value="7">7 jours</option>
            <option value="14">14 jours</option>
            <option value="30" selected>30 jours</option>
            <option value="90">90 jours</option>
        </select>
    </div>
    <div class="control-group">
        <div class="metric-chips" id="metric-chips">
            <button class="metric-chip active" data-metric="trs" onclick="toggleMetric(this)">TRS</button>
            <button class="metric-chip" data-metric="tdo" onclick="toggleMetric(this)">TDO</button>
            <button class="metric-chip" data-metric="tp" onclick="toggleMetric(this)">TP</button>
            <button class="metric-chip" data-metric="tq" onclick="toggleMetric(this)">TQ</button>
        </div>
    </div>
</div>

<!-- Stats Summary -->
<div class="stats-grid" id="stats-grid">
    <div class="stat-card">
        <div class="stat-value c-green" id="stat-avg">—</div>
        <div class="stat-label">Moyenne</div>
    </div>
    <div class="stat-card">
        <div class="stat-value c-blue" id="stat-max">—</div>
        <div class="stat-label">Maximum</div>
    </div>
    <div class="stat-card">
        <div class="stat-value c-red" id="stat-min">—</div>
        <div class="stat-label">Minimum</div>
    </div>
    <div class="stat-card">
        <div class="stat-value c-purple" id="stat-trend">—</div>
        <div class="stat-label">Tendance</div>
    </div>
</div>

<!-- Main Chart -->
<div class="chart-card">
    <div class="chart-title" id="chart-title">Évolution du TRS</div>
    <div class="chart-subtitle" id="chart-subtitle">Sélectionnez une machine pour voir ses tendances</div>
    <div class="chart-wrapper">
        <canvas id="main-chart"></canvas>
    </div>
</div>

<!-- Comparison Chart -->
<div class="chart-card">
    <div class="chart-title">Comparaison inter-machines</div>
    <div class="chart-subtitle">TRS de toutes les machines sur la même période</div>
    <div class="compare-chart-wrapper">
        <canvas id="compare-chart"></canvas>
    </div>
</div>
{% endblock %}

{% block extra_scripts %}
<script src="{{ url_for('static', filename='js/analysis.js') }}"></script>
{% endblock %}
```

### `templates/base.html`
**Path:** `c:\Users\user\Desktop\pfa backend\trs_digitalisation\templates\base.html`

```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TRS IoT — {% block title %}Dashboard{% endblock %}</title>
    <link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/base.css') }}">
    {% block extra_head %}{% endblock %}
</head>
<body>

<!-- ═══ SIDEBAR ═══ -->
<aside class="sidebar" id="sidebar">
    <div class="sidebar-header">
        <button class="sidebar-toggle" id="sidebar-toggle" onclick="toggleSidebar()">☰</button>
        <div class="sidebar-logo">TRS · IOT</div>
    </div>
    <nav class="sidebar-nav">
        <a href="/dashboard" class="nav-item {% if page == 'dashboard' %}active{% endif %}">
            <span class="nav-icon">📊</span>
            <span class="nav-label">Dashboard</span>
        </a>
        <a href="/analysis" class="nav-item {% if page == 'analysis' %}active{% endif %}">
            <span class="nav-icon">📈</span>
            <span class="nav-label">Analyse TRS</span>
        </a>
        <div class="nav-separator"></div>
        <a href="/settings" class="nav-item {% if page == 'settings' %}active{% endif %}">
            <span class="nav-icon">⚙️</span>
            <span class="nav-label">Usines & Machines</span>
        </a>
        <a href="/profile" class="nav-item {% if page == 'profile' %}active{% endif %}">
            <span class="nav-icon">👤</span>
            <span class="nav-label">Profil</span>
        </a>
    </nav>
    <div class="sidebar-footer">
        <a href="/logout" class="nav-item">
            <span class="nav-icon">🚪</span>
            <span class="nav-label">Déconnexion</span>
        </a>
    </div>
</aside>

<!-- ═══ TOPBAR ═══ -->
<header class="topbar">
    <div class="topbar-left">
        <button class="mobile-toggle" onclick="toggleMobileSidebar()">☰</button>
        <span class="topbar-title">{% block page_title %}Dashboard{% endblock %}</span>
    </div>
    <div class="topbar-right">
        <span class="topbar-user">
            <strong>{{ client.prenom }} {{ client.nom }}</strong> · {{ client.entreprise }}
        </span>
        <div class="topbar-avatar">{{ client.prenom[0] }}{{ client.nom[0] }}</div>
    </div>
</header>

<!-- ═══ MAIN ═══ -->
<main class="main-content">
    {% block content %}{% endblock %}
</main>

<!-- ═══ TOAST ═══ -->
<div class="toast" id="toast"></div>

<script src="{{ url_for('static', filename='js/base.js') }}"></script>
{% block extra_scripts %}{% endblock %}
</body>
</html>
```

### `templates/dashboard.html`
**Path:** `c:\Users\user\Desktop\pfa backend\trs_digitalisation\templates\dashboard.html`

```html
{% extends "base.html" %}
{% block title %}Dashboard{% endblock %}
{% block page_title %}Vue d'ensemble{% endblock %}

{% block extra_head %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/dashboard.css') }}">
{% endblock %}

{% block content %}
<!-- KPI Cards -->
<div class="grid-4" id="kpi-grid">
    <div class="kpi-card bl-green">
        <div class="kpi-label">TRS Moyen Global</div>
        <div class="kpi-value c-green" id="kpi-trs">—</div>
        <div class="kpi-sub">Objectif &gt; 85%</div>
    </div>
    <div class="kpi-card bl-blue">
        <div class="kpi-label">Usines actives</div>
        <div class="kpi-value c-blue" id="kpi-usines">—</div>
        <div class="kpi-sub">Sites de production</div>
    </div>
    <div class="kpi-card bl-purple">
        <div class="kpi-label">Machines totales</div>
        <div class="kpi-value c-purple" id="kpi-machines">—</div>
        <div class="kpi-sub">Équipements suivis</div>
    </div>
    <div class="kpi-card bl-red">
        <div class="kpi-label">Alertes</div>
        <div class="kpi-value c-red" id="kpi-alerts">—</div>
        <div class="kpi-sub">Machines TRS &lt; 70%</div>
    </div>
</div>

<!-- Machine Gauges Section -->
<div class="section-header">
    <div class="flex-align-center gap-12">
        <div>
            <div class="section-title">Performance des Machines</div>
            <div class="section-subtitle">TRS · TDO · TP · TQ en temps réel</div>
        </div>
        <div class="badge badge-live">
            <span class="status-dot online pulse"></span>
            LIVE
        </div>
    </div>
    <div class="usine-chips" id="usine-filter"></div>
</div>

<div class="gauges-grid" id="gauges-grid">
    <div class="empty-state">
        <div class="empty-icon">⏳</div>
        <h3>Chargement...</h3>
    </div>
</div>
{% endblock %}

{% block extra_scripts %}
<script src="{{ url_for('static', filename='js/dashboard.js') }}"></script>
{% endblock %}
```

### `templates/login.html`
**Path:** `c:\Users\user\Desktop\pfa backend\trs_digitalisation\templates\login.html`

```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TRS IoT — Connexion</title>
    <link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', sans-serif;
            background: #0d1117;
            display: flex; justify-content: center; align-items: center;
            min-height: 100vh; padding: 24px;
        }
        .bg-grid {
            position: fixed; inset: 0;
            background-image:
                linear-gradient(rgba(59,130,246,0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(59,130,246,0.03) 1px, transparent 1px);
            background-size: 40px 40px; pointer-events: none;
        }
        .wrapper { width: 100%; max-width: 500px; position: relative; z-index: 1; animation: fadeIn 0.4s ease; }
        @keyframes fadeIn { from { opacity:0; transform:translateY(16px); } to { opacity:1; transform:translateY(0); } }
        .card { background: #161b22; border: 1px solid #30363d; border-radius: 16px; padding: 36px; }
        .logo { text-align: center; margin-bottom: 24px; }
        .logo-icon {
            width: 48px; height: 48px;
            background: linear-gradient(135deg, #1d4ed8, #3b82f6);
            border-radius: 12px; display: flex; align-items: center;
            justify-content: center; margin: 0 auto 12px; font-size: 20px;
        }
        .logo h1 { font-family: 'Space Mono', monospace; color: #f0f6ff; font-size: 18px; letter-spacing: 2px; }
        .logo p { color: #8b949e; font-size: 12px; margin-top: 4px; }
        .tabs {
            display: flex; background: #0d1117; border-radius: 10px;
            padding: 4px; margin-bottom: 24px; border: 1px solid #21262d;
        }
        .tab {
            flex: 1; padding: 9px; text-align: center; font-size: 13px;
            font-weight: 500; cursor: pointer; border-radius: 7px;
            color: #8b949e; transition: all 0.2s; border: none;
            background: transparent; font-family: 'Inter', sans-serif;
        }
        .tab.active { background: #161b22; color: #f0f6ff; border: 1px solid #30363d; }
        .form-section { display: none; }
        .form-section.active { display: block; }
        .form-group { margin-bottom: 14px; }
        .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
        label {
            color: #8b949e; font-size: 11px; font-weight: 500;
            text-transform: uppercase; letter-spacing: 0.8px;
            display: block; margin-bottom: 6px;
        }
        input, select {
            width: 100%; padding: 10px 13px;
            background: #0d1117; border: 1px solid #30363d;
            border-radius: 8px; color: #f0f6ff; font-size: 13px;
            font-family: 'Inter', sans-serif; transition: border-color 0.2s;
        }
        input:focus, select:focus {
            outline: none; border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(59,130,246,0.1);
        }
        input::placeholder { color: #484f58; }
        select option { background: #161b22; }
        .btn {
            width: 100%; padding: 11px; background: #1d4ed8; color: #fff;
            border: none; border-radius: 8px; font-size: 13px; font-weight: 500;
            cursor: pointer; margin-top: 6px; transition: background 0.2s;
            font-family: 'Inter', sans-serif;
        }
        .btn:hover { background: #2563eb; }
        .btn-outline {
            background: transparent; border: 1px solid #30363d;
            color: #8b949e; margin-top: 8px;
        }
        .btn-outline:hover { border-color: #8b949e; color: #f0f6ff; background: transparent; }
        .error {
            background: rgba(248,81,73,0.1); border: 1px solid rgba(248,81,73,0.3);
            color: #f85149; padding: 10px 14px; border-radius: 8px;
            font-size: 13px; margin-bottom: 14px;
        }
        .steps {
            display: flex; align-items: center; justify-content: center;
            gap: 8px; margin-bottom: 20px;
        }
        .step { display: flex; align-items: center; gap: 6px; font-size: 11px; color: #484f58; }
        .step.active { color: #58a6ff; }
        .step.done { color: #3fb950; }
        .step-num {
            width: 22px; height: 22px; border-radius: 50%;
            background: #21262d; display: flex; align-items: center;
            justify-content: center; font-size: 11px; font-weight: 600;
            border: 1px solid #30363d;
        }
        .step.active .step-num { background: #1d4ed8; border-color: #3b82f6; color: #fff; }
        .step.done .step-num { background: #0d4429; border-color: #3fb950; color: #3fb950; }
        .step-line { width: 20px; height: 1px; background: #21262d; }
        .section-label {
            font-size: 11px; color: #58a6ff; text-transform: uppercase;
            letter-spacing: 1px; font-weight: 600; margin-bottom: 14px;
            padding-bottom: 8px; border-bottom: 1px solid #21262d;
        }
        .machine-block {
            background: #0d1117; border: 1px solid #21262d;
            border-radius: 10px; padding: 14px; margin-bottom: 10px;
        }
        .machine-block-title {
            font-size: 12px; color: #8b949e; margin-bottom: 12px;
            font-weight: 500; display: flex; justify-content: space-between; align-items: center;
        }
        .add-machine-btn {
            width: 100%; padding: 9px; background: transparent;
            border: 1px dashed #30363d; border-radius: 8px;
            color: #58a6ff; font-size: 12px; cursor: pointer;
            transition: all 0.2s; font-family: 'Inter', sans-serif; margin-top: 4px;
        }
        .add-machine-btn:hover { border-color: #58a6ff; background: rgba(59,130,246,0.05); }
        .remove-btn { background: none; border: none; color: #f85149; cursor: pointer; font-size: 12px; }
        .divider { height: 1px; background: #21262d; margin: 16px 0; }
        .hint { font-size: 11px; color: #484f58; margin-top: 4px; }
        .nav-btns { display: flex; gap: 10px; margin-top: 14px; }
        .nav-btns .btn { margin-top: 0; }
        .link-switch { margin-top: 14px; text-align: center; font-size: 12px; color: #484f58; }
        .link-switch a { color: #58a6ff; text-decoration: none; }
    </style>
</head>
<body>
<div class="bg-grid"></div>
<div class="wrapper">
    <div class="card">
        <div class="logo">
            <div class="logo-icon">⚙</div>
            <h1>TRS · IOT</h1>
            <p>Plateforme de suivi industriel temps réel</p>
        </div>

        <div class="tabs">
            <button class="tab active" id="tab-btn-login" onclick="showTab('login')">Se connecter</button>
            <button class="tab" id="tab-btn-register" onclick="showTab('register')">Créer un compte</button>
        </div>

        <!-- ═══ LOGIN ═══ -->
        <div class="form-section active" id="tab-login">
            {% if error %}
            <div class="error">⚠ {{ error }}</div>
            {% endif %}
            <form method="POST" action="/login">
                <div class="form-group">
                    <label>Email professionnel</label>
                    <input type="email" name="email" placeholder="client@entreprise.com" required>
                </div>
                <div class="form-group">
                    <label>Mot de passe</label>
                    <input type="password" name="password" placeholder="••••••••" required>
                </div>
                <button type="submit" class="btn">→ Se connecter</button>
            </form>
            <div class="link-switch">
                Pas encore de compte ? <a href="#" onclick="showTab('register')">Créer un compte →</a>
            </div>
        </div>

        <!-- ═══ REGISTER ═══ -->
        <div class="form-section" id="tab-register">
            <div class="steps">
                <div class="step active" id="step-ind-1"><div class="step-num">1</div><span>Compte</span></div>
                <div class="step-line"></div>
                <div class="step" id="step-ind-2"><div class="step-num">2</div><span>Usine</span></div>
                <div class="step-line"></div>
                <div class="step" id="step-ind-3"><div class="step-num">3</div><span>Machines</span></div>
            </div>

            <form method="POST" action="/register" id="register-form">

                <!-- Étape 1 -->
                <div id="step-1">
                    <div class="section-label">👤 Informations personnelles</div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Prénom</label>
                            <input type="text" name="prenom" placeholder="Ahmed" required>
                        </div>
                        <div class="form-group">
                            <label>Nom</label>
                            <input type="text" name="nom" placeholder="Ben Ali" required>
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Email professionnel</label>
                        <input type="email" name="email" placeholder="ahmed@entreprise.com" required>
                    </div>
                    <div class="form-group">
                        <label>Mot de passe</label>
                        <input type="password" name="password" id="pwd" placeholder="Min. 8 caractères" required>
                        <div class="hint">Au moins 8 caractères</div>
                    </div>
                    <div class="form-group">
                        <label>Confirmer le mot de passe</label>
                        <input type="password" name="password2" id="pwd2" placeholder="••••••••" required>
                    </div>
                    <div class="form-group">
                        <label>Nom de l'entreprise</label>
                        <input type="text" name="entreprise" placeholder="Entreprise SARL" required>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Téléphone</label>
                            <input type="tel" name="telephone" placeholder="+216 XX XXX XXX">
                        </div>
                        <div class="form-group">
                            <label>Secteur</label>
                            <select name="secteur">
                                <option value="">Choisir...</option>
                                <option>Agroalimentaire</option>
                                <option>Textile</option>
                                <option>Mécanique</option>
                                <option>Électronique</option>
                                <option>Chimie</option>
                                <option>Autre</option>
                            </select>
                        </div>
                    </div>
                    <button type="button" class="btn" onclick="nextStep(1)">Suivant →</button>
                </div>

                <!-- Étape 2 -->
                <div id="step-2" style="display:none;">
                    <div class="section-label">🏭 Informations de l'usine</div>
                    <div class="form-group">
                        <label>Nom de l'usine</label>
                        <input type="text" name="usine_nom" placeholder="Usine principale" required>
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Ville</label>
                            <input type="text" name="usine_ville" placeholder="Tunis" required>
                        </div>
                        <div class="form-group">
                            <label>Pays</label>
                            <select name="usine_pays">
                                <option>Tunisie</option>
                                <option>Algérie</option>
                                <option>Maroc</option>
                                <option>France</option>
                                <option>Autre</option>
                            </select>
                        </div>
                    </div>
                    <div class="form-group">
                        <label>Adresse</label>
                        <input type="text" name="usine_adresse" placeholder="Zone industrielle, Rue...">
                    </div>
                    <div class="form-row">
                        <div class="form-group">
                            <label>Nombre de postes / jour</label>
                            <select name="usine_postes">
                                <option value="1">1 poste (8h)</option>
                                <option value="2">2 postes (16h)</option>
                                <option value="3">3 postes (24h)</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Temps requis Tr (h/jour)</label>
                            <input type="number" name="usine_tr" placeholder="8" min="1" max="24" value="8">
                            <div class="hint">Tr = ouverture - arrêts planifiés</div>
                        </div>
                    </div>
                    <div class="nav-btns">
                        <button type="button" class="btn btn-outline" onclick="prevStep(2)">← Retour</button>
                        <button type="button" class="btn" onclick="nextStep(2)">Suivant →</button>
                    </div>
                </div>

                <!-- Étape 3 -->
                <div id="step-3" style="display:none;">
                    <div class="section-label">⚙ Caractéristiques des machines</div>
                    <div id="machines-container">
                        <div class="machine-block" id="machine-0">
                            <div class="machine-block-title">
                                <span>Machine 1</span>
                            </div>
                            <div class="form-group">
                                <label>Nom de la machine</label>
                                <input type="text" name="machine_nom_0" placeholder="Machine de découpe" required>
                            </div>
                            <div class="form-row">
                                <div class="form-group">
                                    <label>Cadence théorique (pièces/min)</label>
                                    <input type="number" name="machine_cadence_0" placeholder="50" min="1" step="0.1" required>
                                    <div class="hint">Vitesse nominale constructeur</div>
                                </div>
                                <div class="form-group">
                                    <label>Temps cycle théorique (s)</label>
                                    <input type="number" name="machine_tc_0" placeholder="1.2" min="0.1" step="0.1">
                                    <div class="hint">= 60 / cadence</div>
                                </div>
                            </div>
                            <div class="form-row">
                                <div class="form-group">
                                    <label>Seuil Vibration</label>
                                    <input type="number" name="machine_seuil_vibration_0" placeholder="0.0" step="0.1">
                                </div>
                                <div class="form-group">
                                    <label>Seuil Pièce CM</label>
                                    <input type="number" name="machine_seuil_piece_cm_0" placeholder="0.0" step="0.1">
                                </div>
                            </div>
                            <div class="form-group">
                                <label>Délai entre mesures (s)</label>
                                <input type="number" name="machine_delai_0" placeholder="60" min="1">
                            </div>
                            <div class="form-row">
                                <div class="form-group">
                                    <label>Capteur vitesse</label>
                                    <select name="machine_capteur_vitesse_0">
                                        <option value="hall">Hall effect</option>
                                        <option value="encodeur">Encodeur</option>
                                        <option value="inductif">Inductif</option>
                                        <option value="simulation">Simulation</option>
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label>Capteur pièces</label>
                                    <select name="machine_capteur_pieces_0">
                                        <option value="ultrason">Ultrason HC-SR04</option>
                                        <option value="barrage">Barrage optique</option>
                                        <option value="camera">Caméra USB</option>
                                        <option value="simulation">Simulation</option>
                                    </select>
                                </div>
                            </div>
                            <div class="form-row">
                                <div class="form-group">
                                    <label>Capteur disponibilité</label>
                                    <select name="machine_capteur_dispo_0">
                                        <option value="adxl345">ADXL345 (vibration)</option>
                                        <option value="courant">Capteur courant</option>
                                        <option value="simulation">Simulation</option>
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label>Capteur qualité</label>
                                    <select name="machine_capteur_qualite_0">
                                        <option value="camera">Caméra + IA</option>
                                        <option value="manuel">Saisie manuelle</option>
                                        <option value="simulation">Simulation</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                    </div>
                    <button type="button" class="add-machine-btn" onclick="addMachine()">+ Ajouter une machine</button>
                    <div class="divider"></div>
                    <div class="nav-btns">
                        <button type="button" class="btn btn-outline" onclick="prevStep(3)">← Retour</button>
                        <button type="submit" class="btn">✓ Créer mon compte</button>
                    </div>
                </div>

            </form>
            <div class="link-switch">
                Déjà un compte ? <a href="#" onclick="showTab('login')">Se connecter →</a>
            </div>
        </div>

    </div>
</div>

<script>
let machineCount = 1;

function showTab(tab) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.form-section').forEach(f => f.classList.remove('active'));
    document.getElementById('tab-' + tab).classList.add('active');
    document.getElementById('tab-btn-' + tab).classList.add('active');
}

function nextStep(current) {
    if (current === 1) {
        const pwd = document.getElementById('pwd').value;
        const pwd2 = document.getElementById('pwd2').value;
        if (pwd.length < 8) { alert('Le mot de passe doit avoir au moins 8 caractères.'); return; }
        if (pwd !== pwd2) { alert('Les mots de passe ne correspondent pas.'); return; }
    }
    document.getElementById('step-' + current).style.display = 'none';
    document.getElementById('step-' + (current + 1)).style.display = 'block';
    updateSteps(current + 1);
}

function prevStep(current) {
    document.getElementById('step-' + current).style.display = 'none';
    document.getElementById('step-' + (current - 1)).style.display = 'block';
    updateSteps(current - 1);
}

function updateSteps(active) {
    for (let i = 1; i <= 3; i++) {
        const el = document.getElementById('step-ind-' + i);
        el.classList.remove('active', 'done');
        if (i < active) el.classList.add('done');
        else if (i === active) el.classList.add('active');
    }
}

function addMachine() {
    const idx = machineCount;
    const container = document.getElementById('machines-container');
    const block = document.createElement('div');
    block.className = 'machine-block';
    block.id = 'machine-' + idx;
    block.innerHTML = `
        <div class="machine-block-title">
            <span>Machine ${idx + 1}</span>
            <button type="button" class="remove-btn" onclick="removeMachine(${idx})">✕ Supprimer</button>
        </div>
        <div class="form-group">
            <label>Nom de la machine</label>
            <input type="text" name="machine_nom_${idx}" placeholder="Machine de découpe">
        </div>
        <div class="form-row">
            <div class="form-group">
                <label>Cadence théorique (pièces/min)</label>
                <input type="number" name="machine_cadence_${idx}" placeholder="50" min="1" step="0.1">
            </div>
            <div class="form-group">
                <label>Temps cycle théorique (s)</label>
                <input type="number" name="machine_tc_${idx}" placeholder="1.2" min="0.1" step="0.1">
            </div>
        </div>
        <div class="form-row">
            <div class="form-group">
                <label>Seuil Vibration</label>
                <input type="number" name="machine_seuil_vibration_${idx}" placeholder="0.0" step="0.1">
            </div>
            <div class="form-group">
                <label>Seuil Pièce CM</label>
                <input type="number" name="machine_seuil_piece_cm_${idx}" placeholder="0.0" step="0.1">
            </div>
        </div>
        <div class="form-group">
            <label>Délai entre mesures (s)</label>
            <input type="number" name="machine_delai_${idx}" placeholder="60" min="1">
        </div>
        <div class="form-row">
            <div class="form-group">
                <label>Capteur vitesse</label>
                <select name="machine_capteur_vitesse_${idx}">
                    <option value="hall">Hall effect</option>
                    <option value="encodeur">Encodeur</option>
                    <option value="simulation">Simulation</option>
                </select>
            </div>
            <div class="form-group">
                <label>Capteur pièces</label>
                <select name="machine_capteur_pieces_${idx}">
                    <option value="ultrason">Ultrason HC-SR04</option>
                    <option value="camera">Caméra USB</option>
                    <option value="simulation">Simulation</option>
                </select>
            </div>
        </div>
        <div class="form-row">
            <div class="form-group">
                <label>Capteur disponibilité</label>
                <select name="machine_capteur_dispo_${idx}">
                    <option value="adxl345">ADXL345</option>
                    <option value="simulation">Simulation</option>
                </select>
            </div>
            <div class="form-group">
                <label>Capteur qualité</label>
                <select name="machine_capteur_qualite_${idx}">
                    <option value="camera">Caméra + IA</option>
                    <option value="simulation">Simulation</option>
                </select>
            </div>
        </div>`;
    container.appendChild(block);
    machineCount++;
}

function removeMachine(idx) {
    document.getElementById('machine-' + idx).remove();
}
</script>
</body>
</html>
```

### `templates/machine.html`
**Path:** `c:\Users\user\Desktop\pfa backend\trs_digitalisation\templates\machine.html`

```html
{% extends "base.html" %}
{% block title %}Détails Machine{% endblock %}
{% block page_title %}
    <a href="/dashboard" class="btn btn-secondary btn-icon" style="margin-right: 12px; font-size: 13px; text-decoration: none;">←</a> Supervision Machine
{% endblock %}

{% block extra_head %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/machine.css') }}">
{% endblock %}

{% block content %}
<div id="machine-loader" class="loader-container">
    <div class="loader">Chargement...</div>
</div>

<div id="machine-content" style="display: none;">
    <!-- Header Section -->
    <div class="machine-header card">
        <div class="flex-between">
            <div class="flex-align-center gap-12">
                <div>
                    <h1 class="machine-title" id="m-nom">—</h1>
                    <p class="machine-subtitle">📍 <span id="m-usine">—</span></p>
                </div>
            </div>
            <div class="machine-badges flex-align-center gap-12">
                <div class="badge badge-live">
                    <span class="status-dot online pulse"></span>
                    LIVE
                </div>
                <div class="badge" id="m-status-badge">
                    <span class="status-dot" id="m-status-dot"></span>
                    <span id="m-status-text">OFFLINE</span>
                </div>
            </div>
        </div>
    </div>

    <!-- KPIs Section -->
    <div class="section-title mt-24">Indicateurs de Performance</div>
    <div class="gauges-row">
        <!-- TRS Main -->
        <div class="card kpi-gauge-card main-kpi">
            <div class="gauge-header">
                <div class="kpi-gauge-label">TRS Global</div>
                <div class="badge" id="m-trs-badge">N/A</div>
            </div>
            <div class="gauge-chart-container main">
                <canvas id="gauge-trs"></canvas>
                <div class="gauge-value" id="m-trs-val" style="font-size: 32px;">—</div>
            </div>
        </div>
        <!-- TDO -->
        <div class="card kpi-gauge-card">
            <div class="gauge-header">TDO (Dispo)</div>
            <div class="gauge-chart-container">
                <canvas id="gauge-tdo"></canvas>
                <div class="gauge-value" id="m-tdo-val">—</div>
            </div>
        </div>
        <!-- TP -->
        <div class="card kpi-gauge-card">
            <div class="gauge-header">TP (Perf)</div>
            <div class="gauge-chart-container">
                <canvas id="gauge-tp"></canvas>
                <div class="gauge-value" id="m-tp-val">—</div>
            </div>
        </div>
        <!-- TQ -->
        <div class="card kpi-gauge-card">
            <div class="gauge-header">TQ (Qualité)</div>
            <div class="gauge-chart-container">
                <canvas id="gauge-tq"></canvas>
                <div class="gauge-value" id="m-tq-val">—</div>
            </div>
        </div>
    </div>

    <!-- Details Section -->
    <div class="grid-2 mt-24">
        <!-- Production Data (Mock from Node-RED) -->
        <div class="card">
            <div class="card-header">
                <div class="card-title">Données de Production (Node-RED)</div>
            </div>
            <div class="production-stats">
                <div class="stat-box">
                    <div class="stat-label">Pièces Bonnes (OK)</div>
                    <div class="stat-value c-green" id="m-pieces-ok">—</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Pièces Rejetées (Rebuts)</div>
                    <div class="stat-value c-red" id="m-pieces-rebus">—</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Temps de Cycle Actuel</div>
                    <div class="stat-value" id="m-cycle-time">— <span style="font-size: 13px; color: var(--text-secondary);">s/pièce</span></div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Cadence Théorique</div>
                    <div class="stat-value c-blue" id="m-cadence">— <span style="font-size: 13px; color: var(--text-secondary);">pcs/min</span></div>
                </div>
            </div>
            
            <!-- Extra Node Red Env mock -->
            <div class="card-header" style="margin-top: 24px;">
                <div class="card-title">Environnement Machine (IoT)</div>
            </div>
            <div class="production-stats">
                <div class="stat-box">
                    <div class="stat-label">Température Moteur</div>
                    <div class="stat-value" id="m-temp">— <span style="font-size: 13px; color: var(--text-secondary);">°C</span></div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Niveau de Vibration</div>
                    <div class="stat-value" id="m-vib">— <span style="font-size: 13px; color: var(--text-secondary);">mm/s</span></div>
                </div>
            </div>
        </div>

        <!-- Sensor Health -->
        <div class="card">
            <div class="card-header">
                <div class="card-title">État des Capteurs Configurés</div>
                <div class="badge badge-green" id="m-sensor-health">Optimal</div>
            </div>
            <ul class="sensor-list">
                <li class="sensor-item">
                    <div class="sensor-info flex-align-center gap-12">
                        <div class="sensor-icon">🔄</div>
                        <div>
                            <div class="sensor-name">Vitesse & Cadence</div>
                            <div class="sensor-type" id="s-type-vit">—</div>
                        </div>
                    </div>
                    <div class="sensor-status c-green">Actif</div>
                </li>
                <li class="sensor-item">
                    <div class="sensor-info flex-align-center gap-12">
                        <div class="sensor-icon">📸</div>
                        <div>
                            <div class="sensor-name">Comptage Pièces</div>
                            <div class="sensor-type" id="s-type-pcs">—</div>
                        </div>
                    </div>
                    <div class="sensor-status c-green">Actif</div>
                </li>
                <li class="sensor-item">
                    <div class="sensor-info flex-align-center gap-12">
                        <div class="sensor-icon">⚡</div>
                        <div>
                            <div class="sensor-name">Disponibilité Électrique</div>
                            <div class="sensor-type" id="s-type-disp">—</div>
                        </div>
                    </div>
                    <div class="sensor-status c-green">Actif</div>
                </li>
                <li class="sensor-item">
                    <div class="sensor-info flex-align-center gap-12">
                        <div class="sensor-icon">🔍</div>
                        <div>
                            <div class="sensor-name">Inspection Qualité</div>
                            <div class="sensor-type" id="s-type-qual">—</div>
                        </div>
                    </div>
                    <div class="sensor-status c-green">Actif</div>
                </li>
            </ul>
            <div style="margin-top:20px; font-size: 12px; color: var(--text-muted); line-height: 1.5;">
                <p><strong>Note:</strong> Ces informations simulées seront remplacées par le flux MQTT réel (Node-RED) dans la prochaine version du projet, en utilisant l'ingestion API mise en place.</p>
            </div>
        </div>
    </div>
</div>

<script>
    const MACHINE_ID = parseInt("{{ machine_id }}", 10);
</script>
{% endblock %}

{% block extra_scripts %}
<script src="{{ url_for('static', filename='js/machine.js') }}"></script>
{% endblock %}
```

### `templates/profile.html`
**Path:** `c:\Users\user\Desktop\pfa backend\trs_digitalisation\templates\profile.html`

```html
{% extends "base.html" %}
{% block title %}Profil{% endblock %}
{% block page_title %}Mon Profil{% endblock %}

{% block extra_head %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/profile.css') }}">
{% endblock %}

{% block content %}
<div class="profile-grid">
    <!-- Left sidebar -->
    <div class="profile-sidebar">
        <div class="profile-avatar" id="avatar-initials">{{ client.prenom[0] }}{{ client.nom[0] }}</div>
        <div class="profile-name" id="display-name">{{ client.prenom }} {{ client.nom }}</div>
        <div class="profile-email">{{ client.email }}</div>
        <div style="margin-bottom: 16px;">
            <span class="badge badge-green">Actif</span>
        </div>
        <div class="profile-meta">
            <div class="profile-meta-item">
                <span class="profile-meta-label">Entreprise</span>
                <span class="profile-meta-value" id="display-entreprise">{{ client.entreprise or '—' }}</span>
            </div>
            <div class="profile-meta-item">
                <span class="profile-meta-label">Secteur</span>
                <span class="profile-meta-value" id="display-secteur">{{ client.secteur or '—' }}</span>
            </div>
            <div class="profile-meta-item">
                <span class="profile-meta-label">Usines</span>
                <span class="profile-meta-value">{{ client.usines | length }}</span>
            </div>
            <div class="profile-meta-item">
                <span class="profile-meta-label">Machines</span>
                <span class="profile-meta-value">
                    {% set total = [] %}
                    {% for u in client.usines %}{% for m in u.machines %}{% if total.append(1) %}{% endif %}{% endfor %}{% endfor %}
                    {{ total | length }}
                </span>
            </div>
        </div>
    </div>

    <!-- Right forms -->
    <div class="profile-forms">
        <!-- Personal Info -->
        <div class="profile-card">
            <div class="profile-card-title">
                👤 Informations personnelles
                <span class="save-indicator" id="info-saved">✅ Enregistré</span>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label class="form-label">Prénom</label>
                    <input class="form-input" id="edit-prenom" value="{{ client.prenom or '' }}">
                </div>
                <div class="form-group">
                    <label class="form-label">Nom</label>
                    <input class="form-input" id="edit-nom" value="{{ client.nom or '' }}">
                </div>
            </div>
            <div class="form-group">
                <label class="form-label">Téléphone</label>
                <input class="form-input" id="edit-telephone" value="{{ client.telephone or '' }}" placeholder="+216 XX XXX XXX">
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label class="form-label">Entreprise</label>
                    <input class="form-input" id="edit-entreprise" value="{{ client.entreprise or '' }}">
                </div>
                <div class="form-group">
                    <label class="form-label">Secteur</label>
                    <select class="form-select" id="edit-secteur">
                        <option value="">Choisir...</option>
                        {% for s in ['Agroalimentaire', 'Textile', 'Mécanique', 'Électronique', 'Chimie', 'Autre'] %}
                        <option {% if client.secteur == s %}selected{% endif %}>{{ s }}</option>
                        {% endfor %}
                    </select>
                </div>
            </div>
            <button class="btn btn-primary" onclick="saveProfile()" style="margin-top:8px;">
                💾 Enregistrer les modifications
            </button>
        </div>

        <!-- Password Change -->
        <div class="profile-card">
            <div class="profile-card-title">
                🔒 Changer le mot de passe
                <span class="save-indicator" id="pwd-saved">✅ Enregistré</span>
            </div>
            <div class="form-group">
                <label class="form-label">Mot de passe actuel</label>
                <input class="form-input" type="password" id="current-password" placeholder="••••••••">
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label class="form-label">Nouveau mot de passe</label>
                    <input class="form-input" type="password" id="new-password" placeholder="Min. 8 caractères">
                </div>
                <div class="form-group">
                    <label class="form-label">Confirmer</label>
                    <input class="form-input" type="password" id="confirm-password" placeholder="••••••••">
                </div>
            </div>
            <button class="btn btn-primary" onclick="changePassword()" style="margin-top:8px;">
                🔒 Mettre à jour le mot de passe
            </button>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_scripts %}
<script src="{{ url_for('static', filename='js/profile.js') }}"></script>
{% endblock %}
```

### `templates/settings.html`
**Path:** `c:\Users\user\Desktop\pfa backend\trs_digitalisation\templates\settings.html`

```html
{% extends "base.html" %}
{% block title %}Usines & Machines{% endblock %}
{% block page_title %}Gestion des Usines & Machines{% endblock %}

{% block extra_head %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/settings.css') }}">
{% endblock %}

{% block content %}
<!-- Usines Section -->
<div class="settings-section">
    <div class="section-bar">
        <h2>🏭 Vos Usines</h2>
        <button class="btn btn-primary" onclick="openUsineModal()">+ Ajouter une usine</button>
    </div>
    <div id="usines-list">
        <div class="empty-machines">Chargement...</div>
    </div>
</div>

<!-- ═══ USINE MODAL ═══ -->
<div class="modal-overlay" id="usine-modal">
    <div class="modal">
        <div class="modal-title" id="usine-modal-title">Ajouter une usine</div>
        <input type="hidden" id="usine-edit-id">
        <div class="form-group">
            <label class="form-label">Nom de l'usine</label>
            <input class="form-input" id="usine-nom" placeholder="Usine Tunis">
        </div>
        <div class="form-row">
            <div class="form-group">
                <label class="form-label">Ville</label>
                <input class="form-input" id="usine-ville" placeholder="Tunis">
            </div>
            <div class="form-group">
                <label class="form-label">Pays</label>
                <select class="form-select" id="usine-pays">
                    <option>Tunisie</option>
                    <option>Algérie</option>
                    <option>Maroc</option>
                    <option>France</option>
                    <option>Autre</option>
                </select>
            </div>
        </div>
        <div class="form-row">
            <div class="form-group">
                <label class="form-label">Postes / jour</label>
                <select class="form-select" id="usine-postes">
                    <option value="1">1 poste (8h)</option>
                    <option value="2">2 postes (16h)</option>
                    <option value="3">3 postes (24h)</option>
                </select>
            </div>
            <div class="form-group">
                <label class="form-label">Temps requis Tr (h)</label>
                <input class="form-input" type="number" id="usine-tr" value="8" min="1" max="24">
            </div>
        </div>
        <div class="modal-actions">
            <button class="btn btn-secondary" onclick="closeUsineModal()">Annuler</button>
            <button class="btn btn-primary" onclick="saveUsine()">Enregistrer</button>
        </div>
    </div>
</div>

<!-- ═══ MACHINE MODAL ═══ -->
<div class="modal-overlay" id="machine-modal">
    <div class="modal">
        <div class="modal-title" id="machine-modal-title">Ajouter une machine</div>
        <input type="hidden" id="machine-edit-id">
        <input type="hidden" id="machine-usine-id">
        <div class="form-group">
            <label class="form-label">Nom de la machine</label>
            <input class="form-input" id="machine-nom" placeholder="Machine de découpe">
        </div>
        <div class="form-group">
            <label class="form-label">Cadence théorique (pièces/min)</label>
            <input class="form-input" type="number" id="machine-cadence" placeholder="50" min="1" step="0.1">
        </div>
        <div class="form-row">
            <div class="form-group">
                <label class="form-label">Seuil Vibration</label>
                <input class="form-input" type="number" id="machine-seuil-vibration" placeholder="0.0" step="0.1">
            </div>
            <div class="form-group">
                <label class="form-label">Seuil Pièce CM</label>
                <input class="form-input" type="number" id="machine-seuil-piece-cm" placeholder="0.0" step="0.1">
            </div>
        </div>
        <div class="form-group">
            <label class="form-label">Délai entre mesures (s)</label>
            <input class="form-input" type="number" id="machine-delai" placeholder="60" min="1">
        </div>
        <div class="form-row">
            <div class="form-group">
                <label class="form-label">Capteur vitesse</label>
                <select class="form-select" id="machine-capteur-vitesse">
                    <option value="hall">Hall effect</option>
                    <option value="encodeur">Encodeur</option>
                    <option value="inductif">Inductif</option>
                    <option value="simulation">Simulation</option>
                </select>
            </div>
            <div class="form-group">
                <label class="form-label">Capteur pièces</label>
                <select class="form-select" id="machine-capteur-pieces">
                    <option value="ultrason">Ultrason HC-SR04</option>
                    <option value="barrage">Barrage optique</option>
                    <option value="camera">Caméra USB</option>
                    <option value="simulation">Simulation</option>
                </select>
            </div>
        </div>
        <div class="form-row">
            <div class="form-group">
                <label class="form-label">Capteur disponibilité</label>
                <select class="form-select" id="machine-capteur-dispo">
                    <option value="adxl345">ADXL345 (vibration)</option>
                    <option value="courant">Capteur courant</option>
                    <option value="simulation">Simulation</option>
                </select>
            </div>
            <div class="form-group">
                <label class="form-label">Capteur qualité</label>
                <select class="form-select" id="machine-capteur-qualite">
                    <option value="camera">Caméra + IA</option>
                    <option value="manuel">Saisie manuelle</option>
                    <option value="simulation">Simulation</option>
                </select>
            </div>
        </div>
        <div class="modal-actions">
            <button class="btn btn-secondary" onclick="closeMachineModal()">Annuler</button>
            <button class="btn btn-primary" onclick="saveMachine()">Enregistrer</button>
        </div>
    </div>
</div>

<!-- ═══ CONFIRM MODAL ═══ -->
<div class="modal-overlay" id="confirm-modal">
    <div class="modal" style="max-width:400px;">
        <div class="modal-title">⚠️ Confirmation</div>
        <p id="confirm-message" style="font-size:13px;color:var(--text-secondary);margin-bottom:8px;"></p>
        <div class="modal-actions">
            <button class="btn btn-secondary" onclick="closeConfirm()">Annuler</button>
            <button class="btn btn-danger" id="confirm-btn" onclick="">Supprimer</button>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_scripts %}
<script src="{{ url_for('static', filename='js/settings.js') }}"></script>
{% endblock %}
```

### `templates/usine.html`
**Path:** `c:\Users\user\Desktop\pfa backend\trs_digitalisation\templates\usine.html`

```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TRS IoT — {{ usine.nom }}</title>
    <link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', sans-serif; background: #0d1117; color: #e6edf3; min-height: 100vh; }
        nav { background: #161b22; border-bottom: 1px solid #21262d; padding: 0 32px; height: 56px; display: flex; align-items: center; justify-content: space-between; position: sticky; top: 0; z-index: 100; }
        .nav-logo { font-family: 'Space Mono', monospace; font-size: 15px; color: #58a6ff; letter-spacing: 2px; text-decoration: none; }
        .container { max-width: 1200px; margin: 0 auto; padding: 32px 24px; }
        .page-header { margin-bottom: 32px; }
        .page-header h1 { font-size: 22px; font-weight: 500; color: #f0f6ff; }
        .btn-back { color: #58a6ff; text-decoration: none; font-size: 13px; margin-bottom: 16px; display: inline-block; }
        .machines-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .machine-card { background: #161b22; border: 1px solid #21262d; border-radius: 12px; padding: 24px; text-decoration: none; color: inherit; display: block; }
        .machine-name { font-size: 18px; font-weight: 600; margin-bottom: 12px; color: #f0f6ff; }
        .trs-val { font-family: 'Space Mono', monospace; font-size: 24px; font-weight: 700; color: #3fb950; }
    </style>
</head>
<body>
<nav>
    <a href="/dashboard" class="nav-logo">TRS · IOT</a>
</nav>
<div class="container">
    <a href="/dashboard" class="btn-back">← Retour au dashboard</a>
    <div class="page-header">
        <h1>Usine : {{ usine.nom }}</h1>
        <p>{{ usine.ville }}, {{ usine.pays }}</p>
    </div>
    <div class="machines-grid">
        {% for machine in usine.machines %}
        <a href="/machine/{{ machine.id }}" class="machine-card">
            <div class="machine-name">{{ machine.nom }}</div>
            <div class="trs-val">{{ machine.trs }}%</div>
            <p style="font-size: 12px; color: #8b949e; margin-top: 8px;">Cadence : {{ machine.cadence_theorique }} pcs/min</p>
        </a>
        {% endfor %}
    </div>
</div>
</body>
</html>
```

---

## CSS Files

### `static/css/analysis.css`
**Path:** `c:\Users\user\Desktop\pfa backend\trs_digitalisation\static\css\analysis.css`

```css
/* Analysis page styles */

.analysis-controls {
    display: flex; gap: 12px; align-items: center;
    flex-wrap: wrap; margin-bottom: 24px;
}
.control-group { display: flex; align-items: center; gap: 8px; }
.control-label { font-size: 12px; color: var(--text-secondary); font-weight: 500; }
.control-select {
    padding: 7px 12px; background: var(--bg-secondary);
    border: 1px solid var(--border); border-radius: 8px;
    color: var(--text-primary); font-size: 13px;
    font-family: 'Inter', sans-serif;
}
.control-select:focus { outline: none; border-color: var(--blue); }
.control-select option { background: var(--bg-secondary); }

.chart-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 12px; padding: 24px;
    margin-bottom: 20px;
}
.chart-title { font-size: 14px; font-weight: 600; color: var(--text-primary); margin-bottom: 4px; }
.chart-subtitle { font-size: 12px; color: var(--text-secondary); margin-bottom: 20px; }
.chart-wrapper { position: relative; height: 350px; }

.stats-grid {
    display: grid; grid-template-columns: repeat(4, 1fr);
    gap: 12px; margin-bottom: 24px;
}
.stat-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 10px; padding: 16px; text-align: center;
}
.stat-value {
    font-family: 'Space Mono', monospace;
    font-size: 22px; font-weight: 700; margin-bottom: 4px;
}
.stat-label {
    font-size: 10px; color: var(--text-secondary);
    text-transform: uppercase; letter-spacing: 0.8px;
}

.metric-chips { display: flex; gap: 8px; flex-wrap: wrap; }
.metric-chip {
    padding: 5px 14px; border-radius: 20px;
    font-size: 12px; font-weight: 500;
    cursor: pointer; border: 1px solid var(--border);
    background: transparent; color: var(--text-secondary);
    transition: all 0.2s; font-family: 'Inter', sans-serif;
}
.metric-chip:hover { border-color: var(--text-secondary); }
.metric-chip.active { border-color: var(--blue); color: var(--blue); background: rgba(88,166,255,0.1); }

.compare-chart-wrapper { position: relative; height: 300px; }

@media (max-width: 768px) {
    .stats-grid { grid-template-columns: repeat(2, 1fr); }
    .chart-wrapper { height: 250px; }
}
```

### `static/css/base.css`
**Path:** `c:\Users\user\Desktop\pfa backend\trs_digitalisation\static\css\base.css`

```css
/* ══════════════════════════════════════════════════════════════
   BASE STYLES — shared across all pages
   ══════════════════════════════════════════════════════════════ */

/* ── Reset ── */
*, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }

:root {
    --bg-primary: #0d1117;
    --bg-secondary: #161b22;
    --bg-tertiary: #1c2128;
    --border: #21262d;
    --border-hover: #30363d;
    --text-primary: #e6edf3;
    --text-secondary: #8b949e;
    --text-muted: #484f58;
    --blue: #58a6ff;
    --blue-dark: #1d4ed8;
    --green: #3fb950;
    --green-dim: rgba(63,185,80,0.15);
    --yellow: #d29922;
    --yellow-dim: rgba(210,153,34,0.15);
    --red: #f85149;
    --red-dim: rgba(248,81,73,0.15);
    --purple: #a371f7;
    --sidebar-width: 240px;
    --sidebar-collapsed: 64px;
    --topbar-height: 56px;
}

body {
    font-family: 'Inter', sans-serif;
    background: var(--bg-primary);
    color: var(--text-primary);
    min-height: 100vh;
    overflow-x: hidden;
}

/* ── Sidebar ── */
.sidebar {
    position: fixed; top: 0; left: 0; bottom: 0;
    width: var(--sidebar-width);
    background: var(--bg-secondary);
    border-right: 1px solid var(--border);
    display: flex; flex-direction: column;
    z-index: 200;
    transition: width 0.3s cubic-bezier(0.4,0,0.2,1), transform 0.3s cubic-bezier(0.4,0,0.2,1);
}
.sidebar.collapsed { width: var(--sidebar-collapsed); }
.sidebar-header {
    height: var(--topbar-height);
    display: flex; align-items: center;
    padding: 0 16px; gap: 12px;
    border-bottom: 1px solid var(--border);
    flex-shrink: 0;
}
.sidebar-logo {
    font-family: 'Space Mono', monospace;
    font-size: 14px; color: var(--blue);
    letter-spacing: 2px; white-space: nowrap;
    overflow: hidden; transition: opacity 0.2s;
}
.sidebar.collapsed .sidebar-logo { opacity: 0; width: 0; }
.sidebar-toggle {
    background: none; border: none; color: var(--text-secondary);
    cursor: pointer; font-size: 18px; padding: 4px;
    border-radius: 6px; transition: background 0.2s;
    flex-shrink: 0;
}
.sidebar-toggle:hover { background: var(--bg-tertiary); }
.sidebar-nav {
    flex: 1; padding: 12px 8px;
    display: flex; flex-direction: column; gap: 2px;
    overflow-y: auto;
}
.nav-item {
    display: flex; align-items: center; gap: 12px;
    padding: 10px 12px; border-radius: 8px;
    color: var(--text-secondary); text-decoration: none;
    font-size: 13px; font-weight: 500;
    transition: all 0.15s; white-space: nowrap;
}
.nav-item:hover { background: var(--bg-tertiary); color: var(--text-primary); }
.nav-item.active { background: rgba(88,166,255,0.1); color: var(--blue); }
.nav-item .nav-icon {
    width: 20px; height: 20px;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px; flex-shrink: 0;
}
.nav-item .nav-label { overflow: hidden; transition: opacity 0.2s; }
.sidebar.collapsed .nav-label { opacity: 0; width: 0; }
.nav-separator { height: 1px; background: var(--border); margin: 8px 12px; }
.sidebar-footer { padding: 12px 8px; border-top: 1px solid var(--border); }

/* ── Topbar ── */
.topbar {
    position: fixed; top: 0; right: 0;
    left: var(--sidebar-width);
    height: var(--topbar-height);
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border);
    display: flex; align-items: center;
    justify-content: space-between;
    padding: 0 24px; z-index: 150;
    transition: left 0.3s cubic-bezier(0.4,0,0.2,1);
}
.sidebar.collapsed ~ .topbar { left: var(--sidebar-collapsed); }
.topbar-left { display: flex; align-items: center; gap: 16px; }
.topbar-title { font-size: 15px; font-weight: 600; color: var(--text-primary); }
.topbar-right { display: flex; align-items: center; gap: 16px; }
.topbar-user { font-size: 12px; color: var(--text-secondary); }
.topbar-user strong { color: var(--text-primary); font-weight: 500; }
.topbar-avatar {
    width: 32px; height: 32px; border-radius: 50%;
    background: linear-gradient(135deg, var(--blue-dark), var(--blue));
    display: flex; align-items: center; justify-content: center;
    font-size: 13px; font-weight: 600; color: #fff;
}
.mobile-toggle {
    display: none; background: none; border: none;
    color: var(--text-secondary); font-size: 20px; cursor: pointer;
}

/* ── Main content ── */
.main-content {
    margin-left: var(--sidebar-width);
    margin-top: var(--topbar-height);
    padding: 28px;
    min-height: calc(100vh - var(--topbar-height));
    transition: margin-left 0.3s cubic-bezier(0.4,0,0.2,1);
}
.sidebar.collapsed ~ .main-content { margin-left: var(--sidebar-collapsed); }

/* ── Utilities ── */
.card {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 12px; padding: 24px;
}
.card-header {
    display: flex; justify-content: space-between;
    align-items: center; margin-bottom: 20px;
}
.card-title { font-size: 14px; font-weight: 600; color: var(--text-primary); }
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
.grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }

/* ── Flex Helpers ── */
.flex-align-center { display: flex; align-items: center; }
.flex-between { display: flex; align-items: center; justify-content: space-between; }
.gap-8 { gap: 8px; }
.gap-12 { gap: 12px; }
.gap-16 { gap: 16px; }

/* ── KPI Cards ── */
.kpi-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 12px; padding: 20px;
    border-left: 3px solid;
    transition: transform 0.2s, border-color 0.2s;
}
.kpi-card:hover { transform: translateY(-2px); }
.kpi-label {
    font-size: 11px; color: var(--text-secondary);
    text-transform: uppercase; letter-spacing: 0.8px;
    margin-bottom: 8px;
}
.kpi-value {
    font-family: 'Space Mono', monospace;
    font-size: 28px; font-weight: 700;
}
.kpi-sub { font-size: 11px; color: var(--text-muted); margin-top: 4px; }

/* ── Colors ── */
.c-green  { color: var(--green); }
.c-yellow { color: var(--yellow); }
.c-red    { color: var(--red); }
.c-blue   { color: var(--blue); }
.c-purple { color: var(--purple); }
.bl-green  { border-left-color: var(--green); }
.bl-blue   { border-left-color: var(--blue); }
.bl-purple { border-left-color: var(--purple); }
.bl-yellow { border-left-color: var(--yellow); }
.bl-red    { border-left-color: var(--red); }

/* ── Buttons ── */
.btn {
    padding: 8px 16px; border-radius: 8px;
    font-size: 13px; font-weight: 500;
    cursor: pointer; border: none;
    font-family: 'Inter', sans-serif;
    transition: all 0.2s; display: inline-flex;
    align-items: center; gap: 6px;
}
.btn-primary { background: var(--blue-dark); color: #fff; }
.btn-primary:hover { background: #2563eb; }
.btn-secondary { background: var(--bg-tertiary); color: var(--text-primary); border: 1px solid var(--border); }
.btn-secondary:hover { border-color: var(--text-secondary); }
.btn-danger { background: var(--red-dim); color: var(--red); }
.btn-danger:hover { background: rgba(248,81,73,0.25); }
.btn-sm { padding: 5px 10px; font-size: 12px; }
.btn-icon { padding: 6px 8px; }

/* ── Forms ── */
.form-group { margin-bottom: 16px; }
.form-label {
    display: block; font-size: 11px; color: var(--text-secondary);
    text-transform: uppercase; letter-spacing: 0.8px;
    margin-bottom: 6px; font-weight: 500;
}
.form-input, .form-select {
    width: 100%; padding: 9px 12px;
    background: var(--bg-primary);
    border: 1px solid var(--border);
    border-radius: 8px; color: var(--text-primary);
    font-size: 13px; font-family: 'Inter', sans-serif;
    transition: border-color 0.2s;
}
.form-input:focus, .form-select:focus {
    outline: none; border-color: var(--blue);
    box-shadow: 0 0 0 3px rgba(88,166,255,0.1);
}
.form-select option { background: var(--bg-secondary); }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }

/* ── Modal ── */
.modal-overlay {
    display: none; position: fixed; inset: 0;
    background: rgba(0,0,0,0.6); z-index: 1000;
    align-items: center; justify-content: center;
    backdrop-filter: blur(4px);
}
.modal-overlay.active { display: flex; }
.modal {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 16px; padding: 28px;
    width: 90%; max-width: 500px;
    max-height: 85vh; overflow-y: auto;
    animation: modalIn 0.25s ease;
}
@keyframes modalIn {
    from { opacity: 0; transform: scale(0.95) translateY(10px); }
    to   { opacity: 1; transform: scale(1)    translateY(0); }
}
.modal-title {
    font-size: 16px; font-weight: 600;
    color: var(--text-primary); margin-bottom: 20px;
}
.modal-actions {
    display: flex; gap: 10px; justify-content: flex-end;
    margin-top: 20px; padding-top: 16px;
    border-top: 1px solid var(--border);
}

/* ── Toast ── */
.toast {
    position: fixed; bottom: 24px; right: 24px;
    background: var(--bg-tertiary);
    border: 1px solid var(--border);
    border-radius: 10px; padding: 12px 20px;
    font-size: 13px; color: var(--text-primary);
    z-index: 2000; display: none;
    animation: toastIn 0.3s ease;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
}
.toast.show { display: flex; align-items: center; gap: 8px; }
@keyframes toastIn {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* ── Gauge ── */
.gauge-container { position: relative; width: 140px; height: 90px; margin: 0 auto; }
.gauge-value {
    position: absolute; bottom: 4px; left: 50%;
    transform: translateX(-50%);
    font-family: 'Space Mono', monospace;
    font-size: 20px; font-weight: 700;
}
.gauge-label {
    text-align: center; font-size: 11px;
    color: var(--text-secondary); margin-top: 4px;
    text-transform: uppercase; letter-spacing: 0.5px;
}

/* ── Badge ── */
.badge {
    font-size: 10px; padding: 3px 8px;
    border-radius: 20px; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.5px;
}
.badge-green  { background: var(--green-dim);  color: var(--green); }
.badge-yellow { background: var(--yellow-dim); color: var(--yellow); }
.badge-red    { background: var(--red-dim);    color: var(--red); }
.badge-live   { background: rgba(59, 130, 246, 0.1); color: var(--blue); border: 1px solid rgba(88, 166, 255, 0.3); display: flex; align-items: center; gap: 6px; }

/* ── Status dot ── */
.status-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
.status-dot.online  { background: var(--green); box-shadow: 0 0 6px var(--green); }
.status-dot.offline { background: var(--red); }
.status-dot.pulse {
    animation: pulse-animation 2s infinite;
}

@keyframes pulse-animation {
    0% { box-shadow: 0 0 0 0px rgba(88, 166, 255, 0.4); }
    70% { box-shadow: 0 0 0 10px rgba(88, 166, 255, 0); }
    100% { box-shadow: 0 0 0 0px rgba(88, 166, 255, 0); }
}

/* ── Tables ── */
.data-table { width: 100%; border-collapse: collapse; }
.data-table th {
    text-align: left; font-size: 11px;
    color: var(--text-secondary); text-transform: uppercase;
    letter-spacing: 0.8px; padding: 10px 12px;
    border-bottom: 1px solid var(--border);
}
.data-table td { padding: 12px; font-size: 13px; border-bottom: 1px solid var(--border); }
.data-table tr:hover td { background: var(--bg-tertiary); }
.data-table .actions { display: flex; gap: 6px; }

/* ── Responsive ── */
@media (max-width: 1024px) {
    .grid-4 { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 768px) {
    .sidebar { transform: translateX(-100%); width: var(--sidebar-width); }
    .sidebar.mobile-open { transform: translateX(0); }
    .sidebar.collapsed { transform: translateX(-100%); }
    .topbar { left: 0; }
    .main-content { margin-left: 0; }
    .sidebar.collapsed ~ .topbar { left: 0; }
    .sidebar.collapsed ~ .main-content { margin-left: 0; }
    .mobile-toggle { display: block; }
    .grid-4 { grid-template-columns: 1fr 1fr; }
    .grid-3 { grid-template-columns: 1fr; }
    .grid-2 { grid-template-columns: 1fr; }
    .form-row { grid-template-columns: 1fr; }
    .modal { width: 95%; margin: 0 10px; }
}
@media (max-width: 480px) {
    .grid-4 { grid-template-columns: 1fr; }
    .main-content { padding: 16px; }
    .topbar-user { display: none; }
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }
```

### `static/css/dashboard.css`
**Path:** `c:\Users\user\Desktop\pfa backend\trs_digitalisation\static\css\dashboard.css`

```css
/* Dashboard-specific styles */

.gauges-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px; margin-top: 24px;
}
.machine-gauge-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 12px; padding: 20px;
    transition: border-color 0.2s, transform 0.2s;
    overflow: hidden;
}
.machine-gauge-card:hover { border-color: var(--blue); transform: translateY(-2px); }
.machine-gauge-header {
    display: flex; justify-content: space-between;
    align-items: center; margin-bottom: 12px;
}
.machine-gauge-name { font-size: 14px; font-weight: 600; color: var(--text-primary); }
.machine-gauge-usine { font-size: 11px; color: var(--text-secondary); }

/* Big TRS gauge */
.main-gauge { display: flex; flex-direction: column; align-items: center; padding: 8px 0 4px; }
.main-gauge canvas { width: 160px !important; height: 90px !important; }
.main-gauge-value {
    font-family: 'Space Mono', monospace;
    font-size: 26px; font-weight: 700; margin-top: -2px;
}
.main-gauge-label {
    font-size: 11px; color: var(--text-secondary);
    text-transform: uppercase; letter-spacing: 1px; margin-top: 2px;
}

/* Small gauges row */
.sub-gauges-row {
    display: grid; grid-template-columns: repeat(3, 1fr);
    gap: 4px; margin-top: 12px; padding-top: 12px;
    border-top: 1px solid var(--border);
}
.mini-gauge { display: flex; flex-direction: column; align-items: center; }
.mini-gauge canvas { width: 70px !important; height: 42px !important; }
.mini-gauge-value {
    font-family: 'Space Mono', monospace;
    font-size: 13px; font-weight: 700; margin-top: -2px;
}
.mini-gauge-label {
    font-size: 9px; color: var(--text-secondary);
    text-transform: uppercase; letter-spacing: 0.5px; margin-top: 2px;
}

/* Section header & filters */
.section-header {
    display: flex; justify-content: space-between;
    align-items: center; margin-bottom: 16px; margin-top: 32px;
}
.section-title { font-size: 14px; font-weight: 600; color: var(--text-primary); }
.section-subtitle { font-size: 12px; color: var(--text-secondary); }
.usine-chips { display: flex; gap: 8px; flex-wrap: wrap; }
.usine-chip {
    padding: 5px 14px; border-radius: 20px;
    font-size: 12px; font-weight: 500;
    cursor: pointer; border: 1px solid var(--border);
    background: transparent; color: var(--text-secondary);
    transition: all 0.2s; font-family: 'Inter', sans-serif;
}
.usine-chip:hover, .usine-chip.active {
    background: rgba(88,166,255,0.1);
    border-color: var(--blue); color: var(--blue);
}

/* Empty state */
.empty-state { text-align: center; padding: 60px 20px; color: var(--text-secondary); }
.empty-state .empty-icon { font-size: 48px; margin-bottom: 16px; opacity: 0.5; }
.empty-state h3 { font-size: 16px; margin-bottom: 8px; color: var(--text-primary); }
.empty-state p { font-size: 13px; margin-bottom: 20px; }
```

### `static/css/machine.css`
**Path:** `c:\Users\user\Desktop\pfa backend\trs_digitalisation\static\css\machine.css`

```css
/* ── Machine Detailed View ── */

.loader-container {
    display: flex; justify-content: center; align-items: center;
    height: 60vh; color: var(--text-secondary);
}

.machine-header {
    margin-top: 10px;
    padding: 20px 24px;
}

.machine-title {
    font-size: 24px; font-weight: 700; color: var(--text-primary);
    margin-bottom: 4px;
}

.machine-subtitle {
    font-size: 14px; color: var(--text-secondary);
}

/* KPIs Gauges */
.gauges-row {
    display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px;
    margin-top: 16px;
}

@media (max-width: 1024px) {
    .gauges-row { grid-template-columns: 1fr 1fr; }
    .main-kpi { grid-column: span 2; }
}

@media (max-width: 600px) {
    .gauges-row { grid-template-columns: 1fr; }
    .main-kpi { grid-column: span 1; }
}

.kpi-gauge-card {
    padding: 20px;
    display: flex; flex-direction: column;
    min-width: 0; /* Prevents CSS Grid overflow */
}

.gauge-header {
    display: flex; justify-content: space-between; align-items: center;
    font-size: 14px; font-weight: 600; color: var(--text-primary);
    margin-bottom: 20px;
}

.gauge-chart-container {
    position: relative; width: 100%; height: 100%;
    display: flex; justify-content: center; align-items: center;
    min-height: 120px;
    min-width: 0; /* Constraints canvas growth */
}
.gauge-chart-container.main { min-height: 180px; }

.gauge-value {
    position: absolute; bottom: 10px; left: 50%;
    transform: translateX(-50%);
    font-family: 'Space Mono', monospace;
    font-size: 20px; font-weight: 700; color: var(--text-primary);
}

/* Stats grid */
.production-stats {
    display: grid; grid-template-columns: 1fr 1fr; gap: 16px;
    margin-top: 16px;
}

.stat-box {
    background: var(--bg-tertiary);
    border: 1px solid var(--border);
    border-radius: 8px; padding: 16px;
}

.stat-label {
    font-size: 11px; color: var(--text-secondary);
    text-transform: uppercase; letter-spacing: 0.5px;
    margin-bottom: 8px; font-weight: 500;
}

.stat-value {
    font-family: 'Space Mono', monospace;
    font-size: 24px; font-weight: 700;
}

/* Sensor List */
.sensor-list {
    list-style: none; padding: 0; margin: 16px 0 0 0;
}

.sensor-item {
    display: flex; justify-content: space-between; align-items: center;
    padding: 14px 16px; 
    background: var(--bg-tertiary);
    border: 1px solid var(--border);
    border-radius: 8px; margin-bottom: 8px;
}

.sensor-info {
    display: flex; align-items: center; gap: 14px;
}

.sensor-icon {
    font-size: 20px; width: 32px; height: 32px;
    display: flex; align-items: center; justify-content: center;
    background: var(--bg-secondary); border-radius: 6px;
    border: 1px solid var(--border);
}

.sensor-name {
    font-size: 13px; font-weight: 600; color: var(--text-primary);
}

.sensor-type {
    font-size: 11px; color: var(--text-secondary); margin-top: 2px;
    font-family: monospace;
}

.sensor-status {
    font-size: 12px; font-weight: 500;
}

.mt-24 { margin-top: 24px; }
```

### `static/css/profile.css`
**Path:** `c:\Users\user\Desktop\pfa backend\trs_digitalisation\static\css\profile.css`

```css
/* Profile page styles */

.profile-grid {
    display: grid; grid-template-columns: 300px 1fr;
    gap: 24px; align-items: start;
}
.profile-sidebar {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 12px; padding: 32px 24px; text-align: center;
}
.profile-avatar {
    width: 80px; height: 80px; border-radius: 50%;
    background: linear-gradient(135deg, var(--blue-dark), var(--blue));
    display: flex; align-items: center; justify-content: center;
    font-size: 28px; font-weight: 700; color: #fff;
    margin: 0 auto 16px;
    box-shadow: 0 4px 20px rgba(88,166,255,0.25);
}
.profile-name { font-size: 18px; font-weight: 600; color: var(--text-primary); margin-bottom: 4px; }
.profile-email { font-size: 13px; color: var(--text-secondary); margin-bottom: 16px; }
.profile-meta { text-align: left; padding-top: 16px; border-top: 1px solid var(--border); }
.profile-meta-item { display: flex; justify-content: space-between; padding: 8px 0; font-size: 13px; }
.profile-meta-label { color: var(--text-secondary); }
.profile-meta-value { color: var(--text-primary); font-weight: 500; }
.profile-forms { display: flex; flex-direction: column; gap: 20px; }
.profile-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 12px; padding: 24px;
}
.profile-card-title {
    font-size: 15px; font-weight: 600;
    color: var(--text-primary); margin-bottom: 20px;
    display: flex; align-items: center; gap: 8px;
}
.save-indicator {
    font-size: 12px; color: var(--green);
    display: none; align-items: center; gap: 4px;
    margin-left: auto;
}
.save-indicator.show { display: flex; }

@media (max-width: 768px) {
    .profile-grid { grid-template-columns: 1fr; }
}
```

### `static/css/settings.css`
**Path:** `c:\Users\user\Desktop\pfa backend\trs_digitalisation\static\css\settings.css`

```css
/* Settings page styles */

.settings-section { margin-bottom: 32px; }
.section-bar {
    display: flex; justify-content: space-between;
    align-items: center; margin-bottom: 16px;
}
.section-bar h2 { font-size: 16px; font-weight: 600; }

.usine-block {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 12px; margin-bottom: 16px; overflow: hidden;
}
.usine-block-header {
    display: flex; justify-content: space-between;
    align-items: center; padding: 16px 20px;
    background: var(--bg-tertiary);
    border-bottom: 1px solid var(--border);
    cursor: pointer; transition: background 0.2s;
}
.usine-block-header:hover { background: rgba(88,166,255,0.05); }
.usine-block-title { display: flex; align-items: center; gap: 12px; }
.usine-block-name { font-size: 14px; font-weight: 600; color: var(--text-primary); }
.usine-block-info { font-size: 12px; color: var(--text-secondary); }
.usine-block-actions { display: flex; gap: 6px; }
.usine-block-body { padding: 16px 20px; }
.machines-table-wrap { overflow-x: auto; }
.add-machine-row {
    display: flex; justify-content: center;
    padding: 12px; border-top: 1px solid var(--border);
}
.empty-machines {
    text-align: center; padding: 32px;
    color: var(--text-secondary); font-size: 13px;
}

@media (max-width: 768px) {
    .usine-block-header {
        flex-direction: column; align-items: flex-start; gap: 12px;
    }
    .usine-block-actions { align-self: flex-end; }
}
```
