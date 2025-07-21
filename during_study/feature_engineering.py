import pandas as pd
from sklearn.impute import KNNImputer
import numpy as np
import matplotlib.pyplot as plt
import ast
import seaborn as sns

student_metrics = pd.read_csv(f"new_results/june11/student_metrics.csv")
new_metrics = pd.read_csv(f"new_results/june11/student_metrics_mod.csv")
# new_metrics = student_metrics

#########################################################################
# Pre-processing

# Students who are missing values in these columns likely never got to these activities.  So I will give them a 0
# for total time
columns_to_fill = ['assemblesyllables_totaltime', 'matchcollocations_totaltime', 
                   'matchsentenceblank_totaltime', 'matchsynonyms_totaltime',
                   'popquizcollocation_totaltime', 'popquizsynonym_totaltime']
new_metrics[columns_to_fill] = new_metrics[columns_to_fill].fillna(0)
# Generate a better metric for total time

## for the 21 students missing from words_learned, impute them with 10th percentile to be conservative
word_learning_cols = ['first_exposure_wrong', 'second_exposure_wrong', 'avg_exposure_attempts', 
                     'total_exposures_wrong', 'avg_wic_attempts', 'total_wic_wrong', 'total_wrong']
new_metrics['imputed_word_data'] = new_metrics['first_exposure_wrong'].isna()

# Get 10th percentile from students who have data
percentile_values = new_metrics[word_learning_cols].quantile(0.1)

for col in word_learning_cols:
    new_metrics[col] = new_metrics[col].fillna(percentile_values[col])
# Some students don't have total_playtime data, but we can use nearest neighbors to impute their values
# 5d52e4b119ca9b0c7dde876b total_playtime -> 141.41 days_active -> 11.4 avg_daily_pns -> 11.7
# 5e7ced16d590eb03461053ae total_playtime -> 279.522 days_active -> 12.8 avg_daily_pns -> 16.69

# features_for_imputation = ['avg_daily_pns', 'improved_learning_time', 'total_playtime', 'days_active', 'total_pns', 'missions_completed']
# imputer = KNNImputer(n_neighbors=5)
# new_metrics[features_for_imputation] = imputer.fit_transform(new_metrics[features_for_imputation])
# new_metrics.to_csv("new_results/june11/student_metrics_mod.csv", index=False)
#########################################################################
# New Features

### Engagement and Efficiency Metrics
new_metrics["improved_learning_time"] = (new_metrics['assemblesyllables_totaltime'] +
                                        new_metrics['matchcollocations_totaltime'] + 
                                        new_metrics['matchsentenceblank_totaltime'] + 
                                        new_metrics['matchsynonyms_totaltime'] +
                                        new_metrics['popquizcollocation_totaltime'] + 
                                        new_metrics['popquizsynonym_totaltime']).round(2)

# sns.histplot(new_metrics["improved_learning_time"], bins='auto', kde=False) 
# plt.title('Improved Learning Time')
# plt.xlabel('Sum of time spent in different learning activities') 
# plt.ylabel('Number of Students') 
# plt.show()
improved_learning_summary = new_metrics["improved_learning_time"].describe()
print("Summary of learning time: ", improved_learning_summary)

new_metrics["avg_response_time"] = (new_metrics["improved_learning_time"] / new_metrics["total_pns"])
avg_response_summary = new_metrics["avg_response_time"].describe()
print("Summary of Average Response Time: ", avg_response_summary)
# sns.histplot(new_metrics["avg_response_time"], bins='auto', kde=False) 
# plt.title('Average Response Time')
# plt.xlabel('Learning Time / Total PNS') 
# plt.ylabel('Number of Students') 
# plt.show()

new_metrics["learning_focus"] = (new_metrics["improved_learning_time"] / (new_metrics["total_playtime"] * 60))
learning_focus_summary = new_metrics["learning_focus"].describe()
print("Summary of Learning Focus: ", learning_focus_summary)
# sns.histplot(new_metrics["learning_focus"], bins='auto', kde=False) 
# plt.title('Learning Focus')
# plt.xlabel('Learning Time / Total Playtime') 
# plt.ylabel('Number of Students') 
# plt.show()
new_metrics['mission_persistence'] = (new_metrics["missions_completed"] / new_metrics["missions_started"])
mission_persistence_summary = new_metrics["mission_persistence"].describe()
print("Summary of Mission Persistence: ", mission_persistence_summary)
# sns.histplot(new_metrics["mission_persistence"], bins='auto', kde=False) 
# plt.title('Mission Persistence')
# plt.xlabel('Completed Missions / Started Missions (%)') 
# plt.ylabel('Number of Students') 
# plt.show()
new_metrics["learning_efficiency"] = (new_metrics["total_pns"] / new_metrics["improved_learning_time"])
learning_efficiency_summary = new_metrics["learning_efficiency"].describe()
print("Summary of Learning Efficiency: ", learning_efficiency_summary)
# sns.histplot(new_metrics["learning_efficiency"], bins='auto', kde=False) 
# plt.title('Learning Efficiency')
# plt.xlabel('Total Activities / Learning Time') 
# plt.ylabel('Number of Students') 
# plt.show()
### Learning Effectiveness
new_metrics["first_try_success"] = (1 - new_metrics["first_exposure_wrong"] / new_metrics["unique_words_exposed"])

new_metrics["accuracy"] = new_metrics["accuracy"]
accuracy_summary = new_metrics["accuracy"].describe()
print("Summary of Accuracy: ", accuracy_summary)
# sns.histplot(new_metrics["accuracy"], bins='auto', kde=False) 
# plt.title('Accuracy')
# plt.xlabel('Total Correct / Total pns') 
# plt.ylabel('Number of Students') 
# plt.show()
# new_metrics["accuracy_per_exposure"] = (new_metrics["accuracy"] / new_metrics["total_pns"])
# accuracy_per_exposure_summary = new_metrics["accuracy_per_exposure"].describe()
# print("Summary of Accuracy per Exposure: ", accuracy_per_exposure_summary)
# sns.histplot(new_metrics["accuracy_per_exposure"], bins='auto', kde=False) 
# plt.title('Accuracy per Exposure')
# plt.xlabel('Accuracy / Average Interactions per Word') 
# plt.ylabel('Number of Students') 
# plt.show()
### Behavioral Patterns
new_metrics["gaming_behavior"] = (new_metrics["total_wrong"] / new_metrics["improved_learning_time"])
gaming_behavior_summary = new_metrics["gaming_behavior"].describe()
print("Summary of Gaming Behavior: ", gaming_behavior_summary)
# sns.histplot(new_metrics["gaming_behavior"], bins='auto', kde=False) 
# plt.title('Potential Gaming')
# plt.xlabel('Wrong Attempts / Learning Time') 
# plt.ylabel('Number of Students') 
# plt.show()
new_metrics["speed_vs_accuracy"] = (new_metrics["accuracy"] / new_metrics["avg_response_time"])
speed_vs_accuracy_summary = new_metrics["speed_vs_accuracy"].describe()
print("Summary of Speed vs Accuracy: ", speed_vs_accuracy_summary)
# sns.histplot(new_metrics["speed_vs_accuracy"], bins='auto', kde=False) 
# plt.title('Speed vs Accuracy')
# plt.xlabel('Accuracy / Average Response Time') 
# plt.ylabel('Number of Students') 
# plt.show()
new_metrics["early_errors"] = ((new_metrics["first_exposure_wrong"] + new_metrics["second_exposure_wrong"]) / 2)
early_errors_summary = new_metrics["early_errors"].describe()
print("Summary of Early Errors: ", early_errors_summary)
# sns.histplot(new_metrics["early_errors"], bins='auto', kde=False) 
# plt.title('Early Errors')
# plt.xlabel('First Exposure Wrong + Second Exposure Wrong / 2') 
# plt.ylabel('Number of Students') 
# plt.show()
# students who never did a race 
new_metrics["race_ratio"] = (new_metrics["total_days_completed"].fillna(0) / new_metrics["races_started"].fillna(0).replace(0, np.nan))
race_ratio_summary = new_metrics["race_ratio"].describe()
print("Summary of Race Ratios: ",race_ratio_summary)
# sns.histplot(new_metrics["race_ratio"], bins='auto', kde=False) 
# plt.title('Race Ratio')
# plt.xlabel('Days Completed / Races Started') 
# plt.ylabel('Number of Students') 
# plt.show()
### Word Learning depth
new_metrics["trained_exposures"] = (new_metrics["trained_count"] / 30)
new_metrics["trained_learned"] = (new_metrics["learned_trained_count"].fillna(0) / 30)
trained_learned_summary = new_metrics["trained_learned"].describe()
print("Summary of Learned Trained Words: ", trained_learned_summary)
# sns.histplot(new_metrics["trained_learned"], bins='auto', kde=False) 
# plt.title('Trained Words Learned')
# plt.xlabel('Words Learned / Total Trained Words Possible') 
# plt.ylabel('Number of Students') 
# plt.show()
# new_metrics["deep_learning"] = (new_metrics["words_with_4plus_exposures"] / new_metrics["unique_words_exposed"])
columns_to_keep = [
    'service_id',
    # Learning Time & Efficiency
    "improved_learning_time",  "avg_response_time",  "learning_focus", "learning_efficiency",
    # Mission & Persistence
    "mission_persistence",
    # Learning Effectiveness
    "first_try_success", "accuracy", # "accuracy_per_exposure",
    # Behavioral Patterns
    "gaming_behavior", "speed_vs_accuracy",  "early_errors", "race_ratio",
    # Word Learning Depth
    "trained_exposures", "trained_learned", # "deep_learning",
    # Flag if data was imputed
    'imputed_word_data'
]

# Keep only these columns
new_metrics = new_metrics[columns_to_keep]
new_metrics.to_csv("new_results/june11/engineered_metrics.csv", index=False)

#########################################################################
# Archived Code
# learning_time_outliers = student_metrics[student_metrics["total_learning_time"] > 2000]
# print(f"Number of students who spent more than {2000 / 60} minutes learning: {len(learning_time_outliers)} according to ")

# really_suspicious = student_metrics[student_metrics["total_learning_time"] / 60 > student_metrics["total_playtime"]]
# print(f"Number of students who 'learned' for longer than they played the game: {len(really_suspicious)}")
# columns_to_keep = ['service_id', 'total_playtime', 'total_learning_time', 'total_pns', 'days_active']

# really_suspicious = really_suspicious[columns_to_keep]
# really_suspicious.to_csv(f"new_results/june11/inspect.csv", index=False)