import pandas as pd
import numpy as np
import os
from colorama import Fore, Style
from registry import SystemRegistry
from sklearn.preprocessing import LabelEncoder


class IntelligentCleaner:
    def __init__(
        self,
        registry: SystemRegistry,
        output_dir="cleaned_datasets",
        dirty_dir="dirty_datasets",
    ):
        self.registry = registry
        self.output_dir = output_dir
        self.dirty_dir = dirty_dir

        # Initialize Research Zones
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.dirty_dir, exist_ok=True)
        self.log_report = []

    def scrub(self, file_id):
        """
        Performs high-level data surgery and triages files.
        PURGE POLICY: Deletes source file after classification is finalized.
        """
        # --- 1. MEMORY SYNC & SECURITY CHECK ---
        allowed, msg, _ = self.registry.check_clearance(file_id, "CLEANED")
        if not allowed:
            print(
                f"{Fore.YELLOW}🛡️  REGISTRY BLOCK: {file_id} -> {msg}{Style.RESET_ALL}"
            )
            return None

        file_path = self.registry.memory[file_id]["metadata"]["path"]
        if not os.name == "nt":  # Path fix for cross-platform stability
            file_path = file_path.replace("\\", "/")

        if not os.path.exists(file_path):
            print(f"{Fore.RED}❌ Source missing: {file_path}{Style.RESET_ALL}")
            return None

        print(f"{Fore.CYAN}🧬 [NEURAL SCAN] Analyzing: {file_id}...{Style.RESET_ALL}")

        try:
            df = pd.read_csv(file_path)

            # --- 2. ZERO-SIZE PROTECTION ---
            if df.empty or df.size == 0:
                self._handle_rejection(
                    file_id, df, "EMPTY_REJECT", "Empty Dataset Detected.", file_path
                )
                return None

            original_rows, original_cols = df.shape

            # --- 3. UNIVERSAL SANITIZATION ---
            df.columns = [
                str(c).strip().lower().replace(" ", "_").replace(".", "_")
                for c in df.columns
            ]

            # --- 4. THE STABILITY INDEX (INTELLIGENCE) ---
            null_ratio = df.isnull().sum().sum() / df.size
            constant_cols = [col for col in df.columns if df[col].nunique() <= 1]

            # Mathematical Stability Formula
            stability_score = (
                1.0 - (null_ratio * 1.5) - (len(constant_cols) / len(df.columns))
            )

            # --- 5. THE TRIAGE GATEKEEPER ---
            if stability_score < 0.6:
                reason = f"Instability Detected (Score: {stability_score:.2f}). Nulls: {null_ratio:.1%}"
                self._handle_rejection(
                    file_id, df, "STABILITY_REJECT", reason, file_path
                )
                return None

            # --- 6. DATA SURGERY (AUTO-REPAIR) ---
            # Step A: Drop useless constant features
            df = df.drop(columns=constant_cols)
            df = df.dropna(axis=1, how="all")

            # Step B: Robust Imputation
            num_cols = df.select_dtypes(include=[np.number]).columns
            df[num_cols] = df[num_cols].fillna(df[num_cols].median())
            cat_cols = [c for c in df.columns if c not in num_cols]
            df[cat_cols] = df[cat_cols].fillna("unknown")

            # --- 7. NUCLEAR ENCODING (The XGBoost Fix) ---
            # We force every non-numeric column into a float/int representation
            le = LabelEncoder()
            for col in df.columns:
                if not pd.api.types.is_numeric_dtype(df[col]):
                    df[col] = le.fit_transform(df[col].astype(str))

                # Special Fix: Target must be 0-indexed (0, 1, 2...) for XGBoost
                if col == "target":
                    df[col] = le.fit_transform(df[col])

            df = df.drop_duplicates()

            # --- 8. FINAL QUALITY VALIDATION ---
            new_rows, new_cols = df.shape
            data_loss = 1 - (new_rows / original_rows) if original_rows > 0 else 0

            if new_rows < 100:
                reason = f"Post-clean row count insufficient: {new_rows}"
                self._handle_rejection(file_id, df, "SIZE_REJECT", reason, file_path)
                return None

            # --- 9. ARCHIVING & REGISTRY UPDATE ---
            clean_path = os.path.join(self.output_dir, f"CLEAN_{file_id}.csv")
            df.to_csv(clean_path, index=False)

            self.registry.update(
                file_id,
                "CLEANED",
                {
                    "clean_path": clean_path,
                    "stability_score": round(stability_score, 3),
                    "data_loss": f"{data_loss:.1%}",
                    "final_features": new_cols,
                    "dropped_constants": len(constant_cols),
                },
            )

            # --- 10. THE PURGE ---
            os.remove(file_path)

            print(
                f"{Fore.GREEN}✅ {file_id} STABILIZED. Source Purged.{Style.RESET_ALL}"
            )
            return clean_path

        except Exception as e:
            self._log(file_id, "SYSTEM_CRASH", str(e))
            print(
                f"{Fore.RED}💥 SYSTEM ERROR during surgery: {str(e)}{Style.RESET_ALL}"
            )
            return None

    def _handle_rejection(self, file_id, df, status, reason, original_path):
        """Helper to quarantine dirty datasets and purge the raw source."""
        dirty_path = os.path.join(self.dirty_dir, f"DIRTY_{file_id}.csv")
        df.to_csv(dirty_path, index=False)
        self.registry.update(
            file_id, "REJECTED", {"reason": reason, "dirty_path": dirty_path}
        )

        if os.path.exists(original_path):
            os.remove(original_path)

        self._log(file_id, status, reason)
        print(
            f"{Fore.RED}⚠️  DATASET REJECTED: {reason}. Quarantined & Purged.{Style.RESET_ALL}"
        )

    def _log(self, name, status, message):
        self.log_report.append(
            {"Dataset": name, "Status": status, "Diagnostics": message}
        )

    def export_report(self):
        report_df = pd.DataFrame(self.log_report)
        report_df.to_csv("cleaning_intelligence_report.csv", index=False)
        print(
            f"\n📑 Intelligence Report Exported. Total Operations: {len(self.log_report)}"
        )
