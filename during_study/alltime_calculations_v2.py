import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import seaborn as sns
import matplotlib.pyplot as plt
import ast

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
trained_second = {
    "recover", "calm", "stormy", "struggle", "telescope", "disaster", "tropical", "delicious", "guide", "competition", "gentle", "improve", "pressure", "peaceful", "feast", "important", "communicate", "purpose", "repair", "howl", "comfort", "effect", "wreckage", "habit", "speechless", "ancient", "ripe", "hollow", "enormous", "unmistakable" }

untrained_second = { 
    "explore", "jealous", "patient", "unusual", "scent", "opinion", "balance", "experiment", "complete", "imagine", "natural", "unkind", "powerful", "impatient", "comfortable", "successful", "gobble", "wise", "describe", "method", "invent", "defeat", "relax", "effort", "voyage", "conversation", "dreamy", "hearty", "steep", "overgrown" }
####################
## PRE-PROCESSING ##
####################
start = datetime.strptime("3/6/2025",'%m/%d/%Y')
end = datetime.strptime("4/17/2025",'%m/%d/%Y')

# Read CSV files
exposures_data = pd.read_csv(f"flag_files/{date_var}/exposures_per_day.csv")
all_events_data = pd.read_csv(f"flag_files/{date_var}/int_game_events_000.csv")
mission_data = pd.read_csv(f"flag_files/{date_var}/mission_counts.csv")
playtime_data = pd.read_csv(f"flag_files/{date_var}/playtime.csv")
pns_data = pd.read_csv(f"flag_files/{date_var}/pns_daily_totals.csv")
interaction_data = pd.read_csv(f"flag_files/{date_var}/updated_events.csv")
word_data = pd.read_csv(f"flag_files/{date_var}/updated_words_learned.csv")

# Rename columns for easier handling
exposures_data = exposures_data.rename(columns={'wt_daycycle_event_date': 'date'})
all_events_data = all_events_data.rename(columns={'wt_daycycle_event_date': 'date'})
mission_data = mission_data.rename(columns={'wt_daycycle_event_date': 'date'})
playtime_data = playtime_data.rename(columns={'wt_daycycle_event_date': 'date'})
pns_data = pns_data.rename(columns={'wt_daycycle_event_date': 'date'})
interaction_data = interaction_data.rename(columns={'start_date': 'date'})
word_data = word_data.rename(columns={'first_served': 'date'})

# Convert date strings to datetime objects
exposures_data['date'] = pd.to_datetime(exposures_data['date']).dt.date
all_events_data['date'] = pd.to_datetime(all_events_data['date']).dt.date
mission_data['date'] = pd.to_datetime(mission_data['date']).dt.date
playtime_data['date'] = pd.to_datetime(playtime_data['date']).dt.date
pns_data['date'] = pd.to_datetime(pns_data['date']).dt.date
interaction_data['date'] = pd.to_datetime(interaction_data['date'], errors="coerce").dt.date
word_data['date'] = pd.to_datetime(word_data['date'], errors= "coerce").dt.date

# No PopQuiz
interaction_data = interaction_data[~interaction_data['activity_type'].str.startswith('PopQuiz', na=False)]
all_events_data = all_events_data[(all_events_data['event_name'] == 'pnsCompleted') | (all_events_data['event_name'] == 'dailyActivitiesCompleted')]

# Create time-filtered datasets
exposures_data = exposures_data[(exposures_data['date'] >= start.date()) & (exposures_data['date'] <= end.date())]
all_events_data = all_events_data[(all_events_data['date'] >= start.date()) & (all_events_data['date'] <= end.date())]
mission_data = mission_data[(mission_data['date'] >= start.date()) & (mission_data['date'] <= end.date())]
playtime_data = playtime_data[(playtime_data['date'] >= start.date()) & (playtime_data['date'] <= end.date())]
pns_data = pns_data[(pns_data['date'] >= start.date()) & (pns_data['date'] <= end.date())]
interaction_data = interaction_data[(interaction_data['date'] >= start.date()) & (interaction_data['date'] <= end.date())]
word_data = word_data[(word_data['date'] >= start.date()) & (word_data['date'] <= end.date())]

# Create directory if it doesn't exist
os.makedirs(f"new_results/{date_var}", exist_ok=True)

##########################
## INITIAL DATA CHECKS ###
##########################

print("Size of datasets")
print(f""" Exposures per day {len(exposures_data)} rows;
      PNS Events Completed: {len(all_events_data)} rows; 
      Mission Events: {len(mission_data)} rows; 
      Playtime: {len(playtime_data)} rows; 
      Time spent with PNS: {len(pns_data)} rows; 
      Interaction data: {len(interaction_data)} rows
      Words Learned: {len(word_data)} rows; """)
print("Number of students in each dataset")
print(f""" Exposures {exposures_data['service_id'].nunique()} students;
      PNS Events {all_events_data['service_id'].nunique()} students;
      Mission Events {mission_data['service_id'].nunique()} students;
      Playtime: {playtime_data['service_id'].nunique()} students;
      PNS (time spent): {pns_data['service_id'].nunique()} students;
      Words Events: {interaction_data['service_id'].nunique()} students; 
      Words Learned: {word_data['service_id'].nunique()} students """)
########################################################################################################################
# Exposure Data Analysis: 
# Questions we want to answer:
# Do students who collect more word stars do better? Are word stars accurate for measuring learning progression?
student_stars = exposures_data.groupby('service_id').agg({
    'word_stars': ['sum', 'mean']
}).round(2)

student_stars.columns = ['total_stars', 'avg_daily_stars']
student_stars = student_stars.reset_index()

stars_summary = student_stars['total_stars'].describe()
stars_median = student_stars['total_stars'].median()

print(f"Stars summary: {stars_summary} \n Stars median: {stars_median}")

########################################################################################################################
# Event Data Analysis
# Questions we want to answer:
# On average, how many days did students complete some word activities, complete all word activities
# On average, how many word activities did they complete per day

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

print(f"Students average daily pns data: {pns_summary}; \n Median number of activities per day: {pns_median}")

total_pns = student_activities['total_pns'].describe()
total_pns_median = student_activities['total_pns'].median()

print(f"Students total pns data: {total_pns}; \n Median number of activities: {total_pns_median}")

daily_summary = student_activities['total_days_completed'].describe()
daily_median = student_activities['total_days_completed'].median()
print(f"Summary of students who completed all word activities in a day: {daily_summary}; \n Median number of days completed: {daily_median}")

# Identify students who have a low completion rate of all daily activities

print(f"Number of students who never completed a full day of activities {len(student_activities[student_activities['total_days_completed'] == 0])}")
print(f"""Students who rarely (more than once but less than 5 times) completed a full day of activities {len(student_activities[
    (student_activities['total_days_completed'] > 0) & 
    (student_activities['total_days_completed'] <= 5)
])}""")

# sns.histplot(student_activities['avg_daily_pns'], bins='auto', kde=False)
# plt.title('Average Daily word activities completed')
# plt.xlabel('Word Activivities Completed')
# plt.ylabel('Number of Students')
# plt.show()
########################################################################################################################
# Mission Data Analyses
# Questions we want to answer: 
# How does number of missions completed relate to performance? Number of missions aborted?
# Race Activities?  Popquizzes?

# raceactivity_started,raceactivity_completed,raceactivity_failed,popquiz_started,popquiz_completed
student_missions = mission_data.groupby('service_id').agg({
    'mission_started': 'sum',
    'mission_completed': 'sum',
    'mission_aborted': 'sum',
    'raceactivity_started': 'sum',
    'popquiz_started': 'sum',
    'popquiz_completed': 'sum'
}).round(2)

student_missions.columns = ['missions_started', 'missions_completed', 
                            'missions_aborted', 'races_started',
                            'popquizzes_started', 'popquizzes_completed']
student_missions = student_missions.reset_index()

student_missions["missing_missions"] = (
    student_missions["missions_started"] 
    - (student_missions["missions_completed"] + student_missions["missions_aborted"]))
print("Missing missions summary", student_missions["missing_missions"].describe())
# All about missions
started_missions_summary = student_missions['missions_started'].describe()
started_missions_median = student_missions['missions_started'].median()

completed_missions_summary = student_missions['missions_completed'].describe()
completed_missions_median = student_missions['missions_completed'].median()

aborted_missions_summary = student_missions['missions_aborted'].describe()
aborted_missions_median = student_missions['missions_aborted'].median()

print(f"Missions started summary: {started_missions_summary}; Missions started median: {started_missions_median}")
print(f"Missions completed summary: {completed_missions_summary}; Missions completed median: {completed_missions_median}")
print(f"Missions aborted summary: {aborted_missions_summary}; Missions aborted median: {aborted_missions_median}")
# All about popquizzes
started_popquizzes_summary = student_missions['popquizzes_started'].describe()
started_popquizzes_median = student_missions['popquizzes_started'].median()

completed_popquizzes_summary = student_missions['popquizzes_completed'].describe()
completed_popquizzes_median = student_missions['popquizzes_completed'].median()

print(f"Popquizzes started summary: {started_popquizzes_summary}; Popquizzes started median: {started_popquizzes_median}")
print(f"Popquizzes completed summary: {completed_popquizzes_summary}; Popquizzes completed median: {completed_popquizzes_median}")

# All about races
started_races_summary = student_missions['races_started'].describe()
started_races_median = student_missions['races_started'].median()

# sns.histplot(student_missions['missions_started'], bins='auto', kde=False)
# plt.title('Total Number of Missions Started by Students')
# plt.xlabel('Missions Started')
# plt.ylabel('Number of Students')
# plt.show()

# print(f"Races started summary: {started_races_summary}; Races started median: {started_races_median}")
# extreme = student_missions[student_missions['races_started'] > 20]
# print(extreme['races_started'].describe())
# print("Number of extreme students: ", len(extreme['races_started']))

########################################################################################################################
# Playtime Data Analysis
# Questions we want to answer
# How many days did students play on average?  For how long?
# How many students played in goldilocks zone (10-20 minutes)? For too short (< 10 minutes)? For too long (> 20 minutes)?

# 1. Aggregate playtime data per student
student_playtime = playtime_data.groupby('service_id').agg({
    'time_played_minutes': ['sum', 'mean', 'count']
}).round(2)

# Flatten column names
student_playtime.columns = ['total_playtime', 'avg_daily_playtime', 'days_active']
student_playtime = student_playtime.reset_index()

playtime_summary = student_playtime['avg_daily_playtime'].describe()
print("Playtime Summary: ", playtime_summary)

total_playtime_summary = student_playtime['total_playtime'].describe()
print("Total Playtime Summary", total_playtime_summary)
# Students playing less than 10 mins / day
too_cold = student_playtime[
    student_playtime['avg_daily_playtime'] < 10
]

# Students playing 10-20 mins a day
goldilocks = student_playtime[
    (student_playtime['avg_daily_playtime'] >= 10) & (student_playtime['avg_daily_playtime'] <= 20)
]
# Students playing more than 20 mins a day
too_hot = student_playtime[
    student_playtime['avg_daily_playtime'] > 20
]
print("On average...")
print(f"Number of students who played less than 10 minutes a day: {len(too_cold)}")
print(f"Number of students who played 10-20 minutes a day: {len(goldilocks)}")
print(f"Number of students who played more than 20 minutes a day: {len(too_hot)}")

# Active days
print("Between March 6th and April 17th, students played WT: ")
days_summary = student_playtime['days_active'].describe()
print(days_summary)

days_students = student_playtime[
    student_playtime['days_active'] < 6
]

print(f"Number of students who played for less than 5 days: {len(days_students)}")

# sns.histplot(student_playtime['avg_daily_playtime'], bins='auto', kde=False)
# plt.title('Average Number of Minutes Played / Day')
# plt.xlabel('Minutes')
# plt.ylabel('Number of Students')
# plt.show()

########################################################################################################################
# PNS Daily Totals Analysis
# Questions we want to answer
# How does total time spent on different pns activities relate to performance
# How does total number of different pns activities relate to performance

different_activities = pns_data.groupby(['service_id', 'pnsmode']).agg({
    'number_of_word_activites': 'sum',
    'word_activites_time': 'sum', 
    'avg_time_per_word_activity': 'mean'
}).round(2).reset_index()

# Pivot to get columns for each activity type
result = different_activities.pivot(index='service_id', columns='pnsmode')

# Flatten column names (e.g., 'MatchSynonyms_totalnumber')
result.columns = [f"{col[1].lower()}_{col[0].replace('number_of_word_activites', 'totalnumber').replace('word_activites_time', 'totaltime').replace('avg_time_per_word_activity', 'avgtime')}" 
                 for col in result.columns]

result = result.reset_index()
# Delete this line / keep result if you want to see how # of activities relates
columns_to_keep = ['service_id', 'assemblesyllables_avgtime', 'matchcollocations_avgtime', 'matchsentenceblank_avgtime', 'matchsynonyms_avgtime']

pns_daily_totals = result[columns_to_keep]

assemble_summary = pns_daily_totals['assemblesyllables_avgtime'].describe()
print("Assemble syllables Summary", assemble_summary)

matchcollocations_summary = pns_daily_totals['matchcollocations_avgtime'].describe()
print("Match collocations Summary", matchcollocations_summary)

matchsentenceblank_summary = pns_daily_totals['matchsentenceblank_avgtime'].describe()
print("Match sentence blank Summary", matchsentenceblank_summary)

matchsynonyms_summary = pns_daily_totals['matchsynonyms_avgtime'].describe()
print("Match synonyms Summary", matchsynonyms_summary)

# sns.histplot(pns_daily_totals['assemblesyllables_avgtime'], bins='auto', kde=False) 
# plt.title('Average time per AssembleSyllables Activity')
# plt.xlabel('Seconds') 
# plt.ylabel('Number of Students') 
# plt.show()


########################################################################################################################
# Interaction Data Analysis
# Questions we want to answer:
# How correct were students (first try)?
# On average, how many words did students "learn"

student_interactions = interaction_data.groupby('service_id').agg({
    'success': lambda x: (x == 't').sum() / len(x),  # accuracy
    'interaction_duration': ['sum', 'mean']           # total and average time
}).round(2)

# Flatten column names
student_interactions.columns = ['accuracy', 'total_learning_time', 'avg_response_time']
student_interactions.reset_index()

# All about interactions
success_summary = student_interactions['accuracy'].describe()

total_time_summary = student_interactions['total_learning_time'].describe()

avg_time_summary = student_interactions['avg_response_time'].describe()

print(f"Student success  summary: {success_summary}")
print(f"Total Time summary: {total_time_summary}")
print(f"Average time per activity summary: {avg_time_summary}")

# sns.histplot(student_interactions['accuracy'], bins='auto', kde=False) 
# plt.title('Student Accuracy Distribution')
# plt.xlabel('Accuracy') 
# plt.ylabel('Number of Students') 
# plt.show()


def calculate_word_metrics(df):
    # Calculate word exposure metrics for each student
    
    # Group by service_id and target_id to count interactions per word per student
    word_interactions = df.groupby(['service_id', 'target_id']).size().reset_index(name='interaction_count')

    word_interactions['is_trained'] = word_interactions['target_id'].isin(trained_fourth | trained_second)
    word_interactions['is_untrained'] = word_interactions['target_id'].isin(untrained_fourth | untrained_second)
    word_interactions['is_random'] = ~word_interactions['target_id'].isin(trained_fourth | untrained_fourth | trained_second | untrained_second)
    # word_interactions['trained_4plus'] = (word_interactions['is_trained']) & (word_interactions['interaction_count'] >= 4)
    
    # Calculate metrics per student
    student_word_metrics = word_interactions.groupby('service_id').agg({
        'target_id': 'nunique',  # Number of unique words exposed to
        'interaction_count': ['mean', lambda x: sum(x > 8)],  # Average interactions per word + count with 4+ exposures
        'is_trained': 'sum',
        'is_untrained': 'sum',
        'is_random': 'sum',
    }).round(2)
    
    # Flatten column names and rename for clarity
    student_word_metrics.columns = ['unique_words_exposed', 'avg_interactions_per_word', 'words_with_9plus_exposures',
                                    'trained_count', 'untrained_count', 'random_count']
    student_word_metrics = student_word_metrics.reset_index()
    
    return student_word_metrics, word_interactions

student_word_metrics, word_interactions = calculate_word_metrics(interaction_data)

print(f"\nWord Exposure Analysis Results:")
print(f"Number of students analyzed: {len(student_word_metrics)}")
# print(f"\nSample results:")
# print(student_word_metrics.head(10))

# Additional analysis: summary statistics
print(f"\nSummary Statistics:")

# Print .describe() for each metric
unique_words_summary = student_word_metrics['unique_words_exposed'].describe()
print("Unique words exposed Summary:", unique_words_summary)

avg_interactions_summary = student_word_metrics['avg_interactions_per_word'].describe()
print("Avg interactions per word Summary:", avg_interactions_summary)

words_9plus_summary = student_word_metrics['words_with_9plus_exposures'].describe()
print("Words with 9+ exposures Summary:", words_9plus_summary)

# words_4plus_summary = student_word_metrics['words_with_4_exposures'].describe()
# print("Words with exactly 4 exposures Summary:", words_4plus_summary)

trained_count_summary = student_word_metrics['trained_count'].describe()
print("Number of trained words exposed Summary:", trained_count_summary)

# trained_4plus_summary = student_word_metrics['trained_with_4plus_exposures'].describe()
# print("Number of trained words with > 4 exposures Summary:", trained_4plus_summary)

untrained_count_summary = student_word_metrics['untrained_count'].describe()
print("Number of untrained words exposed Summary:", untrained_count_summary)

random_count_summary = student_word_metrics['random_count'].describe()
print("Number of random words exposed Summary:", random_count_summary)

# Then all the plots
# sns.histplot(student_word_metrics['unique_words_exposed'], bins='auto', kde=False) 
# plt.title('Unique Words Exposed Distribution')
# plt.xlabel('Number of Words') 
# plt.ylabel('Number of Students') 
# plt.show()


########################################################################################################################
# Words Learned
# How does number of attempts per exposure relate to performance generally
# Average number of exposures per word
# Do more attempts mean less effort?
word_data['is_trained'] = word_data['word'].isin(trained_fourth | trained_second)

# Count trained words learned per student
trained_words_learned = word_data.groupby('service_id')['is_trained'].sum().reset_index()
trained_words_learned.columns = ['service_id', 'learned_trained_count']

# sns.histplot(trained_words_learned['learned_trained_count'], bins='auto', kde=False) 
# plt.title('Trained Words Learned')
# plt.xlabel('Count') 
# plt.ylabel('Number of Students') 
# plt.show()
learned_trained_summary = trained_words_learned['learned_trained_count'].describe()
print("Summary of 'learned' trained words:", learned_trained_summary)
# Parse the attempts column from string to list
word_data['attempts_list'] = word_data['attempts'].apply(ast.literal_eval)

# Separate WIC from regular exposure attempts
def get_exposure_wic_attempts(row):
    attempts = row['attempts_list']
    
    # Regular exposures: 1, 2, 3, 5, 7 (odd positions)
    # WIC exposures: 4, 6, 8 (even positions starting from 4)
    exposure_attempts = [attempts[i] for i in [0, 1, 2, 4, 6] if i < len(attempts)]
    wic_attempts = [attempts[i] for i in [3, 5, 7] if i < len(attempts)]
    
    return exposure_attempts, wic_attempts

word_data[['exposure_attempts', 'wic_attempts']] = word_data.apply(
    lambda row: pd.Series(get_exposure_wic_attempts(row)), axis=1
)

# Calculate gaming metrics per student
gaming_metrics = word_data.groupby('service_id').agg({
    'attempts_list': [
        lambda x: sum(attempts[0] > 1 for attempts in x if len(attempts) > 0),  # first_exposure_wrong
        lambda x: sum(attempts[1] > 1 for attempts in x if len(attempts) > 1),  # second_exposure_wrong
    ],
    'exposure_attempts': [
        lambda x: sum(sum(attempts) for attempts in x if attempts) / len([a for a in x if a]),  # avg_exposure_attempts
        lambda x: sum(len([a for a in attempts if a > 1]) for attempts in x if attempts)        # total_exposure_wrong
    ],
    'wic_attempts': [
        lambda x: sum(sum(attempts) for attempts in x if attempts) / len([a for a in x if a]) if any(x) else 0,  # avg_wic_attempts
        lambda x: sum(len([a for a in attempts if a > 1]) for attempts in x if attempts)        # total_wic_wrong
    ]
}).round(2)

gaming_metrics.columns = ['first_exposure_wrong', 'second_exposure_wrong', 'avg_exposure_attempts', 'total_exposures_wrong', 'avg_wic_attempts', 'total_wic_wrong']
gaming_metrics = gaming_metrics.reset_index()

gaming_metrics["total_wrong"] = (
    gaming_metrics["total_exposures_wrong"] + gaming_metrics["total_wic_wrong"]
)
# All about gaming
# Summary statistics first
avg_exposure_attempts_summary = gaming_metrics['avg_exposure_attempts'].describe()
print("Average exposure attempts Summary:", avg_exposure_attempts_summary)

avg_wic_attempts_summary = gaming_metrics['avg_wic_attempts'].describe()
print("Average WIC attempts Summary:", avg_wic_attempts_summary)

first_exposure_wrong_summary = gaming_metrics['first_exposure_wrong'].describe()
print("First exposure wrong Summary:", first_exposure_wrong_summary)

second_exposure_wrong_summary = gaming_metrics['second_exposure_wrong'].describe()
print("Second exposure wrong Summary:", second_exposure_wrong_summary)

total_exposures_wrong_summary = gaming_metrics['total_exposures_wrong'].describe()
print("Total exposures wrong Summary:", total_exposures_wrong_summary)

total_wic_wrong_summary = gaming_metrics['total_wic_wrong'].describe()
print("Total WIC wrong Summary:", total_wic_wrong_summary)

total_wrong_summary = gaming_metrics['total_wrong'].describe()
print("Total wrong Summary:", total_wrong_summary)

# Then all the plots
# sns.histplot(gaming_metrics['avg_exposure_attempts'], bins='auto', kde=False) 
# plt.title('Average Exposure Attempts Distribution')
# plt.xlabel('Average Attempts') 
# plt.ylabel('Number of Students') 
# plt.show()

##############
## SUMMARY ###
##############

# student_metrics = student_playtime.merge(student_activities, on='service_id', how='left')
# student_metrics = student_metrics.merge(student_word_metrics, on='service_id', how='left')
student_metrics = (student_stars
                  .merge(student_activities, on='service_id', how='left')
                  .merge(student_missions, on='service_id', how='left')
                  .merge(student_playtime, on='service_id', how='left')
                  .merge(result, on='service_id', how='left')
                  .merge(student_interactions, on='service_id', how='left')
                  .merge(student_word_metrics, on='service_id', how='left')
                  .merge(gaming_metrics, on='service_id', how='left')
                  .merge(trained_words_learned, on='service_id', how="left")
                  )

########################
######## OUTPUT ########
########################

# Create a combined dataset with all metrics

# Output the combined metrics for all students

student_metrics.to_csv(f"new_results/{date_var}/student_metrics.csv", index=False)

# Histogram for words_with_4plus_exposures
# sns.histplot(student_metrics['words_with_4plus_exposures'], bins='auto', kde=False)
# plt.title('Distribution of Words with 4+ Exposures')
# plt.xlabel('Words with ≥4 Exposures')
# plt.ylabel('Number of Students')
# plt.show()