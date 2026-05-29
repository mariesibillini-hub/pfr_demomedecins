import numpy as np
import pandas as pd
from models.data_loader import charger_donnees # à supprimer après

df_med, df_pop, df_deces = charger_donnees() # à supprimer après

def dfs_totals(year):
    df_med_tot = df_med[df_med["libelle_secteur_conventionnel"] == "tout secteur compris"]
    df_med_tot = df_med_tot[["code_dep", "annee", "libelle_dep", "effectif_medecins"]]

    df_deces_tot = df_deces[(df_deces["age"] == "Tous âges") & (df_deces["type_mesure"] == "Décès enregistrés (département de résidence)")]
    df_deces_tot = df_deces_tot[["code_dep", "annee", "nombre_deces"]]

    df_densite_totale = (df_med_tot.merge(df_pop, on=["code_dep", "annee"], how="inner")
                               .merge(df_deces_tot, on=["code_dep", "annee"], how="inner"))
    df_densite_totale["densite_medicale_100k"] = df_densite_totale["effectif_medecins"] / df_densite_totale["nombre_residents"] * 100000
    df_densite_totale["nombre_deces_100k"] = df_densite_totale["nombre_deces"] / df_densite_totale["nombre_residents"] * 100000

    df_densite_year = df_densite_totale[df_densite_totale["annee"] == year]
    
    return df_densite_year

def get_valeurs_filtres(df_med, df_deces):
    departements = sorted(df_med["libelle_dep"].unique())
    secteurs = sorted(df_med["libelle_secteur_conventionnel"].unique())
    ages = sorted(df_deces["age"].unique())
    return departements, secteurs, ages


