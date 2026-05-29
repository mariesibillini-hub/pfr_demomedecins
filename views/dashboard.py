import plotly.express as px
import requests
import streamlit as st
from config import YEARS

# geojson des départements français
geojson_url = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements-version-simplifiee.geojson"
geojson_dep = requests.get(geojson_url).json()

def afficher_analyses(df_densite_year):
    col1, col2 = st.columns(2)
    with col1:
        st.write("Colonne 1")
    with col2:
        _afficher_map(df_densite_year, "densite_medicale_100k", "blues")

def _afficher_map(df, values, color):
    # affiche une carte de France métropolitaine découpée par département 
    fig = px.choropleth(
        df,
        geojson=geojson_dep,
        locations="code_dep",
        featureidkey="properties.code",
        color=values, # densite_medicale_100k ou nombre_deces_100k
        color_continuous_scale=color, # bleu pour densite_medicale_100k ou rouge pour nombre_deces_100k
        scope="europe",
        # labels={values: "Population"}
    )
    fig.update_geos(
        center={"lat": 46.5, "lon": 2.5},
        projection_scale=6
    )

    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    st.plotly_chart(fig, use_container_width=True)

def get_filtres(departements, ages):
    choix_annee = st.sidebar.slider("Année :", min(YEARS), max(YEARS), max(YEARS))
    choix_dep = st.sidebar.multiselect("Département :", departements)
    choix_age = st.sidebar.selectbox("Tranche d'âge :", ages)
    return choix_annee, choix_dep, choix_age