import streamlit as st
from models.data_loader import charger_donnees
from models.data_analysis import dfs_totals, get_valeurs_filtres
from views.dashboard import afficher_analyses, get_filtres
from config import YEARS

@st.cache_data
def _charger_donnees_cache():
    return charger_donnees()

with st.spinner("Chargement des données..."):
    df_med, df_pop, df_deces = _charger_donnees_cache()

def run():
    departements, secteurs, ages = get_valeurs_filtres(df_med, df_deces)
    choix_annee, choix_dep, choix_age = get_filtres(departements, ages)
    df_densite_year = dfs_totals(choix_annee)
    afficher_analyses(df_densite_year)
    

