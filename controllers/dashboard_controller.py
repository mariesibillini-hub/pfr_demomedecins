from models.data_analysis import dfs_totals
from views.dashboard import afficher_map

def map_2023():
    df = dfs_totals(2023)
    fig = afficher_map(df, "densite_medicale_100k", "blues")
    

