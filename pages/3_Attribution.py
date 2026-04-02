"""
3_Attribution.py — Attribution avec authentification et confirmation en 2 étapes.
"""
import streamlit as st
import pandas as pd
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from data_manager import load_data, attribuer_demande, GIE_LIST
from ui_components import (
    inject_css, render_header, section_header, status_badge,
    info_box, render_sidebar, export_excel_button, notify_success,
    PLACEHOLDER,
)
from auth import require_auth, check_admin_access

st.set_page_config(page_title="Attribution", page_icon="🎯", layout="wide", initial_sidebar_state="expanded")
inject_css()
render_sidebar(active_page="attribution")

# Authentification utilisateur puis vérification admin
user = require_auth()
render_header("Attribution des demandes aux entreprises d'études")
if not check_admin_access():
    st.stop()

df = load_data()
soumises = df[df["Statut"] == "Soumise"].copy()

if len(soumises) == 0:
    info_box("✅ Aucune demande en attente d'attribution.")
    attribuees = df[df["Statut"] == "Attribuée"].sort_values("Date_Attribution", ascending=False).head(10)
    if len(attribuees) > 0:
        section_header("Dernières attributions", "📜")
        for _, row in attribuees.iterrows():
            c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
            with c1:
                st.markdown(f"**{row.get('Nom_Ouvrage_Projet', 'N/A')}**")
            with c2:
                st.markdown(f"🏢 {row.get('Attribution_Finale', 'N/A')}")
            with c3:
                st.markdown(f"📅 {row.get('Date_Attribution', 'N/A')}")
            with c4:
                st.markdown(status_badge("Attribuée"), unsafe_allow_html=True)
    st.stop()

# ── Demandes en attente ───────────────────────────────────────────────
section_header(f"Demandes en attente d'attribution ({len(soumises)})", "⏳")

info_box(
    "⚠️ <b>Attention :</b> L'attribution est <b>irréversible</b>. "
    "Une confirmation vous sera demandée avant toute attribution."
)

cols_display = ["ID_Demande", "Nom_Ouvrage_Projet", "Manager_Projet",
                "Trimestre_Attribution", "Tension", "Montant_Total",
                "Pref_GIE_1", "Pref_GIE_2", "Pref_GIE_3"]

html = '<table style="width:100%;border-collapse:collapse;font-size:0.83rem;"><tr>'
headers = {"ID_Demande": "ID", "Nom_Ouvrage_Projet": "Projet", "Manager_Projet": "Manager",
           "Trimestre_Attribution": "Trim.", "Tension": "Tension", "Montant_Total": "Montant (k€)",
           "Pref_GIE_1": "Préf. 1", "Pref_GIE_2": "Préf. 2", "Pref_GIE_3": "Préf. 3"}
for c in cols_display:
    html += f'<th style="background:#005F83;color:white;padding:6px 8px;text-align:left;white-space:nowrap;">{headers.get(c,c)}</th>'
html += '</tr>'
for _, row in soumises.iterrows():
    html += '<tr style="border-bottom:1px solid #E0E0E0;">'
    for c in cols_display:
        v = str(row.get(c, "") or "")
        if c == "ID_Demande":
            v = f'<code style="color:#005F83;font-weight:600;font-size:0.8rem;">{v}</code>'
        html += f'<td style="padding:5px 8px;">{v}</td>'
    html += '</tr>'
html += '</table>'
st.markdown(html, unsafe_allow_html=True)
export_excel_button(soumises[cols_display], "demandes_en_attente.xlsx", "En attente", key="export_attente")

# ── Formulaire d'attribution ─────────────────────────────────────────
st.markdown("---")
section_header("Attribuer une demande", "🎯")

demande_labels = [
    f"{row['ID_Demande']} — {row.get('Nom_Ouvrage_Projet', 'N/A')}"
    for _, row in soumises.iterrows()
]

selected_label = st.selectbox("Sélectionnez la demande à attribuer", [PLACEHOLDER] + demande_labels)

if selected_label and selected_label != PLACEHOLDER:
    sel_id = selected_label.split(" — ")[0]
    row = df[df["ID_Demande"] == sel_id].iloc[0]

    st.markdown("#### Résumé de la demande")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"**Projet :** {row.get('Nom_Ouvrage_Projet', '')}")
        st.markdown(f"**Manager :** {row.get('Manager_Projet', '')}")
        st.markdown(f"**EOTP2 :** {row.get('EOTP2', '')}")
    with c2:
        st.markdown(f"**Tension :** {row.get('Tension', '')}")
        st.markdown(f"**Trimestre :** {row.get('Trimestre_Attribution', '')}")
        st.markdown(f"**Type :** {row.get('Type_Projet', '')}")
    with c3:
        st.markdown(f"**Montant LA :** {row.get('Montant_LA_kE', '')} k€")
        st.markdown(f"**Montant LS :** {row.get('Montant_LS_kE', '')} k€")
        st.markdown(f"**Montant Total :** {row.get('Montant_Total', '')} k€")

    prefs_raw = [row.get("Pref_GIE_1", ""), row.get("Pref_GIE_2", ""), row.get("Pref_GIE_3", "")]
    prefs = [str(p) for p in prefs_raw if pd.notna(p) and str(p).strip()]
    if prefs:
        st.markdown("**Préférences du manager :** " + " → ".join(prefs))
    justif = row.get("Pref_Justification", "")
    if pd.notna(justif) and str(justif).strip():
        st.markdown(f"**Justification :** {justif}")

    st.markdown("---")

    gie_selected = st.selectbox("Entreprise d'études (GIE) à attribuer", [PLACEHOLDER] + GIE_LIST, key="gie_attr")

    if gie_selected and gie_selected != PLACEHOLDER:
        # ── ÉTAPE 1 : Demander la confirmation ───────────────────
        confirm_key = f"confirm_{sel_id}_{gie_selected}"
        is_confirming = st.session_state.get(confirm_key, False)

        if not is_confirming:
            # Bouton initial : déclenche la demande de confirmation
            if st.button("🎯 Attribuer cette demande", type="primary", use_container_width=True):
                st.session_state[confirm_key] = True
                st.rerun()
        else:
            # ── ÉTAPE 2 : Encart de confirmation explicite ────────
            st.markdown(f"""
            <div class="confirm-box">
                <h4>⚠️ Confirmation requise</h4>
                <p>Vous êtes sur le point d'attribuer la demande
                <b>{sel_id}</b> à <b>{gie_selected}</b>.<br>
                Cette action est <b>irréversible</b> — la demande sera verrouillée.</p>
            </div>
            """, unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ Oui, confirmer l'attribution", type="primary", use_container_width=True):
                    try:
                        attribuer_demande(sel_id, gie_selected, user["email"])
                        # Nettoyer l'état de confirmation
                        st.session_state.pop(confirm_key, None)
                        notify_success(f"Demande {sel_id} attribuée à {gie_selected}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Erreur : {e}")
            with c2:
                if st.button("❌ Annuler", use_container_width=True):
                    st.session_state.pop(confirm_key, None)
                    st.rerun()
