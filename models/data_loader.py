import numpy as np
import pandas as pd
import streamlit as st

@st.cache
def charger_donnees(chemin):
    df = pd.read_csv(chemin, sep=";")
    _supprimer_inutile(df)
    _nettoyer_types(df)
    return df

def _nettoyer_types(df):
    df = df.rename(columns={"﻿annee": 'annee'}) #renommer annee car a un caractère spécial
    # Remplacer le type de "annee", "region", "secteur_conventionnel" en string, car ce sont des nombres catégoriels, et certains ont des 0 significatifs
    # + ajout des 0 significatifs pour les régions et les départements.
    df[["annee", "region", "secteur_conventionnel"]] = df[["annee", "region", "secteur_conventionnel"]].astype(str)
    df = df.replace({'departement': {"1": "01",
                            "2": "02",
                            "3": "03",
                            "4": "04",
                            "5": "05",
                            "6": "06",
                            "7": "07",
                            "8": "08",
                            "9": "09"},
                'region': {"1": "01",
                            "2": "02",
                            "3": "03",
                            "4": "04",
                            "5": "05",
                            "6": "06",
                            "7": "07",
                            "8": "08",
                            "9": "09"}})
    return df

def _supprimer_inutile(df):
    # mon analyse porte uniquement sur les médecins généralistes donc je garde uniquement ces données
    df = df[df["profession_sante"].isin(["Médecins généralistes (hors médecins à expertise particulière - MEP)", "Médecins généralistes à expertise particulière (MEP)"])].reset_index(drop=True)
    # Je supprime également les lignes incluant departement : 999, car c'est redondant (total des autres lignes)
    df = df.replace({"departement" : {"999" : np.nan}})
    df = df.dropna()
    return df

df = charger_donnees(r"C:\Users\USER\Desktop\Learning Data Analyst\DataRockStar\Projet Fil Rouge\mon_projet\data\demographie-secteurs-conventionnels.csv")
