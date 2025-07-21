# Load required libraries
library(dplyr)
library(tidyr)
library(ggplot2)
# Load datasets
playtime_data <- read.csv("WT_Analyses/during_study/flag_files/april16/wt_guid__wt_daycycle_event_date___playtime_000.csv", check.names = TRUE)
mission_data <- read.csv("WT_Analyses/during_study/flag_files/april16/wt_guid__wt_daycycle_event_date___mission_counts_000.csv", check.names = TRUE)
pns_events_data <- read.csv("WT_Analyses/during_study/flag_files/april16/wt_guid__wt_daycycle_event_date___pns_daily_totals_000.csv", check.names = TRUE)
# all_events_data <- read.csv("WT_Analyses/during_study/flag_files/april16/int_game_events_000.csv", check.names = TRUE)

# Rename columns for easier handling
colnames(playtime_data)[colnames(playtime_data) == "wt_daycycle_event_date"] <- "date"

colnames(mission_data)[colnames(mission_data) == "wt_daycycle_event_date"] <- "date"

colnames(pns_events_data)[colnames(pns_events_data) == "wt_daycycle_event_date"] <- "date"

# 1. Identify Inactive Students (no playtime)
# Aggregate playtime data per student
student_playtime <- playtime_data %>%
    group_by(service_id) %>%
    summarize(
        total_playtime = sum(time_played_minutes, na.rm = TRUE),
        avg_daily_playtime = mean(time_played_minutes, na.rm = TRUE),
        days_active = n_distinct(date),
        .groups = "drop"
    )

# Identify inactive students (zero total playtime)
inactive_students <- student_playtime %>%
    filter(total_playtime == 0)

# Summary statistics for playtime
playtime_summary <- summary(student_playtime$total_playtime)
playtime_median <- median(student_playtime$total_playtime, na.rm = TRUE)

print("1. Inactive Students (No Playtime):")
print(paste("Number of inactive students:", nrow(inactive_students)))
print("Summary of playtime across all students:")
print(playtime_summary)

# 2. Identify Not Engaged Students (less playtime)
# Define threshold for "not engaged" (e.g., bottom 20% of playtime)
playtime_threshold <- quantile(student_playtime$total_playtime[student_playtime$total_playtime > 0], 0.2, na.rm = TRUE)

not_engaged_students <- student_playtime %>%
    filter(total_playtime > 0 & total_playtime <= playtime_threshold)

print("\n2. Not Engaged Students (Less Playtime):")
print(paste("Playtime threshold for 'not engaged':", playtime_threshold, "minutes"))
print(paste("Number of 'not engaged' students:", nrow(not_engaged_students)))

# 3. Identify Off-task Students (more races, less everything else)
# Aggregate mission data per student
student_activities <- mission_data %>%
    group_by(service_id) %>%
    summarize(
        total_missions_started = sum(mission_started, na.rm = TRUE),
        total_missions_completed = sum(mission_completed, na.rm = TRUE),
        total_races_started = sum(raceactivity_started, na.rm = TRUE),
        total_races_completed = sum(raceactivity_completed, na.rm = TRUE),
        total_quizzes_started = sum(popquiz_started, na.rm = TRUE),
        total_quizzes_completed = sum(popquiz_completed, na.rm = TRUE),
        total_activities = sum(mission_started, raceactivity_started, popquiz_started, na.rm = TRUE),
        .groups = "drop"
    ) %>%
    mutate(
        mission_completion_rate = ifelse(total_missions_started > 0,
            total_missions_completed / total_missions_started, NA
        ),
        race_completion_rate = ifelse(total_races_started > 0,
            total_races_completed / total_races_started, NA
        ),
        race_ratio = ifelse(total_activities > 0,
            total_races_started / total_activities, 0
        )
    )

# Define threshold for "off-task" (e.g., race activities > 60% of total activities)
off_task_threshold <- 0.6

off_task_students <- student_activities %>%
    filter(race_ratio > off_task_threshold & total_activities >= 5) # At least 5 activities to be meaningful

print("\n3. Off-task Students (More Races, Less Everything Else):")
print(paste("Race ratio threshold for 'off-task':", off_task_threshold))
print(paste("Number of 'off-task' students:", nrow(off_task_students)))

# 4. Identify Poorly Performing Students
# Aggregate PNS data per student to check performance
student_performance <- pns_events_data %>%
    filter(result %in% c("correct", "incorrect")) %>%
    group_by(service_id, result) %>%
    summarize(count = n(), .groups = "drop") %>%
    pivot_wider(names_from = result, values_from = count, values_fill = 0) %>%
    mutate(
        total_attempts = correct + incorrect,
        success_rate = correct / total_attempts
    )

# Define threshold for "poor performance" (e.g., success rate below 40%)
performance_threshold <- 0.4

poor_performers <- student_performance %>%
    filter(total_attempts >= 10 & success_rate <= performance_threshold) # At least 10 attempts to be meaningful

performance_summary <- summary(student_performance$success_rate)
performance_median <- median(student_performance$success_rate, na.rm = TRUE)

print("\n4. Poorly Performing Students:")
print(paste("Performance threshold for 'poor performance':", performance_threshold))
print(paste("Number of 'poorly performing' students:", nrow(poor_performers)))
print("Summary of success rates across all students:")
print(performance_summary)

# Create a combined dataset with all metrics
student_metrics <- student_playtime %>%
    left_join(student_activities, by = "service_id") %>%
    left_join(student_performance, by = "service_id") %>%
    mutate(
        is_inactive = service_id %in% inactive_students$service_id,
        is_not_engaged = service_id %in% not_engaged_students$service_id,
        is_off_task = service_id %in% off_task_students$service_id,
        is_poor_performer = service_id %in% poor_performers$service_id,
        flags_count = is_inactive + is_not_engaged + is_off_task + is_poor_performer
    )

# Output the list of students for each metric
write.csv(inactive_students, "inactive_students.csv", row.names = FALSE)
write.csv(not_engaged_students, "not_engaged_students.csv", row.names = FALSE)
write.csv(off_task_students, "off_task_students.csv", row.names = FALSE)
write.csv(poor_performers, "poor_performers.csv", row.names = FALSE)

# Output the combined metrics for all students
write.csv(student_metrics, "student_metrics_combined.csv", row.names = FALSE)

# Count students with multiple flags
students_with_multiple_flags <- student_metrics %>%
    filter(flags_count > 1) %>%
    arrange(desc(flags_count))

print("\nStudents with Multiple Flags:")
print(paste("Number of students with multiple flags:", nrow(students_with_multiple_flags)))
print(paste("Number of students with all 4 flags:", sum(student_metrics$flags_count == 4)))

# Generate a detailed report for the top 10 most concerning students
top_concerning_students <- student_metrics %>%
    arrange(
        desc(flags_count), desc(is_poor_performer), desc(is_off_task),
        desc(is_not_engaged), desc(is_inactive)
    ) %>%
    head(10)

print("\nTop 10 Most Concerning Students:")
print(top_concerning_students[, c(
    "service_id", "flags_count", "total_playtime",
    "avg_daily_playtime", "success_rate", "race_ratio"
)])

# Create a function to compare a student to averages
student_comparison <- function(student_id) {
    student <- student_metrics %>% filter(service_id == student_id)

    if (nrow(student) == 0) {
        return(paste("Student", student_id, "not found in the dataset."))
    }

    avg_playtime <- mean(student_metrics$total_playtime, na.rm = TRUE)
    avg_success <- mean(student_metrics$success_rate, na.rm = TRUE, finite = TRUE)
    avg_race_ratio <- mean(student_metrics$race_ratio, na.rm = TRUE)

    comparison <- data.frame(
        metric = c("Total Playtime", "Success Rate", "Race Ratio"),
        student_value = c(student$total_playtime, student$success_rate, student$race_ratio),
        average_value = c(avg_playtime, avg_success, avg_race_ratio),
        difference_pct = c(
            (student$total_playtime - avg_playtime) / avg_playtime * 100,
            (student$success_rate - avg_success) / avg_success * 100,
            (student$race_ratio - avg_race_ratio) / avg_race_ratio * 100
        )
    )

    flags <- c()
    if (student$is_inactive) flags <- c(flags, "Inactive")
    if (student$is_not_engaged) flags <- c(flags, "Not Engaged")
    if (student$is_off_task) flags <- c(flags, "Off-Task")
    if (student$is_poor_performer) flags <- c(flags, "Poor Performer")

    list(
        student_id = student_id,
        flags = flags,
        comparison = comparison
    )
}

# Example: Get detailed comparison for the most concerning student
if (nrow(top_concerning_students) > 0) {
    most_concerning_id <- top_concerning_students$service_id[1]
    print("\nDetailed Comparison for Most Concerning Student:")
    print(student_comparison(most_concerning_id))
}

# Visualize the distribution of students across metrics
students_per_metric <- c(
    nrow(inactive_students),
    nrow(not_engaged_students),
    nrow(off_task_students),
    nrow(poor_performers)
)

metrics_names <- c("Inactive", "Not Engaged", "Off-Task", "Poor Performer")

# Create a data frame for plotting
metrics_plot_data <- data.frame(
    metric = metrics_names,
    count = students_per_metric
)

# Plot count of students per metric
ggplot(metrics_plot_data, aes(x = metric, y = count, fill = metric)) +
    geom_bar(stat = "identity") +
    labs(
        title = "Number of Students per Metric",
        x = "Metric", y = "Count"
    ) +
    theme_minimal()

# Save the plot
ggsave("students_per_metric.png", width = 8, height = 6)

# Finally, provide a summary of all metrics
cat("\n----- OVERALL SUMMARY -----\n")
cat("Total number of students:", length(unique(student_metrics$service_id)), "\n")
cat("Inactive students:", nrow(inactive_students), "\n")
cat("Not engaged students:", nrow(not_engaged_students), "\n")
cat("Off-task students:", nrow(off_task_students), "\n")
cat("Poor performing students:", nrow(poor_performers), "\n")
cat("Students with multiple flags:", nrow(students_with_multiple_flags), "\n")


summary_df <- all_events_data %>%
    summarize(unique_count = n_distinct(service_id))

print(summary_df)
