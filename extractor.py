import pandas as pd
import numpy as np
from scipy.stats import skew, kurtosis
from colorama import Fore, Style
from registry import SystemRegistry


def get_dataset_dna(df, target_col):
    """
    Advanced Medical DNA Engine: Extracts high-fidelity statistical markers.
    Now includes: Null Density, Feature Type Ratios, and Internal Correlation.
    """
    # Isolate features and target
    feat = df.drop(columns=[target_col])
    n_rows, n_cols = df.shape

    # Identify data types
    numeric_feat = feat.select_dtypes(include=[np.number])
    categorical_feat = feat.select_dtypes(exclude=[np.number])

    # 1. Class Probabilities (Strictly Binary for this phase)
    probs = df[target_col].value_counts(normalize=True)

    # 2. Advanced Feature: Internal Correlation (Detects redundancy)
    if not numeric_feat.empty and len(numeric_feat.columns) > 1:
        # Calculate mean absolute correlation between numeric features
        corr_matrix = numeric_feat.corr().abs()
        # Take the mean of the upper triangle to avoid self-correlation (1.0)
        upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
        avg_correlation = float(upper.stack().mean())
    else:
        avg_correlation = 0.0

    # 3. Advanced Feature: Missing Value Density
    null_density = float(df.isnull().sum().sum() / (n_rows * n_cols))

    # 4. Advanced Feature: Feature Type Ratio
    num_ratio = float(len(numeric_feat.columns) / n_cols)

    # --- The Expanded DNA Mapping ---
    dna = {
        "n_rows": int(n_rows),
        "n_cols": int(n_cols),
        "imbalance": float(probs.min()),  # How rare is the 'sick' class?
        "skew": (
            float(numeric_feat.apply(lambda x: skew(x.dropna())).mean())
            if not numeric_feat.empty
            else 0.0
        ),
        "kurt": (
            float(numeric_feat.apply(lambda x: kurtosis(x.dropna())).mean())
            if not numeric_feat.empty
            else 0.0
        ),
        "entropy": float(-(probs * np.log2(probs + 1e-9)).sum()),
        "null_density": null_density,
        "num_cat_ratio": num_ratio,
        "avg_correlation": avg_correlation,
    }
    return dna


def run_dna_extraction_pipeline(registry: SystemRegistry):
    """
    The Pipeline Master: Optimized for the 40-dataset Medical specialist objective.
    """
    print(
        f"\n{Fore.MAGENTA}🧬 [SEQUENCE INITIATED] Extracting Medical Data DNA...{Style.RESET_ALL}"
    )

    targets = [
        fid for fid, info in registry.memory.items() if info["state"] == "CLEANED"
    ]

    if not targets:
        print(
            f"{Fore.YELLOW}ℹ️  No new cleaned medical datasets found.{Style.RESET_ALL}"
        )
        return

    warehouse = []

    for fid in targets:
        allowed, msg, _ = registry.check_clearance(fid, "EXTRACTED")
        if not allowed:
            continue

        try:
            clean_path = registry.memory[fid]["metadata"]["clean_path"]
            df = pd.read_csv(clean_path)

            # Execute Extraction
            dna = get_dataset_dna(df, target_col="target")

            # Update Registry with specialized markers
            registry.update(fid, "EXTRACTED", dna)

            # Prepare for Warehouse export
            dna_record = dna.copy()
            dna_record["dataset_id"] = fid
            warehouse.append(dna_record)

            print(
                f"{Fore.GREEN}✨ {fid:<25} -> DNA Encoded. [Imbalance: {dna['imbalance']:.2f}]{Style.RESET_ALL}"
            )

        except Exception as e:
            print(f"{Fore.RED}❌ Failed to encode {fid}: {str(e)}{Style.RESET_ALL}")
            continue

    if warehouse:
        warehouse_df = pd.DataFrame(warehouse)
        # Professional ordering for the specialized study
        cols = [
            "dataset_id",
            "n_rows",
            "n_cols",
            "imbalance",
            "skew",
            "kurt",
            "entropy",
            "null_density",
            "num_cat_ratio",
            "avg_correlation",
        ]
        warehouse_df[cols].to_csv("Specialized_Medical_Warehouse.csv", index=False)
        print(
            f"\n{Fore.CYAN}📂 Specialized Warehouse generated with {len(warehouse)} medical records.{Style.RESET_ALL}"
        )
        print(
            f"{Fore.CYAN}🚀 Data ready for 10-Category Algorithmic Combat.{Style.RESET_ALL}"
        )
