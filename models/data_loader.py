import numpy as np
import pandas as pd
import streamlit as st

@st.cache
def charger_donnees():
    df_med = pd.read_csv(r"C:\Users\USER\Desktop\Learning Data Analyst\DataRockStar\Projet Fil Rouge\mon_projet\data\demographie-secteurs-conventionnels.csv", sep=";")
    df_pop = pd.read_csv(r"C:\Users\USER\Desktop\Learning Data Analyst\DataRockStar\Projet Fil Rouge\mon_projet\data\DS_POPULATIONS_HISTORIQUES_data.csv", sep=";")
    df_deces = pd.read_csv(r"C:\Users\USER\Desktop\Learning Data Analyst\DataRockStar\Projet Fil Rouge\mon_projet\data\DS_DECES_MORTALITE_SERIES_data.csv", sep=";")

    _supprimer_inutile(df_med, df_pop, df_deces)
    _nettoyer_types(df_med, df_pop, df_deces)
    _ligne_total(df_med)
    return df_med, df_pop, df_deces

def _supprimer_inutile(df1, df2, df3):
    # mon analyse porte uniquement sur les médecins généralistes donc je garde uniquement ces données
    df1 = df1[df1["profession_sante"].isin(["Médecins généralistes (hors médecins à expertise particulière - MEP)", "Médecins généralistes à expertise particulière (MEP)"])].reset_index(drop=True)
    # Je supprime également les lignes incluant departement : 999, car c'est redondant (total des autres lignes)
    df1 = df1.replace({"departement" : {"999" : np.nan},
                       "annee" : {2024 : np.nan}}).dropna()
    ok_year = [int(year) for year in df1['annee'].unique()]

    df1 = df1.drop(columns=["region", "vision generale all", "vision_generale_prescriptions", "vision profession territoire"])

    # Je supprime toutes les lignes inutiles pour ne garder que les lignes avec les années souhaitées (entre 2010 et 2024 incluses) 
    # et les lignes traitant des départements
    df2 = df2[df2["TIME_PERIOD"].isin(ok_year)]
    df2 = df2[df2["GEO_OBJECT"] == "DEP"].reset_index(drop=True)
    # Je supprimes les colonnes inutiles
    df2 = df2.drop(columns=["FREQ", "GEO_OBJECT", "POPREF_MEASURE"])
    
    # Suppression des lignes inutiles pour mes analyses cf keepers
    # Suppression des lignes qui ne contiennent pas de données départementales
    # Suppression des lignes hors des années étudiées (2010 à 2024)
    df3 = df3[
        (df3["GEO_OBJECT"] == "DEP") 
        & (df3["FREQ"] == "A")
        & (df3["OBS_STATUS"] == "A")
        & (df3["OBS_STATUS_FR"] == "D")
        & (df3["EC_MEASURE"].isin(["DTH_PLACE_RES", "MOR_STANDARD_RT"]))
        & (df3["AGE"].isin(["Y_LT1", "Y_LT65", "Y_GE65", "_T"]))]
    df3["TIME_PERIOD"] = df3["TIME_PERIOD"].astype(int)
    df3 = df3[(df3["TIME_PERIOD"].isin(ok_year))]

    return df1, df2, df3

def _nettoyer_types(df1, df2, df3):
    # Renommer les colonnes et les valeurs
    df1 = df1.rename(columns={
        "﻿annee": 'annee',
        "departement": "code_dep"
    })
    df1 = df1.replace({'libelle_secteur_conventionnel': {
        "conventionnés de secteur 2 ayant adhéré à l'Optam/Optam-CO": "conventionnés de secteur 2",
        "conventionnés de secteur 2 n'ayant pas adhéré à l'Optam/Optam-CO": "conventionnés de secteur 2"
    }})
    
    df2 = df2.rename(columns={
        "GEO": "code_dep",
        "TIME_PERIOD": "annee"
    })
    df2.columns = df2.columns.str.lower()

    df3 = df3.rename(columns={
        "GEO": "code_dep",
        "TIME_PERIOD": "annee"
    })
    df3.columns = df3.columns.str.lower()

    # Remplacer le type de "secteur_conventionnel" en string, car ce sont des nombres catégoriels, et certains ont des 0 significatifs
    # + ajout des 0 significatifs pour les régions et les départements.
    df["secteur_conventionnel"] = df["secteur_conventionnel"].astype(str)
    df = df.replace({'code_dep': {"1": "01",
                            "2": "02",
                            "3": "03",
                            "4": "04",
                            "5": "05",
                            "6": "06",
                            "7": "07",
                            "8": "08",
                            "9": "09"}})
    return df1, df2, df3

def _ligne_total(df1):
    # Créer une ligne avec un total
    df1_total = df1.groupby(["code_dep", "annee"], as_index=False)["effectif"].sum()

    # Ajout d'une valeur spécifique dans les colonnes où total devra apparaître
    df1_total["profession_sante"] = "Tous médecins généralistes"
    df1_total["libelle_secteur_conventionnel"] = "tout secteur compris"
    df1_total["secteur_conventionnel"] = "_T"

    libelles = df1[["code_dep", "libelle_region", "libelle_departement"]].drop_duplicates()
    df1_total = pd.merge(df1_total, libelles, on="code_dep", how="left")
    # pd.concat() s'applique sur : liste de DataFrames → retourne un DataFrame
    df1 = pd.concat([df1, df1_total], ignore_index=True)
    return df1