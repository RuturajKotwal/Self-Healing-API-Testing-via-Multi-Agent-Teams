import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io

# Setup Academic Plotting Style
sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)

# ==========================================
# FIGURE 8.8: The Active Parameter Threshold
# ==========================================
def plot_active_parameter_threshold():
    # Model configuration data (Derived from empirical testing + architectural specs)
    # Note: gpt-4.1 is represented theoretically at ~200B active parameters for visual scaling
    data = {
        'Model': ['DeepSeek-Coder-V2-Lite', 'Qwen2.5-Coder-7B', 'Llama-3.1-8B', 'gpt-4o-mini', 'gpt-4.1'],
        'Total_Parameters_B': [16, 7, 8, 100, 1000],  # Theoretical upper-bounds for proprietary models
        'Active_Parameters_B': [2.4, 7, 8, 50, 200],  # Active parameters per token
        'MAS_Success_Rate': [0, 0, 0, 73.3, 100],     # Averaged MAS success rate across all tasks
        'Architecture': ['MoE (Local)', 'Dense (Local)', 'Dense (Local)', 'Dense (Cloud API)', 'Dense (Cloud API)']
    }
    
    df_params = pd.DataFrame(data)
    
    plt.figure(figsize=(10, 6))
    
    # Create scatter plot where X is Active Parameters
    scatter = sns.scatterplot(
        data=df_params,
        x='Active_Parameters_B',
        y='MAS_Success_Rate',
        hue='Architecture',
        style='Architecture',
        s=400, # Marker size
        palette=['#D62728', '#FF7F0E', '#1F77B4'],
        edgecolor='black',
        linewidth=1.5
    )
    
    # Draw the "Cognitive Threshold" Region
    plt.axvspan(0, 20, color='red', alpha=0.1, label='The Failure Zone (Context Collapse)')
    plt.axvspan(30, 210, color='green', alpha=0.1, label='The Viability Zone (Stable State-Passing)')
    plt.axvline(x=25, color='black', linestyle='--', linewidth=2, label='Estimated Cognitive Threshold (~30B)')
    
    # Annotate specific models
    for i in range(df_params.shape[0]):
        plt.text(df_params['Active_Parameters_B'][i], 
                 df_params['MAS_Success_Rate'][i] + 4, 
                 df_params['Model'][i], 
                 horizontalalignment='left', 
                 size='medium', color='black', weight='bold')

    # Formatting using logarithmic scale for X to handle massive proprietary parameter ranges
    plt.xscale('log')
    plt.title("The Cognitive Threshold (Active Parameters vs. Agentic Viability)", fontweight="bold", pad=20)
    plt.xlabel("Active Parameters per Token (Log Scale - Billions)", fontweight="bold", labelpad=10)
    plt.ylabel("Multi-Agent Remediation Success Rate (%)", fontweight="bold", labelpad=10)
    plt.ylim(-10, 115)
    plt.legend(loc='lower right', framealpha=1)
    
    plt.tight_layout()
    plt.savefig("Figure_8_8_Active_Parameters.png", dpi=300, bbox_inches='tight')
    print("✅ Saved Figure 8.8: Figure_8_8_Active_Parameters.png")

# ==========================================
# FIGURE 8.9: Typology of Systemic Failure
# ==========================================
def plot_failure_typology():
    # Extracted exactly from the CSV forensic audit of the failing local models (Single Agent + MAS combined)
    # Categories:
    # 1. Logical Rest Bias: "assert 404 == 200"
    # 2. Schema Hallucination: "KeyError", "assert 'Not Found' =="
    # 3. AST/Syntax Collapse: "found no collectors", "not found: (no match in module)"
    
    failure_data = {
        'Model': ['Qwen2.5-Coder-7B', 'Meta-Llama-3.1-8B', 'DeepSeek-V2-MoE-16B'],
        'Logical/REST Bias (%)': [85, 75, 40],
        'Schema Hallucination (%)': [10, 20, 17],
        'AST/Syntax Collapse (%)': [5, 5, 43]
    }
    
    df_fails = pd.DataFrame(failure_data)
    df_fails.set_index('Model', inplace=True)
    
    # Plot 100% Stacked Bar Chart
    ax = df_fails.plot(kind='barh', stacked=True, figsize=(11, 6), color=['#F39C12', '#E74C3C', '#8E44AD'], edgecolor='white')
    
    plt.title("Structural Degradation vs. Logical Bias in Sub-Optimal Models", fontweight="bold", pad=20)
    plt.xlabel("Proportion of Total Execution Failures (%)", fontweight="bold", labelpad=10)
    plt.ylabel("Local Edge Model", fontweight="bold", labelpad=10)
    
    # Formatting
    plt.legend(title="Failure Topology", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.xlim(0, 100)
    
    # Annotate percentages inside the bars
    for c in ax.containers:
        # Format the text to only show if value > 0
        labels = [f'{w:.0f}%' if (w := v.get_width()) > 0 else '' for v in c]
        ax.bar_label(c, labels=labels, label_type='center', color='white', weight='bold')

    plt.tight_layout()
    plt.savefig("Figure_8_9_Failure_Typology.png", dpi=300, bbox_inches='tight')
    print("✅ Saved Figure 8.9: Figure_8_9_Failure_Typology.png")

if __name__ == "__main__":
    plot_active_parameter_threshold()
    plot_failure_typology()
    print("\nVisualizations rendered and saved at 300 DPI.")