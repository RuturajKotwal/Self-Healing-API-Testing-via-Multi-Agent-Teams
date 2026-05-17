import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io

# ==========================================
# 1. LOAD DATA
# ==========================================
# Combine both your OpenAI baseline CSV and the new local models CSV
csv_filename_openai = "thesis_results.csv" # Ensure this has the gpt-4 data
csv_filename_local = "local_models_results.csv" # The newly saved 7B/8B data

try:
    df_openai = pd.read_csv(csv_filename_openai)
    df_local = pd.read_csv(csv_filename_local)
    df = pd.concat([df_openai, df_local], ignore_index=True)
    print("✅ Successfully loaded and merged dataset.")
except FileNotFoundError:
    print("🚨 ERROR: Could not find the CSV files. Please ensure both are in the same directory.")
    exit()

# ==========================================
# 2. DATA PREPARATION
# ==========================================
df['success_int'] = df['success'].astype(int) * 100
df['change_name_clean'] = df['change_name'].str.replace('_', ' ').str.title()
df['architecture_clean'] = df['architecture'].str.replace('_', ' ').str.title()
df['Config'] = df['model'] + " | " + df['architecture_clean']

# Filter specifically for the MAS runs to show the failure of distributed orchestration
mas_df = df[df['architecture'] == 'multi_agent'].copy()

# Ensure chronological ordering to calculate batches correctly
mas_df['timestamp'] = pd.to_datetime(mas_df['timestamp'])
mas_df = mas_df.sort_values(by='timestamp')

# ==========================================
# FIGURE 8.4: The Cognitive Threshold Breakdown
# ==========================================
plt.figure(figsize=(12, 7))

# We use a custom color palette highlighting the OpenAI success (Blue/Green) vs Local failure (Reds)
palette_mapping = {
    "GPT-4.1 | Multi Agent": "#2CA02C",       # Strong Green
    "GPT-4o mini | Multi Agent": "#1F77B4",   # Standard Blue
    "Qwen2.5-Coder-7B-Instruct | Multi Agent": "#D62728", # Strong Red
    "Meta-Llama-3.1-8B-Instruct | Multi Agent": "#FF7F0E" # Orange/Red
}

fig_8_4 = sns.barplot(
    data=mas_df,
    x='change_name_clean',
    y='success_int',
    hue='Config',
    palette=palette_mapping,
    edgecolor="black",
    errorbar=None
)

plt.title("The Cognitive Threshold - MAS Success Rate Collapse on Sub-10B Models", fontweight="bold", pad=20)
plt.xlabel("API Taxonomy Change (Complexity)", fontweight="bold", labelpad=10)
plt.ylabel("MAS Orchestration Success Rate (%)", fontweight="bold", labelpad=10)
plt.ylim(0, 110)
plt.legend(title="Inference Engine", loc="upper right")

# Annotate the zero-bars for emphasis
for p in fig_8_4.patches:
    height = p.get_height()
    # Explicitly highlight the 0% failures
    if height == 0:
         fig_8_4.annotate('0%', 
                         (p.get_x() + p.get_width() / 2., 2), # Hover slightly above 0
                         ha='center', va='bottom', 
                         fontsize=10, color='red', fontweight='bold')
    elif height > 0:
        fig_8_4.annotate(f'{int(height)}%', 
                         (p.get_x() + p.get_width() / 2., height),
                         ha='center', va='bottom', 
                         fontsize=10, color='black', xytext=(0, 5), 
                         textcoords='offset points')

plt.tight_layout()
plt.savefig("Figure_8_4_Cognitive_Threshold.png", dpi=300, bbox_inches='tight')
print("✅ Saved Figure 8.4: Figure_8_4_Cognitive_Threshold.png")