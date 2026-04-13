import pandas as pd
import os
import numpy as np
from colorama import Fore, Style


class AnalyticsManager:
    def __init__(self, filename="Specialized_Medical_Warehouse.csv"):
        self.filename = filename

    def generate_report(self):
        if not os.path.exists(self.filename):
            print(f"{Fore.RED}❌ ERROR: DATA WAREHOUSE OFFLINE. BUILD CSV FIRST.")
            return

        df = pd.read_csv(self.filename)
        total = len(df)

        if total == 0:
            print(f"{Fore.YELLOW}⚠️  DATABASE EMPTY. NO INTELLIGENCE TO GATHER.")
            return

        # --- HEADER ---
        os.system("cls" if os.name == "nt" else "clear")
        print(
            f"{Fore.GREEN}{Style.BRIGHT}┌────────────────────────────────────────────────────────────┐"
        )
        print(
            f"│ {Fore.WHITE}📊 METALEARNER GLOBAL INTELLIGENCE STATION {total:<10}    {Fore.GREEN}│"
        )
        print(f"└────────────────────────────────────────────────────────────┘")

        # 1. THE WINNERS (Core Stats)
        print(f"\n{Fore.CYAN}⚡ ALGORITHM DOMINANCE MATRIX:")
        winners = df["best_algo"].value_counts()
        for algo, count in winners.items():
            perc = (count / total) * 100
            bar = "█" * int(perc / 2)
            color = (
                Fore.GREEN if "XGBoost" in algo or "Gradient" in algo else Fore.WHITE
            )
            print(f" {Fore.WHITE}{algo:<20} {Fore.CYAN}│ {color}{bar:<50} {perc:.1f}%")

        # 2. SIZE-BASED INTELLIGENCE (The "Hacking" Logic)
        print(f"\n{Fore.MAGENTA}🧬 SECTOR ANALYSIS (Winners by Dataset Size):")
        # Define Small < 10k rows, Medium < 100k, Large > 100k
        small_wins = df[df["n_rows"] < 10000]["best_algo"].mode().tolist()
        large_wins = df[df["n_rows"] >= 100000]["best_algo"].mode().tolist()

        s_win = small_wins[0] if small_wins else "N/A"
        l_win = large_wins[0] if large_wins else "N/A"

        print(f" 📁 {Fore.WHITE}Small Datasets (<10k)  : {Fore.YELLOW}{s_win}")
        print(f" 🏢 {Fore.WHITE}Large Datasets (>100k) : {Fore.RED}{l_win}")

        # 3. COMBAT EFFICIENCY (Time vs Accuracy)
        print(f"\n{Fore.YELLOW}⚔️  COMBAT EFFICIENCY (Avg. Training Time):")
        time_cols = [c for c in df.columns if c.startswith("time_")]
        if time_cols:
            avg_times = df[time_cols].mean().sort_values()
            for col, t in avg_times.items():
                name = col.replace("time_", "")
                t_bar = "▰" * int(t * 2) if t < 25 else "▰" * 25  # Cap visual bar
                print(f" {Fore.WHITE}{name:<20} {Fore.YELLOW}{t:>6.2f}s │ {t_bar}")

        # 4. DATA DNA OVERVIEW
        print(f"\n{Fore.BLUE}📡 GLOBAL DATASET DNA:")
        avg_acc = df["accuracy_score"].mean()
        avg_entropy = df["entropy"].mean() if "entropy" in df.columns else 0
        avg_imb = df["imbalance"].mean() if "imbalance" in df.columns else 0

        print(f" 🎯 {Fore.WHITE}Global Accuracy  : {Fore.GREEN}{avg_acc:.2%}")
        print(
            f" 🌪️  {Fore.WHITE}Avg. Complexity  : {Fore.CYAN}{avg_entropy:.2f} (Entropy)"
        )
        print(f" ⚖️  {Fore.WHITE}Avg. Imbalance   : {Fore.CYAN}{avg_imb:.2f}")

        # --- FOOTER ---
        print(
            f"\n{Fore.GREEN}┌────────────────────────────────────────────────────────────┐"
        )
        print(
            f"│ {Fore.WHITE}SCAN COMPLETE. SYSTEM STANDBY.                             {Fore.GREEN}│"
        )
        print(f"└────────────────────────────────────────────────────────────┘")
        input(
            f"\n{Fore.BLACK}{Style.BRIGHT}PRESS [ENTER] TO DISCONNECT...{Style.RESET_ALL}"
        )
