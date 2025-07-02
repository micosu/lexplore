import statsmodels.api as sm
from statsmodels.formula.api import ols
import pandas as pd

# Example assumes you have a 'gain_score' column (post - pre)

student_metrics = pd.read_csv("during_study/results/june11/student_metrics.csv")
student_scores = pd.read_csv("test_metrics.csv")

all_metrics = student_metrics.merge(student_scores, left_on="service_id", right_on="id", how="inner")

print(f"Size of student metrics: {len(student_metrics)}; Size of Student Scores: {len(student_scores)}; Size of combined: {len(all_metrics)}")

all_metrics['exposure_group'] = pd.qcut(all_metrics['words_with_4plus_exposures'], q=3, labels=['low', 'med', 'high'])
all_metrics['days_group'] = pd.qcut(all_metrics['days_active'], q=3, labels=['low', 'med', 'high'])
all_metrics['playtime_group'] = pd.qcut(all_metrics['total_playtime'], q=3, labels=['low', 'med', 'high'])
all_metrics['pns_group'] = pd.qcut(all_metrics['total_pns'], q=3, labels=['low', 'med', 'high'])
all_metrics['days_completed_group'] = pd.qcut(all_metrics['total_days_completed'], q=3, labels=['low', 'med', 'high'])
all_metrics['unique_words_group'] = pd.qcut(all_metrics['unique_words_exposed'], q=3, labels=['low', 'med', 'high'])
all_metrics['avg_interactions_group'] = pd.qcut(all_metrics['avg_interactions_per_word'], q=3, labels=['low', 'med', 'high'])
all_metrics['trained_words_group'] = pd.qcut(all_metrics['trained_count'], q=3, labels=['low', 'med', 'high'])
all_metrics['trained_with_4plus_group'] = pd.qcut(all_metrics['trained_with_4plus_exposures'], q=3, labels=['low', 'med', 'high'])

all_metrics.to_csv(f"all_metrics.csv", index=False)
# total_days_completed,unique_words_exposed,avg_interactions_per_word,words_with_4plus_exposures
# Column names: overall_change,trained_change,untrained_change
print("Best Results")
print("Average Interactions per Word")
model = ols('overall_change ~ C(avg_interactions_group)', data=all_metrics).fit()
anova_table = sm.stats.anova_lm(model, typ=2)
print(anova_table)

print("Words w/ 4+ exposures")
model = ols('overall_change ~ C(trained_with_4plus_group)', data=all_metrics).fit()
anova_table = sm.stats.anova_lm(model, typ=2)
print(anova_table)

print("Trained words")
model = ols('overall_change ~ C(trained_words_group)', data=all_metrics).fit()
anova_table = sm.stats.anova_lm(model, typ=2)
print(anova_table)

print("Activities")
model = ols('overall_change ~ C(pns_group)', data=all_metrics).fit()
anova_table = sm.stats.anova_lm(model, typ=2)
print(anova_table)

print("Playtime")
model = ols('overall_change ~ C(playtime_group)', data=all_metrics).fit()
anova_table = sm.stats.anova_lm(model, typ=2)
print(anova_table)

print("Days Active")
model = ols('overall_change ~ C(days_active)', data=all_metrics).fit()
anova_table = sm.stats.anova_lm(model, typ=2)
print(anova_table)