import pandas as pd
import numpy as np
import warnings
import time
import os
import sys
from datetime import timedelta
from colorama import Fore, Style

# --- CORE ARSENAL ---
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

from sklearn.model_selection import cross_validate
from sklearn.preprocessing import StandardScaler, LabelEncoder
from registry import SystemRegistry

# --- SILENCE THE NOISE ---
warnings.filterwarnings("ignore")


class MetaBenchmarker:
    def __init__(self, registry: SystemRegistry):
        self.registry = registry

        # 10 Algorithms representing 10 unique mathematical approaches
        self.models = {
            "Linear": LogisticRegression(max_iter=3000, n_jobs=-1),
            "Instance": KNeighborsClassifier(n_jobs=-1),
            "S_Vector": SVC(probability=True, kernel="rbf"),
            "Bayes": GaussianNB(),
            "Tree": DecisionTreeClassifier(max_depth=15),
            "Bagging": RandomForestClassifier(n_jobs=-1, n_estimators=100),
            "Boosting": XGBClassifier(eval_metric="logloss", n_jobs=-1),
            "Neural": MLPClassifier(hidden_layer_sizes=(100, 50), max_iter=500),
            "Discriminant": LinearDiscriminantAnalysis(),
            "Stochastic": SGDClassifier(loss="log_loss", n_jobs=-1),
        }

    def run_benchmarks(self):
        """Executes combat with atomic algorithm-level resuming and incremental saving."""
        unsorted_targets = []
        for fid, info in self.registry.memory.items():
            # Include both new and partially completed datasets
            if info["state"] in ["EXTRACTED", "BENCHMARKED"]:
                meta = info.get("metadata", {})
                complexity = meta.get("n_rows", 0) * meta.get("n_cols", 0)
                unsorted_targets.append({"id": fid, "complexity": complexity})

        if not unsorted_targets:
            print(f"{Fore.BLUE}ℹ️  No datasets found for combat.")
            return

        # Sort by complexity (Ascending) to maintain momentum
        sorted_targets = sorted(unsorted_targets, key=lambda x: x["complexity"])
        targets = [t["id"] for t in sorted_targets]
        total_targets = len(targets)

        print(
            f"\n{Fore.YELLOW}⚔️  [META-LEARNER ACTIVE] Benchmarking {total_targets} Datasets..."
        )
        print(
            f"{Fore.CYAN}💡 HINT: Press Ctrl+C to safely halt. State is saved per algorithm.{Style.RESET_ALL}"
        )

        scoring = {"acc": "accuracy", "prec": "precision", "rec": "recall", "f1": "f1"}
        phase_start_time = time.time()

        try:
            for idx, fid in enumerate(targets, 1):
                metadata = self.registry.memory[fid].get("metadata", {})

                # Header Readout
                phase_elapsed = time.time() - phase_start_time
                print(
                    f"\n{Fore.WHITE}┌── {Fore.CYAN}[Target {idx} of {total_targets}]{Fore.WHITE} ─"
                )
                print(
                    f"│ 🚀 ID: {Fore.YELLOW}{fid}{Fore.WHITE} | ⏱️  Elapsed: {Fore.GREEN}{str(timedelta(seconds=int(phase_elapsed)))}{Style.RESET_ALL}"
                )

                # Load Clean Data
                path = metadata.get("clean_path")
                if not path or not os.path.exists(path):
                    print(
                        f"│ {Fore.RED}❌ Error: Clean path missing. Skipping.{Style.RESET_ALL}"
                    )
                    continue

                df = pd.read_csv(path)
                X = df.drop(columns=["target"])
                y = LabelEncoder().fit_transform(df["target"])
                X_scaled = StandardScaler().fit_transform(X)

                results = {}
                ds_start = time.time()

                # Inner Loop: Atomic Algorithm Combat
                for m_idx, (category, model) in enumerate(self.models.items(), 1):

                    # 1. ATOMIC RESUME CHECK (Check if this specific algo is done)
                    existing_f1 = metadata.get(f"f1_{category}", 0)
                    if existing_f1 > 0:
                        print(
                            f"   🔹 {category:<15}: {Fore.BLUE}[RESUMED] Existing F1: {existing_f1:.2%}"
                        )
                        results[category] = {
                            "acc": metadata.get(f"score_{category}", 0),
                            "f1": existing_f1,
                            "time": metadata.get(f"time_{category}", 0),
                        }
                        continue

                    # 2. CALCULATION
                    print(
                        f"   [{m_idx}/10] ⚔️  Deploying {Fore.CYAN}{category:<15}{Style.RESET_ALL}",
                        end="\r",
                    )

                    try:
                        algo_start = time.time()
                        # Memory Optimization: n_jobs=1 for massive files to prevent RAM lock
                        current_jobs = -1 if len(df) < 50000 else 1

                        cv_res = cross_validate(
                            model,
                            X_scaled,
                            y,
                            cv=5,
                            scoring=scoring,
                            n_jobs=current_jobs,
                        )
                        duration = time.time() - algo_start

                        results[category] = {
                            "acc": cv_res["test_acc"].mean(),
                            "f1": cv_res["test_f1"].mean(),
                            "time": duration,
                        }

                        color = (
                            Fore.GREEN if results[category]["f1"] > 0.8 else Fore.WHITE
                        )
                        print(
                            f"   🔹 {category:<15}: {color}{results[category]['acc']:>7.2%} Acc | {results[category]['f1']:>7.2%} F1 ({duration:.2f}s)  "
                        )

                        # Partial Save: Update registry per algorithm for 'Ironclad' safety
                        metadata[f"score_{category}"] = round(
                            results[category]["acc"], 4
                        )
                        metadata[f"f1_{category}"] = round(results[category]["f1"], 4)
                        metadata[f"time_{category}"] = round(
                            results[category]["time"], 3
                        )
                        self.registry.save()

                    except Exception as e:
                        print(
                            f"   🔹 {category:<15}: {Fore.RED}CALC_ERROR ({str(e)[:40]})"
                        )
                        results[category] = {"acc": 0, "f1": 0, "time": 0}

                # 3. CONCLUDE DATASET
                best_cat = max(results, key=lambda k: results[k]["f1"])
                metadata.update(
                    {
                        "accuracy_score": round(results[best_cat]["acc"], 4),
                        "f1_score": round(results[best_cat]["f1"], 4),
                        "total_battle_time": round(time.time() - ds_start, 2),
                        "best_algo": best_cat,
                    }
                )

                # Sync Registry and Warehouse
                self.registry.update(fid, "BENCHMARKED", metadata)
                self.generate_final_warehouse()

                print(
                    f"   {Fore.YELLOW}🏆 WINNER: {Style.BRIGHT}{best_cat} (F1: {metadata['f1_score']:.2%})"
                )
                print(
                    f"   {Fore.MAGENTA}📦 WAREHOUSE SYNCED SUCCESSFULLY.{Style.RESET_ALL}"
                )

        except KeyboardInterrupt:
            print(
                f"\n\n{Fore.RED}🛑 INTERRUPT DETECTED. SAFE-SAVING SYSTEM STATE...{Style.RESET_ALL}"
            )
            self.registry.save()
            self.generate_final_warehouse()
            sys.exit(0)

    def generate_final_warehouse(self, filename="Specialized_Medical_Warehouse.csv"):
        """
        Transforms wide registry data into a Long-Format Meta-Dataset (10 rows per ID).
        Optimized for Meta-ML Training.
        """
        long_data = []

        for fid, info in self.registry.memory.items():
            if info["state"] == "BENCHMARKED":
                meta = info["metadata"]

                # DNA remains constant for all 10 trials of a single dataset
                dna_features = {
                    k: v
                    for k, v in meta.items()
                    if not k.startswith(("score_", "f1_", "time_")) and k != "best_algo"
                }

                for algo_name in self.models.keys():
                    row = {
                        "dataset_id": fid,
                        "tested_algo": algo_name,
                        "is_best": 1 if meta.get("best_algo") == algo_name else 0,
                        "algo_label": (
                            f"{algo_name} (best)"
                            if meta.get("best_algo") == algo_name
                            else algo_name
                        ),
                        "current_acc": meta.get(f"score_{algo_name}", 0),
                        "current_f1": meta.get(f"f1_{algo_name}", 0),
                        "current_time": meta.get(f"time_{algo_name}", 0),
                    }
                    row.update(dna_features)

                    # Provide 'Relational Context' (how did others do?)
                    for other_algo in self.models.keys():
                        row[f"ref_f1_{other_algo}"] = meta.get(f"f1_{other_algo}", 0)

                    long_data.append(row)

        if not long_data:
            return

        df = pd.DataFrame(long_data)

        # Columns Organization: Identity -> Trial Result -> DNA Features -> Contextual Stats
        identity_cols = ["dataset_id", "tested_algo", "is_best", "algo_label"]
        metrics_cols = ["current_acc", "current_f1", "current_time"]
        dna_cols = sorted([c for c in dna_features.keys() if c not in identity_cols])
        ref_cols = sorted([c for c in df.columns if c.startswith("ref_f1_")])

        ordered_columns = identity_cols + metrics_cols + dna_cols + ref_cols
        df = df[[c for c in ordered_columns if c in df.columns]]

        try:
            df.to_csv(filename, index=False)
        except PermissionError:
            pass  # Fails gracefully if user has Excel open
