import openml
import pandas as pd
import numpy as np
import os
import time
from colorama import Fore, Style, init
from joblib import Parallel, delayed
from scipy.stats import skew, kurtosis

# --- ACADEMIC INFERENCE ARCHITECTURE ---
from brain_bridge import MetaBrainBridge
from benchmarker import MetaBenchmarker
from registry import SystemRegistry
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import cross_val_score
from sklearn.impute import SimpleImputer

init(autoreset=True)


class GeneralizationStudy:
    def __init__(self):
        # Initializing Persistent Audit Trail
        self.registry = SystemRegistry(path="benchmark_memory.json")
        self.inference_layer = MetaBrainBridge()
        self.validation_suite = MetaBenchmarker(self.registry)

        # Injecting High-Throughput Parallel DNA Engine
        self.inference_layer._extract_dna = self._extract_dna_parallel

    def _extract_dna_parallel(self, df):
        """High-Throughput Meta-Feature Characterization."""
        if "target" not in df.columns:
            df = df.rename(columns={df.columns[-1]: "target"})
        n_rows, n_cols = df.shape
        feat = df.drop(columns=["target"])
        num_df = feat.select_dtypes(include=[np.number])
        probs = df["target"].value_counts(normalize=True)

        def get_col_stats(col):
            c = col.dropna()
            return (float(skew(c)), float(kurtosis(c))) if not c.empty else (0.0, 0.0)

        if not num_df.empty and len(num_df.columns) > 0:
            stats = Parallel(n_jobs=-1, prefer="threads")(
                delayed(get_col_stats)(num_df[c]) for c in num_df.columns
            )
            avg_skew = np.mean([s[0] for s in stats])
            avg_kurt = np.mean([s[1] for s in stats])
        else:
            avg_skew, avg_kurt = 0.0, 0.0

        dna = {
            "entropy": float(-(probs * np.log2(probs + 1e-9)).sum()),
            "imbalance": float(
                probs.max() - (1.0 / len(probs)) if len(probs) > 1 else 0.0
            ),
            "kurt": avg_kurt,
            "n_cols": float(n_cols),
            "n_rows": float(n_rows),
            "skew": avg_skew,
            "stability_score": 0.5,
            "null_density": (
                df.isnull().sum().sum() / (n_rows * n_cols) if n_rows > 0 else 0
            ),
            "num_cat_ratio": len(feat.select_dtypes(exclude=[np.number]).columns)
            / n_cols,
            "avg_correlation": 0.0,
        }
        if not num_df.empty and n_rows > 1 and len(num_df.columns) > 1:
            corr = num_df.corr().abs()
            dna["avg_correlation"] = corr.values[np.triu_indices_from(corr, k=1)].mean()
        return dna

    def execute_robustness_study(self):
        print(
            f"{Fore.MAGENTA}{Style.BRIGHT}🚀 [SYSTEM INITIATED] Executing High-Throughput Generalization Study..."
        )
        try:
            suite = openml.study.get_suite(218)
            total_tasks = len(suite.tasks)
            print(
                f"{Fore.CYAN}📂 Repository: OpenML Study 218 | Identified Tasks: {total_tasks}"
            )
        except Exception as e:
            print(f"{Fore.RED}❌ Repository Access Failed: {e}")
            return

        for idx, task_id in enumerate(suite.tasks, 1):
            try:
                task_id_str = str(task_id)
                if (
                    task_id_str in self.registry.memory
                    and self.registry.memory[task_id_str]["state"] == "BENCHMARKED"
                ):
                    print(
                        f"{Fore.BLUE}🔹 [{idx} of {total_tasks}] Task {task_id}: State Restored."
                    )
                    continue

                print(
                    f"\n{Fore.WHITE}┌── {Fore.CYAN}[{idx} of {total_tasks}]{Fore.WHITE} ─ Task: {Fore.YELLOW}{task_id}"
                )
                task = openml.tasks.get_task(task_id)
                dataset = task.get_dataset()
                dataset_name = (
                    dataset.name
                    if "pentest" not in dataset.name.lower()
                    else f"Task_{task_id}"
                )
                X_raw, y_raw, _, _ = dataset.get_data(
                    target=dataset.default_target_attribute
                )
                print(
                    f"│ 📊 Dataset: {Fore.YELLOW}{dataset_name:<25}{Fore.WHITE} | Shape: {X_raw.shape}"
                )

                # Imputation
                num_cols = X_raw.select_dtypes(include=[np.number])
                cat_cols = X_raw.select_dtypes(exclude=[np.number])

                def pi_safe(df_c, strat):
                    if df_c.empty:
                        return df_c
                    return pd.DataFrame(
                        SimpleImputer(strategy=strat).fit_transform(df_c),
                        columns=df_c.columns,
                    )

                X_imputed = pd.concat(
                    Parallel(n_jobs=-1)(
                        [
                            delayed(pi_safe)(num_cols, "mean"),
                            delayed(pi_safe)(cat_cols, "most_frequent"),
                        ]
                    ),
                    axis=1,
                )
                X_imputed["target"] = y_raw

                # Forecast
                rec, f_f1 = self.generate_performance_forecast(X_imputed)
                print(
                    f"│ 🧠 Oracle Forecast: {Fore.GREEN}{rec:<15} {Fore.WHITE}(Est. F1: {f_f1:.4f})"
                )

                # Validation
                y = LabelEncoder().fit_transform(y_raw.fillna(y_raw.mode()[0]))
                X_feat = X_imputed.drop(columns=["target"])
                X_num = X_feat.select_dtypes(include=[np.number])
                X_v = (
                    StandardScaler().fit_transform(X_num)
                    if not X_num.empty
                    else pd.get_dummies(X_feat).values
                )

                # Memory Guard
                cv_jobs = 1 if (X_v.shape[0] * len(np.unique(y)) > 5_000_000) else -1

                start_t = time.time()
                scores = cross_val_score(
                    self.validation_suite.models[rec],
                    X_v,
                    y,
                    cv=5,
                    scoring="f1_weighted",
                    n_jobs=cv_jobs,
                )
                e_f1 = scores.mean()
                print(
                    f"│ ⚔️  Empirical Trial: {Fore.YELLOW}{e_f1:.4f} {Fore.WHITE}(Time: {time.time()-start_t:.2f}s)"
                )

                self.registry.update(
                    task_id_str,
                    "BENCHMARKED",
                    {
                        "Dataset": dataset_name,
                        "Recommendation": rec,
                        "Forecasted_F1": round(float(f_f1), 4),
                        "Empirical_F1": round(float(e_f1), 4),
                        "Error_Rate": round(abs(float(f_f1) - float(e_f1)), 4),
                    },
                )
                print(f"└─ {Fore.MAGENTA}📦 Audit Trail Updated.")
            except Exception as e:
                print(f"\n│ ⚠️  Task {task_id} Deferred: {e}")



    def generate_performance_forecast(self, df):
        metadata = self.inference_layer._extract_dna(df)
        m_vec = [
            metadata[f]
            for f in [
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
        ]
        cats = self.inference_layer.algo_encoder.categories_[0]

        def pred_a(a):
            v = np.hstack(
                [m_vec, self.inference_layer.algo_encoder.transform([[a]])[0]]
            )
            return (
                a,
                np.clip(
                    self.inference_layer.model.predict(
                        self.inference_layer.scaler.transform([v])
                    )[0],
                    0.0,
                    1.0,
                ),
            )

        res = Parallel(n_jobs=-1)(delayed(pred_a)(a) for a in cats)
        res.sort(key=lambda x: x[1], reverse=True)
        return res[0]




# --- THE BOOT MENU ---
if __name__ == "__main__":
    study = GeneralizationStudy()

    print(f"\n{Fore.YELLOW}{Style.BRIGHT}--- MetaLearner Framework Controller ---")
    print(f"{Fore.WHITE}[1] Start / Resume All-Core Benchmark (39 Tasks)")
    print(f"{Fore.WHITE}[2] Exit")

    choice = input(f"\n{Fore.CYAN}Select an action: ")

    if choice == "1":
        study.execute_robustness_study()
    else:
        print(f"{Fore.WHITE}Exiting...")
