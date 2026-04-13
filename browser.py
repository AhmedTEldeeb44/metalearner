import os
from colorama import Fore, Style
from brain_bridge import MetaBrainBridge


class BronzeBrowser:
    def __init__(self, bridge: MetaBrainBridge):
        self.bridge = bridge
        self.raw_folder = "data"

    def open_browser(self):
        """Interactive terminal UI to browse and test raw datasets."""
        if not os.path.exists(self.raw_folder):
            print(f"{Fore.RED}❌ Error: Raw data folder '{self.raw_folder}' not found.")
            return

        # Get all CSV files in the raw folder
        files = [f for f in os.listdir(self.raw_folder) if f.endswith(".csv")]

        if not files:
            print(f"{Fore.YELLOW}ℹ️ No raw datasets found in the books yet.")
            return

        while True:
            print(f"\n{Fore.CYAN}--- 🧪 BRONZE DATASET BROWSER ---{Style.RESET_ALL}")
            print(f"Total Raw Files: {len(files)}")
            print("-" * 40)

            # Display files with indices
            for idx, file in enumerate(files, 1):
                print(f" [{Fore.YELLOW}{idx}{Style.RESET_ALL}] {file}")

            print(f" [{Fore.RED}0{Style.RESET_ALL}] Return to Command Center")

            choice = input(
                f"\n{Fore.GREEN}Select Dataset to Test: {Style.RESET_ALL}"
            ).strip()

            if choice == "0":
                break

            try:
                file_idx = int(choice) - 1
                if 0 <= file_idx < len(files):
                    selected_file = files[file_idx]
                    full_path = os.path.join(self.raw_folder, selected_file)

                    print(
                        f"\n{Fore.MAGENTA}📡 Analyzing Raw DNA: {selected_file}...{Style.RESET_ALL}"
                    )

                    # Run Oracle prediction on the uncleaned file
                    winner, confidence = self.bridge.predict_from_csv(full_path)

                    if winner:
                        print(f"┌──────────────────────────────────────────┐")
                        print(f"  🏆 ORACLE PREDICTION (BRONZE)")
                        print(f"  Target: {Fore.YELLOW}{selected_file}{Fore.WHITE}")
                        print(f"  Result: {Fore.GREEN}{winner}{Fore.WHITE}")
                        print(f"  Confidence: {Fore.CYAN}{confidence:.2%}{Fore.WHITE}")
                        print(f"└──────────────────────────────────────────┘")
                        input(f"\n{Fore.WHITE}Press Enter to continue browsing...")
                else:
                    print(f"{Fore.RED}🚫 Invalid index.")
            except ValueError:
                print(f"{Fore.RED}🚫 Please enter a number.")
