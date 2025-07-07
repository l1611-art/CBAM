import pandas as pd

# Charger les données
df = pd.read_excel(r"C:\Users\Louis D'Anglade\Documents\MACF\Achatcertif\prix.xlsx")
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df = df.sort_values("Date").reset_index(drop=True)

# Indicateurs historiques
df['MA12'] = df['Carbon'].rolling(window=12).mean()
rolling_std = df['Carbon'].rolling(window=12).std()
df['MA50'] = df['Carbon'].rolling(window=50).mean()
df['Min52'] = df['Carbon'].rolling(window=52).min()
df['Max52'] = df['Carbon'].rolling(window=52).max()

# Z-score & moyennes globales
mean_global = df['Carbon'].mean()
std_global = df['Carbon'].std()

# Spread charbon-gaz
df['Spread'] = df['Gaz'] - df['Coal']
df['Spread_Z'] = (df['Spread'] - df['Spread'].rolling(window=12).mean()) / df['Spread'].rolling(window=12).std()
spread_z = df['Spread_Z'].iloc[-2]  # semaine précédente

# === Entrées utilisateur ===
prix_actuel = float(input("Quel est le prix actuel de l'actif ? "))
quantite_base = float(input("Quelle est la quantité de base à acheter ? "))
score_exogene = float(input("Notez l'impact exogène cette semaine (entre -1 et +1) : "))
score_exogene = max(-1, min(1, score_exogene))

# === Calcul du score en fonction du PRIX ACTUEL par rapport aux repères techniques ===
ma12 = df['MA12'].iloc[-1]
ma50 = df['MA50'].iloc[-1]
bollinger_inf = ma12 - 2 * rolling_std.iloc[-1]
min52 = df['Min52'].iloc[-1]
max52 = df['Max52'].iloc[-1]

# Ratios dynamiques (comparaison avec le prix actuel)
ecart_ma12 = (prix_actuel - ma12) / ma12
ecart_bollinger = (prix_actuel - bollinger_inf) / prix_actuel
volatilite = rolling_std.iloc[-1] / ma12
variation_2s = (prix_actuel - df['Carbon'].iloc[-2]) / df['Carbon'].iloc[-2]
range52 = (prix_actuel - min52) / (max52 - min52)
ecart_ma50 = (prix_actuel - ma50) / ma50
zscore = (prix_actuel - mean_global) / std_global
ecart_moy_hist = (prix_actuel - mean_global) / mean_global

# === Score pondéré ===
score = 0
score += -0.23 * ecart_ma12
score += -0.19 * ecart_bollinger
score += -0.05 * volatilite
score += -0.05 * variation_2s
score += -0.13 * (1 - range52)
score += -0.07 * ecart_ma50
score += -0.13 * zscore
score += -0.05 * ecart_moy_hist
score += -0.08 * max(-1, min(1, spread_z))
score += -0.02 * score_exogene

# === Quantité ajustée ===
if score < 0:
    facteur = 1 + max(score, -0.20)
else:
    facteur = 1 + min(score, 0.33)

quantite_finale = round(quantite_base * facteur, 2)

# === Affichage ===
print("\n--- Résultat ---")
print(f"Score total pondéré : {round(score, 4)}")
print(f"Quantité recommandée : {quantite_finale} (soit un ajustement de {round((facteur - 1)*100, 2)}%)")

