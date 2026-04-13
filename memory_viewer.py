import os
import pandas as pd
from colorama import Fore, Style
from registry import SystemRegistry


class MemoryExplorer:
    def __init__(self, registry: SystemRegistry):
        self.registry = registry

    def _nlp_detect(self, query):
        """Simple NLP intent detection for states and names."""
        query = query.lower()
        states = {
            "downloaded": "DOWNLOADED",
            "raw": "DOWNLOADED",
            "cleaned": "CLEANED",
            "scrubbed": "CLEANED",
            "extracted": "EXTRACTED",
            "dna": "EXTRACTED",
            "benchmarked": "BENCHMARKED",
            "finished": "BENCHMARKED",
            "winner": "BENCHMARKED",
        }

        detected_state = None
        for keyword, state_val in states.items():
            if keyword in query:
                detected_state = state_val
                break

        # Strip common words to find the potential dataset name
        potential_name = (
            query.replace("show", "")
            .replace("me", "")
            .replace("find", "")
            .replace("the", "")
            .replace("datasets", "")
            .replace("data", "")
            .strip()
        )

        return detected_state, potential_name

    def open_console(self):
        while True:
            os.system("cls" if os.name == "nt" else "clear")
            print(f"{Fore.CYAN}{Style.BRIGHT}🔍 METALEARNER NEURAL MEMORY EXPLORER")
            print(f"{Fore.WHITE}Total Records in Synapse: {len(self.registry.memory)}")
            print(f"{Fore.CYAN}═" * 60)

            print(f"\n{Fore.GREEN}COMMAND EXAMPLES:")
            print(f" > 'show 5' | 'find letter' | 'cleaned data' | 'all'")
            print(f" > Type 'exit' to return to menu.")

            user_input = (
                input(f"\n{Fore.YELLOW}Neural Query: {Style.RESET_ALL}").strip().lower()
            )

            if user_input == "exit":
                break

            # 1. Intent Detection
            det_state, det_name = self._nlp_detect(user_input)

            # 2. Filtering Logic
            results = []
            for fid, info in self.registry.memory.items():
                match = False

                # Filter by State
                if det_state and info["state"] == det_state:
                    match = True
                # Filter by Name (Fuzzy)
                if det_name and (det_name in fid.lower()):
                    match = True
                # Show All
                if user_input == "all" or user_input == "":
                    match = True

                if match:
                    results.append(
                        {
                            "ID": fid,
                            "STATE": info["state"],
                            "METADATA": info["metadata"],
                        }
                    )

            # 3. Limit view if numbers are mentioned
            limit = 10
            words = user_input.split()
            for w in words:
                if w.isdigit():
                    limit = int(w)
                    break

            # 4. Visualization (The Hacking Table)
            self._draw_table(results[:limit])
            input(f"\n{Fore.BLACK}{Style.BRIGHT}PRESS [ENTER] TO CLEAR SEARCH...")

    def _draw_table(self, data):
        if not data:
            print(f"\n{Fore.RED}🚫 NO MATCHING SYNAPSES FOUND.")
            return

        print(
            f"\n{Fore.WHITE}{'DATASET ID':<25} │ {'PIPELINE STATE':<15} │ {'DNA SUMMARY'}"
        )
        print(f"{Fore.CYAN}─" * 80)

        for item in data:
            state_color = Fore.GREEN if item["STATE"] == "BENCHMARKED" else Fore.YELLOW

            # Format DNA summary based on state
            meta = item["METADATA"]
            if item["STATE"] == "EXTRACTED" or item["STATE"] == "BENCHMARKED":
                dna = f"Rows: {meta.get('n_rows', '?')} | Ent: {round(meta.get('entropy', 0), 2)}"
            else:
                dna = f"Path: ...{str(meta.get('path', ''))[-20:]}"

            print(
                f"{Fore.WHITE}{item['ID']:<25} │ {state_color}{item['STATE']:<15} {Fore.WHITE}│ {Fore.BLUE}{dna}"
            )
