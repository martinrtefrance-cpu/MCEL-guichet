"""
ui_components.py — Composants d'interface réutilisables, style RTE.
CSS, header, sidebar (navigation + utilisateur connecté), notifications, export.
"""
import streamlit as st
import pandas as pd
import io
import os

# ── Couleurs RTE ──────────────────────────────────────────────────────
RTE_BLUE = "#00B2E3"
RTE_DARK_BLUE = "#005F83"
RTE_LIGHT_BLUE = "#E8F7FC"
LOGO_PATH = os.path.join(os.path.dirname(__file__), "assets", "logo_rte.png")

# Placeholder affiché dans les listes déroulantes vides
PLACEHOLDER = "..."

PAGE_PATHS = {
    "dashboard":   "Tableau_de_Bord.py",
    "nouvelle":    "pages/1_Nouvelle_Demande.py",
    "demandes":    "pages/2_Mes_Demandes.py",
    "attribution": "pages/3_Attribution.py",
    "import":      "pages/4_Import_Commandes.py",
    "donnees":     "pages/5_Donnees.py",
    "suivi":       "pages/6_Suivi.py",
}


def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Source Sans 3', 'Segoe UI', sans-serif; }

    .block-container { padding-top: 2rem !important; }

    /* Header */
    .rte-header {
        background: linear-gradient(135deg, #005F83 0%, #00B2E3 100%);
        padding: 1rem 2rem; border-radius: 0 0 16px 16px;
        display: flex; align-items: center; gap: 1rem;
        margin-bottom: 1.5rem; box-shadow: 0 4px 20px rgba(0,94,131,0.15);
    }
    .rte-header img { height: 50px; border-radius: 50%; }
    .rte-header h1 { color: white; font-size: 1.5rem; font-weight: 600; margin: 0; }
    .rte-header p { color: rgba(255,255,255,0.85); margin: 0; font-size: 0.9rem; }

    /* KPI */
    .kpi-card {
        background: white; border-radius: 12px; padding: 1.2rem;
        text-align: center; box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        border-left: 4px solid #00B2E3; transition: transform 0.2s;
    }
    .kpi-card:hover { transform: translateY(-2px); }
    .kpi-value { font-size: 2rem; font-weight: 700; color: #005F83; line-height: 1.1; }
    .kpi-label { font-size: 0.8rem; color: #6B7280; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 0.3rem; }

    /* Badges */
    .badge { display: inline-block; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.78rem; font-weight: 600; }
    .badge-brouillon { background: #E0E0E0; color: #424242; }
    .badge-soumise   { background: #FFF3E0; color: #E65100; }
    .badge-attribuee { background: #E3F2FD; color: #1565C0; }
    .badge-commandee { background: #E8F5E9; color: #2E7D32; }
    .badge-annulee   { background: #FFEBEE; color: #C62828; }

    /* Section headers */
    .section-header {
        background: linear-gradient(90deg, #00B2E3 0%, #005F83 100%);
        color: white; padding: 0.6rem 1.2rem; border-radius: 8px;
        font-weight: 600; font-size: 1rem; margin: 1.2rem 0 0.8rem 0;
    }

    /* Tables */
    .dataframe { font-size: 0.85rem !important; }
    .dataframe th { background: #005F83 !important; color: white !important; font-weight: 600 !important; padding: 0.6rem !important; }
    .dataframe td { padding: 0.5rem !important; }

    /* Info box */
    .info-box { background: #E8F7FC; border-left: 4px solid #00B2E3; padding: 1rem 1.2rem; border-radius: 0 8px 8px 0; margin: 0.8rem 0; font-size: 0.9rem; }

    /* Admin lock */
    .admin-lock-box { background: #FFF8E1; border: 1px solid #FFE082; border-radius: 12px; padding: 2rem; text-align: center; max-width: 420px; margin: 3rem auto; }
    .admin-lock-box h3 { color: #005F83; margin-bottom: 0.5rem; }

    /* Confirmation box */
    .confirm-box {
        background: #FFF3E0; border: 2px solid #FF9800; border-radius: 12px;
        padding: 1.5rem; margin: 1rem 0;
    }
    .confirm-box h4 { color: #E65100; margin: 0 0 0.5rem 0; }

    /* Big success alert — very visible for managers */
    @keyframes alert-slide-in {
        from { transform: translateY(-20px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    .success-alert {
        background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
        border: 2px solid #4CAF50; border-radius: 12px;
        padding: 1.5rem 2rem; margin: 1rem 0 1.5rem;
        display: flex; align-items: center; gap: 1rem;
        animation: alert-slide-in 0.4s ease-out;
        box-shadow: 0 4px 16px rgba(76,175,80,0.2);
    }
    .success-alert-icon { font-size: 2.5rem; flex-shrink: 0; }
    .success-alert-title { font-size: 1.15rem; font-weight: 700; color: #2E7D32; margin: 0; }
    .success-alert-msg { font-size: 0.9rem; color: #1B5E20; margin: 0.2rem 0 0; }

    /* ── Sidebar ─────────────────────────────────────── */
    section[data-testid="stSidebar"] { background: #FAFCFE; }
    section[data-testid="stSidebar"] > div:first-child { padding-top: 0 !important; }

    /* Force sidebar always open — hide collapse button */
    button[data-testid="stSidebarCollapseButton"],
    [data-testid="collapsedControl"] {
        display: none !important;
        pointer-events: none !important;
    }
    section[data-testid="stSidebar"] {
        min-width: 280px !important;
        max-width: 320px !important;
        transform: none !important;
    }
    section[data-testid="stSidebar"] ul[data-testid="stSidebarNavItems"],
    section[data-testid="stSidebar"] nav[data-testid="stSidebarNav"] { display: none !important; }

    .sidebar-brand {
        background: linear-gradient(135deg, #005F83 0%, #00B2E3 100%);
        margin: -1rem -1rem 0 -1rem; padding: 1.4rem 1.2rem 1.1rem;
        display: flex; align-items: center; gap: 0.75rem;
    }
    .sidebar-brand img { width: 42px; height: 42px; border-radius: 50%; border: 2px solid rgba(255,255,255,0.4); }
    .sidebar-brand-text { color: white; font-weight: 700; font-size: 1.05rem; line-height: 1.2; }
    .sidebar-brand-sub { color: rgba(255,255,255,0.7); font-size: 0.72rem; text-transform: uppercase; }

    /* Connected user pill in sidebar */
    .sidebar-user-pill {
        background: white; border: 1px solid #E6EDF3; border-radius: 10px;
        padding: 0.55rem 0.8rem; margin: 0.7rem 0 0.2rem;
        display: flex; align-items: center; gap: 0.55rem;
    }
    .sidebar-user-dot { width: 8px; height: 8px; border-radius: 50%; background: #4CAF50; flex-shrink: 0; }
    .sidebar-user-email { font-size: 0.78rem; color: #374151; font-weight: 500; overflow: hidden; text-overflow: ellipsis; }

    .sidebar-nav-label { font-size: 0.68rem; font-weight: 600; color: #9CA3AF; text-transform: uppercase; letter-spacing: 1px; padding: 0.9rem 0 0.25rem 0.2rem; }

    section[data-testid="stSidebar"] [data-testid="stPageLink"] { margin-bottom: 1px; width: 100%; }
    section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"] {
        display: block !important; width: 100% !important; border-radius: 8px !important;
        padding: 0.5rem 0.7rem !important; font-size: 0.88rem !important; font-weight: 500 !important;
        color: #374151 !important; transition: background 0.15s ease !important;
        border: none !important; text-decoration: none !important;
    }
    section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"]:hover { background: #E8F7FC !important; color: #005F83 !important; }
    section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"][disabled],
    section[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"][aria-disabled="true"] {
        background: linear-gradient(135deg, #E8F7FC 0%, #D1EFFA 100%) !important;
        color: #005F83 !important; font-weight: 600 !important;
        box-shadow: inset 3px 0 0 #00B2E3 !important; opacity: 1 !important;
    }

    .sidebar-stats { display: grid; grid-template-columns: 1fr 1fr; gap: 0.45rem; margin: 0.8rem 0; }
    .sidebar-stat { background: white; border: 1px solid #E6EDF3; border-radius: 8px; padding: 0.5rem 0.6rem; text-align: center; }
    .sidebar-stat-val { font-size: 1.15rem; font-weight: 700; line-height: 1.1; }
    .sidebar-stat-lbl { font-size: 0.65rem; color: #8B95A5; text-transform: uppercase; }
    .sidebar-footer { margin-top: 1.5rem; padding-top: 0.8rem; border-top: 1px solid #E6EDF3; text-align: center; font-size: 0.7rem; color: #9CA3AF; line-height: 1.6; }

    /* Accordion / Expander — RTE style */
    .streamlit-expanderHeader {
        background: linear-gradient(90deg, #E8F7FC 0%, #F0F4F8 100%) !important;
        border-radius: 8px !important;
        font-weight: 600 !important; color: #005F83 !important;
        font-size: 0.95rem !important;
        border-left: 3px solid #00B2E3 !important;
    }
    .streamlit-expanderContent {
        border: 1px solid #E6EDF3 !important;
        border-top: none !important;
        border-radius: 0 0 8px 8px !important;
    }

    /* Buttons */
    .stButton > button { border-radius: 8px; font-weight: 600; transition: all 0.2s; }
    .stButton > button:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,178,227,0.3); }
    .stTabs [data-baseweb="tab"] { font-weight: 600; color: #005F83; }

    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════

def render_header(subtitle=""):
    logo_b64 = ""
    if os.path.exists(LOGO_PATH):
        import base64
        with open(LOGO_PATH, "rb") as f:
            logo_b64 = base64.b64encode(f.read()).decode()
    st.markdown(f"""
    <div class="rte-header">
        <img src="data:image/png;base64,{logo_b64}" alt="RTE">
        <div>
            <h1>Guichet Unique — Demandes d'Études</h1>
            <p>{subtitle}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════
# KPI CARDS
# ══════════════════════════════════════════════════════════════════════

def render_kpi_cards(kpi: dict):
    cols = st.columns(6)
    items = [
        ("total", "Total Demandes", "#005F83"), ("brouillon", "Brouillons", "#9E9E9E"),
        ("soumises", "Soumises", "#FF9800"), ("attribuees", "Attribuées", "#2196F3"),
        ("commandees", "Commandées", "#4CAF50"), ("annulees", "Annulées", "#F44336"),
    ]
    for col, (key, label, color) in zip(cols, items):
        with col:
            st.markdown(f"""
            <div class="kpi-card" style="border-left-color: {color};">
                <div class="kpi-value" style="color: {color};">{kpi[key]}</div>
                <div class="kpi-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)


def render_taux_cards(kpi: dict):
    c1, c2, _ = st.columns([1, 1, 2])
    with c1:
        st.markdown(f"""
        <div class="kpi-card" style="border-left-color: #2196F3;">
            <div class="kpi-value" style="color: #2196F3;">{kpi['taux_attribution']}%</div>
            <div class="kpi-label">Taux d'attribution</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="kpi-card" style="border-left-color: #4CAF50;">
            <div class="kpi-value" style="color: #4CAF50;">{kpi['taux_commande']}%</div>
            <div class="kpi-label">Taux de commande</div>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════
# SMALL COMPONENTS
# ══════════════════════════════════════════════════════════════════════

def section_header(title: str, icon: str = "📋"):
    st.markdown(f'<div class="section-header">{icon} {title}</div>', unsafe_allow_html=True)

def status_badge(statut: str) -> str:
    css_class = {"Brouillon": "badge-brouillon", "Soumise": "badge-soumise", "Attribuée": "badge-attribuee", "Commandée": "badge-commandee", "Annulée": "badge-annulee"}.get(statut, "badge-brouillon")
    return f'<span class="badge {css_class}">{statut}</span>'

def info_box(text: str):
    st.markdown(f'<div class="info-box">{text}</div>', unsafe_allow_html=True)


def clean_select(val: str) -> str:
    """Convertit la valeur placeholder '...' en chaîne vide pour le stockage."""
    return "" if val == PLACEHOLDER else val


def show_success_alert(title: str, message: str):
    """Affiche une alerte de succès très visible (bannière verte animée)."""
    st.markdown(f"""
    <div class="success-alert">
        <div class="success-alert-icon">✅</div>
        <div>
            <p class="success-alert-title">{title}</p>
            <p class="success-alert-msg">{message}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════
# TOAST NOTIFICATIONS
# ══════════════════════════════════════════════════════════════════════

def notify_success(message: str):
    st.toast(message, icon="✅")

def notify_error(message: str):
    st.toast(message, icon="❌")


# ══════════════════════════════════════════════════════════════════════
# EXPORT EXCEL
# ══════════════════════════════════════════════════════════════════════

def export_excel_button(df: pd.DataFrame, filename="export.xlsx", sheet_name="Données", label="📥 Exporter en Excel", key=None):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
        wb = writer.book
        ws = writer.sheets[sheet_name]
        hfmt = wb.add_format({"bold": True, "bg_color": "#005F83", "font_color": "#FFFFFF", "border": 1, "text_wrap": True, "valign": "vcenter", "font_name": "Arial", "font_size": 10})
        for i, v in enumerate(df.columns):
            ws.write(0, i, v, hfmt)
            max_len = max(len(str(v)), df.iloc[:, i].astype(str).str.len().max() if len(df) > 0 else 0)
            ws.set_column(i, i, min(max_len + 4, 40))
    st.download_button(label=label, data=buffer.getvalue(), file_name=filename, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key=key)


# ══════════════════════════════════════════════════════════════════════
# SIDEBAR — avec utilisateur connecté et déconnexion
# ══════════════════════════════════════════════════════════════════════

def render_sidebar(active_page: str = "dashboard"):
    """Sidebar unifiée : brand + utilisateur connecté + stats + navigation + déconnexion."""
    import base64 as _b64
    from data_manager import load_data, get_kpi
    from auth import get_current_user, logout

    with st.sidebar:

        # Brand
        logo_b64 = ""
        if os.path.exists(LOGO_PATH):
            with open(LOGO_PATH, "rb") as f:
                logo_b64 = _b64.b64encode(f.read()).decode()
        st.markdown(f"""
        <div class="sidebar-brand">
            <img src="data:image/png;base64,{logo_b64}" alt="RTE">
            <div>
                <div class="sidebar-brand-text">Guichet Unique</div>
                <div class="sidebar-brand-sub">Demandes d'Études</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Utilisateur connecté
        user = get_current_user()
        if user:
            email = user["email"]
            admin_tag = " · admin" if user.get("is_admin") else ""
            st.markdown(f"""
            <div class="sidebar-user-pill">
                <div class="sidebar-user-dot"></div>
                <div class="sidebar-user-email">{email}{admin_tag}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🚪 Se déconnecter", key="btn_logout", use_container_width=True):
                logout()
                st.rerun()
        else:
            st.markdown("""
            <div class="sidebar-user-pill" style="border-color: #FFE082;">
                <div class="sidebar-user-dot" style="background: #FF9800;"></div>
                <div class="sidebar-user-email" style="color: #9CA3AF;">Non connecté</div>
            </div>
            """, unsafe_allow_html=True)

        # Mini-stats
        df = load_data()
        kpi = get_kpi(df)
        st.markdown(f"""
        <div class="sidebar-stats">
            <div class="sidebar-stat"><div class="sidebar-stat-val" style="color:#FF9800;">{kpi['soumises']}</div><div class="sidebar-stat-lbl">En attente</div></div>
            <div class="sidebar-stat"><div class="sidebar-stat-val" style="color:#2196F3;">{kpi['attribuees']}</div><div class="sidebar-stat-lbl">Attribuées</div></div>
            <div class="sidebar-stat"><div class="sidebar-stat-val" style="color:#4CAF50;">{kpi['commandees']}</div><div class="sidebar-stat-lbl">Commandées</div></div>
            <div class="sidebar-stat"><div class="sidebar-stat-val" style="color:#005F83;">{kpi['total']}</div><div class="sidebar-stat-lbl">Total</div></div>
        </div>
        """, unsafe_allow_html=True)

        # Navigation
        st.markdown('<div class="sidebar-nav-label">Navigation</div>', unsafe_allow_html=True)
        nav_items = [
            ("dashboard", "🏠  Tableau de bord"), ("nouvelle", "➕  Nouvelle demande"),
            ("demandes", "📋  Mes demandes"), ("attribution", "🔒  Attribution"),
            ("import", "🔒  Import commandes"), ("donnees", "📊  Données"),
            ("suivi", "📈  Suivi & analyses"),
        ]
        for key, label in nav_items:
            st.page_link(PAGE_PATHS[key], label=label, disabled=(key == active_page))

        # Footer
        from config import APP_VERSION
        st.markdown(f"""
        <div class="sidebar-footer">Guichet Unique v{APP_VERSION}<br>RTE — Réseau de Transport d'Électricité</div>
        """, unsafe_allow_html=True)
