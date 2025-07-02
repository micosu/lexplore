import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import seaborn as sns
import matplotlib.pyplot as plt

# Load datasets
date_var = "june11"

# Trained words
trained_fourth = {
    "accumulate",
    "adventurous",
    "assemble",
    "assist",
    "clarify",
    "contrast",
    "cunning",
    "define",
    "deforestation",
    "deliberate",
    "demonstrate",
    "diversity",
    "empathy",
    "evaluate",
    "fragrance",
    "glorious",
    "grudge",
    "justify",
    "lethal",
    "pandemonium",
    "pandemonioum", # incorrect spelling added to match quiz misspelling
    "phenomenon",
    "precise",
    "rebellious",
    "refer",
    "scamper",
    "sturdy",
    "treacherous",
    "twilight",
    "uncertain",
    "wholesome"
}

untrained_fourth = {
    "anticipation",
    "assume",
    "breathtaking",
    "celestial",
    "consume",
    "conviction",
    "deceitful",
    "delirious",
    "emphasis",
    "energetic",
    "enhance",
    "feud",
    "hostile",
    "informal",
    "intense",
    "interpret",
    "luscious",
    "mutter",
    "nuisance",
    "opinionated",
    "prejudice",
    "reliable",
    "resentful",
    "revolt",
    "substantial",
    "superior",
    "thorough",
    "tolerance",
    "velocity",
    "watchful"
}
####################
## PRE-PROCESSING ##
####################
start = datetime.strptime("3/6/2025",'%m/%d/%Y')
end = datetime.strptime("4/17/2025",'%m/%d/%Y')

# Read CSV files
playtime_data = pd.read_csv(f"flag_files/{date_var}/wt_guid__wt_daycycle_event_date___playtime_000.csv")
word_data = pd.read_csv(f"flag_files/{date_var}/wt_guid__word_id___words_learned_000.csv")
# interaction_data = pd.read_csv(f"flag_files/june11/stg_mysql__word_events__interaction_events000.csv")
interaction_data = pd.read_csv(f"flag_files/june11/updated_events.csv")
all_events_data = pd.read_csv(f"flag_files/{date_var}/int_game_events_000.csv")

# Rename columns for easier handling
playtime_data = playtime_data.rename(columns={'wt_daycycle_event_date': 'date'})
all_events_data = all_events_data.rename(columns={'wt_daycycle_event_date': 'date'})
interaction_data = interaction_data.rename(columns={'start_date': 'date'})

# Convert date strings to datetime objects
playtime_data['date'] = pd.to_datetime(playtime_data['date']).dt.date
all_events_data['date'] = pd.to_datetime(all_events_data['date']).dt.date
interaction_data['date'] = pd.to_datetime(interaction_data['date'], errors="coerce").dt.date

# No PopQuiz
interaction_data = interaction_data[~interaction_data['activity_type'].str.startswith('PopQuiz', na=False)]
all_events_data = all_events_data[(all_events_data['event_name'] == 'pnsCompleted') | (all_events_data['event_name'] == 'dailyActivitiesCompleted')]

# Create time-filtered datasets
playtime_data = playtime_data[(playtime_data['date'] >= start.date()) & (playtime_data['date'] <= end.date())]
all_events_data = all_events_data[(all_events_data['date'] >= start.date()) & (all_events_data['date'] <= end.date())]
interaction_data = interaction_data[(interaction_data['date'] >= start.date()) & (interaction_data['date'] <= end.date())]

# Create directory if it doesn't exist
os.makedirs(f"results/{date_var}", exist_ok=True)

##########################
## INITIAL DATA CHECKS ###
##########################
# 0. Identify students with no playtime data
# Get service_ids that are in all_events_data but not in playtime_data
# only_in_dataset = list(set(interaction_data['service_id']) - set(playtime_data['service_id']))
# print(only_in_dataset)

print("Size of datasets")
print(f"Playtime: {len(playtime_data)} rows; PNS Events: {len(all_events_data)} rows; Words Learned: {len(interaction_data)} rows")
print("Number of students in each dataset")
print(f"Playtime: {playtime_data['service_id'].nunique()}; PNS Events: {all_events_data["service_id"].nunique()}; Words Events: {interaction_data["service_id"].nunique()}")


# Save the list of students with no data
# pd.DataFrame({'service_id': only_in_dataset}).to_csv(
#     f"results/{date_var}/no_data.csv", 
#     index=False
# )

quant = .33
print(f"Quantile is {quant:.0%}")
########################
## PLAYTIME ANALYSIS ###
########################
# 1. Aggregate playtime data per student
student_playtime = playtime_data.groupby('service_id').agg({
    'time_played_minutes': ['sum', 'mean', 'count']
}).round(2)

# Flatten column names
student_playtime.columns = ['total_playtime', 'avg_daily_playtime', 'days_active']
student_playtime = student_playtime.reset_index()

playtime_summary = student_playtime['avg_daily_playtime'].describe()
playtime_median = student_playtime['avg_daily_playtime'].median()

# Define threshold for "not engaged" (e.g., bottom 20% of playtime)
playtime_threshold = student_playtime['avg_daily_playtime'].quantile(quant)

not_playing_students = student_playtime[
    student_playtime['avg_daily_playtime'] <= playtime_threshold
]
print(f"\nNot Engaged Students (Less Playtime):")
print(f"Playtime threshold for 'not engaged': {playtime_threshold:.2f} minutes")
print(f"Number of 'not engaged' students: {len(not_playing_students)}")

# Define threshold for "less days played"
days_played_threshold = student_playtime['days_active'].quantile(quant)
days_summary = student_playtime['days_active'].describe()
print(days_summary)
days_students = student_playtime[
    student_playtime['days_active'] <= days_played_threshold
]
print(f"\nNot Engaged Students (Less Days):")
print(f"Playtime threshold for 'not engaged': {days_played_threshold:.2f} days")
print(f"Number of 'not engaged' students: {len(days_students)}")
########################
## PNS ANALYSIS ###
########################
# Calculate student activities
# First group by both service_id AND date
daily_activities = all_events_data.groupby(['service_id', 'date']).agg({
    'event_name': lambda x: sum(x == 'pnsCompleted')
}).rename(columns={'event_name': 'daily_pns'}).reset_index()

# Add daily activities completed count
daily_activities['daily_activities'] = all_events_data.groupby(['service_id', 'date'])['event_name'].apply(
    lambda x: sum(x == 'dailyActivitiesCompleted')
).values

# Then group just by service_id to get student-level stats
student_activities = daily_activities.groupby('service_id').agg({
    'daily_pns': ['sum', 'mean'],
    'daily_activities': 'sum'
}).round(2)

# Flatten column names
student_activities.columns = ['total_pns', 'avg_daily_pns', 'total_days_completed']
student_activities = student_activities.reset_index()

# Summary Statistics
pns_summary = student_activities['avg_daily_pns'].describe()
pns_median = student_activities['avg_daily_pns'].median()

daily_summary = student_activities['total_days_completed'].describe()
daily_median = student_activities['total_days_completed'].median()

# Identify Not Engaged Students (less activities)
# Define threshold for "not engaged" (e.g., bottom 20% of completion)
pns_threshold = student_activities['avg_daily_pns'].quantile(quant)

not_pnsing_students = student_activities[
    student_activities['avg_daily_pns'] > pns_threshold
]

print(f"\nNot Engaged Students (Less PNS):")
print(f"PNS threshold for 'not engaged': {pns_threshold:.2f} activities")
print(f"Number of 'not engaged' students: {len(not_pnsing_students)}")

# Identify students who have a low completion rate of all daily activities
daily_nonzero = student_activities[student_activities['total_days_completed'] > 0]['total_days_completed']
daily_threshold = daily_nonzero.quantile(quant)

not_dailying_students = student_activities[
    (student_activities['total_days_completed'] > 0) & 
    (student_activities['total_days_completed'] <= daily_threshold)
]

####################
## WORD ANALYSES ###
####################


def calculate_word_metrics(df):
    """Calculate word exposure metrics for each student"""
    
    # Group by service_id and target_id to count interactions per word per student
    word_interactions = df.groupby(['service_id', 'target_id']).size().reset_index(name='interaction_count')

    word_interactions['is_trained'] = word_interactions['target_id'].isin(trained_fourth)
    word_interactions['is_untrained'] = word_interactions['target_id'].isin(untrained_fourth)
    word_interactions['is_random'] = ~word_interactions['target_id'].isin(trained_fourth | untrained_fourth)
    word_interactions['trained_4plus'] = (word_interactions['is_trained']) & (word_interactions['interaction_count'] >= 4)
    
    # Calculate metrics per student
    student_word_metrics = word_interactions.groupby('service_id').agg({
        'target_id': 'nunique',  # Number of unique words exposed to
        'interaction_count': ['mean', lambda x: sum(x >= 4)],  # Average interactions per word + count with 4+ exposures
        'is_trained': 'sum',
        'is_untrained': 'sum',
        'is_random': 'sum',
        'trained_4plus': 'sum'  # Count of trained words with 4+ interactions
    }).round(2)
    
    # Flatten column names and rename for clarity
    student_word_metrics.columns = ['unique_words_exposed', 'avg_interactions_per_word', 'words_with_4plus_exposures', 
                                    'trained_count', 'untrained_count', 'random_count', 'trained_with_4plus_exposures']
    student_word_metrics = student_word_metrics.reset_index()
    
    return student_word_metrics, word_interactions


student_word_metrics, word_interactions = calculate_word_metrics(interaction_data)

print(f"\nWord Exposure Analysis Results:")
print(f"Number of students analyzed: {len(student_word_metrics)}")
# print(f"\nSample results:")
# print(student_word_metrics.head(10))

# Additional analysis: summary statistics
print(f"\nSummary Statistics:")
print(f"Unique words exposed - Mean: {student_word_metrics['unique_words_exposed'].mean():.2f}, Median: {student_word_metrics['unique_words_exposed'].median():.2f}")
print(f"Avg interactions per word - Mean: {student_word_metrics['avg_interactions_per_word'].mean():.2f}, Median: {student_word_metrics['avg_interactions_per_word'].median():.2f}")
print(f"Words with 4+ exposures - Mean: {student_word_metrics['words_with_4plus_exposures'].mean():.2f}, Median: {student_word_metrics['words_with_4plus_exposures'].median():.2f}")
print(f"Number of trained words exposed - Mean: {student_word_metrics['trained_count'].mean():.2f}, Median: {student_word_metrics['trained_count'].median():.2f}")
print(f"Number of trained words with > 4 exposures - Mean: {student_word_metrics['trained_with_4plus_exposures'].mean():.2f}, Median: {student_word_metrics['trained_with_4plus_exposures'].median():.2f}")
print(f"Number of untrained words exposed - Mean: {student_word_metrics['untrained_count'].mean():.2f}, Median: {student_word_metrics['untrained_count'].median():.2f}")
print(f"Number of random words exposed - Mean: {student_word_metrics['random_count'].mean():.2f}, Median: {student_word_metrics['random_count'].median():.2f}")
# Identify students who learned less words
low_words_threshold = student_word_metrics['words_with_4plus_exposures'].quantile(quant)
low_words_students = student_word_metrics[student_word_metrics['words_with_4plus_exposures'] <= low_words_threshold]

print(f"\nStudents with Low Word Exposure (bottom {quant:.0%}):")
print(f"Threshold: {low_words_threshold:.0f} words or less with > 4 exposures")
print(f"Number of students: {len(low_words_students)}")

# Identify students with low word exposure
low_exposure_threshold = student_word_metrics['unique_words_exposed'].quantile(quant)
low_exposure_students = student_word_metrics[student_word_metrics['unique_words_exposed'] <= low_exposure_threshold]

print(f"\nStudents with Low Word Exposure (bottom {quant:.0%}):")
print(f"Threshold: {low_exposure_threshold:.0f} unique words")
print(f"Number of students: {len(low_exposure_students)}")

# Identify students with low interaction rates
low_interaction_threshold = student_word_metrics['avg_interactions_per_word'].quantile(quant)
low_interaction_students = student_word_metrics[student_word_metrics['avg_interactions_per_word'] <= low_interaction_threshold]

print(f"\nStudents with Low Interaction Rates (bottom {quant:.0%}):")
print(f"Threshold: {low_interaction_threshold:.2f} avg interactions per word")
print(f"Number of students: {len(low_interaction_students)}")

# Optional: Get detailed breakdown by activity type
activity_breakdown = interaction_data.groupby(['service_id', 'activity_type']).agg({
    'target_id': 'nunique',
    'event_id': 'count'
}).reset_index()
activity_breakdown.columns = ['service_id', 'activity_type', 'unique_words', 'total_interactions']

# print(f"\nActivity Type Breakdown (first 10 rows):")
# print(activity_breakdown.head(10))
##############
## SUMMARY ###
##############

student_metrics = student_playtime.merge(student_activities, on='service_id', how='left')
student_metrics = student_metrics.merge(student_word_metrics, on='service_id', how='left')

# Add flag columns
# student_metrics['is_inactive'] = student_metrics['service_id'].isin(inactive_students['service_id'])
# student_metrics['is_never_completed'] = student_metrics['service_id'].isin(no_completion_students['service_id'])
# student_metrics['is_playing_less'] = student_metrics['service_id'].isin(not_playing_students['service_id'])
# student_metrics['is_pnsing_less'] = student_metrics['service_id'].isin(not_pnsing_students['service_id'])
# student_metrics['is_finishing_less'] = student_metrics['service_id'].isin(not_dailying_students['service_id'])



########################
######## OUTPUT ########
########################

# Create a combined dataset with all metrics

# Output the combined metrics for all students

student_metrics.to_csv(f"results/{date_var}/student_metrics.csv", index=False)

# Histogram for days_active
sns.histplot(student_metrics['days_active'], bins=3, kde=False)
plt.title('Distribution of Days Active')
plt.xlabel('Days Active')
plt.ylabel('Number of Students')
plt.show()

# Histogram for words_with_4plus_exposures
sns.histplot(student_metrics['words_with_4plus_exposures'], bins=3, kde=False)
plt.title('Distribution of Words with 4+ Exposures')
plt.xlabel('Words with ≥4 Exposures')
plt.ylabel('Number of Students')
plt.show()
# Find top concerning students
# top_concerning_students = student_metrics.sort_values(
#     by=['flags_count', 'is_playing_less', 'is_pnsing_less', 'is_finishing_less', 'is_inactive'],
#     ascending=[False, False, False, False, False]
# ).head(10)

# print("\nTop 10 Most Concerning Students:")
# print(top_concerning_students[['service_id', 'flags_count', 'total_playtime', 'avg_daily_playtime']])