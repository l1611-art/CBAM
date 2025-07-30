import pandas as pd

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

df = pd.read_excel("prix.xlsx")
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df = df.sort_values("Date").reset_index(drop=True)

df['MA12'] = df['Carbon'].rolling(window=12).mean()
df['MA50'] = df['Carbon'].rolling(window=50).mean()
df['Min104'] = df['Carbon'].rolling(window=104).min() 
df['Max104'] = df['Carbon'].rolling(window=104).max()
df['RollingStd'] = df['Carbon'].rolling(window=12).std()
df['RSI'] = compute_rsi(df['Carbon'])

prix_actuel = float(input("Quel est le prix actuel de l'actif ? "))
quantite_base = float(input("Quelle est la quantité de base à acheter ? "))
score_exogene = float(input("Notez l'impact exogène cette semaine (entre -1 et +1) : "))
score_exogene = max(-1, min(1, score_exogene))

ma12 = df['MA12'].iloc[-1]
ma50 = df['MA50'].iloc[-1]
bollinger_inf = ma12 - 2 * df['RollingStd'].iloc[-1]
min104 = df['Min104'].iloc[-1]
max104 = df['Max104'].iloc[-1]
mean_global = df['Carbon'].mean()
std_global = df['Carbon'].std()
rsi = df['RSI'].iloc[-1]

ecart_ma12 = (prix_actuel - ma12) / ma12
ecart_bollinger = (prix_actuel - bollinger_inf) / prix_actuel
volatilite = df['RollingStd'].iloc[-1] / ma12
variation_2s = (prix_actuel - df['Carbon'].iloc[-3]) / df['Carbon'].iloc[-3]
variation_1s = (prix_actuel - df['Carbon'].iloc[-1]) / df['Carbon'].iloc[-1]
variation_1s = min(variation_1s, 0.05)
range104 = (prix_actuel - min104) / (max104 - min104) if max104 != min104 else 0
ecart_ma50 = (prix_actuel - ma50) / ma50
zscore = (prix_actuel - mean_global) / std_global
ecart_moy_hist = (prix_actuel - mean_global) / mean_global
momentum_3s = (prix_actuel - df['Carbon'].iloc[-3]) / df['Carbon'].iloc[-3]

score = 0
score += -0.21 * ecart_ma12
score += -0.18 * ecart_bollinger
score += -0.05 * volatilite
score += -0.06 * variation_2s
score += -0.07 * variation_1s
score += -0.05 * (1 - range104)
score += -0.07 * ecart_ma50
score += -0.15 * zscore
score += -0.08 * momentum_3s
score += -0.03 * score_exogene
score += 0.05 * (rsi - 50) / 100

if score < 0:
    facteur = 1 + max(score / 2.5, -0.12)
else:
    facteur = 1 + min(score * 2, 0.35)

quantite_finale = round(quantite_base * facteur, 1)

print("\n--- Résultat ---")
print(f"Score total pondéré : {round(score, 4)}")
print(f"Quantité recommandée : {quantite_finale} (soit un ajustement de {round((facteur - 1) * 100, 2)}%)")
