import re
import pandas as pd

# 1. Read the truncated JSON content
with open("system_memory.json", "r") as f:
    content = f.read()

# 2. Extract top-level dataset keys using indentation patterns
matches = re.finditer(r'^    "([\w-]+)"\s*:\s*\{', content, re.MULTILINE)

parsed_datasets = []
match_list = list(matches)

for i in range(len(match_list)):
    name = match_list[i].group(1)
    start = match_list[i].end()
    end = match_list[i + 1].start() if i + 1 < len(match_list) else len(content)
    block = content[start:end]

    # Helper to find numerical values in the metadata block
    def get_val(key, text):
        m = re.search(f'"{key}":\\s*([\\d.]+)', text)
        return float(m.group(1)) if m else None

    parsed_datasets.append(
        {
            "Dataset": name,
            "Rows": get_val("n_rows", block),
            "Cols": get_val("n_cols", block),
            "Entropy": get_val("entropy", block),
            "Imbalance": get_val("imbalance", block),
            "Actual F1": get_val("f1_score", block),
        }
    )

# 3. Create DataFrame and generate compressed summary
df = pd.DataFrame(parsed_datasets).dropna(subset=["Rows", "Cols"])
compressed_table = df.drop(columns="Dataset").describe().transpose()
compressed_table = compressed_table[["mean", "std", "min", "max"]]

# 4. Display Results
print(compressed_table.to_markdown())
