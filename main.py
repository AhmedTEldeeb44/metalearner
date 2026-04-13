import os
import sys
import importlib
from datetime import datetime
from colorama import Fore, Style, init, Back

# --- MODULE NAMESPACES (Required for Hot-Reload) ---
import registry
import downloader
import cleaner
import extractor
import benchmarker
import smart_mode
import brain_bridge
import analytics
import memory_viewer
import browser

init(autoreset=True)


def print_header():
    """Renders the Project ASCII Header and Clears the Terminal."""
    os.system("cls" if os.name == "nt" else "clear")

    # Top decorative border
    print(f"{Fore.CYAN}{Style.BRIGHT}╔{'═' * 78}╗")
    print(
        f"{Fore.CYAN}{Style.BRIGHT}║{Fore.WHITE}{Style.BRIGHT}{'METALEARNER v2.0':^78}{Fore.CYAN}{Style.BRIGHT}║"
    )
    print(f"{Fore.CYAN}{Style.BRIGHT}╠{'═' * 78}╣")

    # ASCII Art with gradient effect
    ascii_lines = [
        r"  __  __ ______ _______       _      ______       _____  _   _ ______ _____  ",
        r" |  \/  |  ____|__   __|/\   | |    |  ____|/\   |  __ \| \ | |  ____|  __ \ ",
        r" | \  / | |__     | |  /  \  | |    | |__  /  \  | |__) |  \| | |__  | |__) |",
        r" | |\/| |  __|    | | / /\ \ | |    |  __|/ /\ \ |  _  /| . ` |  __| |  _  / ",
        r" | |  | | |____   | |/ ____ \| |____| |__/ ____ \| | \ \| |\  | |____| | \ \ ",
        r" |_|  |_|______|  |_/_/    \_\______|____/_/    \_\_|  \_\_| \_|______|_|  \_\ ",
    ]

    colors = [Fore.CYAN, Fore.BLUE, Fore.MAGENTA, Fore.CYAN, Fore.BLUE, Fore.MAGENTA]
    for i, line in enumerate(ascii_lines):
        print(
            f"{Fore.CYAN}{Style.BRIGHT}║{colors[i]}{Style.BRIGHT}{line}{Fore.CYAN}{Style.BRIGHT}║"
        )

    print(f"{Fore.CYAN}{Style.BRIGHT}╠{'═' * 78}╣")
    print(
        f"{Fore.CYAN}{Style.BRIGHT}║{Fore.YELLOW}{Style.BRIGHT}{'⚡ NEURAL ARCHITECTURE v3.0 ⚡':^78}{Fore.CYAN}{Style.BRIGHT}║"
    )
    print(
        f"{Fore.CYAN}{Style.BRIGHT}║{Fore.WHITE}{f'Architect: MR. AHMED | Session: {datetime.now().strftime("%Y-%m-%d %H:%M")}':^78}{Fore.CYAN}{Style.BRIGHT}║"
    )
    print(f"{Fore.CYAN}{Style.BRIGHT}╚{'═' * 78}╝{Style.RESET_ALL}\n")


def create_progress_bar(value, max_value, width=20, color=Fore.GREEN):
    """Creates a visual progress bar."""
    filled = int((value / max_value) * width) if max_value > 0 else 0
    bar = "█" * filled + "░" * (width - filled)
    percentage = f"{(value/max_value*100):.1f}%" if max_value > 0 else "0.0%"
    return f"{color}{bar}{Style.RESET_ALL} {Fore.WHITE}{percentage}"


def display_menu(status, registry_len, brain_ready):
    """Prints the current pipeline state and all available commands with enhanced visuals."""

    # Pipeline Status Panel
    print(f"\n{Fore.CYAN}{Style.BRIGHT}┌{'─' * 78}┐")
    print(
        f"{Fore.CYAN}{Style.BRIGHT}│{Fore.WHITE}{Style.BRIGHT}{' 📊 PIPELINE STATUS DASHBOARD ':^78}{Fore.CYAN}{Style.BRIGHT}│"
    )
    print(f"{Fore.CYAN}{Style.BRIGHT}├{'─' * 78}┤")

    # Total Registry Overview
    print(
        f"{Fore.CYAN}{Style.BRIGHT}│{Fore.WHITE}  📚 Total Registry Entries: {Fore.YELLOW}{registry_len:>4}{' ' * 53}{Fore.CYAN}{Style.BRIGHT}│"
    )
    print(f"{Fore.CYAN}{Style.BRIGHT}│{' ' * 78}│")

    # Stage 1: Harvest
    harvest_color = Fore.GREEN if status["RAW"] > 0 else Fore.WHITE
    print(f"{Fore.CYAN}{Style.BRIGHT}│{Fore.WHITE}  [1] 📥 HARVEST")
    print(
        f"{Fore.CYAN}{Style.BRIGHT}│{Fore.WHITE}      ├─ Raw Data Pool: {harvest_color}{status['RAW']:>3} files{Fore.WHITE}"
    )
    print(
        f"{Fore.CYAN}{Style.BRIGHT}│      └─ {create_progress_bar(status['RAW'], max(registry_len, 1), 30, harvest_color)}"
    )

    # Stage 2: Scrub
    scrub_color = Fore.YELLOW if status["CLEAN"] > 0 else Fore.WHITE
    print(f"{Fore.CYAN}{Style.BRIGHT}│{Fore.WHITE}  [2] 🩺 SURGICAL SCRUBBING")
    print(
        f"{Fore.CYAN}{Style.BRIGHT}│      ├─ Awaiting Cleaning: {scrub_color}{status['RAW']:>3} files{Fore.WHITE}"
    )
    print(
        f"{Fore.CYAN}{Style.BRIGHT}│      └─ Cleaned Dataset: {scrub_color}{status['CLEAN']:>3} files{Fore.WHITE}"
    )

    # Stage 3: DNA Extraction
    dna_color = Fore.MAGENTA if status["DNA"] > 0 else Fore.WHITE
    print(f"{Fore.CYAN}{Style.BRIGHT}│{Fore.WHITE}  [3] 🧬 GENETIC SEQUENCING")
    print(
        f"{Fore.CYAN}{Style.BRIGHT}│      ├─ Awaiting Extraction: {dna_color}{status['CLEAN']:>3} files{Fore.WHITE}"
    )
    print(
        f"{Fore.CYAN}{Style.BRIGHT}│      └─ DNA Signatures: {dna_color}{status['DNA']:>3} files{Fore.WHITE}"
    )

    # Stage 4: Combat
    combat_queue = status["DNA"] + status["PRED"]
    combat_color = Fore.RED if combat_queue > 0 else Fore.WHITE
    print(f"{Fore.CYAN}{Style.BRIGHT}│{Fore.WHITE}  [4] ⚔️  COMBAT ARENA")
    print(
        f"{Fore.CYAN}{Style.BRIGHT}│      ├─ Combat Ready: {combat_color}{combat_queue:>3} files{Fore.WHITE}"
    )
    print(
        f"{Fore.CYAN}{Style.BRIGHT}│      └─ New DNA: {Fore.RED}{status['DNA']:>3} | Predicted: {Fore.YELLOW}{status['PRED']:>3}{Fore.WHITE}"
    )

    # Stage 5: Brain Status
    brain_status_text = (
        f"{Fore.GREEN}● ONLINE" if brain_ready else f"{Fore.RED}○ OFFLINE"
    )
    print(f"{Fore.CYAN}{Style.BRIGHT}│{Fore.WHITE}  [5] 🔮 META-BRAIN ORACLE")
    print(
        f"{Fore.CYAN}{Style.BRIGHT}│      └─ Status: {brain_status_text}{' ' * 56}{Fore.CYAN}{Style.BRIGHT}│"
    )

    print(f"{Fore.CYAN}{Style.BRIGHT}├{'─' * 78}┤")

    # Quick Actions
    print(
        f"{Fore.CYAN}{Style.BRIGHT}│{Fore.WHITE}{Style.BRIGHT}{' ⚡ QUICK COMMANDS ':^78}{Fore.CYAN}{Style.BRIGHT}│"
    )
    print(
        f"{Fore.CYAN}{Style.BRIGHT}│{Fore.WHITE}  [6] 📈 Analytics Dashboard  │  [7] 🔄 Sync Warehouse     {Fore.CYAN}{Style.BRIGHT}│"
    )
    print(
        f"{Fore.CYAN}{Style.BRIGHT}│{Fore.WHITE}  [8] 🔍 Memory Explorer     │  [B] 🧪 Bronze Browser     {Fore.CYAN}{Style.BRIGHT}│"
    )
    print(
        f"{Fore.CYAN}{Style.BRIGHT}│{Fore.WHITE}  [R] ♻️  Hot Reload Modules  │  [0] 🧹 Clear Terminal     {Fore.CYAN}{Style.BRIGHT}│"
    )
    print(
        f"{Fore.CYAN}{Style.BRIGHT}│{Fore.WHITE}  [9] 🚀 Exit System         │                            {Fore.CYAN}{Style.BRIGHT}│"
    )

    print(f"{Fore.CYAN}{Style.BRIGHT}├{'─' * 78}┤")

    # Smart Mode Hints
    print(
        f"{Fore.CYAN}{Style.BRIGHT}│{Fore.YELLOW}  💡 SMART MODES: s1 (Harvest→Scrub) | s2 (DNA→Combat) | s3 (Full Pipeline){' ' * 8}{Fore.CYAN}{Style.BRIGHT}│"
    )
    print(
        f"{Fore.CYAN}{Style.BRIGHT}│{Fore.YELLOW}     s4 (Auto-Optimize) - Let the Brain choose the best path{' ' * 20}{Fore.CYAN}{Style.BRIGHT}│"
    )

    print(f"{Fore.CYAN}{Style.BRIGHT}└{'─' * 78}┘{Style.RESET_ALL}")


def print_success(message):
    """Prints a formatted success message."""
    print(f"\n{Fore.GREEN}{Style.BRIGHT}✅ {message}{Style.RESET_ALL}")


def print_error(message):
    """Prints a formatted error message."""
    print(f"\n{Fore.RED}{Style.BRIGHT}❌ {message}{Style.RESET_ALL}")


def print_info(message):
    """Prints a formatted info message."""
    print(f"\n{Fore.CYAN}{Style.BRIGHT}ℹ️  {message}{Style.RESET_ALL}")


def print_warning(message):
    """Prints a formatted warning message."""
    print(f"\n{Fore.YELLOW}{Style.BRIGHT}⚠️  {message}{Style.RESET_ALL}")


def print_section_header(title, color=Fore.MAGENTA):
    """Prints a section header."""
    print(f"\n{color}{Style.BRIGHT}{'═' * 80}")
    print(f"{color}{Style.BRIGHT}  {title}")
    print(f"{color}{Style.BRIGHT}{'═' * 80}{Style.RESET_ALL}")


def animate_processing(message, duration=0.5):
    """Shows an animated processing indicator."""
    import time

    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    for _ in range(int(duration * 10)):
        for frame in frames:
            sys.stdout.write(f"\r{Fore.CYAN}{frame} {message}{Style.RESET_ALL}")
            sys.stdout.flush()
            time.sleep(0.05)
    sys.stdout.write("\r" + " " * (len(message) + 2) + "\r")
    sys.stdout.flush()


def get_targets(reg, states):
    """Retrieves file IDs for specific pipeline states."""
    if isinstance(states, str):
        states = [states]
    return [fid for fid, info in reg.memory.items() if info["state"] in states]


def main():
    print_header()

    # Initial object instantiation
    reg_obj = registry.SystemRegistry()
    bridge_obj = brain_bridge.MetaBrainBridge()
    analytics_obj = analytics.AnalyticsManager()
    explorer_obj = memory_viewer.MemoryExplorer(reg_obj)
    bronze_browser = browser.BronzeBrowser(bridge_obj)

    while True:
        stats = {
            "RAW": len(get_targets(reg_obj, "DOWNLOADED")),
            "CLEAN": len(get_targets(reg_obj, "CLEANED")),
            "DNA": len(get_targets(reg_obj, "EXTRACTED")),
            "PRED": len(get_targets(reg_obj, "PREDICTED")),
        }

        display_menu(stats, len(reg_obj.memory), bridge_obj.ready)

        # Enhanced input prompt
        choice = (
            input(
                f"\n{Fore.CYAN}{Style.BRIGHT}┌──[{Fore.YELLOW}METALEARNER{Fore.CYAN}]─[{Fore.GREEN}v2.0{Fore.CYAN}]\n{Fore.CYAN}└─> {Style.RESET_ALL}"
            )
            .strip()
            .lower()
        )

        try:
            # --- [R] HOT RELOAD LOGIC ---
            if choice == "r":
                print_section_header("♻️  HOT RELOAD - NEURAL MODULE SYNC", Fore.CYAN)
                animate_processing("Reinitializing neural pathways...", 1.0)

                modules = [
                    registry,
                    downloader,
                    cleaner,
                    extractor,
                    benchmarker,
                    smart_mode,
                    brain_bridge,
                    analytics,
                    memory_viewer,
                    browser,
                ]
                for m in modules:
                    importlib.reload(m)

                # Re-bind all objects to the new code
                reg_obj = registry.SystemRegistry()
                bridge_obj = brain_bridge.MetaBrainBridge()
                analytics_obj = analytics.AnalyticsManager()
                explorer_obj = memory_viewer.MemoryExplorer(reg_obj)
                bronze_browser = browser.BronzeBrowser(bridge_obj)

                print_success("All modules reinitialized. System updated successfully.")

            # --- [B] BRONZE BROWSER LOGIC ---
            elif choice == "b":
                print_info("Launching Bronze Dataset Browser...")
                bronze_browser.open_browser()

            # --- [0] CLEAR LOGIC ---
            elif choice in ["0", "clear", "cls"]:
                print_header()

            # --- SMART MODES ---
            elif choice.startswith("s") and choice[1:].isdigit():
                mode_num = int(choice[1:])
                mode_names = {
                    1: "Harvest → Scrub",
                    2: "DNA → Combat",
                    3: "Full Pipeline",
                    4: "Auto-Optimize",
                }
                print_section_header(
                    f"🎯 SMART MODE {mode_num}: {mode_names.get(mode_num, 'Unknown')}",
                    Fore.YELLOW,
                )
                smart_mode.run_smart_mode(reg_obj, mode_num)

            # --- MODULE 1: HARVEST ---
            elif choice == "1":
                print_section_header("📥 HARVEST MODULE - Data Acquisition", Fore.GREEN)
                downloader.fetch_openml_curated_batch(reg_obj)

            # --- MODULE 2: SCRUB ---
            elif choice == "2":
                print_section_header(
                    "🩺 SURGICAL SCRUBBING - Data Cleaning", Fore.YELLOW
                )
                targets = get_targets(reg_obj, "DOWNLOADED")
                if not targets:
                    print_warning("No raw data waiting for cleaning.")
                    continue

                print_info(f"Found {len(targets)} datasets awaiting cleaning")
                scrubber = cleaner.IntelligentCleaner(reg_obj)

                for i, f in enumerate(targets, 1):
                    print(
                        f"\n{Fore.CYAN}[{i}/{len(targets)}] Processing: {f}{Style.RESET_ALL}"
                    )
                    scrubber.scrub(f)

                scrubber.export_report()
                print_success(f"Cleaning complete. {len(targets)} datasets processed.")

            # --- MODULE 3: DNA SEQUENCING ---
            elif choice == "3":
                print_section_header(
                    "🧬 GENETIC SEQUENCING - Feature Extraction", Fore.MAGENTA
                )
                if not get_targets(reg_obj, "CLEANED"):
                    print_warning("No cleaned data waiting for DNA extraction.")
                    continue
                extractor.run_dna_extraction_pipeline(reg_obj)

            # --- MODULE 4: COMBAT ---
            elif choice == "4":
                print_section_header(
                    "⚔️  COMBAT ARENA - Algorithm Benchmarking", Fore.RED
                )
                targets = get_targets(reg_obj, ["EXTRACTED", "PREDICTED"])
                if not targets:
                    print_warning("No combat-ready data found.")
                    continue

                print_info(f"Deploying {len(targets)} datasets to the arena")
                combat_engine = benchmarker.MetaBenchmarker(reg_obj)
                combat_engine.run_benchmarks()
                combat_engine.generate_final_warehouse()
                print_success(
                    "Combat operations complete. Results stored in warehouse."
                )

            # --- MODULE 5: ORACLE ---
            elif choice == "5":
                print_section_header(
                    "🔮 META-BRAIN ORACLE - Neural Predictions", Fore.CYAN
                )

                if bridge_obj.ready:
                    targets = get_targets(reg_obj, "EXTRACTED")
                    if not targets:
                        print_info("No new datasets waiting for Neural Analysis.")
                        continue

                    print_info(f"Consulting the Oracle for {len(targets)} targets...")
                    print(
                        f"\n{Fore.CYAN}{'Dataset ID':<30} {'Prediction':<20} {'Confidence':<10}{Style.RESET_ALL}"
                    )
                    print(f"{Fore.CYAN}{'─' * 60}{Style.RESET_ALL}")

                    for fid in targets:
                        meta = reg_obj.memory[fid].get("metadata", {})
                        path = meta.get("clean_path")
                        if path and os.path.exists(path):
                            animate_processing(f"Analyzing {fid}...", 0.3)
                            winner, conf = bridge_obj.predict_from_csv(path)
                            if winner:
                                meta.update(
                                    {
                                        "predicted_best": winner,
                                        "brain_confidence": round(conf, 4),
                                        "analysis_date": datetime.now().strftime(
                                            "%Y-%m-%d %H:%M:%S"
                                        ),
                                    }
                                )
                                reg_obj.update(fid, "PREDICTED", meta)
                                conf_color = (
                                    Fore.GREEN
                                    if conf > 0.7
                                    else Fore.YELLOW if conf > 0.4 else Fore.RED
                                )
                                print(
                                    f"{Fore.WHITE}{fid:<30} {Fore.GREEN}{winner:<20} {conf_color}{conf:.1%}{Style.RESET_ALL}"
                                )

                    print_success("Neural analysis complete. Predictions stored.")
                else:
                    print_error(
                        "Meta-Brain is currently offline. Unable to consult Oracle."
                    )

            # --- MODULE 6: ANALYTICS ---
            elif choice == "6":
                print_section_header(
                    "📈 ANALYTICS DASHBOARD - Global Reports", Fore.BLUE
                )
                analytics_obj.generate_report()

            # --- MODULE 7: SYNC ---
            elif choice == "7":
                print_section_header("🔄 WAREHOUSE SYNC - Force Update", Fore.YELLOW)
                combat_engine = benchmarker.MetaBenchmarker(reg_obj)
                combat_engine.generate_final_warehouse()
                print_success("Warehouse synchronized successfully.")

            # --- MODULE 8: EXPLORER ---
            elif choice == "8":
                print_section_header(
                    "🔍 NEURAL MEMORY EXPLORER - Search & Filter", Fore.CYAN
                )
                explorer_obj.open_console()

            # --- MODULE 9: EXIT ---
            elif choice == "9":
                print_section_header("🚀 SHUTTING DOWN METALEARNER", Fore.YELLOW)
                animate_processing("Saving system state...", 0.5)
                reg_obj.save()
                print_success("System state preserved. Until next time, Architect.")
                print(
                    f"{Fore.CYAN}{Style.BRIGHT}\n    Thank you for using MetaLearner Neural Architecture\n{Style.RESET_ALL}"
                )
                break

            else:
                print_error(
                    f"Invalid command: '{choice}'. Type a number or letter from the menu."
                )

        except KeyboardInterrupt:
            print_warning("\nOperation cancelled by user.")
            continue
        except Exception as e:
            print_error(f"System Error: {str(e)}")
            print_info("Attempting to save current state...")
            reg_obj.save()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(
            f"\n{Fore.YELLOW}{Style.BRIGHT}⚠️  Emergency shutdown initiated.{Style.RESET_ALL}"
        )
        print(f"{Fore.CYAN}MetaLearner terminated safely.{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}{Style.BRIGHT}💥 CRITICAL ERROR: {e}{Style.RESET_ALL}")
        print(
            f"{Fore.YELLOW}Please report this issue to the Architect.{Style.RESET_ALL}"
        )
