import numpy as np
import pandas as pd
from pathlib import Path
from config import YEARS, KEPT_PROFESSIONS

DATA_DIR = Path(__file__).parent.parent / "data"

def charger_donnees():
    try:
        df_med = pd.read_csv(DATA_DIR / "demographie-secteurs-conventionnels.csv", sep=";", encoding="utf-8-sig")
        df_pop = pd.read_csv(DATA_DIR / "DS_POPULATIONS_HISTORIQUES_data.csv", sep=";")
        df_deces = pd.read_csv(DATA_DIR / "DS_DECES_MORTALITE_SERIES_data.csv", sep=";")
    except FileNotFoundError:
        raise FileNotFoundError(f"Un fichier est introuvable dans {DATA_DIR}")

    df_med, df_pop, df_deces = _supprimer_inutile(df_med, df_pop, df_deces)
    df_med, df_pop, df_deces = _nettoyer_types(df_med, df_pop, df_deces)
    df_med = _ligne_total(df_med)
    return df_med, df_pop, df_deces

def _supprimer_inutile(df1, df2, df3):
    # mon analyse porte sur les médecins généralistes donc je garde uniquement ces données
    df1 = df1[df1["profession_sante"].isin(KEPT_PROFESSIONS)].reset_index(drop=True)
    # Je supprime également les lignes incluant departement : 999, car c'est redondant (total des autres lignes)
    df1 = df1.replace({"departement": {"999" : np.nan},
                       "annee": {2024 : np.nan}}).dropna()

    df1 = df1.drop(columns=["region", "vision generale all", "vision_generale_prescriptions", "vision profession territoire", "libelle_region", "secteur_conventionnel"])

    # Je supprime toutes les lignes inutiles pour ne garder que les lignes avec les années souhaitées (entre 2010 et 2024 incluses) 
    # et les lignes traitant des départements
    df2 = df2[df2["TIME_PERIOD"].isin(YEARS)] # YEARS est compris entre 2010 et 2023 inclus
    df2 = df2[df2["GEO_OBJECT"] == "DEP"].reset_index(drop=True)
    # Je supprimes les colonnes inutiles
    df2 = df2.drop(columns=["FREQ", "GEO_OBJECT", "POPREF_MEASURE"])
    
    # Suppression des lignes inutiles pour mes analyses cf keepers
    # Suppression des lignes qui ne contiennent pas de données départementales
    # Suppression des lignes hors des années étudiées (2010 à 2024)
    df3 = df3[
        (df3["GEO_OBJECT"] == "DEP") 
        & (df3["FREQ"] == "A") # observations annuelles
        & (df3["OBS_STATUS"] == "A") # valeur normale
        & (df3["OBS_STATUS_FR"] == "D") # valeur definitive
        & (df3["EC_MEASURE"].isin([
                        "DTH_PLACE_RES", # décès enregistrés dans le département de résidence
                        "MOR_STANDARD_RT" # taux de mortalité standardisé
                    ]))
        & (df3["AGE"].isin([
                        "Y_LT1", # moins de 1 an
                        "Y_LT65", # moins de 65 ans
                        "Y_GE65", # 65 ans ou plus
                        "_T" # tous
                    ]))]
    df3["TIME_PERIOD"] = df3["TIME_PERIOD"].astype(int)
    df3 = df3[(df3["TIME_PERIOD"].isin(YEARS))] # YEARS est compris entre 2010 et 2023 inclus
    # Suppression des colonnes contenant une valeur unique
    for col in df3.columns:
        if len(df3[col].unique()) == 1:
            df3 = df3.drop(columns=col)
    df3 = df3.drop(columns=["UNIT_MEASURE", "DECIMALS"])
    return df1, df2, df3

def _nettoyer_types(df1, df2, df3):
    # Renommer les colonnes et les valeurs
    df1 = df1.rename(columns={
        "departement": "code_dep",
        "libelle_departement": "libelle_dep",
        "effectif": "effectif_medecins"
    })

    df1 = df1.replace({'libelle_secteur_conventionnel': {
        "conventionnés de secteur 2 ayant adhéré à l'Optam/Optam-CO": "conventionnés de secteur 2",
        "conventionnés de secteur 2 n'ayant pas adhéré à l'Optam/Optam-CO": "conventionnés de secteur 2"
    }})
    
    df2 = df2.rename(columns={
        "GEO": "code_dep",
        "TIME_PERIOD": "annee",
        "OBS_VALUE": "nombre_residents"
    })
    df2.columns = df2.columns.str.lower()

    df3 = df3.rename(columns={
        "GEO": "code_dep",
        "TIME_PERIOD": "annee",
        "OBS_VALUE": "nombre_deces",
        "EC_MEASURE": "type_mesure"
    })
    df3.columns = df3.columns.str.lower()

    df3 = df3.replace({"age": {
        "Y_LT1": "Moins d'1 an",
        "Y_LT65": "Moins de 65 ans",
        "Y_GE65": "65 ans et plus",
        "_T": "Tous âges"
        },
        "type_mesure": {
            "DTH_PLACE_RES": "Décès enregistrés (département de résidence)",
            "MOR_STANDARD_RT": "Taux de mortalité (standardisé)"
        }
    })

    # Ajout des 0 significatifs pour les régions et les départements.
    df1["code_dep"] = df1["code_dep"].str.zfill(2)

    return df1, df2, df3

def _ligne_total(df1):
    # Créer une ligne avec un total
    df1_total = df1.groupby(["code_dep", "annee"], as_index=False)["effectif_medecins"].sum()

    # Ajout d'une valeur spécifique dans les colonnes où total devra apparaître
    df1_total["profession_sante"] = "Tous médecins généralistes"
    df1_total["libelle_secteur_conventionnel"] = "tout secteur compris"

    libelles = df1[["code_dep", "libelle_dep"]].drop_duplicates()
    df1_total = pd.merge(df1_total, libelles, on="code_dep", how="left")
    # pd.concat() s'applique sur : liste de DataFrames → retourne un DataFrame
    df1 = pd.concat([df1, df1_total], ignore_index=True)
    return df1
