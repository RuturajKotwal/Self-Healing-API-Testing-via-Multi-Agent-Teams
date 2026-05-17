import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Setup Academic Plotting Style
sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)

# ==========================================
# FIGURE 8.10: The Ultimate Architectural Benchmark
# ==========================================
def plot_ultimate_benchmark():
    # Synthetic aggregation of all empirical data (Success Rates %)
    models = ['Qwen2.5-7B', 'Llama-3.1-8B', 'DeepSeek-16B-MoE', 'Qwen2.5-32B-AWQ', 'gpt-4o-mini', 'gpt-4.1']
    
    # Success rates based on thesis CSV data
    single_agent_success = [0, 6.6, 0, 0, 100, 93.3]
    mas_success = [0, 0, 0, 0, 73.3, 100]
    
    x = np.arange(len(models))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    rects1 = ax.bar(x - width/2, single_agent_success, width, label='Single-Agent Baseline', color='#7F8C8D', edgecolor='black')
    rects2 = ax.bar(x + width/2, mas_success, width, label='LangGraph MAS', color='#2980B9', edgecolor='black')
    
    # Draw the Density Floor line separating Local vs Cloud APIs
    ax.axvline(x=3.5, color='red', linestyle='--', linewidth=2)
    ax.text(3.5, 80, ' The Density Floor\n (Cloud API Transition)', color='red', weight='bold', ha='left')
    
    ax.set_ylabel('Overall Remediation Success Rate (%)', fontweight='bold')
    ax.set_title('The Ultimate Architectural Benchmark (All Models)', fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(models, rotation=15, ha='right')
    ax.set_ylim(0, 115)
    ax.legend(loc='upper left')
    
    # Labeling bars
    for rects in [rects1, rects2]:
        for rect in rects:
            height = rect.get_height()
            if height > 0:
                ax.annotate(f'{height:.1f}%',
                            xy=(rect.get_x() + rect.get_width() / 2, height),
                            xytext=(0, 3),  # 3 points vertical offset
                            textcoords="offset points",
                            ha='center', va='bottom', fontsize=10, weight='bold')
            elif height == 0:
                 ax.annotate('0%',
                            xy=(rect.get_x() + rect.get_width() / 2, 0),
                            xytext=(0, 3),
                            textcoords="offset points",
                            ha='center', va='bottom', fontsize=10, color='red')

    fig.tight_layout()
    plt.savefig("Figure_8_10_Ultimate_Benchmark.png", dpi=300, bbox_inches='tight')
    print("✅ Saved Figure 8.10: Figure_8_10_Ultimate_Benchmark.png")

# ==========================================
# FIGURE 8.11: The Enterprise Viability Matrix
# ==========================================
def plot_viability_matrix():
    # X = Latency (Seconds per MAS loop), Y = Success Rate (%)
    data = {
        'Model': ['Qwen2.5-7B\n(Local FP16)', 'Llama-3.1-8B\n(Local BF16)', 'DeepSeek-16B\n(Local AWQ)', 'Qwen2.5-32B\n(Local AWQ+Eager)', 'gpt-4o-mini\n(Cloud API)', 'gpt-4.1\n(Cloud API)'],
        'Latency_Sec': [45, 48, 55, 290, 15, 22],
        'Success_Rate': [0, 0, 0, 0, 73.3, 100],
        'Category': ['Local Sub-10B', 'Local Sub-10B', 'Local MoE', 'Local 32B Bottleneck', 'Cloud API', 'Cloud API']
    }
    
    df_viability = pd.DataFrame(data)
    
    plt.figure(figsize=(11, 7))
    
    # Custom palette
    palette = {'Local Sub-10B': '#E74C3C', 'Local MoE': '#9B59B6', 'Local 32B Bottleneck': '#34495E', 'Cloud API': '#2ECC71'}
    
    scatter = sns.scatterplot(
        data=df_viability,
        x='Latency_Sec',
        y='Success_Rate',
        hue='Category',
        s=500,
        palette=palette,
        edgecolor='black',
        linewidth=1.5
    )
    
    # Annotate points
    for i in range(df_viability.shape[0]):
        plt.text(df_viability['Latency_Sec'][i], 
                 df_viability['Success_Rate'][i] + 4, 
                 df_viability['Model'][i], 
                 horizontalalignment='center', 
                 size=9, weight='bold')

    # Draw Viability Quadrants
    plt.axhline(y=80, color='gray', linestyle='--', alpha=0.5)
    plt.axvline(x=60, color='gray', linestyle='--', alpha=0.5)
    
    plt.text(10, 90, 'HIGH VIABILITY\n(Fast & Reliable)', color='green', alpha=0.6, weight='bold')
    plt.text(150, 90, 'COMPUTE BOTTLENECK\n(Slow but Reliable)', color='gray', alpha=0.6, weight='bold')
    plt.text(10, 10, 'FALSE ECONOMY\n(Fast but Broken)', color='red', alpha=0.6, weight='bold')
    plt.text(150, 10, 'UNVIABLE ZONE\n(Slow & Broken)', color='darkred', alpha=0.6, weight='bold')

    plt.title("The Enterprise Viability Matrix (Capability vs. Latency)", fontweight="bold", pad=20)
    plt.xlabel("Average Execution Latency per MAS Loop (Seconds)", fontweight="bold", labelpad=10)
    plt.ylabel("MAS Remediation Success Rate (%)", fontweight="bold", labelpad=10)
    plt.ylim(-10, 115)
    plt.xlim(0, 320)
    plt.legend(loc='center right', bbox_to_anchor=(1, 0.5))
    
    plt.tight_layout()
    plt.savefig("Figure_8_11_Viability_Matrix.png", dpi=300, bbox_inches='tight')
    print("✅ Saved Figure 8.11: Figure_8_11_Viability_Matrix.png")

if __name__ == "__main__":
    plot_ultimate_benchmark()
    plot_viability_matrix()
    print("\nFinal capstone visualizations rendered and saved at 300 DPI.")