
import pandas as pd
import numpy as np
from scipy.stats import ttest_ind


def compare_groups_analysis(df, group_col, outcome_col, high_group_name, low_group_name):
    """
    Complete analysis comparing two groups
    """
    # Extract groups
    high_data = df[df[group_col] == high_group_name][outcome_col].dropna()
    low_data = df[df[group_col] == low_group_name][outcome_col].dropna()
    
    # Basic statistics
    high_mean = high_data.mean()
    low_mean = low_data.mean()
    # print("Low data: ", low_data, "Length: ", len(low_data))
    high_std = high_data.std()
    low_std = low_data.std()
    
    # Independent t-test
    t_stat, p_value = ttest_ind(high_data, low_data, equal_var=False)
    
    # Effect size (Cohen's d)
    pooled_std = np.sqrt(((len(high_data) - 1) * high_std**2 + 
                         (len(low_data) - 1) * low_std**2) / 
                        (len(high_data) + len(low_data) - 2))
    cohens_d = (high_mean - low_mean) / pooled_std
    
    # Results dictionary
    results = {
        'high_group': {
            'mean': high_mean,
            'std': high_std,
            'n': len(high_data)
        },
        'low_group': {
            'mean': low_mean,
            'std': low_std,
            'n': len(low_data)
        },
        'difference': high_mean - low_mean,
        't_statistic': t_stat,
        'p_value': p_value,
        'cohens_d': cohens_d
    }
    
    return results


def test_group_normality(data, metric, bins):
        # Create your bins
        bins = pd.cut(data[metric], bins=bins, include_lowest=True)

        # Extract the actual groups (lists of student values)
        groups = []
        for bin_category in bins.cat.categories:
            group_data = data[metric][bins == bin_category]
            if len(group_data) > 0:
                groups.append(group_data.values)

        # Check each group
        for i, group in enumerate(groups):
            print(f"Group {i}: n={len(group)}, mean={group.mean():.1f}")
            
            if len(group) >= 8:
                from scipy.stats import shapiro
                _, p_val = shapiro(group)
                normal = "Normal" if p_val > 0.05 else "Not normal"
                print(f"  {normal} (p={p_val:.3f})")
                
                if p_val > 0.05 or len(group) >= 15:
                    print(f"  ✓ OK to use")
                else:
                    print(f"  ✗ Too small AND not normal")
            else:
                print(f"  ✗ Too small for testing")
def debug_group_analysis(student_metrics, student_scores, metric, bin_edges):
    # Load your data
    
    print("=== DEBUGGING GROUP ANALYSIS ===\n")
    
    # Step 1: Check original data
    print("1. ORIGINAL DATA SIZES:")
    print(f"   student_metrics: {len(student_metrics)} rows")
    print(f"   student_scores: {len(student_scores)} rows")
    
    # Step 2: Check the metric distribution in original data
    print(f"\n2. METRIC DISTRIBUTION IN ORIGINAL DATA ({metric}):")
    print(f"   Min: {student_metrics[metric].min()}")
    print(f"   Max: {student_metrics[metric].max()}")
    print(f"   Missing values: {student_metrics[metric].isna().sum()}")
    
    # Step 3: Create bins on original data (like your histogram)
    original_bins = pd.cut(student_metrics[metric], bins=bin_edges, include_lowest=True)
    print(f"\n3. ORIGINAL BINNING (before merge):")
    print(original_bins.value_counts().sort_index())
    
    # Step 4: Check merge operation
    print(f"\n4. MERGE OPERATION:")
    print(f"   Unique service_ids in student_metrics: {student_metrics['service_id'].nunique()}")
    print(f"   Unique ids in student_scores: {student_scores['id'].nunique()}")
    
    # Check for missing matches
    missing_in_scores = ~student_metrics['service_id'].isin(student_scores['id'])
    missing_in_metrics = ~student_scores['id'].isin(student_metrics['service_id'])
    
    print(f"   Students in metrics but not in scores: {missing_in_scores.sum()}")
    print(f"   Students in scores but not in metrics: {missing_in_metrics.sum()}")
    
    # Step 5: Perform merge and check result
    all_metrics = student_metrics.merge(student_scores, left_on="service_id", right_on="id", how="inner")
    print(f"   After merge: {len(all_metrics)} rows")
    
    # Step 6: Check metric distribution after merge
    print(f"\n5. METRIC DISTRIBUTION AFTER MERGE:")
    print(f"   Min: {all_metrics[metric].min()}")
    print(f"   Max: {all_metrics[metric].max()}")
    print(f"   Missing values: {all_metrics[metric].isna().sum()}")
    
    # Step 7: Create bins on merged data
    merged_bins = pd.cut(all_metrics[metric], bins=bin_edges, include_lowest=True)
    print(f"\n6. BINNING AFTER MERGE:")
    print(merged_bins.value_counts().sort_index())
    
    # Step 8: Check for missing values in outcome
    print(f"\n7. OUTCOME VARIABLE (overall_change):")
    print(f"   Missing values: {all_metrics['overall_change'].isna().sum()}")
    
    # Step 9: Final groups after all filtering
    all_metrics['group'] = pd.cut(all_metrics[metric], bins=bin_edges, include_lowest=True, labels=["low", "high"])
    
    # Check final groups
    print(f"\n8. FINAL GROUPS:")
    final_groups = all_metrics['group'].value_counts()
    print(final_groups)
    
    # Check after dropna
    print(f"\n9. AFTER REMOVING MISSING outcome_col VALUES:")
    clean_data = all_metrics.dropna(subset=['overall_change'])
    clean_groups = clean_data['group'].value_counts()
    print(clean_groups)
    
    # Step 10: Check the actual values to understand the counterintuitive result
    print(f"\n10. CHECKING THE COUNTERINTUITIVE RESULT:")
    print("Group statistics:")
    for group_name in ['low', 'high']:
        group_data = clean_data[clean_data['group'] == group_name]
        print(f"\n{group_name.upper()} GROUP:")
        print(f"   N: {len(group_data)}")
        print(f"   {metric} range: {group_data[metric].min():.2f} - {group_data[metric].max():.2f}")
        print(f"   {metric} mean: {group_data[metric].mean():.2f}")
        print(f"   overall_change mean: {group_data['overall_change'].mean():.4f}")
        print(f"   overall_change std: {group_data['overall_change'].std():.4f}")
        
        # Show some examples
        print(f"   Sample of {metric} values: {group_data[metric].head().tolist()}")
        print(f"   Sample of overall_change values: {group_data['overall_change'].head().tolist()}")
    
    return all_metrics

if __name__ == "__main__":
    
    student_metrics = pd.read_csv(f"student_metrics.csv")
    student_scores = pd.read_csv("fourth_test_metrics.csv")
    # student_scores = pd.read_csv("test_metrics.csv")
    all_metrics = student_metrics.merge(student_scores, left_on="service_id", right_on="id", how="inner")
    metric = "words_with_4plus_exposures"
    
    print("RESULTS FOR METRIC: ", metric)
    # Look for visual separations
    # bin_edges = [0, 211.00578947, 985.44] # total playtime
    # bin_edges = [0, 140, 388.0] # total_pns
    # bin_edges = [1.0,5.4, 8.87] # avg_interactions_per_word
    bin_edges = [0.0, 18, 68.0] # words_with_4plus_exposures
    # bin_edges = [0.0, 18, 31] # trained_with_4plus_exposures
    debug_group_analysis(student_metrics, student_scores, metric, bin_edges)
    print("Bin edges: ", [float(i) for i in bin_edges])
    
    # Usage with your data
    # First, you might need to convert your group labels
    
    
    print(f"Size of student metrics: {len(student_metrics)}; Size of Student Scores: {len(student_scores)}; Size of combined: {len(all_metrics)}")
    print("Checking whether each of our groups are ok to use for t-test")
    test_group_normality(all_metrics, metric, bin_edges)
    all_metrics['group'] = pd.cut(all_metrics[metric], bins=bin_edges, include_lowest=True, labels=["low", "high"])

    # Run the analysis
    results = compare_groups_analysis(
        all_metrics, 
        'group', 
        'overall_change', 
        'high',  # or whatever your high group is labeled
        'low'    # or whatever your low group is labeled
    )

    print("Group Comparison Results:")
    print(f"High group: Mean = {results['high_group']['mean']:.4f}, N = {results['high_group']['n']}")
    print(f"Low group: Mean = {results['low_group']['mean']:.4f}, N = {results['low_group']['n']}")
    print(f"Difference: {results['difference']:.4f}")
    print(f"T-statistic: {results['t_statistic']:.4f}")
    print(f"P-value: {results['p_value']:.4f}")
    print(f"Cohen's d: {results['cohens_d']:.4f}")

    all_metrics.to_csv(f"all_metrics_all.csv", index=False)
