import streamlit as st
import pandas as pd
import os
import plotly.express as px

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="AgroCam", page_icon="🌾", layout="wide")
DATA_FILE = "data_agricole.csv"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE)
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            return df
        except:
            pass
    # Retourne une structure propre si le fichier est absent ou corrompu
    return pd.DataFrame(columns=["Culture", "Surface (ha)", "Engrais (kg)", "Rendement (t)", "Marché", "Prix (FCFA)", "Date"])

# --- 2. BARRE LATÉRALE (SAISIE) ---
st.sidebar.header("🖊️ Saisie des données")
with st.sidebar.form("form_collecte"):
    culture = st.selectbox("🌱 Culture", ["Maïs 🌽", "Tomate", "Pasteque", "Café ☕", "Riz 🍚"])
    marche = st.selectbox("📍 Marché de vente", ["Marché Central", "Mfoundi", "Mokolo", "Etoudi"])
    prix = st.number_input("💰 Prix (FCFA/t)", min_value=0, step=500)
    date = st.date_input("📅 Date de vente")
    surface = st.number_input("📏 Surface (ha)", min_value=0.1, step=0.1)
    engrais = st.number_input("🧪 Engrais (kg)", min_value=0.0, step=1.0)
    rendement = st.number_input("⚖️ Rendement (t)", min_value=0.0, step=0.1)
    
    if st.form_submit_button("💾 Enregistrer"):
        df = load_data()
        # On convertit la date en texte pour éviter les erreurs de format lors de la sauvegarde
        date_str = date.strftime("%Y-%m-%d")
        new_row = pd.DataFrame([[culture.split(' ')[0], surface, engrais, rendement, marche, prix, date_str]], 
                               columns=["Culture", "Surface (ha)", "Engrais (kg)", "Rendement (t)", "Marché", "Prix (FCFA)", "Date"])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(DATA_FILE, index=False)
        st.sidebar.success("✅ Donnée enregistrée !")

# --- 3. ZONE PRINCIPALE ---
st.title("🌾 AgroCam : Analyse & Collecte De Donnees Agricoles")
df = load_data()

if not df.empty and 'Date' in df.columns:
    tab1, tab2, tab3 = st.tabs(["📈 Analyse Marchés & Prix", "🤖 Modèle Prédictif", "📋 Données Brutes"])

    with tab1:
        st.subheader("Analyse des prix par Marché")
        fig1 = px.bar(df, x="Marché", y="Prix (FCFA)", color="Culture", barmode="group")
        st.plotly_chart(fig1, use_container_width=True)
        
        st.subheader("Saisonnalité des prix")
        df['Mois'] = df['Date'].dt.month_name()
        fig2 = px.line(df.groupby(['Mois', 'Culture'])['Prix (FCFA)'].mean().reset_index(), 
                       x="Mois", y="Prix (FCFA)", color="Culture", markers=True)
        st.plotly_chart(fig2, use_container_width=True)

    with tab2:
        st.subheader("Modèle de Régression Linéaire Personnalisé")
        coef = 1.0000
        intercept = 0.59
        
        st.write(f"📈 **Équation du modèle :** Rendement = {coef} * Engrais + {intercept}")
        val_engrais = st.number_input("Simulateur : Entrez la quantité d'engrais (kg)", min_value=0.0, value=10.0)
        rendement_estime = (coef * val_engrais) + intercept
        st.success(f"🚀 Rendement estimé : {rendement_estime:.2f} tonnes")        
        
        # Visualisation de la droite
        max_engrais = df['Engrais (kg)'].max() + 20
        df_droite = pd.DataFrame({'Engrais': [0, max_engrais], 'Rendement': [intercept, (coef * max_engrais) + intercept]})
        fig_reg = px.scatter(df, x="Engrais (kg)", y="Rendement (t)", title="Droite de régression forcée")
        fig_reg.add_scatter(x=df_droite['Engrais'], y=df_droite['Rendement'], mode='lines', name='Modèle théorique')
        st.plotly_chart(fig_reg, use_container_width=True)

    with tab3:
        st.dataframe(df.sort_values(by="Date", ascending=False), use_container_width=True)
else:
    st.info("👈 Saisissez vos premières données dans la barre latérale pour activer les analyses.")
    
# --- 4. PIED DE PAGE ---
st.markdown("---")
st.info("Projet Academique INF 232 EC2 - Analyse & Collecte De Donnees Agricoles")    
