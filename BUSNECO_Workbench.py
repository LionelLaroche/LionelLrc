import streamlit as st
import pandas as pd

st.set_page_config(page_title='BUSNECO_Workbench', page_icon='datachart', layout='wide')
st.title("BUSNECO Workbench")
st.sidebar.image("MTN-new-logo1.png", width=200)

@st.cache_data
def load_segmentation():
    return pd.read_excel("SEGMENTATION_Q3.xlsx", sheet_name="RGA")

@st.cache_data
def load_dsm_site():
    return pd.read_excel("DSM_&_Sites.xlsx")

# Sidebar for navigation
choice = st.sidebar.selectbox("Choississez Une page", ["Etat des stocks", "Listing des commerciaux"])

if choice == "Etat des stocks":
    st.title("Etat des stocks")

    
    segmentation = load_segmentation()
    dsm_site = load_dsm_site()
    sheet_name = dsm_site["DSM"].unique().tolist()      

    # Afficher le lien de téléchargement
    uploaded_file = st.sidebar.file_uploader("Téléverse un fichier pour analyse :", type=["xlsx"])  # (label: str, type=None, accept_multiple_files=False, ...)

    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file).dropna()
            df = df[df['Segment Group'] != '3-LVC']

        except Exception as e:
            st.error(f"Erreur lors du chargement du fichier : {e}")
            st.stop()
            
        # Recherche des commerciaux par site en faisant une recherche verticale
        try:
            df = df.merge(dsm_site[['Locality', 'DSM']], on='Locality', how='left')
            df['MSISDN'] = df['MSISDN'].astype(int)
            df = df.merge(segmentation[['MSISDN', 'full_name']], on='MSISDN', how='left')
        except Exception as e:
            st.error(f"Erreur lors de la fusion des données : {e}")
            st.stop()
        df = df.rename(columns={'DSM': 'Nom DSM', 'full_name': 'Nom Agents'})
        
        # Sélection colonnes par noms, éviter iloc fragile
        desired_order = ['MSISDN', 'Nom Agents', 'Nom DSM', 'Locality'] + \
                        [col for col in df.columns if col not in ['MSISDN', 'Nom Agents', 'Nom DSM', 'Locality']]
        df = df[desired_order]

        st.markdown("**Selectionnez les donnees a afficher**")
        coloumns_to_display = st.multiselect("Colonnes a afficher", df.columns.tolist(), default=['MSISDN', 'Nom Agents', 'Locality', 'Nom DSM'])
        df_display = df[coloumns_to_display]
      
        # Afficher les resultats pour un DSM specifique
        st.markdown("**Choisissez un ou plusieurs commerciaux**")
        commerciaux = sorted(dsm_site["DSM"].unique())
        selections = st.multiselect("Nom(s) du/des Commercial(aux)", options=commerciaux)
        if selections:
            for commercial in selections:
                try:
                    df_selection = df_display[df_display['Nom DSM'] == commercial]
                except KeyError:
                    st.error(f"Erreur: Veuillez référencer la colonne 'Nom DSM' dans votre selection.")
                    continue
                if not df_selection.empty:
                    st.markdown(f"### Donnees Points de ventes en rupture pour le commercial: **{commercial}**")
                    st.dataframe(df_selection)

