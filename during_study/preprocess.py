import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

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
####################
## PRE-PROCESSING ##
####################
start = datetime.strptime("3/6/2025",'%m/%d/%Y')
end = datetime.strptime("4/17/2025",'%m/%d/%Y')

# Read CSV files
playtime_data = pd.read_csv(f"flag_files/{date_var}/wt_guid__wt_daycycle_event_date___playtime_000.csv")
word_data = pd.read_csv(f"flag_files/{date_var}/wt_guid__word_id___words_learned_000.csv")
interaction_data = pd.read_csv(f"flag_files/june11/stg_mysql__word_events__interaction_events000.csv")
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