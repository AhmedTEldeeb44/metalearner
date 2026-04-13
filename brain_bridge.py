import pandas as pd
import numpy as np
import joblib
import os
from scipy.stats import entropy as scipy_entropy
from colorama import Fore, Style


class MetaBrainBridge:
    def __init__(self):
        """
        Initializes the bridge with absolute path detection.
        Expects Neural Ranker artifacts in a 'brain/' subdirectory.
        """
        self.ready = False

        # --- PATH RESOLUTION ---
        base_dir = os.path.dirname(os.path.abspath(__file__))
        brain_dir = os.path.join(base_dir, "brain")

        self.paths = {
            "model": os.path.join(brain_dir, "meta_brain_final.pkl"),
            "scaler": os.path.join(brain_dir, "dna_scaler.pkl"),
            "algo_encoder": os.path.join(brain_dir, "algo_encoder.pkl"),
        }

        self._establish_neural_link()

    def _establish_neural_link(self):
        """Loads the Scikit-Learn/XGBoost artifacts into memory."""
        try:
            if all(os.path.exists(p) for p in self.paths.values()):
                self.model = joblib.load(self.paths["model"])
                self.scaler = joblib.load(self.paths["scaler"])
                self.algo_encoder = joblib.load(self.paths["algo_encoder"])
                self.ready = True
                print(f"{Fore.GREEN}✅ Neural Ranker Online. Simulation engine ready.")
            else:
                print(
                    f"{Fore.RED}⚠️ Neural Matrix Offline: Missing .pkl artifacts in /brain folder."
                )
        except Exception as e:
            print(f"{Fore.RED}💥 Neural Link Failed: {e}")

    def _extract_dna(self, df):
        """Calculates the core 10-dimensional DNA signature."""
        if "target" not in df.columns:
            df = df.rename(columns={df.columns[-1]: "target"})

        n_rows, n_cols = df.shape
        feat = df.drop(columns=["target"])
        num_df = feat.select_dtypes(include=[np.number])

        probs = df["target"].value_counts(normalize=True)

        dna = {
            "entropy": scipy_entropy(probs) if len(probs) > 1 else 0.0,
            "imbalance": probs.max() - (1.0 / len(probs)) if len(probs) > 1 else 0.0,
            "kurt": num_df.kurt().fillna(0).mean() if not num_df.empty else 0.0,
            "n_cols": float(n_cols),
            "n_rows": float(n_rows),
            "skew": num_df.skew().fillna(0).mean() if not num_df.empty else 0.0,
            "stability_score": 0.5,
            "null_density": (
                df.isnull().sum().sum() / (n_rows * n_cols) if n_rows > 0 else 0
            ),
            "num_cat_ratio": len(feat.select_dtypes(exclude=[np.number]).columns)
            / n_cols,
            "avg_correlation": 0.0,
        }

        if not num_df.empty and n_rows > 1:
            cv = num_df.std() / (num_df.mean().abs() + 1e-6)
            dna["stability_score"] = (1 / (1 + cv)).mean()
            if len(num_df.columns) > 1:
                corr = num_df.corr().abs()
                dna["avg_correlation"] = corr.values[
                    np.triu_indices_from(corr, k=1)
                ].mean()

        return dna

    def predict_from_csv(self, file_path):
        """Simulates all algorithms to find the optimal solution."""
        if not self.ready:
            return None, 0.0

        try:
            df = pd.read_csv(file_path)
            if df.empty:
                return None, 0.0

            # Step 1: Extract DNA (Core 10 features)
            dna_dict = self._extract_dna(df)
            dna_order = [
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
            dna_vector = [dna_dict[f] for f in dna_order]

            # Step 2: Simulate All 10 Algorithm Categories
            algo_categories = self.algo_encoder.categories_[0]
            leaderboard = []

            for algo in algo_categories:
                # Create One-Hot vector for the algorithm
                algo_encoded = self.algo_encoder.transform([[algo]])[0]

                # Stack DNA + Algorithm Identity
                full_vector = np.hstack([dna_vector, algo_encoded])

                # Scale and Predict F1-Score
                scaled_input = self.scaler.transform([full_vector])
                predicted_f1 = self.model.predict(scaled_input)[0]
                leaderboard.append((algo, predicted_f1))

            # Step 3: Rank and Report
            leaderboard.sort(key=lambda x: x[1], reverse=True)

            print(
                f"\n{Fore.CYAN}📊 ORACLE NEURAL SIMULATION: {os.path.basename(file_path)}"
            )
            print(f"  {'RANK':<5} | {'ALGORITHM':<15} | {'PREDICTED F1'}")
            print(f"  {'-'*40}")
            for rank, (name, score) in enumerate(leaderboard[:3], 1):
                color = Fore.GREEN if rank == 1 else Fore.WHITE
                print(f"  {color}#{rank:<4} | {name:<15} | {score:.4f}")

            winner, top_score = leaderboard[0]
            return winner, top_score

        except Exception as e:
            print(f"{Fore.RED}💥 Oracle Simulation Error: {e}")
            return None, 0.0
