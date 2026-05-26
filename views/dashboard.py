import plotly.express as px
import requests

# geojson des départements français
geojson_url = "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements-version-simplifiee.geojson"
geojson_dep = requests.get(geojson_url).json()

def afficher_map(df, values, color):
    # affiche une carte de France métropolitaine découpée par département 
    fig = px.choropleth(
        df,
        geojson=geojson_dep,
        locations="code_dep",
        featureidkey="properties.code", #
        color=values, # effectif_medecins ou nombre_deces
        color_continuous_scale=color, # bleu pour effectif_medecins et rouge pour nombre_deces
        scope="europe",
        # labels={values: "Population"}
    )
    fig.update_geos(
        center={"lat": 46.5, "lon": 2.5},
        projection_scale=6
    )

    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    # fig.show()