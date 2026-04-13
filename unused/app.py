import pandas as pd
import numpy as np
import warnings
import time
import os
from datetime import timedelta
from sklearn.model_selection import cross_validate
from sklearn.preprocessing import StandardScaler, LabelEncoder
from colorama import Fore, Style

# --- 10-CATEGORY ARSENAL ---
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from xgboost import XGBClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

from registry import SystemRegistry

# --- SILENCE THE NOISE ---
warnings.filterwarnings("ignore")


class MetaBenchmarker:
    def __init__(self, registry: SystemRegistry):
        self.registry = registry
        # 10 Algorithms representing 10 unique mathematical approaches
        self.models = {
            "Linear": LogisticRegression(max_iter=2000, n_jobs=-1),
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
        targets = [
            fid
            for fid, info in self.registry.memory.items()
            if info["state"] == "EXTRACTED"
        ]
        total_targets = len(targets)

        if not total_targets:
            print(f"{Fore.BLUE}ℹ️  No new extracted medical datasets found for combat.")
            return

        print(
            f"\n{Fore.YELLOW}⚔️  [SPECIALIZED COMBAT] Benchmarking {total_targets} Medical Datasets...{Style.RESET_ALL}"
        )

        # Metrics to track for high-quality medical research
        scoring = {"acc": "accuracy", "prec": "precision", "rec": "recall", "f1": "f1"}

        phase_start_time = time.time()
        for idx, fid in enumerate(targets, 1):
            allowed, _, _ = self.registry.check_clearance(fid, "BENCHMARKED")
            if not allowed:
                continue

            phase_elapsed = time.time() - phase_start_time
            eta_display = (
                f"{Fore.MAGENTA}{str(timedelta(seconds=int((phase_elapsed/idx)*(total_targets-idx))))}"
                if idx > 1
                else "Estimating..."
            )

            print(
                f"\n{Fore.WHITE}┌── {Fore.CYAN}[Target {idx} of {total_targets}]{Fore.WHITE} ────────────────────────"
            )
            print(f"│ 🚀 Medical ID : {Fore.YELLOW}{fid}{Style.RESET_ALL}")
            print(
                f"│ ⏱️  Total Time : {Fore.GREEN}{str(timedelta(seconds=int(phase_elapsed)))}{Fore.WHITE} | ETA: {eta_display}{Style.RESET_ALL}"
            )
            print(f"└──────────────────────────────────────────────────────────")

            try:
                path = self.registry.memory[fid]["metadata"]["clean_path"]
                df = pd.read_csv(path)
                X = df.drop(columns=["target"])
                y = LabelEncoder().fit_transform(df["target"])  # Strict Binary Encoding

                X_scaled = StandardScaler().fit_transform(X)

                results = {}
                ds_start = time.time()

                for m_idx, (name, model) in enumerate(self.models.items(), 1):
                    print(
                        f"   [{m_idx}/10] ⚔️  Testing {Fore.CYAN}{name:<15}{Style.RESET_ALL}",
                        end="\r",
                    )

                    try:
                        algo_start = time.time()
                        # Cross-validate for multiple metrics
                        cv_res = cross_validate(
                            model, X_scaled, y, cv=5, scoring=scoring, n_jobs=-1
                        )

                        duration = time.time() - algo_start

                        results[name] = {
                            "acc": cv_res["test_acc"].mean(),
                            "prec": cv_res["test_prec"].mean(),
                            "rec": cv_res["test_rec"].mean(),
                            "f1": cv_res["test_f1"].mean(),
                            "time": duration,
                        }

                        color = Fore.GREEN if results[name]["acc"] > 0.8 else Fore.WHITE
                        print(
                            f"   🔹 {name:<15}: {color}{results[name]['acc']:>7.2%} Acc | {results[name]['f1']:>7.2%} F1 ({duration:.2f}s)   "
                        )

                    except MemoryError:
                        print(
                            f"   ⚠️  {Fore.RED}{name:<15}: [RAM FAIL] Skipping...               "
                        )
                        results[name] = {
                            "acc": 0,
                            "prec": 0,
                            "rec": 0,
                            "f1": 0,
                            "time": 0,
                        }

                # Determine Winner based on F1-Score (Better for Medical than Accuracy)
                best_algo = max(results, key=lambda k: results[k]["f1"])

                # Update Registry
                meta = {
                    "accuracy_score": round(results[best_algo]["acc"], 4),
                    "f1_score": round(results[best_algo]["f1"], 4),
                    "total_battle_time": round(time.time() - ds_start, 2),
                    "best_algo": best_algo,
                }

                # Store all sub-metrics for the Brain's training
                for name in self.models.keys():
                    meta[f"score_{name}"] = round(results[name]["acc"], 4)
                    meta[f"f1_{name}"] = round(results[name]["f1"], 4)
                    meta[f"time_{name}"] = round(results[name]["time"], 3)

                self.registry.update(fid, "BENCHMARKED", meta)
                print(
                    f"   {Fore.YELLOW}🏆 WINNER: {Style.BRIGHT}{best_algo} {Style.RESET_ALL}(F1: {meta['f1_score']:.2%})"
                )

            except Exception as e:
                print(f"\n{Fore.RED}💥 Benchmark Failed: {e}{Style.RESET_ALL}")

    def generate_final_warehouse(self, filename="Specialized_Medical_Warehouse.csv"):
        """Syncs the deep DNA and performance metrics into the Final Warehouse."""
        final_data = []
        for fid, info in self.registry.memory.items():
            if info["state"] == "BENCHMARKED":
                row = info["metadata"].copy()
                row["dataset_id"] = fid
                final_data.append(row)

        if not final_data:
            print(f"{Fore.RED}⚠️ No benchmarked data available.")
            return

        df = pd.DataFrame(final_data)

        # Logical column organization
        score_cols = sorted(
            [c for c in df.columns if c.startswith("score_") or c.startswith("f1_")]
        )
        time_cols = sorted([c for c in df.columns if c.startswith("time_")])
        meta_cols = [
            "dataset_id",
            "total_battle_time",
            "accuracy_score",
            "f1_score",
            "best_algo",
        ]
        dna_cols = sorted(
            [c for c in df.columns if c not in (score_cols + time_cols + meta_cols)]
        )

        df = df[
            ["dataset_id"]
            + dna_cols
            + score_cols
            + time_cols
            + ["total_battle_time", "accuracy_score", "f1_score", "best_algo"]
        ]

        while True:
            try:
                df.to_csv(filename, index=False)
                print(
                    f"\n{Fore.GREEN}📦 MEDICAL WAREHOUSE UPDATED: '{filename}' ({len(df)} Records)"
                )
                break
            except PermissionError:
                print(
                    f"\n{Fore.RED}🚫 ACCESS DENIED: Close the CSV in Excel and press Enter."
                )
                if input("Retry? (y/n): ").lower() != "y":
                    break
