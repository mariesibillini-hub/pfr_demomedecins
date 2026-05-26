import streamlit as st
from models.data_analysis import dfs_totals
from views.dashboard import afficher_map

def map_2023():
    df = dfs_totals(2023)
    fig = afficher_map(df, "densite_medicale_100k", "blues")
    st.plotly_chart(fig, use_container_width=True)

