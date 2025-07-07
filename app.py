
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Analyse d'achat carbone", layout="centered")

# 🔐 Sécurité par mot de passe
PASSWORD = "FLCBAM25"
mdp = st.text_input("🔐 Entrez le mot de passe pour accéder à l'application :", type="password")
if mdp != PASSWORD:
    st.warning("Accès restreint. Veuillez entrer le mot de passe correct.")
    st.stop()

st.title("📉 Outil d'analyse d'achat carbone")
st.markdown("Ce programme calcule une **quantité optimale d'achat** en fonction du prix actuel et de l'historique.")

uploaded_file = st.file_uploader("📤 Importer le fichier Excel (.xlsx)", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.sort_values("Date").reset_index(drop=True)

        # Indicateurs historiques
        df['MA12'] = df['Carbon'].rolling(window=12).mean()
        rolling_std = df['Carbon'].rolling(window=12).std()
        df['MA50'] = df['Carbon'].rolling(window=50).mean()
        df['Min52'] = df['Carbon'].rolling(window=52).min()
        df['Max52'] = df['Carbon'].rolling(window=52).max()
        mean_global = df['Carbon'].mean()
        std_global = df['Carbon'].std()

        # Spread
        df['Spread'] = df['Gaz'] - df['Coal']
        df['Spread_Z'] = (df['Spread'] - df['Spread'].rolling(window=12).mean()) / df['Spread'].rolling(window=12).std()
        spread_z = df['Spread_Z'].iloc[-2]

        st.success("✅ Données chargées avec succès.")

        prix_actuel = st.number_input("💰 Prix actuel de l'actif", min_value=0.0, value=70.0)
        quantite_base = st.number_input("📦 Quantité de base prévue", min_value=0.0, value=100.0)
        score_exogene = st.slider("🧠 Score exogène (–1 à +1)", min_value=-1.0, max_value=1.0, step=0.1, value=0.0)

        if st.button("Calculer la quantité recommandée"):
            ma12 = df['MA12'].iloc[-1]
            ma50 = df['MA50'].iloc[-1]
            bollinger_inf = ma12 - 2 * rolling_std.iloc[-1]
            min52 = df['Min52'].iloc[-1]
            max52 = df['Max52'].iloc[-1]

            ecart_ma12 = (prix_actuel - ma12) / ma12
            ecart_bollinger = (prix_actuel - bollinger_inf) / prix_actuel
            volatilite = rolling_std.iloc[-1] / ma12
            variation_2s = (prix_actuel - df['Carbon'].iloc[-2]) / df['Carbon'].iloc[-2]
            range52 = (prix_actuel - min52) / (max52 - min52)
            ecart_ma50 = (prix_actuel - ma50) / ma50
            zscore = (prix_actuel - mean_global) / std_global
            ecart_moy_hist = (prix_actuel - mean_global) / mean_global

            score = 0
            score += -0.21 * ecart_ma12
            score += -0.18 * ecart_bollinger
            score += -0.05 * volatilite
            score += -0.05 * variation_2s
            score += -0.13 * (1 - range52)
            score += -0.06 * ecart_ma50
            score += -0.13 * zscore
            score += -0.05 * ecart_moy_hist
            score += -0.08 * max(-1, min(1, spread_z))
            score += -0.02 * score_exogene

            if score < 0:
                facteur = 1 + max(score, -0.20)
            else:
                facteur = 1 + min(score, 0.33)

            quantite_finale = round(quantite_base * facteur, 2)

            st.markdown("### 🧮 Résultat")
            st.write(f"**Score total pondéré** : `{round(score, 4)}`")
            st.write(f"**Quantité recommandée** : `{quantite_finale}` (soit un ajustement de `{round((facteur - 1)*100, 2)}%`)")

    except Exception as e:
        st.error(f"❌ Erreur lors du traitement du fichier : {e}")
