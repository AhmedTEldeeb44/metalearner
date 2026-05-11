import openml
import os
import pandas as pd
from tqdm import tqdm
from colorama import Fore, Style
from .registry import SystemRegistry


def fetch_openml_curated_batch(registry: SystemRegistry, limit: int = 40):
    print(f"\n{Fore.GREEN}--- 🩺 BRUTE-FORCE MEDICAL HARVESTER ---{Style.RESET_ALL}")

    target_folder = "data"
    os.makedirs(target_folder, exist_ok=True)

    print(
        f"{Fore.CYAN}📡 Initializing Deep Scan of OpenML Archives...{Style.RESET_ALL}"
    )

    # 1. Fetching the Master List or Using Fallback
    # OpenML API often times out on list_datasets, so we provide a robust fallback
    known_medical_ids = [13, 15, 25, 37, 38, 43, 49, 51, 53, 55, 77, 140, 164, 267, 336, 337, 446, 466, 481, 844, 1003, 1122, 1123, 1124, 1125, 1126, 1127, 1128, 1129, 1130, 1131, 1132, 1133, 1134, 1135, 1136, 1137, 1138, 31, 1461, 1504, 1510, 1590, 41188, 41189, 41190, 41191]
    
    try:
        print(f"{Fore.CYAN}📡 Attempting to fetch OpenML Master List...{Style.RESET_ALL}")
        df_datasets = openml.datasets.list_datasets(output_format="dataframe")
        
        # --- FIX: Using the correct CamelCase column names ---
        # OpenML uses 'NumberOfClasses' and 'NumberOfInstances'
        binary_df = df_datasets[
            (df_datasets["NumberOfClasses"] == 2) & (df_datasets["NumberOfInstances"] > 100)
        ]
        
        datasets_to_scan = [(int(row["did"]), str(row["name"]).lower()) for _, row in binary_df.iterrows()]
        
        print(
            f"{Fore.BLUE}🔍 Found {len(datasets_to_scan)} potential binary datasets. Filtering for Medical DNA...{Style.RESET_ALL}"
        )
    except Exception as e:
        print(f"{Fore.YELLOW}⚠️ OpenML Server Timeout/Error (504). Falling back to curated offline registry of {len(known_medical_ids)} medical datasets...{Style.RESET_ALL}")
        datasets_to_scan = [(d_id, "") for d_id in known_medical_ids]

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
        for d_id, name in datasets_to_scan:
            if download_count >= limit:
                break

            try:
                # Fetch metadata if name is missing (fallback mode)
                if not name:
                    dataset_meta = openml.datasets.get_dataset(d_id, download_data=False)
                    name = str(dataset_meta.name).lower()

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
