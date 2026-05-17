import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ==========================================
# 1. LOAD DATA FROM CSV
# ==========================================
# Point this to your actual CSV filename
csv_filename = "thesis_results_gpt4_1.csv" 

try:
    df = pd.read_csv(csv_filename)
    print(f"✅ Successfully loaded {csv_filename}")
except FileNotFoundError:
    print(f"🚨 ERROR: Could not find '{csv_filename}'. Please ensure it is in the same folder as this script.")
    exit()

# ==========================================
# 2. DATA PREPARATION & FORMATTING
# ==========================================
# Format columns for visualization
df['success_int'] = df['success'].astype(int) * 100
df['setup'] = df['model'] + " (" + df['architecture'] + ")"
df['change_name_clean'] = df['change_name'].str.replace('_', ' ').str.title()

# Dynamically assign batch numbers (1-5) by tracking the chronological run order
df['timestamp'] = pd.to_datetime(df['timestamp'])
df = df.sort_values(by='timestamp')
df['batch_number'] = df.groupby(['model', 'architecture', 'change_name']).cumcount() + 1

# Setup Academic Plotting Style
sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)
color_palette = sns.color_palette("colorblind")

# ==========================================
# FIGURE 8.1: Architectural Success Rate Divergence
# ==========================================
plt.figure(figsize=(10, 6))
fig_8_1 = sns.barplot(
    data=df, 
    x='change_name_clean', 
    y='success_int', 
    hue='setup',
    errorbar=None, 
    palette="deep",
    edgecolor="black"
)

plt.title("Remediation Success Rate by Architecture and Task", fontweight="bold", pad=20)
plt.xlabel("API Taxonomy Change", fontweight="bold", labelpad=10)
plt.ylabel("Success Rate (%)", fontweight="bold", labelpad=10)
plt.ylim(0, 110) # Pad slightly above 100 for visual clarity
plt.legend(title="Execution Setup", loc="lower right")

# Annotate bars with exact percentages
for p in fig_8_1.patches:
    height = p.get_height()
    if height > 0:
        fig_8_1.annotate(f'{int(height)}%', 
                         (p.get_x() + p.get_width() / 2., height),
                         ha='center', va='bottom', 
                         fontsize=10, color='black', xytext=(0, 5), 
                         textcoords='offset points')

plt.tight_layout()
plt.savefig("Figure_8_1_Success_Rates.png", dpi=300, bbox_inches='tight')
print("✅ Saved Figure 8.1: Figure_8_1_Success_Rates.png")

# ==========================================
# FIGURE 8.2: Token Consumption vs. Structural Complexity
# ==========================================
# Grouping data to show the mean token tax across configurations
token_summary = df.groupby(['change_name_clean', 'architecture'])['total_tokens'].mean().reset_index()

plt.figure(figsize=(10, 6))
fig_8_2 = sns.barplot(
    data=token_summary,
    x='change_name_clean',
    y='total_tokens',
    hue='architecture',
    palette=['#A0C4FF', '#FFADAD'], # Distinct colors for Baseline vs MAS
    edgecolor="black"
)

plt.title("Mean Token Consumption", fontweight="bold", pad=20)
plt.xlabel("API Taxonomy Change", fontweight="bold", labelpad=10)
plt.ylabel("Mean Total Tokens Consumed", fontweight="bold", labelpad=10)
plt.legend(title="Orchestration Layer", loc="upper left")

# Annotate token numbers
for p in fig_8_2.patches:
    height = p.get_height()
    fig_8_2.annotate(f'{int(height):,}', 
                     (p.get_x() + p.get_width() / 2., height),
                     ha='center', va='bottom', 
                     fontsize=10, color='black', xytext=(0, 5), 
                     textcoords='offset points')

plt.tight_layout()
plt.savefig("Figure_8_2_Token_Consumption.png", dpi=300, bbox_inches='tight')
print("✅ Saved Figure 8.2: Figure_8_2_Token_Consumption.png")

# ==========================================
# FIGURE 8.3: Algorithmic Convergence and Determinism
# ==========================================
# We isolate just the Multi-Agent System (MAS) runs to demonstrate gpt-4.1's stabilization
mas_df = df[df['architecture'] == 'multi_agent']

plt.figure(figsize=(10, 6))
sns.stripplot(
    data=mas_df, 
    x='change_name_clean', 
    y='llm_calls', 
    hue='model',
    jitter=0.05,  # Slight jitter to prevent exact dot overlap 
    size=10, 
    alpha=0.8,
    palette="Set2",
    dodge=True,
    edgecolor="gray",
    linewidth=1
)

plt.title("Algorithmic Convergence", fontweight="bold", pad=20)
plt.xlabel("API Taxonomy Change", fontweight="bold", labelpad=10)
plt.ylabel("Total LLM Inference Calls (Iterations)", fontweight="bold", labelpad=10)
plt.yticks([1, 2, 3, 4, 5, 6, 7]) # Ensure discrete ticks for iteration counts

# Draw a red dashed line at y=6 to explicitly mark the "Algorithmic Termination Ceiling"
plt.axhline(y=6, color='red', linestyle='--', linewidth=1.5, label='Termination Ceiling (Failure)')
plt.text(0.5, 6.2, 'Algorithmic Termination (Max Attempts Reached)', color='red', ha='center', fontsize=10)

plt.legend(title="Cloud Model", loc="upper right")
plt.tight_layout()
plt.savefig("Figure_8_3_Algorithmic_Convergence.png", dpi=300, bbox_inches='tight')
print("✅ Saved Figure 8.3: Figure_8_3_Algorithmic_Convergence.png")

print("\nAll visualizations have been rendered and saved at 300 DPI.")