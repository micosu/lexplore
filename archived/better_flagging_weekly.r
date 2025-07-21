# Load required libraries
library(dplyr)
library(tidyr)
library(ggplot2)
library(lubridate)

date_var <- "may21"
playtime_data <- read.csv(paste0("WT_Analyses/during_study/flag_files/", date_var, "/wt_guid__wt_daycycle_event_date___playtime_000.csv"), check.names = TRUE)
# mission_data <- read.csv(paste0("WT_Analyses/during_study/flag_files/", date_var, "/wt_guid__wt_daycycle_event_date___mission_counts_000.csv"), check.names = TRUE)
# pns_events_data <- read.csv(paste0("WT_Analyses/during_study/flag_files/", date_var, "/wt_guid__wt_daycycle_event_date___pns_daily_totals_000.csv"), check.names = TRUE)
all_events_data <- read.csv(paste0("WT_Analyses/during_study/flag_files/", date_var, "/int_game_events_000.csv"), check.names = TRUE)

# Rename columns for easier handling
colnames(playtime_data)[colnames(playtime_data) == "wt_daycycle_event_date"] <- "date"

# colnames(pns_events_data)[colnames(pns_events_data) == "wt_daycycle_event_date"] <- "date"

colnames(all_events_data)[colnames(all_events_data) == "wt_daycycle_event_date"] <- "date"

# Convert date strings to Date objects
playtime_data$date <- as.Date(playtime_data$date)
# pns_events_data$date <- as.Date(pns_events_data$date)
all_events_data$data <- as.Date(all_events_data$date)

# Get current date and calculate date ranges
current_date <- Sys.Date()
week_ago <- current_date - 7
yesterday <- current_date - 1

# Create time-filtered datasets
playtime_week <- playtime_data %>% filter(date >= week_ago)
# pns_events_week <- pns_events_data %>% filter(date >= week_ago)
all_events_week <- all_events_data %>% filter(date >= week_ago)

# For yesterday's data
playtime_yesterday <- playtime_data %>% filter(date == yesterday)
# pns_events_yesterday <- pns_events_data %>% filter(date == yesterday)
all_events_yesterday <- all_events_data %>% filter(date == yesterday)

# 0. Identify students with no playtime data
# Only if I want the whole row
# only_in_dataset1 <- anti_join(all_events_data, mission_data, by = "service_id")
# Only if I just want the id's
only_in_dataset1 <- setdiff(all_events_week$service_id, playtime_week$service_id)
# setdiff(all_events_week$service_id, pns_events_week$service_id)

lost_students <- setdiff(playtime_data$service_id, playtime_week$service_id)

write.csv(only_in_dataset1, paste0("WT_Analyses/during_study/results/", date_var, "/no_week_data.csv"), row.names = FALSE)
write.csv(lost_students, paste0("WT_Analyses/during_study/results/", date_var, "/lost_students.csv"), row.names = FALSE)


## All-time Analysis
# 1. Aggregate playtime + pns data per student
student_playtime <- playtime_week %>%
    group_by(service_id) %>%
    summarize(
        total_playtime = sum(time_played_minutes, na.rm = TRUE),
        avg_daily_playtime = mean(time_played_minutes, na.rm = TRUE),
        days_active = n_distinct(date),
        .groups = "drop"
    )

student_activities <- all_events_week %>%
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
    filter(total_days_completed == 0 & total_pns > 0)
print(paste("Number of students who've haven't dailyActivitiesCompleted in past week:", nrow(no_completion_students)))

# 2a. Identify Not Engaged Students (less playtime)
# Define threshold for "not engaged" (e.g., bottom 20% of playtime)
# playtime_threshold <- quantile(student_playtime$avg_daily_playtime[student_playtime$avg_daily_playtime > 0], 0.2, na.rm = TRUE) # nolint: line_length_linter.
playtime_threshold <- 10
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
write.csv(student_metrics, paste0("WT_Analyses/during_study/results/", date_var, "/week_student_metrics.csv"), row.names = FALSE)
write.csv(inactive_students, paste0("WT_Analyses/during_study/results/", date_var, "/week_no_pns.csv"), row.names = FALSE)
write.csv(no_completion_students, paste0("WT_Analyses/during_study/results/", date_var, "/week_nopns_completed.csv"), row.names = FALSE)
write.csv(not_playing_students, paste0("WT_Analyses/during_study/results/", date_var, "/week_playing_less.csv"), row.names = FALSE)


if (FALSE) {
    # Output the list of students for each metric
    write.csv(inactive_students, "alltime_inactive_students.csv", row.names = FALSE)
    write.csv(not_engaged_students, "alltime_not_engaged_students.csv", row.names = FALSE)
    write.csv(off_task_students, "alltime_off_task_students.csv", row.names = FALSE)
    write.csv(poor_performers, "alltime_poor_performers.csv", row.names = FALSE)

    #########################################
    ## PAST WEEK ANALYSIS
    #########################################

    # 1. Inactive Students in Past Week
    student_playtime_week <- playtime_week %>%
        group_by(service_id) %>%
        summarize(
            total_playtime_week = sum(time_played_minutes, na.rm = TRUE),
            avg_daily_playtime_week = mean(time_played_minutes, na.rm = TRUE),
            days_active_week = n_distinct(date),
            .groups = "drop"
        )

    # Get all unique students from the full dataset
    all_students <- unique(c(
        playtime_data$service_id,
        mission_data$service_id,
        pns_events_data$service_id
    ))

    # Create a complete list of students including those who were inactive in the past week
    all_students_df <- data.frame(service_id = all_students)
    student_playtime_week_complete <- all_students_df %>%
        left_join(student_playtime_week, by = "service_id") %>%
        mutate(
            total_playtime_week = ifelse(is.na(total_playtime_week), 0, total_playtime_week),
            days_active_week = ifelse(is.na(days_active_week), 0, days_active_week)
        )

    # Identify inactive students in the past week (zero playtime in the week)
    inactive_students_week <- student_playtime_week_complete %>%
        filter(total_playtime_week == 0)

    # Students who were active before but inactive in the past week
    previously_active_now_inactive <- inactive_students_week %>%
        inner_join(student_playtime %>% filter(total_playtime > 0), by = "service_id")

    print("\n--- PAST WEEK ANALYSIS ---")
    print("1. Inactive Students (Past Week):")
    print(paste("Number of inactive students in past week:", nrow(inactive_students_week)))
    print(paste("Number of previously active students now inactive:", nrow(previously_active_now_inactive)))

    # 2. Not Engaged Students in Past Week (less playtime)
    playtime_threshold_week <- quantile(student_playtime_week_complete$total_playtime_week[student_playtime_week_complete$total_playtime_week > 0], 0.2, na.rm = TRUE)

    not_engaged_students_week <- student_playtime_week_complete %>%
        filter(total_playtime_week > 0 & total_playtime_week <= playtime_threshold_week)

    print("\n2. Not Engaged Students (Past Week):")
    print(paste("Playtime threshold for 'not engaged' in past week:", playtime_threshold_week, "minutes"))
    print(paste("Number of 'not engaged' students in past week:", nrow(not_engaged_students_week)))

    # 3. Off-task Students in Past Week
    student_activities_week <- mission_week %>%
        group_by(service_id) %>%
        summarize(
            total_missions_started_week = sum(mission_started, na.rm = TRUE),
            total_missions_completed_week = sum(mission_completed, na.rm = TRUE),
            total_races_started_week = sum(raceactivity_started, na.rm = TRUE),
            total_races_completed_week = sum(raceactivity_completed, na.rm = TRUE),
            total_quizzes_started_week = sum(popquiz_started, na.rm = TRUE),
            total_quizzes_completed_week = sum(popquiz_completed, na.rm = TRUE),
            total_activities_week = sum(mission_started, raceactivity_started, popquiz_started, na.rm = TRUE),
            .groups = "drop"
        ) %>%
        mutate(
            race_ratio_week = ifelse(total_activities_week > 0,
                total_races_started_week / total_activities_week, 0
            )
        )

    off_task_students_week <- student_activities_week %>%
        filter(race_ratio_week > off_task_threshold & total_activities_week >= 5)

    print("\n3. Off-task Students (Past Week):")
    print(paste("Number of 'off-task' students in past week:", nrow(off_task_students_week)))

    # 4. Poorly Performing Students in Past Week
    student_performance_week <- pns_events_week %>%
        filter(result %in% c("correct", "incorrect")) %>%
        group_by(service_id, result) %>%
        summarize(count = n(), .groups = "drop") %>%
        pivot_wider(names_from = result, values_from = count, values_fill = 0) %>%
        mutate(
            total_attempts_week = correct + incorrect,
            success_rate_week = correct / total_attempts_week
        )

    poor_performers_week <- student_performance_week %>%
        filter(total_attempts_week >= 10 & success_rate_week <= performance_threshold)

    print("\n4. Poorly Performing Students (Past Week):")
    print(paste("Number of 'poorly performing' students in past week:", nrow(poor_performers_week)))

    # Create a combined dataset with all metrics for the past week
    student_metrics_week <- all_students_df %>%
        left_join(student_playtime_week_complete, by = "service_id") %>%
        left_join(student_activities_week, by = "service_id") %>%
        left_join(student_performance_week, by = "service_id") %>%
        mutate(
            is_inactive_week = service_id %in% inactive_students_week$service_id,
            is_not_engaged_week = service_id %in% not_engaged_students_week$service_id,
            is_off_task_week = service_id %in% off_task_students_week$service_id,
            is_poor_performer_week = service_id %in% poor_performers_week$service_id,
            flags_count_week = is_inactive_week + is_not_engaged_week + is_off_task_week + is_poor_performer_week
        )

    # Identify newly flagged students (students who weren't flagged in the overall analysis but are now flagged in the weekly analysis)
    newly_flagged_students <- student_metrics_week %>%
        left_join(student_metrics %>% select(service_id, flags_count), by = "service_id") %>%
        mutate(flags_count = ifelse(is.na(flags_count), 0, flags_count)) %>%
        filter(flags_count == 0 & flags_count_week > 0)

    print("\nNewly Flagged Students (Past Week):")
    print(paste("Number of newly flagged students:", nrow(newly_flagged_students)))

    # Output week-specific files
    write.csv(student_metrics_week, "student_metrics_week.csv", row.names = FALSE)
    write.csv(newly_flagged_students, "newly_flagged_students.csv", row.names = FALSE)

    #########################################
    ## DAILY PERFORMANCE TRACKER
    #########################################

    # Function to analyze a specific day's data
    analyze_day <- function(day_date) {
        date_str <- as.character(day_date)

        # Filter data for the specific day
        playtime_day <- playtime_data %>% filter(date == day_date)
        mission_day <- mission_data %>% filter(date == day_date)
        pns_events_day <- pns_events_data %>% filter(date == day_date)

        # 1. Activity summary
        active_students_count <- length(unique(playtime_day$service_id))

        # 2. Playtime statistics
        if (nrow(playtime_day) > 0) {
            avg_playtime <- mean(playtime_day$time_played_minutes, na.rm = TRUE)
            median_playtime <- median(playtime_day$time_played_minutes, na.rm = TRUE)
            max_playtime <- max(playtime_day$time_played_minutes, na.rm = TRUE)
        } else {
            avg_playtime <- 0
            median_playtime <- 0
            max_playtime <- 0
        }

        # 3. Activity counts
        if (nrow(mission_day) > 0) {
            missions_started <- sum(mission_day$mission_started, na.rm = TRUE)
            missions_completed <- sum(mission_day$mission_completed, na.rm = TRUE)
            races_started <- sum(mission_day$raceactivity_started, na.rm = TRUE)
            races_completed <- sum(mission_day$raceactivity_completed, na.rm = TRUE)
            quizzes_started <- sum(mission_day$popquiz_started, na.rm = TRUE)
            quizzes_completed <- sum(mission_day$popquiz_completed, na.rm = TRUE)

            mission_completion_rate <- ifelse(missions_started > 0,
                missions_completed / missions_started, 0
            )
            race_completion_rate <- ifelse(races_started > 0,
                races_completed / races_started, 0
            )
            quiz_completion_rate <- ifelse(quizzes_started > 0,
                quizzes_completed / quizzes_started, 0
            )
        } else {
            missions_started <- 0
            missions_completed <- 0
            races_started <- 0
            races_completed <- 0
            quizzes_started <- 0
            quizzes_completed <- 0
            mission_completion_rate <- 0
            race_completion_rate <- 0
            quiz_completion_rate <- 0
        }

        # 4. Performance
        if (nrow(pns_events_day) > 0) {
            performance_summary <- pns_events_day %>%
                filter(result %in% c("correct", "incorrect")) %>%
                group_by(result) %>%
                summarize(count = n(), .groups = "drop") %>%
                pivot_wider(names_from = result, values_from = count, values_fill = 0)

            if ("correct" %in% colnames(performance_summary) &&
                "incorrect" %in% colnames(performance_summary)) {
                correct_count <- performance_summary$correct
                incorrect_count <- performance_summary$incorrect
                total_count <- correct_count + incorrect_count
                success_rate <- ifelse(total_count > 0, correct_count / total_count, 0)
            } else {
                correct_count <- 0
                incorrect_count <- 0
                total_count <- 0
                success_rate <- 0
            }
        } else {
            correct_count <- 0
            incorrect_count <- 0
            total_count <- 0
            success_rate <- 0
        }

        # Return summary for the day
        data.frame(
            date = date_str,
            active_students = active_students_count,
            avg_playtime = avg_playtime,
            median_playtime = median_playtime,
            max_playtime = max_playtime,
            missions_started = missions_started,
            missions_completed = missions_completed,
            mission_completion_rate = mission_completion_rate,
            races_started = races_started,
            races_completed = races_completed,
            race_completion_rate = race_completion_rate,
            quizzes_started = quizzes_started,
            quizzes_completed = quizzes_completed,
            quiz_completion_rate = quiz_completion_rate,
            correct_count = correct_count,
            incorrect_count = incorrect_count,
            total_attempts = total_count,
            success_rate = success_rate
        )
    }

    # Create a daily performance tracker
    all_dates <- unique(c(
        playtime_data$date,
        mission_data$date,
        pns_events_data$date
    ))

    all_dates <- sort(all_dates, decreasing = TRUE)

    # Analyze each day
    daily_performance <- lapply(all_dates, analyze_day)
    daily_performance_df <- do.call(rbind, daily_performance)

    # Save the daily performance tracker
    write.csv(daily_performance_df, "daily_performance_tracker.csv", row.names = FALSE)

    # Extract yesterday's performance
    yesterday_performance <- daily_performance_df %>% filter(date == as.character(yesterday))

    print("\n--- YESTERDAY'S PERFORMANCE SUMMARY ---")
    if (nrow(yesterday_performance) > 0) {
        print(paste("Date:", yesterday_performance$date))
        print(paste("Active students:", yesterday_performance$active_students))
        print(paste("Average playtime:", round(yesterday_performance$avg_playtime, 2), "minutes"))
        print(paste("Success rate:", round(yesterday_performance$success_rate * 100, 2), "%"))
    } else {
        print("No data available for yesterday.")
    }

    # Recent Performance Trend Analysis
    if (length(all_dates) >= 5) {
        recent_days <- head(all_dates, 5)
        recent_performance <- daily_performance_df %>% filter(date %in% as.character(recent_days))

        print("\n--- RECENT 5-DAY PERFORMANCE TREND ---")
        print("Active Students:")
        print(recent_performance[order(recent_performance$date), c("date", "active_students")])

        print("\nAverage Playtime (minutes):")
        print(recent_performance[order(recent_performance$date), c("date", "avg_playtime")])

        print("\nSuccess Rate (%):")
        print(recent_performance[order(recent_performance$date), c("date", "success_rate")])
    }

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

        # Get weekly data
        student_week <- student_metrics_week %>% filter(service_id == student_id)

        if (nrow(student_week) > 0) {
            weekly_comparison <- data.frame(
                metric = c("Weekly Playtime", "Weekly Success Rate", "Weekly Race Ratio"),
                student_value = c(
                    student_week$total_playtime_week,
                    student_week$success_rate_week,
                    student_week$race_ratio_week
                ),
                average_value = c(
                    mean(student_metrics_week$total_playtime_week, na.rm = TRUE),
                    mean(student_metrics_week$success_rate_week, na.rm = TRUE, finite = TRUE),
                    mean(student_metrics_week$race_ratio_week, na.rm = TRUE)
                ),
                difference_pct = c(
                    (student_week$total_playtime_week - mean(student_metrics_week$total_playtime_week, na.rm = TRUE)) /
                        mean(student_metrics_week$total_playtime_week, na.rm = TRUE) * 100,
                    (student_week$success_rate_week - mean(student_metrics_week$success_rate_week, na.rm = TRUE, finite = TRUE)) /
                        mean(student_metrics_week$success_rate_week, na.rm = TRUE, finite = TRUE) * 100,
                    (student_week$race_ratio_week - mean(student_metrics_week$race_ratio_week, na.rm = TRUE)) /
                        mean(student_metrics_week$race_ratio_week, na.rm = TRUE) * 100
                )
            )

            comparison <- rbind(comparison, weekly_comparison)
        }

        list(
            student_id = student_id,
            flags = flags,
            comparison = comparison,
            recent_activity = playtime_data %>%
                filter(service_id == student_id) %>%
                arrange(desc(date)) %>%
                head(10)
        )
    }

    # Example: Get detailed comparison for the most concerning student
    if (nrow(top_concerning_students) > 0) {
        most_concerning_id <- top_concerning_students$service_id[1]
        print("\nDetailed Comparison for Most Concerning Student:")
        print(student_comparison(most_concerning_id))
    }

    # Visualize the distribution of students across metrics for overall and past week
    students_per_metric_overall <- c(
        nrow(inactive_students),
        nrow(not_engaged_students),
        nrow(off_task_students),
        nrow(poor_performers)
    )

    students_per_metric_week <- c(
        nrow(inactive_students_week),
        nrow(not_engaged_students_week),
        nrow(off_task_students_week),
        nrow(poor_performers_week)
    )

    metrics_names <- c("Inactive", "Not Engaged", "Off-Task", "Poor Performer")

    # Create a data frame for plotting both overall and weekly metrics
    metrics_plot_data <- data.frame(
        metric = rep(metrics_names, 2),
        count = c(students_per_metric_overall, students_per_metric_week),
        period = rep(c("Overall", "Past Week"), each = 4)
    )

    # Plot count of students per metric - comparing overall vs past week
    comparison_plot <- ggplot(metrics_plot_data, aes(x = metric, y = count, fill = period)) +
        geom_bar(stat = "identity", position = "dodge") +
        labs(
            title = "Number of Students per Metric: Overall vs Past Week",
            x = "Metric", y = "Count", fill = "Time Period"
        ) +
        theme_minimal()

    # Save the comparison plot
    ggsave("students_per_metric_comparison.png", width = 10, height = 6)

    # Create a time series plot of daily performance
    # Select key metrics for time series visualization
    time_series_data <- daily_performance_df %>%
        arrange(date) %>%
        select(date, active_students, avg_playtime, success_rate)

    # Convert date to Date type for proper plotting
    time_series_data$date <- as.Date(time_series_data$date)

    # Plot active students over time
    active_students_plot <- ggplot(time_series_data, aes(x = date, y = active_students)) +
        geom_line() +
        geom_point() +
        labs(
            title = "Active Students Over Time",
            x = "Date", y = "Number of Active Students"
        ) +
        theme_minimal()

    # Plot average playtime over time
    avg_playtime_plot <- ggplot(time_series_data, aes(x = date, y = avg_playtime)) +
        geom_line() +
        geom_point() +
        labs(
            title = "Average Playtime Over Time",
            x = "Date", y = "Average Playtime (minutes)"
        ) +
        theme_minimal()

    # Plot success rate over time
    success_rate_plot <- ggplot(time_series_data, aes(x = date, y = success_rate * 100)) +
        geom_line() +
        geom_point() +
        labs(
            title = "Success Rate Over Time",
            x = "Date", y = "Success Rate (%)"
        ) +
        theme_minimal()

    # Save the time series plots
    ggsave("active_students_trend.png", plot = active_students_plot, width = 10, height = 6)
    ggsave("avg_playtime_trend.png", plot = avg_playtime_plot, width = 10, height = 6)
    ggsave("success_rate_trend.png", plot = success_rate_plot, width = 10, height = 6)

    # Finally, provide a summary of all metrics
    cat("\n----- OVERALL SUMMARY -----\n")
    cat("Total number of students:", length(unique(student_metrics$service_id)), "\n")
    cat("Inactive students:", nrow(inactive_students), "\n")
    cat("Not engaged students:", nrow(not_engaged_students), "\n")
    cat("Off-task students:", nrow(off_task_students), "\n")
    cat("Poor performing students:", nrow(poor_performers), "\n")
    cat("Students with multiple flags:", nrow(students_with_multiple_flags), "\n")

    cat("\n----- PAST WEEK SUMMARY -----\n")
    cat("Active students in past week:", nrow(student_playtime_week_complete %>% filter(total_playtime_week > 0)), "\n")
    cat("Inactive students in past week:", nrow(inactive_students_week), "\n")
    cat("Not engaged students in past week:", nrow(not_engaged_students_week), "\n")
    cat("Off-task students in past week:", nrow(off_task_students_week), "\n")
    cat("Poor performing students in past week:", nrow(poor_performers_week), "\n")
    cat("Newly flagged students (not flagged overall but flagged in past week):", nrow(newly_flagged_students), "\n")

    # Function to get data for a specific student
    get_student_data <- function(student_id) {
        # Overall metrics
        overall_data <- student_metrics %>% filter(service_id == student_id)

        # Weekly metrics
        week_data <- student_metrics_week %>% filter(service_id == student_id)

        # Daily data for this student
        student_daily <- playtime_data %>%
            filter(service_id == student_id) %>%
            arrange(desc(date)) %>%
            head(10) # Last 10 days with activity

        # Daily performance
        student_performance_daily <- pns_events_data %>%
            filter(service_id == student_id) %>%
            group_by(date, result) %>%
            summarize(count = n(), .groups = "drop") %>%
            pivot_wider(names_from = result, values_from = count, values_fill = 0) %>%
            mutate(
                total_attempts = correct + incorrect,
                success_rate = ifelse(total_attempts > 0, correct / total_attempts, 0)
            ) %>%
            arrange(desc(date))

        # Daily race ratio
        student_activities_daily <- mission_data %>%
            filter(service_id == student_id) %>%
            group_by(date) %>%
            summarize(
                total_missions = mission_started,
                total_races = raceactivity_started,
                total_quizzes = popquiz_started,
                total_activities = mission_started + raceactivity_started + popquiz_started,
                race_ratio = ifelse(total_activities > 0, total_races / total_activities, 0),
                .groups = "drop"
            ) %>%
            arrange(desc(date))

        list(
            overall = overall_data,
            weekly = week_data,
            daily_playtime = student_daily,
            daily_performance = student_performance_daily,
            daily_activities = student_activities_daily
        )
    }

    # Example: Generate a report for a specific student
    # Note: In a real application, you might want to run this for each flagged student
    # Function to generate a report for a specific student
    generate_student_report <- function(student_id) {
        # Get student data
        student_data <- get_student_data(student_id)

        # Create a text report
        cat("\n----- STUDENT REPORT: ", student_id, " -----\n")

        # Overall metrics
        if (nrow(student_data$overall) > 0) {
            overall <- student_data$overall
            cat("OVERALL METRICS:\n")
            cat("Total playtime:", overall$total_playtime, "minutes\n")
            cat("Average daily playtime:", round(overall$avg_daily_playtime, 2), "minutes\n")
            cat("Success rate:", ifelse(!is.na(overall$success_rate),
                paste0(round(overall$success_rate * 100, 2), "%"), "N/A"
            ), "\n")
            cat("Race ratio:", ifelse(!is.na(overall$race_ratio),
                paste0(round(overall$race_ratio * 100, 2), "%"), "N/A"
            ), "\n")

            # Flags
            flags <- c()
            if (overall$is_inactive) flags <- c(flags, "Inactive")
            if (overall$is_not_engaged) flags <- c(flags, "Not Engaged")
            if (overall$is_off_task) flags <- c(flags, "Off-Task")
            if (overall$is_poor_performer) flags <- c(flags, "Poor Performer")

            if (length(flags) > 0) {
                cat("Flags:", paste(flags, collapse = ", "), "\n")
            } else {
                cat("Flags: None\n")
            }
        } else {
            cat("No overall metrics available for this student.\n")
        }

        # Weekly metrics
        if (nrow(student_data$weekly) > 0) {
            weekly <- student_data$weekly
            cat("\nPAST WEEK METRICS:\n")
            cat("Total playtime:", weekly$total_playtime_week, "minutes\n")
            cat("Average daily playtime:", round(weekly$avg_daily_playtime_week, 2), "minutes\n")
            cat("Days active in past week:", weekly$days_active_week, "days\n")
            cat("Success rate:", ifelse(!is.na(weekly$success_rate_week),
                paste0(round(weekly$success_rate_week * 100, 2), "%"), "N/A"
            ), "\n")
            cat("Race ratio:", ifelse(!is.na(weekly$race_ratio_week),
                paste0(round(weekly$race_ratio_week * 100, 2), "%"), "N/A"
            ), "\n")

            # Weekly flags
            flags_week <- c()
            if (weekly$is_inactive_week) flags_week <- c(flags_week, "Inactive")
            if (weekly$is_not_engaged_week) flags_week <- c(flags_week, "Not Engaged")
            if (weekly$is_off_task_week) flags_week <- c(flags_week, "Off-Task")
            if (weekly$is_poor_performer_week) flags_week <- c(flags_week, "Poor Performer")

            if (length(flags_week) > 0) {
                cat("Flags (Past Week):", paste(flags_week, collapse = ", "), "\n")
            } else {
                cat("Flags (Past Week): None\n")
            }
        } else {
            cat("No weekly metrics available for this student.\n")
        }

        # Recent daily activity
        if (nrow(student_data$daily_playtime) > 0) {
            cat("\nRECENT DAILY ACTIVITY:\n")
            recent_activity <- student_data$daily_playtime %>%
                select(date, time_played_minutes) %>%
                arrange(desc(date))

            for (i in 1:nrow(recent_activity)) {
                cat(as.character(recent_activity$date[i]), ": ",
                    recent_activity$time_played_minutes[i], " minutes\n",
                    sep = ""
                )
            }
        } else {
            cat("\nNo recent daily activity available for this student.\n")
        }

        # Return a formatted report for saving to file
        report <- capture.output({
            cat("STUDENT REPORT: ", student_id, "\n", sep = "")
            cat("Generated on: ", Sys.Date(), "\n\n")

            if (nrow(student_data$overall) > 0) {
                overall <- student_data$overall
                cat("OVERALL METRICS:\n")
                cat("Total playtime: ", overall$total_playtime, " minutes\n", sep = "")
                cat("Average daily playtime: ", round(overall$avg_daily_playtime, 2), " minutes\n", sep = "")
                cat("Days active: ", overall$days_active, "\n", sep = "")
                cat("Success rate: ", ifelse(!is.na(overall$success_rate),
                    paste0(round(overall$success_rate * 100, 2), "%"), "N/A"
                ), "\n", sep = "")
                cat("Race ratio: ", ifelse(!is.na(overall$race_ratio),
                    paste0(round(overall$race_ratio * 100, 2), "%"), "N/A"
                ), "\n\n", sep = "")
            }

            if (nrow(student_data$weekly) > 0) {
                weekly <- student_data$weekly
                cat("PAST WEEK METRICS:\n")
                cat("Total playtime: ", weekly$total_playtime_week, " minutes\n", sep = "")
                cat("Average daily playtime: ", round(weekly$avg_daily_playtime_week, 2), " minutes\n", sep = "")
                cat("Days active: ", weekly$days_active_week, " days\n", sep = "")
                cat("Success rate: ", ifelse(!is.na(weekly$success_rate_week),
                    paste0(round(weekly$success_rate_week * 100, 2), "%"), "N/A"
                ), "\n", sep = "")
                cat("Race ratio: ", ifelse(!is.na(weekly$race_ratio_week),
                    paste0(round(weekly$race_ratio_week * 100, 2), "%"), "N/A"
                ), "\n\n", sep = "")
            }

            if (nrow(student_data$daily_playtime) > 0) {
                cat("RECENT DAILY ACTIVITY:\n")
                recent_activity <- student_data$daily_playtime %>%
                    select(date, time_played_minutes) %>%
                    arrange(desc(date))

                for (i in 1:nrow(recent_activity)) {
                    cat(as.character(recent_activity$date[i]), ": ",
                        recent_activity$time_played_minutes[i], " minutes\n",
                        sep = ""
                    )
                }
                cat("\n")
            }

            if (nrow(student_data$daily_performance) > 0) {
                cat("RECENT PERFORMANCE:\n")
                recent_perf <- student_data$daily_performance %>%
                    select(date, correct, incorrect, success_rate) %>%
                    arrange(desc(date))

                for (i in 1:min(5, nrow(recent_perf))) {
                    cat(as.character(recent_perf$date[i]), ": ",
                        recent_perf$correct[i], " correct, ",
                        recent_perf$incorrect[i], " incorrect (",
                        round(recent_perf$success_rate[i] * 100, 2), "%)\n",
                        sep = ""
                    )
                }
            }
        })

        # Save the report to a file
        report_filename <- paste0("student_report_", student_id, ".txt")
        writeLines(report, report_filename)

        invisible(report) # Return the report invisibly
    }

    # Function to get data for a specific student (prerequisite for generate_student_report)
    get_student_data <- function(student_id) {
        # Overall metrics
        overall_data <- student_metrics %>% filter(service_id == student_id)

        # Weekly metrics
        week_data <- student_metrics_week %>% filter(service_id == student_id)

        # Daily data for this student
        student_daily <- playtime_data %>%
            filter(service_id == student_id) %>%
            arrange(desc(date)) %>%
            head(10) # Last 10 days with activity

        # Daily performance
        student_performance_daily <- pns_events_data %>%
            filter(service_id == student_id) %>%
            group_by(date, result) %>%
            summarize(count = n(), .groups = "drop") %>%
            pivot_wider(names_from = result, values_from = count, values_fill = 0) %>%
            mutate(
                total_attempts = correct + incorrect,
                success_rate = ifelse(total_attempts > 0, correct / total_attempts, 0)
            ) %>%
            arrange(desc(date))

        # Daily race ratio
        student_activities_daily <- mission_data %>%
            filter(service_id == student_id) %>%
            group_by(date) %>%
            summarize(
                total_missions = mission_started,
                total_races = raceactivity_started,
                total_quizzes = popquiz_started,
                total_activities = mission_started + raceactivity_started + popquiz_started,
                race_ratio = ifelse(total_activities > 0, total_races / total_activities, 0),
                .groups = "drop"
            ) %>%
            arrange(desc(date))

        list(
            overall = overall_data,
            weekly = week_data,
            daily_playtime = student_daily,
            daily_performance = student_performance_daily,
            daily_activities = student_activities_daily
        )
    }
}
