import pandas as pd
from scipy.stats import ttest_rel, ttest_1samp
import matplotlib.pyplot as plt
import seaborn as sns

# Load the files
second_pretest = pd.read_csv("pre_tests/Second_Grading_Results_v2.csv")
second_midtest = pd.read_csv("mid_tests/Second_Grading_Results_v2.csv")

fourth_pretest = pd.read_csv("pre_tests/Fourth_Grading_Results.csv")
fourth_midtest = pd.read_csv("mid_tests/Fourth_Grading_Results.csv")

second_pretest['grade'] = 'Second'
fourth_pretest['grade'] = 'Fourth'
second_midtest['grade'] = 'Second'
fourth_midtest['grade'] = 'Fourth'

# DIAGNOSTIC CODE - Check for duplicates before combining
# print("=== DUPLICATE ANALYSIS ===")
# print("Second grade pretest duplicates:", second_pretest[second_pretest["id"] != "#N/D"]['id'].duplicated().sum())
# print("Second grade midtest duplicates:", second_midtest[second_midtest["id"] != "#N/D"]['id'].duplicated().sum())
# print("Fourth grade pretest duplicates:", fourth_pretest[fourth_pretest["id"] != "#N/D"]['id'].duplicated().sum())
# print("Fourth grade midtest duplicates:", fourth_midtest[fourth_midtest["id"] != "#N/D"]['id'].duplicated().sum())

# Check for overlapping IDs between grades
# second_ids = set(second_pretest['id'].tolist() + second_midtest['id'].tolist())
# fourth_ids = set(fourth_pretest['id'].tolist() + fourth_midtest['id'].tolist())
# overlapping_ids = second_ids.intersection(fourth_ids)
# print(f"IDs that appear in both grades: {len(overlapping_ids)}")
# if overlapping_ids:
#     print(f"Overlapping IDs: {list(overlapping_ids)[:10]}...")  # Show first 10

# Combine pretests
pretest = pd.concat([second_pretest, fourth_pretest], ignore_index=True)

# Combine midtests  
midtest = pd.concat([second_midtest, fourth_midtest], ignore_index=True)

# pretest = fourth_pretest
# midtest = fourth_midtest

# print("\n=== AFTER COMBINING ===")
# print("Total pretest duplicates:", pretest['id'].duplicated().sum())
# print("Total midtest duplicates:", midtest['id'].duplicated().sum())

print("Number of students in the pre test we couldn't identify: ", len(pretest[pretest["id"] == "#N/D"]))
print("Number of students in the post test we couldn't identify: ", len(midtest[midtest["id"] == "#N/D"]))

pretest = pretest[pretest["id"] != "#N/D"]
midtest = midtest[midtest["id"] != "#N/D"]

# Check unique IDs after filtering
# print("Unique pretest IDs:", pretest['id'].nunique())
# print("Unique midtest IDs:", midtest['id'].nunique())

# Remove columns irrelevant for analysis
q = [item for i in range(1, 31) for item in (f"Q{i}_correct", f"Q{i}_answer")] + ["possible_match"]
pretest = pretest.drop(q, axis = 1)
midtest = midtest.drop(q, axis = 1)

all_tests = pd.merge(pretest, midtest, on="id", how="outer")

tests = pd.merge(pretest, midtest, on="id", suffixes=("_pre", "_mid"))

diff = all_tests.merge(tests, on='id', how='left', indicator=True)
missing_rows = diff[diff['_merge'] == 'left_only'].drop('_merge', axis=1)
# Count rows with grade_x = Second and have timestamp_x
second_with_x = (((missing_rows['grade_x'] == 'Second') | (missing_rows['grade_y'] == 'Second')) & 
                 (missing_rows['timestamp_x'].notna())).sum()

# Count rows with grade_x = Second and have timestamp_y  
second_with_y = (((missing_rows['grade_x'] == 'Second') | (missing_rows['grade_y'] == 'Second')) & 
                 (missing_rows['timestamp_y'].notna())).sum()

# Count rows with grade_x = Fourth and have timestamp_x
fourth_with_x = (((missing_rows['grade_x'] == 'Fourth') | (missing_rows['grade_y'] == 'Fourth')) & 
                 (missing_rows['timestamp_x'].notna())).sum()

# Count rows with grade_x = Fourth and have timestamp_y
fourth_with_y = (((missing_rows['grade_x'] == 'Fourth') | (missing_rows['grade_y'] == 'Fourth')) & 
                 (missing_rows['timestamp_y'].notna())).sum()

print(f"Second graders who only took pre-test: {second_with_x}")
print(f"Second graders who only took post-test: {second_with_y}")
print(f"Fourth graders who only took pre-test: {fourth_with_x}")
print(f"Fourth graders who only took post-test: {fourth_with_y}")

missing_rows.to_csv(f"missing_data.csv", index=False)
print("\n=== FINAL RESULTS ===")
print("Number of tests unable to be matched between pretest and posttest: ", len(all_tests) - len(tests))
print("Number of tests to analyze: ", len(tests))

# Additional diagnostics
# print("Unique IDs in final merged dataset:", tests['id'].nunique())
print("Total rows in final dataset:", len(tests))

# Check if there are still duplicates in final dataset
if tests['id'].duplicated().sum() > 0:
    print(f"WARNING: {tests['id'].duplicated().sum()} duplicate IDs in final dataset!")
    duplicate_ids = tests[tests['id'].duplicated(keep=False)]['id'].unique()
    print(f"Duplicate IDs: {duplicate_ids[:5]}...")  # Show first 5


# Descriptive Statistics
print(tests[tests.filter(like="percentage").columns].describe())
# T-tests
overall_result = ttest_rel(tests["percentage_mid"], tests["percentage_pre"])
tests["overall_change"] = tests.apply(lambda row: row.percentage_mid - row.percentage_pre, axis = 1)
print(f"""On average, scores between the pre-test and post-test improved by {tests["overall_change"].mean()} points.
The t-test revealed this difference {'is' if overall_result.pvalue < .05 else 'is not'} significant, (p-value = {overall_result.pvalue}) 
with {overall_result.df} degrees of freedom (one less than sample size).""")

trained_result = ttest_rel(tests["trained_percentage_mid"], tests["trained_percentage_pre"])
print(f"""On average, scores between the pre-test and post-test for trained questions improved by {tests["trained_percentage_mid"].mean() - tests["trained_percentage_pre"].mean()} points.
The t-test revealed this difference {'is' if trained_result.pvalue < .05 else 'is not'} significant, (p-value = {trained_result.pvalue}) 
with {trained_result.df} degrees of freedom (one less than sample size).""")

trained_result = ttest_rel(tests["total_trained_correct_mid"], tests["total_trained_correct_pre"])
print(f"""On average, scores between the pre-test and post-test for trained questions improved by {tests["total_trained_correct_mid"].mean() - tests["total_trained_correct_pre"].mean()} questions.
The t-test revealed this difference {'is' if trained_result.pvalue < .05 else 'is not'} significant, (p-value = {trained_result.pvalue}) 
with {trained_result.df} degrees of freedom (one less than sample size).""")

untrained_result = ttest_rel(tests["untrained_percentage_mid"], tests["untrained_percentage_pre"])
print(f"""On average, scores between the pre-test and post-test for untrained questions improved by {tests["untrained_percentage_mid"].mean() - tests["untrained_percentage_pre"].mean()} points.
The t-test revealed this difference {'is' if untrained_result.pvalue < .05 else 'is not'} significant, (p-value = {untrained_result.pvalue}) 
with {untrained_result.df} degrees of freedom (one less than sample size).""")


# T-test for seeing if trained improvement is significantly more than untrained
tests["trained_change"] = tests.apply(lambda row: row.trained_percentage_mid - row.trained_percentage_pre, axis = 1)
tests["untrained_change"] = tests.apply(lambda row: row.untrained_percentage_mid - row.untrained_percentage_pre, axis = 1)
print("Now, you may be wondering if the difference in improvements between trained and untrained questions from the pre-test to post-test is significant.")
delta_result = ttest_rel(tests["trained_change"], tests["untrained_change"])
print(f"""Well, I'm here to tell you.  On average, the difference between trained and untrained performance improvements between the 
pretest and posttest is {(tests["trained_change"] - tests["untrained_change"]).mean()} points. The t-test revealed this difference {'is' if delta_result.pvalue < .05 else 'is not'} significant, (p-value = {delta_result.pvalue}) 
with {delta_result.df} degrees of freedom (one less than sample size).""")

tests.to_csv(f"test_metrics.csv", index=False)

### Plots

# Melt the data for seaborn
df_melted = pd.melt(tests, value_vars=['percentage_pre', 'percentage_mid'],
                    var_name='Phase', value_name='Score')

plt.figure(figsize=(6, 5))
sns.boxplot(data=df_melted, x='Phase', y='Score')
plt.title("Pretest vs Posttest Scores")
plt.ylabel("Score")
plt.xlabel("")
plt.tight_layout()
plt.show()

plt.figure(figsize=(6, 6))
sns.scatterplot(x=tests['percentage_pre'], y=tests['percentage_mid'])
plt.plot([tests['percentage_pre'].min(), tests['percentage_pre'].max()],
         [tests['percentage_pre'].min(), tests['percentage_pre'].max()],
         color='gray', linestyle='--')  # y=x line
plt.xlabel("Pretest Score")
plt.ylabel("Posttest Score")
plt.title("Student Performance: Pre vs Post")
plt.tight_layout()
plt.show()

tests['delta_total'] = tests['percentage_mid'] - tests['percentage_pre']

plt.figure(figsize=(6, 5))
sns.histplot(tests['delta_total'], bins=15, kde=True)
plt.axvline(0, color='red', linestyle='--')
plt.title("Distribution of Improvement (Post - Pre)")
plt.xlabel("Score Improvement")
plt.ylabel("Number of Students")
plt.tight_layout()
plt.show()

### Trained vs Untrained Plots
# Box Plot
score_data = tests[['percentage_pre', 'percentage_mid', 'trained_percentage_pre', 'trained_percentage_mid', 'untrained_percentage_pre', 'untrained_percentage_mid']]
score_data = score_data.rename(columns={
    'percentage_pre': 'Pre: Overall',
    'percentage_mid': 'Post: Overall',
    'trained_percentage_pre': 'Pre: Trained',
    'trained_percentage_mid': 'Post: Trained',
    'untrained_percentage_pre': 'Pre: Untrained',
    'untrained_percentage_mid': 'Post: Untrained'
})

df_melted = score_data.melt(var_name='Condition', value_name='Score')

plt.figure(figsize=(10, 6))
sns.boxplot(data=df_melted, x='Condition', y='Score')
plt.title("Score Distributions: Pre vs Post")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()


# Scatterplot
fig, axs = plt.subplots(1, 2, figsize=(12, 5))

# Trained
sns.scatterplot(x=tests['trained_percentage_pre'], y=tests['trained_percentage_mid'], ax=axs[0])
axs[0].plot([tests['trained_percentage_pre'].min(), tests['trained_percentage_pre'].max()],
            [tests['trained_percentage_pre'].min(), tests['trained_percentage_pre'].max()],
            'k--')
axs[0].set_title("Trained Items: Pre vs Post")
axs[0].set_xlabel("Pre")
axs[0].set_ylabel("Post")

# Untrained
sns.scatterplot(x=tests['untrained_percentage_pre'], y=tests['untrained_percentage_mid'], ax=axs[1])
axs[1].plot([tests['untrained_percentage_pre'].min(), tests['untrained_percentage_pre'].max()],
            [tests['untrained_percentage_pre'].min(), tests['untrained_percentage_pre'].max()],
            'k--')
axs[1].set_title("Untrained Items: Pre vs Post")
axs[1].set_xlabel("Pre")
axs[1].set_ylabel("Post")

plt.tight_layout()
plt.show()

# Histograms
plt.figure(figsize=(10, 5))
sns.histplot(tests['trained_change'], color='blue', label='Trained', kde=True, bins=15)
sns.histplot(tests['untrained_change'], color='orange', label='Untrained', kde=True, bins=15)
plt.axvline(0, color='black', linestyle='--')
plt.title("Improvement Scores: Trained vs Untrained")
plt.xlabel("Score Improvement")
plt.ylabel("Number of Students")
plt.legend()
plt.tight_layout()
plt.show()

# Histogram of change trained vs untrained
tests['delta_diff'] = tests['trained_change'] - tests['untrained_change']

plt.figure(figsize=(6, 5))
sns.histplot(tests['delta_diff'], bins=15, kde=True)
plt.axvline(0, color='red', linestyle='--')
plt.title("Difference in Improvement: Trained - Untrained")
plt.xlabel("Improvement Advantage (Trained vs Untrained)")
plt.ylabel("Number of Students")
plt.tight_layout()
plt.show()