import numpy as np
import pandas as pd
from models.data_loader import charger_donnees # à supprimer après



def dfs_totals(year):
    df_med, df_pop, df_deces = charger_donnees() # à supprimer après
    
    df_med = df_med[df_med["secteur_conventionnel"] == "_T"]
    df_med = df_med[["code_dep", "annee", "libelle_dep", "effectif_medecins"]]

    df_deces = df_deces[(df_deces["age"] == "_T") & (df_deces["type_mesure"] == "DTH_PLACE_RES")]
    df_deces = df_deces[["code_dep", "annee", "nombre_deces"]]

    df_densite_totale = (df_med.merge(df_pop, on=["code_dep", "annee"], how="inner")
                               .merge(df_deces, on=["code_dep", "annee"], how="inner"))
    df_densite_totale["densite_medicale_100k"] = df_densite_totale["effectif_medecins"] / df_densite_totale["nombre_residents"] * 100000
    df_densite_totale["nombre_deces_100k"] = df_densite_totale["nombre_deces"] / df_densite_totale["nombre_residents"] * 100000

    df_densite_year = df_densite_totale[df_densite_totale["annee"] == year]
    
    return df_densite_year



