# Load required libraries
library(dplyr)
library(tidyr)
library(ggplot2)
library(lubridate)

# Load datasets
date_var <- "may21"
playtime_data <- read.csv(paste0("WT_Analyses/during_study/flag_files/", date_var, "/wt_guid__wt_daycycle_event_date___playtime_000.csv"), check.names = TRUE)
# mission_data <- read.csv(paste0("WT_Analyses/during_study/flag_files/", date_var, "/wt_guid__wt_daycycle_event_date___mission_counts_000.csv"), check.names = TRUE)
# pns_events_data <- read.csv(paste0("WT_Analyses/during_study/flag_files/", date_var, "/wt_guid__wt_daycycle_event_date___pns_daily_totals_000.csv"), check.names = TRUE)
all_events_data <- read.csv(paste0("WT_Analyses/during_study/flag_files/", date_var, "/int_game_events_000.csv"), check.names = TRUE)

# Rename columns for easier handling
colnames(playtime_data)[colnames(playtime_data) == "wt_daycycle_event_date"] <- "date"

# colnames(mission_data)[colnames(mission_data) == "wt_daycycle_event_date"] <- "date"

# colnames(pns_events_data)[colnames(pns_events_data) == "wt_daycycle_event_date"] <- "date"

colnames(all_events_data)[colnames(all_events_data) == "wt_daycycle_event_date"] <- "date"

# Convert date strings to Date objects
playtime_data$date <- as.Date(playtime_data$date)
# mission_data$date <- as.Date(mission_data$date)
# pns_events_data$date <- as.Date(pns_events_data$date)
all_events_data$data <- as.Date(all_events_data$date)

# Get current date and calculate date ranges
current_date <- Sys.Date()
week_ago <- current_date - 7
yesterday <- current_date - 1

# Create time-filtered datasets
playtime_week <- playtime_data %>% filter(date >= week_ago)
# mission_week <- mission_data %>% filter(date >= week_ago)
# pns_events_week <- pns_events_data %>% filter(date >= week_ago)
all_events_week <- all_events_data %>% filter(date >= week_ago)

# For yesterday's data
playtime_yesterday <- playtime_data %>% filter(date == yesterday)
# mission_yesterday <- mission_data %>% filter(date == yesterday)
# pns_events_yesterday <- pns_events_data %>% filter(date == yesterday)
all_events_yesterday <- all_events_data %>% filter(date == yesterday)

# 0. Identify students with no playtime data
# Only if I want the whole row
# only_in_dataset1 <- anti_join(all_events_data, mission_data, by = "service_id")
# Only if I just want the id's
only_in_dataset <- setdiff(all_events_data$service_id, playtime_data$service_id)
# setdiff(all_events_data$service_id, pns_events_data$service_id),
# setdiff(all_events_data$service_id, mission_data$service_id)

write.csv(only_in_dataset1, paste0("WT_Analyses/during_study/results/", date_var, "/no_data.csv"), row.names = FALSE)


## All-time Analysis
# 1. Aggregate playtime + pns data per student
student_playtime <- playtime_data %>%
    group_by(service_id) %>%
    summarize(
        total_playtime = sum(time_played_minutes, na.rm = TRUE),
        avg_daily_playtime = mean(time_played_minutes, na.rm = TRUE),
        days_active = n_distinct(date),
        .groups = "drop"
    )

student_activities <- all_events_data %>%
    # First group by both service_id AND date
    group_by(service_id, date) %>%
    # Count daily PNS completions
    summarize(
        daily_pns = sum(event_name == "pnsCompleted"),
        daily_activities = sum(event_name == "dailyActivitiesCompleted"),
        .groups = "drop"
    ) %>%
    # Then group just by service_id to get student-level stats
    group_by(service_id) %>%
    summarize(
        total_pns = sum(daily_pns),
        total_days_completed = sum(daily_activities),
        avg_daily_pns = mean(daily_pns, na.rm = TRUE)
    )
# Summary statistics
playtime_summary <- summary(student_playtime$avg_daily_playtime)
playtime_median <- median(student_playtime$avg_daily_playtime, na.rm = TRUE)

pns_summary <- summary(student_activities$avg_daily_pns)
pns_median <- median(student_activities$avg_daily_pns, na.rm = TRUE)

daily_summary <- summary(student_activities$total_days_completed)
daily_median <- median(student_activities$total_days_completed, na.rm = TRUE)

# Identify inactive students (zero activities)
inactive_students <- student_activities %>%
    filter(total_pns == 0)
print("1. Inactive Students (No activities):")
print(paste("Number of inactive students (zero activities):", nrow(inactive_students)))

no_completion_students <- student_activities %>%
    filter(total_days_completed == 0)
print(paste("Number of students who've never completed all word activities in a day:", nrow(no_completion_students)))


# 2a. Identify Not Engaged Students (less playtime)
# Define threshold for "not engaged" (e.g., bottom 20% of playtime)
playtime_threshold <- quantile(student_playtime$avg_daily_playtime[student_playtime$avg_daily_playtime > 0], 0.2, na.rm = TRUE) # nolint: line_length_linter.

not_playing_students <- student_playtime %>%
    filter(avg_daily_playtime > 0 & avg_daily_playtime <= playtime_threshold)
print("")
print("\n2a. Not Engaged Students (Less Playtime):")
print(paste("Playtime threshold for 'not engaged':", playtime_threshold, "minutes"))
print(paste("Number of 'not engaged' students:", nrow(not_playing_students)))

# 2b. Identify Not Engaged Students (less activities)
# Define threshold for "not engaged" (e.g., bottom 20% of completion)

pns_threshold <- quantile(student_activities$avg_daily_pns[student_activities$avg_daily_pns > 0], 0.2, na.rm = TRUE) # nolint: line_length_linter.

not_pnsing_students <- student_activities %>%
    filter(avg_daily_pns > 0 & avg_daily_pns <= pns_threshold)
print("")
print("\n2b. Not Engaged Students (Less activities):")
print(paste("Activity threshold for 'not engaged':", pns_threshold, "activities"))
print(paste("Number of 'not engaged' students:", nrow(not_pnsing_students)))


# 2c. Identify students who have a low completion rate of all daily activities
# and see if it's just because they spend less time too
daily_threshold <- quantile(student_activities$total_days_completed[student_activities$total_days_completed > 0], 0.2, na.rm = TRUE) # nolint: line_length_linter.

not_dailying_students <- student_activities %>%
    filter(total_days_completed > 0 & total_days_completed <= daily_threshold)
print("")
print("\n2c. Not Completing Students (Less completions):")
print(paste("Activity threshold for 'not completing':", daily_threshold, "activities"))
print(paste("Number of 'not engaged' students:", nrow(not_dailying_students)))

# Create a combined dataset with all metrics
student_metrics <- student_playtime %>%
    left_join(student_activities, by = "service_id") %>%
    mutate(
        is_inactive = service_id %in% inactive_students$service_id,
        is_never_completed = service_id %in% no_completion_students$service_id,
        is_playing_less = service_id %in% not_playing_students$service_id,
        is_pnsing_less = service_id %in% not_pnsing_students$service_id,
        is_finishing_less = service_id %in% not_dailying_students$service_id,
        flags_count = is_inactive + is_never_completed + is_playing_less + is_pnsing_less + is_finishing_less # nolint
    )
# Output the combined metrics for all students
# EDIT HERE BEFORE RUNNING AGAIN
write.csv(student_metrics, paste0("WT_Analyses/during_study/results/", date_var, "/student_metrics.csv"), row.names = FALSE)

top_concerning_students <- student_metrics %>%
    arrange(
        desc(flags_count), desc(is_playing_less), desc(is_pnsing_less),
        desc(is_finishing_less), desc(is_inactive)
    ) %>%
    head(10)

print("\nTop 10 Most Concerning Students:")


print(top_concerning_students[, c(
    "service_id", "flags_count", "total_playtime",
    "avg_daily_playtime"
)])

# get_student_data <- function(student_id) {
# }
