import os
from colorama import Fore, Style
from downloader import fetch_openml_curated_batch
from cleaner import IntelligentCleaner
from extractor import run_dna_extraction_pipeline
from benchmarker import MetaBenchmarker


def run_smart_mode(registry, start_phase):
    """
    The Autopilot Logic: Executes the pipeline from a specific point to the end.
    """
    print(
        f"\n{Fore.CYAN}{Style.BRIGHT}🚀 [SMART MODE ACTIVATED] Initializing Autopilot Sequence...{Style.RESET_ALL}"
    )

    try:
        # --- PHASE 1: HARVESTING ---
        if start_phase == 1:
            fetch_openml_curated_batch(registry)

        # --- PHASE 2: SURGICAL SCRUBBING ---
        if start_phase <= 2:
            targets = [
                f for f, i in registry.memory.items() if i["state"] == "DOWNLOADED"
            ]
            if targets:
                print(
                    f"\n{Fore.MAGENTA}--- 🤖 [AUTO] PHASE 2: SURGICAL SCRUBBING ({len(targets)} files) ---{Style.RESET_ALL}"
                )
                cleaner = IntelligentCleaner(registry)
                for fid in targets:
                    cleaner.scrub(fid)
                cleaner.export_report()
            else:
                print(
                    f"{Fore.WHITE}ℹ️  Smart Mode: No raw data to scrub. Skipping to next phase."
                )

        # --- PHASE 3: GENETIC SEQUENCING ---
        if start_phase <= 3:
            targets = [f for f, i in registry.memory.items() if i["state"] == "CLEANED"]
            if targets:
                print(
                    f"\n{Fore.MAGENTA}--- 🤖 [AUTO] PHASE 3: GENETIC SEQUENCING ({len(targets)} files) ---{Style.RESET_ALL}"
                )
                run_dna_extraction_pipeline(registry)
            else:
                print(
                    f"{Fore.WHITE}ℹ️  Smart Mode: No cleaned data to sequence. Skipping to next phase."
                )

        # --- PHASE 4: MULTI-THREADED COMBAT ---
        if start_phase <= 4:
            targets = [
                f for f, i in registry.memory.items() if i["state"] == "EXTRACTED"
            ]
            if targets:
                print(
                    f"\n{Fore.MAGENTA}--- 🤖 [AUTO] PHASE 4: MULTI-THREADED COMBAT ({len(targets)} files) ---{Style.RESET_ALL}"
                )
                benchmarker = MetaBenchmarker(registry)
                benchmarker.run_benchmarks()
                benchmarker.generate_final_warehouse()
            else:
                print(f"{Fore.WHITE}ℹ️  Smart Mode: No DNA sequences found for combat.")

        print(
            f"\n{Fore.GREEN}{Style.BRIGHT}🏆 [SMART MODE COMPLETE] The MetaLearner has finished all automated tasks.{Style.RESET_ALL}"
        )

    except Exception as e:
        print(f"\n{Fore.RED}💥 SMART MODE KERNEL ERROR: {e}{Style.RESET_ALL}")
        registry.save()
