"""
data_manager.py — Gestion centralisée de la base de données Excel avec verrouillage fichier.
"""
import os
import pandas as pd
import datetime
import uuid
from filelock import FileLock
from copy import deepcopy

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DB_FILE = os.path.join(DATA_DIR, "guichet_unique_db.xlsx")
LOCK_FILE = DB_FILE + ".lock"
HISTORY_DIR = os.path.join(DATA_DIR, "historique")

# ── Colonnes par section ──────────────────────────────────────────────
COLONNES_INFO_GENERALES = [
    "ID_Demande", "Statut", "Createur_Email", "Date_Creation", "Trimestre_Attribution",
    "Date_Fiche_ATP", "N_Fiche_ATP", "Centre_DI", "RUO", "EOTP2",
    "Depart", "Arrivee", "Nom_Ouvrage_Projet", "Type_Projet", "Tension",
    "Nbre_Lots_Etudes", "Resume_Projet", "Manager_Projet",
    "Tel_Manager", "Charge_Etudes", "Tel_Charge_Etudes",
]

COLONNES_TECH_LA = [
    "LA_Typologie_Projet", "LA_Nbre_Circuits", "LA_Longueur_Liaison_km",
    "LA_Nb_Pylones", "LA_Rural", "LA_Urbain", "LA_Montagneux",
    "LA_Lineaire_Bois", "LA_Geotech_Existante", "LA_Nbre_Conventions",
    "LA_Besoin_LIDAR", "LA_Etat_Lieux_Drone", "LA_TEKLA", "LA_PLS_POLE",
]

COLONNES_TECH_LS = [
    "LS_Typologie_Projet", "LS_Type_Liaison",
    "LS_Lineaire_Faisabilite_km", "LS_Lineaire_Trace_km",
    "LS_Lineaire_Details_km", "LS_Rural", "LS_Urbain", "LS_Urbain_Dense",
    "LS_Poste", "LS_Galerie", "LS_Besoin_LIDAR",
    "LS_Nbre_Franchissement", "LS_Nbre_PSO",
    "LS_Pct_Domaine_Public", "LS_Pct_Domaine_Prive",
    "LS_Nbre_Communes", "LS_Raccordement",
]

COLONNES_GEOTECH = [
    "Geo_G1_Commandees", "Geo_G2_Commandees",
]

COLONNES_JALONS = [
    "Jalon_Date_Consultation", "Jalon_Date_Notification_Commande",
    "Jalon_Fin_Recensement_Patrimoine", "Jalon_Fin_Geotech",
    "Jalon_LA_Fin_Faisabilite_DCT", "Jalon_LA_Debut_Details",
    "Jalon_LA_Fin_Details",
    "Jalon_LS_Fin_Faisabilite", "Jalon_LS_Fin_Trace_Preferentiel",
    "Jalon_LS_Detail_Debut", "Jalon_LS_Detail_Fin",
    "Jalon_Fin_Conventionnement", "Jalon_APD", "Jalon_DI",
]

COLONNES_MONTANT = [
    "Montant_LA_kE", "Montant_LS_kE", "Montant_Total",
]

COLONNES_PREFERENCE = [
    "Pref_GIE_1", "Pref_GIE_2", "Pref_GIE_3",
    "Pref_Justification", "Pref_Niveau_Confiance",
]

COLONNES_ATTRIBUTION = [
    "Attribution_Finale", "Date_Attribution", "Attribue_Par",
]

COLONNES_COMMANDE = [
    "Commande_Numero", "Commande_Date", "Commande_Montant",
    "Commande_Statut", "Commande_Import_Date",
]

COLONNES_HISTORIQUE = [
    "Derniere_Modification", "Modifie_Par",
]

ALL_COLUMNS = (
    COLONNES_INFO_GENERALES + COLONNES_TECH_LA + COLONNES_TECH_LS +
    COLONNES_GEOTECH + COLONNES_JALONS + COLONNES_MONTANT +
    COLONNES_PREFERENCE + COLONNES_ATTRIBUTION +
    COLONNES_COMMANDE + COLONNES_HISTORIQUE
)

STATUTS = [
    "Brouillon", "Soumise", "Attribuée", "Commandée", "Annulée"
]

STATUTS_COLORS = {
    "Brouillon": "#9E9E9E",
    "Soumise": "#FF9800",
    "Attribuée": "#2196F3",
    "Commandée": "#4CAF50",
    "Annulée": "#F44336",
}

TRIMESTRES = [
    "T1 2025", "T2 2025", "T3 2025", "T4 2025",
    "T1 2026", "T2 2026", "T3 2026", "T4 2026",
    "T1 2027", "T2 2027", "T3 2027", "T4 2027",
]

TENSIONS = ["400 kV", "225 kV", "150 kV", "90 kV", "63 kV", "Autre"]

TYPES_PROJET = [
    "Création", "Renouvellement", "Renforcement",
    "Modification", "Dépose", "Autre",
]

GIE_LIST = [
    "GIE 1 - Nom Entreprise A",
    "GIE 2 - Nom Entreprise B",
    "GIE 3 - Nom Entreprise C",
    "GIE 4 - Nom Entreprise D",
    "GIE 5 - Nom Entreprise E",
]


def ensure_db():
    """Crée la base de données si elle n'existe pas."""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(HISTORY_DIR, exist_ok=True)
    if not os.path.exists(DB_FILE):
        df = pd.DataFrame(columns=ALL_COLUMNS)
        df.to_excel(DB_FILE, index=False, engine="openpyxl")
    return DB_FILE


def load_data() -> pd.DataFrame:
    """Charge les données avec verrouillage."""
    ensure_db()
    lock = FileLock(LOCK_FILE, timeout=10)
    with lock:
        df = pd.read_excel(DB_FILE, engine="openpyxl", dtype=str)
    for col in ALL_COLUMNS:
        if col not in df.columns:
            df[col] = ""
    return df


def load_user_data(user_email: str, is_admin: bool = False) -> pd.DataFrame:
    """
    Charge les données filtrées par utilisateur.
    Les admins voient toutes les demandes.
    Les utilisateurs normaux ne voient que leurs propres demandes.
    """
    df = load_data()
    if is_admin or not user_email:
        return df
    return df[df["Createur_Email"].str.lower() == user_email.lower()].copy()


def save_data(df: pd.DataFrame):
    """Sauvegarde avec verrouillage et backup historique."""
    ensure_db()
    lock = FileLock(LOCK_FILE, timeout=10)
    with lock:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = os.path.join(HISTORY_DIR, f"backup_{timestamp}.xlsx")
        if os.path.exists(DB_FILE):
            import shutil
            shutil.copy2(DB_FILE, backup)
        df.to_excel(DB_FILE, index=False, engine="openpyxl")
    # Garder seulement les 50 derniers backups
    backups = sorted(
        [f for f in os.listdir(HISTORY_DIR) if f.startswith("backup_")]
    )
    while len(backups) > 50:
        os.remove(os.path.join(HISTORY_DIR, backups.pop(0)))


def generate_id() -> str:
    """Génère un ID unique pour une demande."""
    return f"DEM-{datetime.datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"


def ajouter_demande(data: dict, utilisateur: str = "Système") -> str:
    """Ajoute une nouvelle demande. Retourne l'ID."""
    df = load_data()
    demande_id = generate_id()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    row = {col: "" for col in ALL_COLUMNS}
    row.update(data)
    row["ID_Demande"] = demande_id
    row["Statut"] = "Brouillon"
    row["Createur_Email"] = utilisateur  # Email du créateur pour le filtrage
    row["Date_Creation"] = now
    row["Derniere_Modification"] = now
    row["Modifie_Par"] = utilisateur
    new_row = pd.DataFrame([row])
    df = pd.concat([df, new_row], ignore_index=True)
    save_data(df)
    return demande_id


def modifier_demande(demande_id: str, data: dict, utilisateur: str = "Système"):
    """Modifie une demande existante (seulement si non attribuée)."""
    df = load_data()
    mask = df["ID_Demande"] == demande_id
    if mask.sum() == 0:
        raise ValueError(f"Demande {demande_id} introuvable.")
    statut = df.loc[mask, "Statut"].values[0]
    if statut in ("Attribuée", "Commandée"):
        raise PermissionError(
            f"La demande {demande_id} est '{statut}' et ne peut plus être modifiée."
        )
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    for key, val in data.items():
        if key in ALL_COLUMNS:
            df.loc[mask, key] = val
    df.loc[mask, "Derniere_Modification"] = now
    df.loc[mask, "Modifie_Par"] = utilisateur
    save_data(df)


def soumettre_demande(demande_id: str, utilisateur: str = "Système"):
    """Passe une demande de Brouillon à Soumise."""
    df = load_data()
    mask = df["ID_Demande"] == demande_id
    if mask.sum() == 0:
        raise ValueError(f"Demande {demande_id} introuvable.")
    df.loc[mask, "Statut"] = "Soumise"
    df.loc[mask, "Derniere_Modification"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    df.loc[mask, "Modifie_Par"] = utilisateur
    save_data(df)


def attribuer_demande(demande_id: str, gie: str, utilisateur: str = "Système"):
    """Attribue une demande à un GIE — verrouille la demande."""
    df = load_data()
    mask = df["ID_Demande"] == demande_id
    if mask.sum() == 0:
        raise ValueError(f"Demande {demande_id} introuvable.")
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    df.loc[mask, "Statut"] = "Attribuée"
    df.loc[mask, "Attribution_Finale"] = gie
    df.loc[mask, "Date_Attribution"] = now
    df.loc[mask, "Attribue_Par"] = utilisateur
    df.loc[mask, "Derniere_Modification"] = now
    df.loc[mask, "Modifie_Par"] = utilisateur
    save_data(df)


def annuler_demande(demande_id: str, utilisateur: str = "Système"):
    """Annule une demande."""
    df = load_data()
    mask = df["ID_Demande"] == demande_id
    if mask.sum() == 0:
        raise ValueError(f"Demande {demande_id} introuvable.")
    df.loc[mask, "Statut"] = "Annulée"
    df.loc[mask, "Derniere_Modification"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    df.loc[mask, "Modifie_Par"] = utilisateur
    save_data(df)


def importer_commandes(df_commandes: pd.DataFrame, col_mapping: dict, utilisateur: str = "Système") -> dict:
    """
    Importe une extraction Excel de commandes et met à jour les demandes.
    col_mapping: dict mappant les noms de colonnes du fichier importé vers nos colonnes.
    Retourne un résumé {matched, unmatched, errors}.
    """
    df = load_data()
    stats = {"matched": 0, "unmatched": 0, "errors": []}
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    for _, row in df_commandes.iterrows():
        eotp = str(row.get(col_mapping.get("EOTP2", ""), "")).strip()
        if not eotp:
            stats["unmatched"] += 1
            continue
        mask = df["EOTP2"] == eotp
        if mask.sum() == 0:
            stats["unmatched"] += 1
            continue
        df.loc[mask, "Statut"] = "Commandée"
        if "Commande_Numero" in col_mapping:
            df.loc[mask, "Commande_Numero"] = str(row.get(col_mapping["Commande_Numero"], ""))
        if "Commande_Date" in col_mapping:
            df.loc[mask, "Commande_Date"] = str(row.get(col_mapping["Commande_Date"], ""))
        if "Commande_Montant" in col_mapping:
            df.loc[mask, "Commande_Montant"] = str(row.get(col_mapping["Commande_Montant"], ""))
        df.loc[mask, "Commande_Statut"] = "Confirmée"
        df.loc[mask, "Commande_Import_Date"] = now
        df.loc[mask, "Derniere_Modification"] = now
        df.loc[mask, "Modifie_Par"] = utilisateur
        stats["matched"] += 1

    save_data(df)
    return stats


def get_kpi(df: pd.DataFrame) -> dict:
    """Calcule les KPI du tableau de bord."""
    total = len(df)
    if total == 0:
        return {
            "total": 0, "brouillon": 0, "soumises": 0,
            "attribuees": 0, "commandees": 0, "annulees": 0,
            "taux_attribution": 0, "taux_commande": 0,
        }
    return {
        "total": total,
        "brouillon": len(df[df["Statut"] == "Brouillon"]),
        "soumises": len(df[df["Statut"] == "Soumise"]),
        "attribuees": len(df[df["Statut"] == "Attribuée"]),
        "commandees": len(df[df["Statut"] == "Commandée"]),
        "annulees": len(df[df["Statut"] == "Annulée"]),
        "taux_attribution": round(
            len(df[df["Statut"].isin(["Attribuée", "Commandée"])]) / total * 100, 1
        ),
        "taux_commande": round(
            len(df[df["Statut"] == "Commandée"]) / total * 100, 1
        ),
    }
