"""
2_Mes_Demandes.py — Consulter, modifier, soumettre ses demandes.
Filtrées par email de l'utilisateur connecté.
"""
import streamlit as st
import pandas as pd
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from data_manager import (
    load_user_data, modifier_demande, soumettre_demande, annuler_demande,
    STATUTS, GIE_LIST, TRIMESTRES, TENSIONS, TYPES_PROJET
)
from ui_components import (
    inject_css, render_header, section_header, status_badge,
    info_box, render_sidebar, export_excel_button, notify_success,
    PLACEHOLDER, clean_select, show_success_alert,
)
from auth import require_auth

st.set_page_config(page_title="Mes Demandes", page_icon="📋", layout="wide", initial_sidebar_state="expanded")
inject_css()
render_sidebar(active_page="demandes")
user = require_auth()
render_header("Gérer vos demandes d'études")

# ── Alerte persistante après soumission (survit au rerun) ─────────────
if st.session_state.get("demande_soumise_id"):
    dem_id = st.session_state.pop("demande_soumise_id")
    show_success_alert(
        "Demande soumise avec succès !",
        f"La demande {dem_id} a été transmise pour attribution. "
        "Vous recevrez une notification lors de l'attribution."
    )

# Charger uniquement les demandes de l'utilisateur connecté
df = load_user_data(user["email"], user.get("is_admin", False))

if len(df) == 0:
    info_box("Aucune demande enregistrée. Créez-en une via <b>➕ Nouvelle Demande</b>.")
    st.stop()

# ── Filtres ───────────────────────────────────────────────────────────
section_header("Filtres", "🔍")
c1, c2, c3 = st.columns(3)
with c1:
    filtre_statut = st.multiselect("Statut", STATUTS, default=["Brouillon", "Soumise"])
with c2:
    filtre_trim = st.multiselect("Trimestre", TRIMESTRES)
with c3:
    filtre_manager = st.text_input("Manager de projet", "")

mask = pd.Series([True] * len(df), index=df.index)
if filtre_statut:
    mask &= df["Statut"].isin(filtre_statut)
if filtre_trim:
    mask &= df["Trimestre_Attribution"].isin(filtre_trim)
if filtre_manager:
    mask &= df["Manager_Projet"].str.contains(filtre_manager, case=False, na=False)

filtered = df[mask].copy()

if len(filtered) == 0:
    st.info("Aucune demande ne correspond aux filtres.")
    st.stop()

# ── Liste des demandes ────────────────────────────────────────────────
section_header(f"Demandes ({len(filtered)})", "📄")

display_cols = ["ID_Demande", "Statut", "Nom_Ouvrage_Projet", "Manager_Projet",
                "Trimestre_Attribution", "EOTP2", "Tension", "Date_Creation"]
display_cols = [c for c in display_cols if c in filtered.columns]

html = '<table style="width:100%; border-collapse: collapse; font-size: 0.85rem;"><tr>'
nice = {"ID_Demande": "ID", "Statut": "Statut", "Nom_Ouvrage_Projet": "Projet",
        "Manager_Projet": "Manager", "Trimestre_Attribution": "Trimestre",
        "EOTP2": "EOTP2", "Tension": "Tension", "Date_Creation": "Créé le"}
for c in display_cols:
    html += f'<th style="background:#005F83;color:white;padding:8px 10px;text-align:left;">{nice.get(c,c)}</th>'
html += '</tr>'
for _, row in filtered.iterrows():
    html += '<tr style="border-bottom:1px solid #E0E0E0;">'
    for c in display_cols:
        v = str(row.get(c, ""))
        if c == "Statut":
            v = status_badge(v)
        elif c == "ID_Demande":
            v = f'<code style="color:#005F83;font-weight:600;">{v}</code>'
        html += f'<td style="padding:6px 10px;">{v}</td>'
    html += '</tr>'
html += '</table>'
st.markdown(html, unsafe_allow_html=True)
export_excel_button(filtered[display_cols], "mes_demandes.xlsx", "Demandes", key="export_demandes")

# ── Détail / Modification ────────────────────────────────────────────
st.markdown("---")
section_header("Modifier une demande", "✏️")

demande_ids = filtered["ID_Demande"].tolist()
selected_id = st.selectbox("Sélectionnez une demande", [PLACEHOLDER] + demande_ids)

if selected_id and selected_id != PLACEHOLDER:
    row = df[df["ID_Demande"] == selected_id].iloc[0]
    statut = row["Statut"]
    is_locked = statut in ("Attribuée", "Commandée")

    if is_locked:
        st.warning(f"🔒 Cette demande est **{statut}** et ne peut plus être modifiée.")

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f"**Projet :** {row.get('Nom_Ouvrage_Projet', '')}")
    with col2:
        st.markdown(f"**Statut :** {status_badge(statut)}", unsafe_allow_html=True)
    with col3:
        st.markdown(f"**Dernière modif :** {row.get('Derniere_Modification', '')}")

    if not is_locked:
        with st.form("form_modifier"):
            section_header("Informations modifiables", "📝")
            c1, c2 = st.columns(2)
            with c1:
                new_nom = st.text_input("Nom du projet", value=str(row.get("Nom_Ouvrage_Projet", "")))
                new_trim = st.selectbox("Trimestre", [PLACEHOLDER] + TRIMESTRES,
                    index=(TRIMESTRES.index(row["Trimestre_Attribution"]) + 1) if row.get("Trimestre_Attribution") in TRIMESTRES else 0)
                new_tension = st.selectbox("Tension", [PLACEHOLDER] + TENSIONS,
                    index=(TENSIONS.index(row["Tension"]) + 1) if row.get("Tension") in TENSIONS else 0)
            with c2:
                new_resume = st.text_area("Résumé", value=str(row.get("Resume_Projet", "")), height=100)
                new_manager = st.text_input("Manager", value=str(row.get("Manager_Projet", "")))

            c1, c2 = st.columns(2)
            with c1:
                new_montant_la = st.number_input("Montant LA (k€)",
                    value=float(row.get("Montant_LA_kE", 0) or 0))
            with c2:
                new_montant_ls = st.number_input("Montant LS (k€)",
                    value=float(row.get("Montant_LS_kE", 0) or 0))

            section_header("Préférences", "🎯")
            c1, c2, c3 = st.columns(3)
            with c1:
                new_pref1 = st.selectbox("GIE n°1", [PLACEHOLDER] + GIE_LIST,
                    index=(GIE_LIST.index(row["Pref_GIE_1"]) + 1) if row.get("Pref_GIE_1") in GIE_LIST else 0)
            with c2:
                new_pref2 = st.selectbox("GIE n°2", [PLACEHOLDER] + GIE_LIST,
                    index=(GIE_LIST.index(row["Pref_GIE_2"]) + 1) if row.get("Pref_GIE_2") in GIE_LIST else 0)
            with c3:
                new_pref3 = st.selectbox("GIE n°3", [PLACEHOLDER] + GIE_LIST,
                    index=(GIE_LIST.index(row["Pref_GIE_3"]) + 1) if row.get("Pref_GIE_3") in GIE_LIST else 0)

            st.markdown("---")
            bc1, bc2, bc3 = st.columns(3)
            with bc1:
                save_btn = st.form_submit_button("💾 Sauvegarder", use_container_width=True, type="primary")
            with bc2:
                submit_btn = st.form_submit_button("📤 Soumettre la demande", use_container_width=True)
            with bc3:
                cancel_btn = st.form_submit_button("🗑️ Annuler la demande", use_container_width=True)

            if save_btn:
                try:
                    modifier_demande(selected_id, {
                        "Nom_Ouvrage_Projet": new_nom,
                        "Trimestre_Attribution": clean_select(new_trim),
                        "Tension": clean_select(new_tension),
                        "Resume_Projet": new_resume,
                        "Manager_Projet": new_manager,
                        "Montant_LA_kE": str(new_montant_la),
                        "Montant_LS_kE": str(new_montant_ls),
                        "Montant_Total": str(new_montant_la + new_montant_ls),
                        "Pref_GIE_1": clean_select(new_pref1),
                        "Pref_GIE_2": clean_select(new_pref2),
                        "Pref_GIE_3": clean_select(new_pref3),
                    }, user["email"])
                    notify_success("Modifications sauvegardées !")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ {e}")

            if submit_btn:
                try:
                    soumettre_demande(selected_id, user["email"])
                    # Stocker l'ID pour afficher l'alerte après rerun
                    st.session_state["demande_soumise_id"] = selected_id
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ {e}")

            if cancel_btn:
                try:
                    annuler_demande(selected_id, user["email"])
                    st.toast("Demande annulée.", icon="🗑️")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ {e}")
    else:
        tabs = st.tabs(["Général", "Technique LA", "Technique LS", "Jalons", "Attribution"])
        with tabs[0]:
            for col_name, label in [
                ("EOTP2", "EOTP2"), ("RUO", "RUO"), ("Tension", "Tension"),
                ("Depart", "Départ"), ("Arrivee", "Arrivée"), ("Type_Projet", "Type"),
                ("Resume_Projet", "Résumé"), ("Manager_Projet", "Manager"),
            ]:
                st.markdown(f"**{label} :** {row.get(col_name, '')}")
        with tabs[4]:
            st.markdown(f"**Entreprise :** {row.get('Attribution_Finale', '')}")
            st.markdown(f"**Date attribution :** {row.get('Date_Attribution', '')}")
            st.markdown(f"**Attribué par :** {row.get('Attribue_Par', '')}")
