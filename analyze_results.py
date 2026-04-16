import pandas as pd

def analyze_thesis_data(csv_file="thesis_results.csv"):
    try:
        df = pd.read_csv(csv_file)
    except FileNotFoundError:
        print(f"Error: {csv_file} not found. Please run your experiments first.")
        return

    # Ensure success is treated as a boolean/integer for calculation
    df['success'] = df['success'].astype(bool)

    print("\n" + "="*70)
    print("📊 THESIS RESULTS: OVERALL ARCHITECTURE COMPARISON")
    print("="*70)
    
    # 1. Overall Comparison (Single vs Multi)
    overall_summary = df.groupby('architecture').agg(
        total_runs=('run_id', 'count'),
        repair_rate_percent=('success', lambda x: (x.sum() / len(x)) * 100),
        avg_llm_calls=('llm_calls', 'mean'),
        avg_tokens=('total_tokens', 'mean')
    ).round(2).reset_index()
    
    print(overall_summary.to_string(index=False))

    print("\n" + "="*70)
    print("🔬 BREAKDOWN BY TEST COMPLEXITY (Easy / Medium / Hard)")
    print("="*70)
    
    # 2. Granular Breakdown (Architecture + Specific Test)
    granular_summary = df.groupby(['change_category', 'change_name', 'architecture']).agg(
        total_runs=('run_id', 'count'),
        repair_rate_percent=('success', lambda x: (x.sum() / len(x)) * 100),
        avg_llm_calls=('llm_calls', 'mean'),
        avg_tokens=('total_tokens', 'mean')
    ).round(2).reset_index()
    
    # Sort for better readability
    granular_summary = granular_summary.sort_values(by=['change_category', 'change_name', 'architecture'])
    
    print(granular_summary.to_string(index=False))
    
    # Export to a markdown file for easy copy/pasting into your thesis document
    with open("thesis_data_tables.md", "w") as f:
        f.write("# Thesis Results Data\n\n")
        f.write("## Overall Architecture Comparison\n")
        f.write(overall_summary.to_markdown(index=False))
        f.write("\n\n## Breakdown by Test Complexity\n")
        f.write(granular_summary.to_markdown(index=False))
        
    print("\n✅ Data tables successfully exported to 'thesis_data_tables.md'")

if __name__ == "__main__":
    analyze_thesis_data()