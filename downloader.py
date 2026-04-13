import openml
import os
import pandas as pd
from tqdm import tqdm
from colorama import Fore, Style
from registry import SystemRegistry


def fetch_openml_curated_batch(registry: SystemRegistry):
    print(f"\n{Fore.GREEN}--- 🩺 BRUTE-FORCE MEDICAL HARVESTER ---{Style.RESET_ALL}")

    target_folder = "data"
    os.makedirs(target_folder, exist_ok=True)

    try:
        limit = int(
            input(
                f"{Fore.YELLOW}How many medical datasets? (Target 40): {Style.RESET_ALL}"
            )
        )
    except:
        limit = 40

    print(
        f"{Fore.CYAN}📡 Initializing Deep Scan of OpenML Archives...{Style.RESET_ALL}"
    )

    # 1. Fetching the Master List
    df_datasets = openml.datasets.list_datasets(output_format="dataframe")

    # --- FIX: Using the correct CamelCase column names ---
    # OpenML uses 'NumberOfClasses' and 'NumberOfInstances'
    binary_df = df_datasets[
        (df_datasets["NumberOfClasses"] == 2) & (df_datasets["NumberOfInstances"] > 100)
    ]

    print(
        f"{Fore.BLUE}🔍 Found {len(binary_df)} potential binary datasets. Filtering for Medical DNA...{Style.RESET_ALL}"
    )

    medical_keywords = [
        "medical",
        "patient",
        "disease",
        "cancer",
        "diabetes",
        "heart",
        "health",
        "blood",
        "tumor",
        "clinical",
        "diagnosis",
        "bio",
        "liver",
        "kidney",
    ]

    download_count = 0

    # 2. Scanning for Medical DNA
    with tqdm(total=limit, desc="🧬 Extraction") as pbar:
        for _, row in binary_df.iterrows():
            if download_count >= limit:
                break

            try:
                name = str(row["name"]).lower()
                d_id = int(row["did"])

                # Check for keywords in the name first
                is_medical = any(word in name for word in medical_keywords)

                # If name isn't enough, fetch metadata for description check
                if not is_medical:
                    dataset_meta = openml.datasets.get_dataset(
                        d_id, download_data=False
                    )
                    if any(
                        word in dataset_meta.description.lower()
                        for word in medical_keywords
                    ):
                        is_medical = True

                if not is_medical:
                    continue

                clean_id = name.replace(" ", "_").replace(".", "_")

                # Registry Clearance Check
                allowed, _, _ = registry.check_clearance(clean_id, "DOWNLOADED")
                if not allowed:
                    continue

                # Actual Download
                dataset = openml.datasets.get_dataset(d_id)
                X, y, _, attr = dataset.get_data(
                    target=dataset.default_target_attribute
                )

                if X is None:
                    continue

                df = pd.DataFrame(X, columns=attr)
                df["target"] = y

                path = f"{target_folder}/{clean_id}.csv"
                df.to_csv(path, index=False)

                registry.update(
                    clean_id,
                    "DOWNLOADED",
                    {
                        "path": path,
                        "url": f"https://www.openml.org/d/{d_id}",
                        "domain": "medical",
                    },
                )

                download_count += 1
                pbar.update(1)

            except Exception:
                continue

    print(
        f"\n{Fore.CYAN}🏆 HARVEST COMPLETE. {download_count} SPECIALIZED DATASETS SECURED."
    )
