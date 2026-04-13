import json
import os
from datetime import datetime
from colorama import Fore, Style


class SystemRegistry:
    def __init__(self, path="system_memory.json"):
        self.path = path
        self.memory = self._load()
        # The strictly enforced "Life Cycle" of a dataset
        self.workflow = ["DOWNLOADED", "CLEANED", "EXTRACTED", "BENCHMARKED"]

    def _load(self):
        """Loads the memory core with a safety check for corrupted files."""
        if os.path.exists(self.path):
            try:
                with open(self.path, "r") as f:
                    return json.load(f)
            except Exception:
                print(
                    f"{Fore.RED}⚠️ WARNING: Memory core corrupted. Initializing fresh registry.{Style.RESET_ALL}"
                )
                return {}
        return {}

    def save(self):
        """Persists the system state to disk."""
        with open(self.path, "w") as f:
            json.dump(self.memory, f, indent=4)

    def check_clearance(self, file_id, target_state):
        """
        The Gatekeeper: Validates if a file can proceed to the next phase.
        Returns: (bool, message, recommendation)
        """
        current_data = self.memory.get(file_id, {})
        current_state = current_data.get("state", "NONE")

        # 1. Redundancy Check
        if current_state == target_state:
            return (
                False,
                "ALREADY_PROCESSED",
                "No action needed. Move to the next module.",
            )

        # 2. Logic Check
        try:
            target_idx = self.workflow.index(target_state)
            if target_idx > 0:
                required_prev = self.workflow[target_idx - 1]
                if current_state != required_prev:
                    rec = f"Run the {required_prev.lower()}.py module first."
                    return (
                        False,
                        f"SECURITY_BLOCK: Stage '{required_prev}' missing.",
                        rec,
                    )
        except ValueError:
            return False, "INVALID_STATE", "Check system workflow definitions."

        return True, "ACCESS_GRANTED", "Proceed with execution."

    def update(self, file_id, state, new_meta=None):
        """
        The Intelligent Update: Merges new data with old data so no history is lost.
        """
        # Fetch existing record or create new
        record = self.memory.get(
            file_id, {"state": "NONE", "history": [], "metadata": {}}
        )

        # Record the transition for the 'Audit Trail'
        old_state = record["state"]
        record["state"] = state
        record["last_sync"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if old_state != state:
            record["history"].append(f"{old_state} -> {state} at {record['last_sync']}")

        # Merge Metadata (This is the 'Overkill' part - it preserves everything)
        if new_meta:
            record["metadata"].update(new_meta)

        self.memory[file_id] = record
        self.save()

    def get_path(self, file_id, key="path"):
        """Helper to quickly find where a file is stored in the warehouse."""
        return self.memory.get(file_id, {}).get("metadata", {}).get(key)


# --- GLOBAL SYSTEM SYNC ---
# This ensures that whenever 'registry' is imported, we are using the same brain.
registry = SystemRegistry()
