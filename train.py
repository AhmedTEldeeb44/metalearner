import pandas as pd
import numpy as np
import joblib
import os
import warnings
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import PowerTransformer, OneHotEncoder
from sklearn.metrics import (
    mean_absolute_error,
    r2_score,
    mean_squared_error,
    explained_variance_score,
)
from colorama import Fore, Style, init

warnings.filterwarnings("ignore")
init(autoreset=True)

# 1. LOAD & PREPARE
FILENAME = "Specialized_Medical_Warehouse.csv"
if not os.path.exists(FILENAME):
    print(f"{Fore.RED}❌ Error: Warehouse file missing.")
    exit()

df = pd.read_csv(FILENAME)

dna_features = [
    "entropy",
    "imbalance",
    "kurt",
    "n_cols",
    "n_rows",
    "skew",
    "stability_score",
    "null_density",
    "num_cat_ratio",
    "avg_correlation",
]
target_col = "current_f1"

X_dna = df[dna_features].fillna(0)
algo_names = df[["tested_algo"]]

# Encoding Algos
algo_encoder = OneHotEncoder(sparse_output=False)
X_algo = algo_encoder.fit_transform(algo_names)
algo_labels = algo_encoder.get_feature_names_out(["tested_algo"])

# Combine Features
feature_names = dna_features + list(algo_labels)
X = np.hstack([X_dna, X_algo])
y = df[target_col].values

# Split & Scale
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42
)
scaler = PowerTransformer(method="yeo-johnson")
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 2. TRAIN THE RANKER
print(
    f"{Fore.MAGENTA}🔥 Training Neural Ranker... {Fore.WHITE}(i7 All-Core Optimization)"
)

ranker = XGBRegressor(
    n_estimators=600,
    max_depth=6,
    learning_rate=0.05,
    n_jobs=-1,
    objective="reg:squarederror",
    importance_type="gain",  # Focus on contribution to accuracy
)

ranker.fit(X_train_scaled, y_train)

# 3. ADVANCED METRICS
y_pred = ranker.predict(X_test_scaled)
r2 = r2_score(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
evs = explained_variance_score(y_test, y_pred)

# 4. TERMINAL VISUALS (ASCII MAPS)
print(f"\n{Fore.CYAN}{Style.BRIGHT}📊 --- NEURAL DIAGNOSTIC REPORT ---")
print(f"  🎯 REAL R² SCORE:      {Fore.GREEN}{r2:.2%}")
print(f"  📉 MEAN ABS ERROR:     {Fore.YELLOW}{mae:.4f} F1-Points")
print(f"  📏 RMSE (PRECISION):   {Fore.YELLOW}{rmse:.4f}")
print(f"  💡 EXPLAINED VAR:      {Fore.GREEN}{evs:.2%}")


print(f"\n{Fore.CYAN}{Style.BRIGHT}🧬 --- DNA FEATURE IMPORTANCE (TERMINAL MAP) ---")
importances = ranker.feature_importances_
# Only show DNA importance (first 10 features) for cleaner visual
dna_imp = pd.Series(importances[: len(dna_features)], index=dna_features).sort_values(
    ascending=False
)

max_imp = dna_imp.max()
for name, val in dna_imp.items():
    bar_len = int((val / max_imp) * 30)
    bar = "█" * bar_len
    print(f"  {Fore.WHITE}{name:<18} | {Fore.GREEN}{bar} {val:.2%}")

print(f"\n{Fore.CYAN}{Style.BRIGHT}🧠 --- ERROR RESIDUAL DISTRIBUTION ---")
# Show how many predictions were "very close" vs "way off"
residuals = np.abs(y_test - y_pred)
bins = [0, 0.01, 0.03, 0.05, 0.1, 1.0]
labels = [
    "Perfect (<0.01)",
    "High (0.01-0.03)",
    "Medium (0.03-0.05)",
    "Low (0.05-0.1)",
    "Failure (>0.1)",
]
dist = pd.cut(residuals, bins=bins, labels=labels).value_counts().sort_index()


for label, count in dist.items():
    pct = (count / len(y_test)) * 100
    bar_len = int(pct / 3)
    bar = "▒" * bar_len
    color = Fore.GREEN if "Perfect" in label or "High" in label else Fore.RED
    print(f"  {Fore.WHITE}{label:<20} | {color}{bar} {pct:.1f}% ({count})")

# 5. SAVE
os.makedirs("brain", exist_ok=True)
joblib.dump(ranker, "brain/meta_brain_final.pkl")
joblib.dump(scaler, "brain/dna_scaler.pkl")
joblib.dump(algo_encoder, "brain/algo_encoder.pkl")
print(
    f"\n{Fore.YELLOW}📦 Neural Ranker artifacts updated. Oracle system re-synchronized."
)
