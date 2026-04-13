import pandas as pd
import os
from colorama import Fore, Style
from downloader import fetch_openml_curated_batch
from cleaner import IntelligentCleaner
from extractor import run_dna_extraction_pipeline


class TestSandbox:
    def __init__(self, main_registry):
        self.registry = main_registry
        self.test_warehouse_path = "Test_Meta_Warehouse.csv"
        # Ensure folders exist
        os.makedirs("test_suite/cleaned", exist_ok=True)

    def harvest_test_batch(self):
        """
        Downloads a new batch of data using the existing downloader.
        Removed the 'n' parameter to match the function signature in downloader.py.
        """
        print(
            f"\n{Fore.MAGENTA}🧪 [SANDBOX] Harvesting Test Datasets...{Style.RESET_ALL}"
        )

        # Calling without 'n=' keyword to resolve the TypeError
        fetch_openml_curated_batch(self.registry)

        print(
            f"{Fore.CYAN}✅ Test data successfully pulled into the local 'data/' directory."
        )

    def process_test_suite(self):
        """Cleans and extracts DNA without touching the main warehouse."""
        targets = [
            f for f, i in self.registry.memory.items() if i["state"] == "DOWNLOADED"
        ]

        if not targets:
            print(
                f"{Fore.RED}⚠️ No fresh test data found in 'DOWNLOADED' state. Harvest first."
            )
            return

        print(
            f"\n{Fore.YELLOW}🛡️  Surgical Scrubbing (Sandbox Mode)...{Style.RESET_ALL}"
        )
        cleaner = IntelligentCleaner(self.registry)
        for fid in targets:
            cleaner.scrub(fid)

        print(f"\n{Fore.CYAN}🧬 Extracting Test DNA...{Style.RESET_ALL}")
        run_dna_extraction_pipeline(self.registry)

        # Generate the temporary Test Warehouse
        self.generate_test_warehouse()

    def generate_test_warehouse(self):
        """Writes current 'EXTRACTED' states into the Test Warehouse CSV."""
        test_data = []
        for fid, info in self.registry.memory.items():
            if info["state"] == "EXTRACTED":
                row = info["metadata"].copy()
                row["dataset_id"] = fid
                test_data.append(row)

        if test_data:
            pd.DataFrame(test_data).to_csv(self.test_warehouse_path, index=False)
            print(
                f"{Fore.GREEN}📦 TEST WAREHOUSE UPDATED: '{self.test_warehouse_path}'"
            )

    def merge_to_main(self):
        """Officially merges the Test Warehouse into the main Final_Meta_Warehouse.csv."""
        if not os.path.exists(self.test_warehouse_path):
            print(f"{Fore.RED}⚠️ No Test Warehouse found to merge.")
            return

        print(
            f"\n{Fore.GREEN}🔄 MERGING TEST DATA INTO PERMANENT WAREHOUSE...{Style.RESET_ALL}"
        )

        main_file = "Final_Meta_Warehouse.csv"
        if os.path.exists(main_file):
            main_df = pd.read_csv(main_file)
            test_df = pd.read_csv(self.test_warehouse_path)

            # Combine and remove any duplicate dataset IDs
            combined = pd.concat([main_df, test_df], ignore_index=True).drop_duplicates(
                subset=["dataset_id"]
            )
            combined.to_csv(main_file, index=False)
            print(f"{Fore.CYAN}✅ {len(test_df)} records merged into {main_file}")
        else:
            # If main file doesn't exist yet, simply rename the test file
            os.rename(self.test_warehouse_path, main_file)
            print(f"{Fore.CYAN}✅ Test Warehouse promoted to Main Warehouse.")

        # Cleanup temporary file
        if os.path.exists(self.test_warehouse_path):
            os.remove(self.test_warehouse_path)
