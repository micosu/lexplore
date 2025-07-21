import pandas as pd
from scipy.stats import ttest_rel, ttest_ind
import matplotlib.pyplot as plt
import seaborn as sns

# Load the files
second_pretest = pd.read_csv("pre_tests/Second_Grading_Results_v2.csv")
second_midtest = pd.read_csv("mid_tests/Second_Grading_Results_v2.csv")

fourth_pretest = pd.read_csv("pre_tests/Fourth_Grading_Results.csv")
fourth_midtest = pd.read_csv("mid_tests/Fourth_Grading_Results.csv")

# Load student metrics to identify experimental group
student_metrics = pd.read_csv("during_study/new_results/june11/student_metrics.csv")

second_pretest['grade'] = 'Second'
fourth_pretest['grade'] = 'Fourth'
second_midtest['grade'] = 'Second'
fourth_midtest['grade'] = 'Fourth'

# Combine pretests and midtests
pretest = pd.concat([second_pretest, fourth_pretest], ignore_index=True)
midtest = pd.concat([second_midtest, fourth_midtest], ignore_index=True)

print("Number of students in the pre test we couldn't identify: ", len(pretest[pretest["id"] == "#N/D"]))
print("Number of students in the post test we couldn't identify: ", len(midtest[midtest["id"] == "#N/D"]))

# Remove unidentified students
pretest = pretest[pretest["id"] != "#N/D"]
midtest = midtest[midtest["id"] != "#N/D"]

# Remove columns irrelevant for analysis
q = [item for i in range(1, 31) for item in (f"Q{i}_correct", f"Q{i}_answer")] + ["possible_match"]
pretest = pretest.drop(q, axis=1)
midtest = midtest.drop(q, axis=1)

# Merge pretest and midtest data
tests = pd.merge(pretest, midtest, on="id", suffixes=("_pre", "_mid"))
all_tests = pd.merge(pretest, midtest, on="id", how="outer")
diff = all_tests.merge(tests, on='id', how='left', indicator=True)
diff = all_tests.merge(tests, on='id', how='left', indicator=True)
missing_rows = diff[diff['_merge'] == 'left_only'].drop('_merge', axis=1)
# Count rows with grade_x = Second and have timestamp_x
second_with_x = (((missing_rows['grade_x'] == 'Second') | (missing_rows['grade_y'] == 'Second')) & 
                 (missing_rows['timestamp_x'].notna())).sum()

# Count rows with grade_x = Second and have timestamp_y  
second_with_y = (((missing_rows['grade_x'] == 'Second') | (missing_rows['grade_y'] == 'Second')) & 
                 (missing_rows['timestamp_y'].notna())).sum()

# Count rows with grade_x = Fourth and have timestamp_x
# fourth_with_x = (((missing_rows['grade_x'] == 'Fourth') | (missing_rows['grade_y'] == 'Fourth')) & 
#                  (missing_rows['timestamp_x'].notna())).sum()

# # Count rows with grade_x = Fourth and have timestamp_y
# fourth_with_y = (((missing_rows['grade_x'] == 'Fourth') | (missing_rows['grade_y'] == 'Fourth')) & 
#                  (missing_rows['timestamp_y'].notna())).sum()

print(f"Second graders who only took pre-test: {second_with_x}")
print(f"Second graders who only took post-test: {second_with_y}")
print("Number of tests to analyze: ", len(tests))

# Calculate overall improvement
tests["overall_change"] = tests["percentage_mid"] - tests["percentage_pre"]
tests["overall_trained_change"] = tests["trained_percentage_mid"] - tests["trained_percentage_pre"]
# Identify experimental vs control groups
experimental_ids = set(student_metrics["service_id"].unique())
tests["group"] = tests["id"].apply(lambda x: "Experimental" if x in experimental_ids else "Control")

# Separate groups
control_group = tests[tests["group"] == "Control"]
experimental_group = tests[tests["group"] == "Experimental"]

print(f"\n=== GROUP SIZES ===")
print(f"Control group size: {len(control_group)}")
print(f"Experimental group size: {len(experimental_group)}")
print(f"Total students analyzed: {len(tests)}")
# Save group assignments
tests.to_csv("group_analysis.csv", index=False)
def ttests(tests, percentages, text = "(Overall)"):
    print(f"\n=== DESCRIPTIVE STATISTICS ===")
    print("Control Group:")
    print(control_group[[percentages[0], percentages[1], percentages[2]]].describe())
    print("\nExperimental Group:")
    print(experimental_group[[percentages[0], percentages[1], percentages[2]]].describe())

    # === WITHIN-GROUP ANALYSES (paired t-tests) ===
    print(f"\n=== WITHIN-GROUP ANALYSES ===")

    # Control group: pre vs post
    control_within_result = ttest_rel(control_group[percentages[1]], control_group[percentages[0]])
    control_mean_change = control_group[percentages[2]].mean()
    print(f"Control Group - Pre to Post Change:")
    print(f"Average improvement: {control_mean_change:.2f} points")
    print(f"t-test result: {'significant' if control_within_result.pvalue < 0.05 else 'not significant'} (p = {control_within_result.pvalue:.4f})")
    print(f"Degrees of freedom: {control_within_result.df}")

    # Experimental group: pre vs post
    exp_within_result = ttest_rel(experimental_group[percentages[1]], experimental_group[percentages[0]])
    exp_mean_change = experimental_group[percentages[2]].mean()
    print(f"\nExperimental Group - Pre to Post Change:")
    print(f"Average improvement: {exp_mean_change:.2f} points")
    print(f"t-test result: {'significant' if exp_within_result.pvalue < 0.05 else 'not significant'} (p = {exp_within_result.pvalue:.4f})")
    print(f"Degrees of freedom: {exp_within_result.df}")

    # === BETWEEN-GROUP ANALYSES (independent t-tests) ===
    print(f"\n=== BETWEEN-GROUP ANALYSES ===")

    # Compare baseline scores (pretest)
    baseline_result = ttest_ind(control_group[percentages[0]], experimental_group[percentages[0]])
    print(f"Baseline (Pretest) Comparison:")
    print(f"Control group mean: {control_group[percentages[0]].mean():.2f}")
    print(f"Experimental group mean: {experimental_group[percentages[0]].mean():.2f}")
    print(f"Difference: {'significant' if baseline_result.pvalue < 0.05 else 'not significant'} (p = {baseline_result.pvalue:.4f})")

    # Compare posttest scores
    posttest_result = ttest_ind(control_group[percentages[1]], experimental_group[percentages[1]])
    print(f"\nPosttest Comparison:")
    print(f"Control group mean: {control_group[percentages[1]].mean():.2f}")
    print(f"Experimental group mean: {experimental_group[percentages[1]].mean():.2f}")
    print(f"Difference: {'significant' if posttest_result.pvalue < 0.05 else 'not significant'} (p = {posttest_result.pvalue:.4f})")

    # Compare improvement scores (key analysis)
    improvement_result = ttest_ind(control_group[percentages[2]], experimental_group[percentages[2]])
    print(f"\nImprovement Comparison (Control vs Experimental):")
    print(f"Control group improvement: {control_mean_change:.2f} points")
    print(f"Experimental group improvement: {exp_mean_change:.2f} points")
    print(f"Difference in improvement: {exp_mean_change - control_mean_change:.2f} points")
    print(f"t-test result: {'significant' if improvement_result.pvalue < 0.05 else 'not significant'} (p = {improvement_result.pvalue:.4f})")

    # === VISUALIZATIONS ===

    # 1. Box plot comparing pre/post scores by group
    plt.figure(figsize=(10, 6))
    plot_data = pd.melt(tests, 
                    id_vars=['group'], 
                    value_vars=[percentages[0], percentages[1]],
                    var_name='Phase', 
                    value_name='Score')
    plot_data['Phase'] = plot_data['Phase'].map({percentages[0]: 'Pre', percentages[1]: 'Post'})

    sns.boxplot(data=plot_data, x='Phase', y='Score', hue='group')
    plt.title(f"Pre vs Post Scores by Group {text}")
    plt.ylabel("Score (%)")
    plt.legend(title="Group")
    plt.tight_layout()
    plt.show()

    # 2. Scatter plot: Pre vs Post by group
    plt.figure(figsize=(8, 6))
    colors = {'Control': 'blue', 'Experimental': 'red'}
    for group in ['Control', 'Experimental']:
        group_data = tests[tests['group'] == group]
        plt.scatter(group_data[percentages[0]], group_data[percentages[1]], 
                color=colors[group], alpha=0.6, label=group)

    # Add diagonal line
    min_score = min(tests[percentages[0]].min(), tests[percentages[1]].min())
    max_score = max(tests[percentages[0]].max(), tests[percentages[1]].max())
    plt.plot([min_score, max_score], [min_score, max_score], 'k--', alpha=0.5)

    plt.xlabel("Pretest Score (%)")
    plt.ylabel("Posttest Score (%)")
    plt.title(f"Pre vs Post Performance by Group {text}")
    plt.legend()
    plt.tight_layout()
    plt.show()

    # 3. Histogram of improvement scores by group
    plt.figure(figsize=(10, 6))
    sns.histplot(data=tests, x=percentages[2], hue='group', kde=True, bins=15, alpha=0.7)
    plt.axvline(0, color='black', linestyle='--', alpha=0.5)
    plt.axvline(control_mean_change, color='blue', linestyle='-', alpha=0.7, label=f'Control Mean: {control_mean_change:.2f}')
    plt.axvline(exp_mean_change, color='red', linestyle='-', alpha=0.7, label=f'Experimental Mean: {exp_mean_change:.2f}')
    plt.title(f"Distribution of Improvement Scores by Group {text}")
    plt.xlabel("Score Improvement (Post - Pre)")
    plt.ylabel("Number of Students")
    plt.legend()
    plt.tight_layout()
    plt.show()

    # 4. Bar plot of mean improvements
    plt.figure(figsize=(8, 6))
    group_means = tests.groupby('group')[percentages[2]].agg(['mean', 'std']).reset_index()
    bars = plt.bar(group_means['group'], group_means['mean'], 
                yerr=group_means['std'], capsize=5, alpha=0.7)
    plt.ylabel("Mean Improvement (Post - Pre)")
    plt.title(f"Average Improvement by Group {text}")
    plt.grid(axis='y', alpha=0.3)

    # Add value labels on bars
    for bar, mean_val in zip(bars, group_means['mean']):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                f'{mean_val:.2f}', ha='center', va='bottom')

    plt.tight_layout()
    plt.show()

    # 5. Individual improvement trajectories
    plt.figure(figsize=(12, 8))
    for group in ['Control', 'Experimental']:
        group_data = tests[tests['group'] == group]
        color = colors[group]
        
        # Plot individual lines
        for _, student in group_data.iterrows():
            plt.plot([1, 2], [student[percentages[0]], student[percentages[1]]], 
                    color=color, alpha=0.3, linewidth=0.5)
        
        # Plot group means
        group_pre_mean = group_data[percentages[0]].mean()
        group_post_mean = group_data[percentages[1]].mean()
        plt.plot([1, 2], [group_pre_mean, group_post_mean], 
                color=color, linewidth=3, label=f'{group} (n={len(group_data)})')

    plt.xlim(0.8, 2.2)
    plt.xticks([1, 2], ['Pre', 'Post'])
    plt.ylabel("Score (%)")
    plt.title(f"Individual Student Trajectories by Group {text}")
    plt.legend()
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.show()

    print(f"\n=== SUMMARY ===")
    print(f"1. Control group {'did' if control_within_result.pvalue < 0.05 else 'did not'} show significant improvement")
    print(f"2. Experimental group {'did' if exp_within_result.pvalue < 0.05 else 'did not'} show significant improvement")
    print(f"3. Groups {'were' if baseline_result.pvalue < 0.05 else 'were not'} significantly different at baseline")
    print(f"4. Experimental group {'did' if improvement_result.pvalue < 0.05 else 'did not'} improve significantly more than control group")

if __name__ == "__main__":

    overall = ["percentage_pre", "percentage_mid", "overall_change"]
    trained = ["trained_percentage_pre", 'trained_percentage_mid', 'overall_trained_change']

    ttests(tests, overall)
    print("=============================================================================")
    ttests(tests, trained, "(Trained)")