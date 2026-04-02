"""
1_Nouvelle_Demande.py — Formulaire de création avec sections accordéon.
Contrôle SIEPR supprimé. Montants estimés restaurés.
"""
import streamlit as st
import sys, os, datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from data_manager import (
    ajouter_demande, TRIMESTRES, TENSIONS, TYPES_PROJET, GIE_LIST
)
from ui_components import (
    inject_css, render_header, section_header, info_box,
    render_sidebar, notify_success, PLACEHOLDER, clean_select,
)
from auth import require_auth

st.set_page_config(page_title="Nouvelle Demande", page_icon="➕", layout="wide", initial_sidebar_state="expanded")
inject_css()
render_sidebar(active_page="nouvelle")
user = require_auth()
render_header("Créer une nouvelle demande d'étude")

info_box(
    "📝 Remplissez le formulaire ci-dessous pour soumettre une nouvelle demande. "
    "Les champs marqués <b>*</b> sont obligatoires. "
    "Cliquez sur chaque section pour la déplier."
)

with st.form("form_nouvelle_demande", clear_on_submit=True):

    # ══════════════════════════════════════════════════════════════════
    # SECTION 1 — Informations Générales (ouverte par défaut)
    # ══════════════════════════════════════════════════════════════════
    with st.expander("📋 Informations Générales", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            trimestre = st.selectbox("Trimestre d'attribution *", [PLACEHOLDER] + TRIMESTRES)
        with c2:
            date_fiche = st.date_input("Date fiche ATP", value=datetime.date.today())
        with c3:
            n_fiche = st.text_input("N° Fiche ATP")
        with c4:
            centre_di = st.text_input("Centre DI")

        c1, c2, c3 = st.columns(3)
        with c1:
            ruo = st.text_input("RUO")
        with c2:
            eotp2 = st.text_input("EOTP2 *")
        with c3:
            tension = st.selectbox("Tension", [PLACEHOLDER] + TENSIONS)

        c1, c2 = st.columns(2)
        with c1:
            depart = st.text_input("Départ")
        with c2:
            arrivee = st.text_input("Arrivée")

        nom_projet = st.text_input("Nom de l'ouvrage / projet *")
        type_projet = st.selectbox("Type de projet", [PLACEHOLDER] + TYPES_PROJET)
        nbre_lots = st.text_input("Nombre de lots d'études")
        resume = st.text_area("Résumé du projet", height=100)

        c1, c2 = st.columns(2)
        with c1:
            manager = st.text_input("Manager de projet *", value="")
            tel_manager = st.text_input("Téléphone du manager")
        with c2:
            charge = st.text_input("Chargé d'études")
            tel_charge = st.text_input("Téléphone du chargé d'études")

    # ══════════════════════════════════════════════════════════════════
    # SECTION 2 — Données Techniques LA
    # ══════════════════════════════════════════════════════════════════
    with st.expander("🗼 Données Techniques — Lignes Aériennes (LA)"):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            la_typo = st.selectbox("Typologie LA", [PLACEHOLDER, "Création", "Renouvellement", "Renforcement", "Modification", "Dépose"])
        with c2:
            la_circuits = st.number_input("Nombre de circuits", min_value=0, value=0, step=1, key="la_circ")
        with c3:
            la_longueur = st.number_input("Longueur liaison (km)", min_value=0.0, value=0.0, step=0.1, key="la_long")
        with c4:
            la_pylones = st.number_input("Nb pylônes à traiter", min_value=0, value=0, step=1, key="la_pyl")

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            la_rural = st.checkbox("Rural", key="la_rural")
        with c2:
            la_urbain = st.checkbox("Urbain", key="la_urbain")
        with c3:
            la_montagneux = st.checkbox("Montagneux", key="la_mont")
        with c4:
            la_lidar = st.checkbox("Besoin LIDAR", key="la_lidar")

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            la_bois = st.text_input("Linéaire Bois")
        with c2:
            la_geotech = st.text_input("Géotechnique existante")
        with c3:
            la_conv = st.text_input("Nbre conventions estimé")
        with c4:
            la_drone = st.checkbox("État des lieux Drone", key="la_drone")

        c1, c2 = st.columns(2)
        with c1:
            la_tekla = st.checkbox("TEKLA", key="la_tekla")
        with c2:
            la_pls = st.checkbox("PLS POLE", key="la_pls")

    # ══════════════════════════════════════════════════════════════════
    # SECTION 3 — Données Techniques LS
    # ══════════════════════════════════════════════════════════════════
    with st.expander("🔌 Données Techniques — Liaisons Souterraines (LS)"):
        c1, c2 = st.columns(2)
        with c1:
            ls_typo = st.selectbox("Typologie LS", [PLACEHOLDER, "Création", "Renouvellement", "Renforcement", "Modification", "Dépose"])
        with c2:
            ls_type_liaison = st.text_input("Type de liaison")

        c1, c2, c3 = st.columns(3)
        with c1:
            ls_faisabilite = st.number_input("Linéaire faisabilité (km)", min_value=0.0, value=0.0, step=0.1, key="ls_fais")
        with c2:
            ls_trace = st.number_input("Linéaire tracé (km)", min_value=0.0, value=0.0, step=0.1, key="ls_trace")
        with c3:
            ls_details = st.number_input("Linéaire détails (km)", min_value=0.0, value=0.0, step=0.1, key="ls_det")

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            ls_rural = st.checkbox("Rural", key="ls_rural")
        with c2:
            ls_urbain = st.checkbox("Urbain", key="ls_urbain")
        with c3:
            ls_urbain_dense = st.checkbox("Urbain dense", key="ls_ud")
        with c4:
            ls_poste = st.checkbox("Poste", key="ls_poste")

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            ls_galerie = st.checkbox("Galerie", key="ls_gal")
        with c2:
            ls_lidar = st.checkbox("Besoin LIDAR", key="ls_lidar")
        with c3:
            ls_franchissement = st.number_input("Nbre franchissements non complexes", min_value=0, value=0, step=1)
        with c4:
            ls_pso = st.number_input("Nbre de PSO", min_value=0, value=0, step=1)

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            ls_public = st.number_input("% domaine public", min_value=0, max_value=100, value=0, key="ls_pub")
        with c2:
            ls_prive = st.number_input("% domaine privé", min_value=0, max_value=100, value=0, key="ls_priv")
        with c3:
            ls_communes = st.number_input("Nombre de communes", min_value=0, value=0, step=1)
        with c4:
            ls_racc = st.text_input("Raccordement (PTF, MESIL)")

    # ══════════════════════════════════════════════════════════════════
    # SECTION 4 — Géotechnique
    # ══════════════════════════════════════════════════════════════════
    with st.expander("🔬 Géotechnique"):
        c1, c2 = st.columns(2)
        with c1:
            geo_g1 = st.selectbox("Études G1 commandées ?", [PLACEHOLDER, "Oui", "Non"])
        with c2:
            geo_g2 = st.selectbox("Études G2 commandées ?", [PLACEHOLDER, "Oui", "Non"])

    # ══════════════════════════════════════════════════════════════════
    # SECTION 5 — Jalons
    # ══════════════════════════════════════════════════════════════════
    with st.expander("📅 Jalons"):
        c1, c2 = st.columns(2)
        with c1:
            j_consultation = st.date_input("Date consultation", value=None, key="j_consult")
            j_patrimoine = st.date_input("Fin recensement patrimoine", value=None, key="j_patri")
            j_la_faisabilite = st.date_input("LA — Fin faisabilité (DCT)", value=None, key="j_la_fais")
            j_la_debut = st.date_input("LA — Début études détails", value=None, key="j_la_deb")
            j_la_fin = st.date_input("LA — Fin études détails", value=None, key="j_la_fin")
        with c2:
            j_notif = st.date_input("Date notification commande", value=None, key="j_notif")
            j_geotech = st.date_input("Fin études géotechniques", value=None, key="j_geo")
            j_ls_faisabilite = st.date_input("LS — Fin faisabilité", value=None, key="j_ls_fais")
            j_ls_trace = st.date_input("LS — Fin tracé préférentiel", value=None, key="j_ls_trace")
            j_ls_detail_deb = st.date_input("LS — Début détails", value=None, key="j_ls_deb")

        c1, c2, c3 = st.columns(3)
        with c1:
            j_ls_detail_fin = st.date_input("LS — Fin détails", value=None, key="j_ls_fin")
        with c2:
            j_conv = st.date_input("Fin conventionnement", value=None, key="j_conv")
        with c3:
            j_apd = st.date_input("APD", value=None, key="j_apd")

        j_di = st.date_input("DI", value=None, key="j_di")

    # ══════════════════════════════════════════════════════════════════
    # SECTION 6 — Montants estimés
    # ══════════════════════════════════════════════════════════════════
    with st.expander("💰 Montants estimés"):
        c1, c2, c3 = st.columns(3)
        with c1:
            montant_la = st.number_input("Montant LA (k€)", min_value=0.0, value=0.0, step=1.0)
        with c2:
            montant_ls = st.number_input("Montant LS (k€)", min_value=0.0, value=0.0, step=1.0)
        with c3:
            montant_total = montant_la + montant_ls
            st.metric("Montant Total (k€)", f"{montant_total:.1f}")

    # ══════════════════════════════════════════════════════════════════
    # SECTION 7 — Préférences d'attribution
    # ══════════════════════════════════════════════════════════════════

    with st.expander("🎯 Préférences d'attribution"):
        c1, c2, c3 = st.columns(3)
        with c1:
            pref1 = st.selectbox("Souhait GIE n°1", [PLACEHOLDER] + GIE_LIST)
        with c2:
            pref2 = st.selectbox("Souhait GIE n°2", [PLACEHOLDER] + GIE_LIST)
        with c3:
            pref3 = st.selectbox("Souhait GIE n°3", [PLACEHOLDER] + GIE_LIST)
        pref_justif = st.text_area("Justification", key="pref_just")
        pref_confiance = st.selectbox("Niveau de confiance", [PLACEHOLDER, "Faible", "Moyen", "Élevé"])

    # ══════════════════════════════════════════════════════════════════
    # BOUTON DE SOUMISSION
    # ══════════════════════════════════════════════════════════════════
    st.markdown("---")
    submitted = st.form_submit_button("💾 Enregistrer la demande", use_container_width=True, type="primary")

    if submitted:
        errors = []
        if not trimestre or trimestre == PLACEHOLDER:
            errors.append("Trimestre d'attribution obligatoire")
        if not eotp2:
            errors.append("EOTP2 obligatoire")
        if not nom_projet:
            errors.append("Nom du projet obligatoire")

        if errors:
            for e in errors:
                st.error(f"⚠️ {e}")
        else:
            # Construction du dictionnaire — Contrôle SIEPR supprimé
            data = {
                "Trimestre_Attribution": clean_select(trimestre),
                "Date_Fiche_ATP": str(date_fiche) if date_fiche else "",
                "N_Fiche_ATP": n_fiche,
                "Centre_DI": centre_di,
                "RUO": ruo,
                "EOTP2": eotp2,
                "Tension": clean_select(tension),
                "Depart": depart,
                "Arrivee": arrivee,
                "Nom_Ouvrage_Projet": nom_projet,
                "Type_Projet": clean_select(type_projet),
                "Nbre_Lots_Etudes": str(nbre_lots),
                "Resume_Projet": resume,
                "Manager_Projet": manager,
                "Tel_Manager": tel_manager,
                "Charge_Etudes": charge,
                "Tel_Charge_Etudes": tel_charge,
                # LA
                "LA_Typologie_Projet": clean_select(la_typo),
                "LA_Nbre_Circuits": str(la_circuits),
                "LA_Longueur_Liaison_km": str(la_longueur),
                "LA_Nb_Pylones": str(la_pylones),
                "LA_Rural": "Oui" if la_rural else "",
                "LA_Urbain": "Oui" if la_urbain else "",
                "LA_Montagneux": "Oui" if la_montagneux else "",
                "LA_Lineaire_Bois": la_bois,
                "LA_Geotech_Existante": la_geotech,
                "LA_Nbre_Conventions": la_conv,
                "LA_Besoin_LIDAR": "Oui" if la_lidar else "",
                "LA_Etat_Lieux_Drone": "Oui" if la_drone else "",
                "LA_TEKLA": "Oui" if la_tekla else "",
                "LA_PLS_POLE": "Oui" if la_pls else "",
                # LS
                "LS_Typologie_Projet": clean_select(ls_typo),
                "LS_Type_Liaison": ls_type_liaison,
                "LS_Lineaire_Faisabilite_km": str(ls_faisabilite),
                "LS_Lineaire_Trace_km": str(ls_trace),
                "LS_Lineaire_Details_km": str(ls_details),
                "LS_Rural": "Oui" if ls_rural else "",
                "LS_Urbain": "Oui" if ls_urbain else "",
                "LS_Urbain_Dense": "Oui" if ls_urbain_dense else "",
                "LS_Poste": "Oui" if ls_poste else "",
                "LS_Galerie": "Oui" if ls_galerie else "",
                "LS_Besoin_LIDAR": "Oui" if ls_lidar else "",
                "LS_Nbre_Franchissement": str(ls_franchissement),
                "LS_Nbre_PSO": str(ls_pso),
                "LS_Pct_Domaine_Public": str(ls_public),
                "LS_Pct_Domaine_Prive": str(ls_prive),
                "LS_Nbre_Communes": str(ls_communes),
                "LS_Raccordement": ls_racc,
                # Geo
                "Geo_G1_Commandees": clean_select(geo_g1),
                "Geo_G2_Commandees": clean_select(geo_g2),
                # Jalons
                "Jalon_Date_Consultation": str(j_consultation) if j_consultation else "",
                "Jalon_Date_Notification_Commande": str(j_notif) if j_notif else "",
                "Jalon_Fin_Recensement_Patrimoine": str(j_patrimoine) if j_patrimoine else "",
                "Jalon_Fin_Geotech": str(j_geotech) if j_geotech else "",
                "Jalon_LA_Fin_Faisabilite_DCT": str(j_la_faisabilite) if j_la_faisabilite else "",
                "Jalon_LA_Debut_Details": str(j_la_debut) if j_la_debut else "",
                "Jalon_LA_Fin_Details": str(j_la_fin) if j_la_fin else "",
                "Jalon_LS_Fin_Faisabilite": str(j_ls_faisabilite) if j_ls_faisabilite else "",
                "Jalon_LS_Fin_Trace_Preferentiel": str(j_ls_trace) if j_ls_trace else "",
                "Jalon_LS_Detail_Debut": str(j_ls_detail_deb) if j_ls_detail_deb else "",
                "Jalon_LS_Detail_Fin": str(j_ls_detail_fin) if j_ls_detail_fin else "",
                "Jalon_Fin_Conventionnement": str(j_conv) if j_conv else "",
                "Jalon_APD": str(j_apd) if j_apd else "",
                "Jalon_DI": str(j_di) if j_di else "",
                # Montants
                "Montant_LA_kE": str(montant_la),
                "Montant_LS_kE": str(montant_ls),
                "Montant_Total": str(montant_total),
                # Préférences
                "Pref_GIE_1": clean_select(pref1),
                "Pref_GIE_2": clean_select(pref2),
                "Pref_GIE_3": clean_select(pref3),
                "Pref_Justification": pref_justif,
                "Pref_Niveau_Confiance": clean_select(pref_confiance),
            }

            try:
                demande_id = ajouter_demande(data, user["email"])
                notify_success(f"Demande créée avec succès — ID : {demande_id}")
                st.success(f"✅ Demande créée avec succès ! ID : **{demande_id}**")
            except Exception as e:
                st.error(f"❌ Erreur : {e}")
