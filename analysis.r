# Load necessary libraries
library(dplyr)
library(ggplot2)
library(tidyr)
library(lubridate)

playtime_data <- read.csv("data/wt_guid__wt_daycycle_event_date___playtime_000.csv", check.names = TRUE)
# names(playtime_data) <- trimws(names(playtime_data))
words_data <- read.csv("data/wt_guid__word_id___words_learned_000.csv", check.names = TRUE)
interaction_data <- read.csv("data/stg_mysql__word_events__interaction_events000.csv", check.names = TRUE)
mission_data <- read.csv("data/wt_guid__wt_daycycle_event_date___mission_counts_000.csv", check.names = TRUE)
# 1. Daily Usage Patterns
# This shows how much time each team member is spending in the game each day
playtime_analysis <- function(playtime_data) {
  playtime_data %>%
    mutate(date = as.Date(wt_daycycle_event_date)) %>%
    group_by(guid, date) %>%
    summarize(daily_minutes = sum(time_played_minutes)) %>%
    ggplot(aes(x = date, y = daily_minutes, color = guid)) +
    geom_line() +
    geom_point() +
    labs(title = "Daily Time Spent in Game", 
         x = "Date", 
         y = "Minutes Played",
         color = "Team Member") +
    theme_minimal()
}

# 2. Words Learned Progress
# This tracks how many new words each person is learning over time
words_learned_analysis <- function(words_data) {
  words_data %>%
    group_by(guid, first_served) %>%
    summarize(count = n()) %>%
    mutate(date = as.Date(first_served)) %>%
    arrange(guid, date) %>%
    group_by(guid) %>%
    mutate(cumulative_words = cumsum(count)) %>%
    ggplot(aes(x = date, y = cumulative_words, color = guid)) +
    geom_line() +
    labs(title = "Cumulative Words Learned Over Time",
         x = "Date",
         y = "Total Words",
         color = "Team Member") +
    theme_minimal()
}

# 3. Activity Success Rates
# This examines success rates across different activity types
activity_success_analysis <- function(interaction_data) {
  interaction_data %>%
    group_by(guid, activity_type) %>%
    summarize(
      attempts = n(),
      successes = sum(success == "t"),
      success_rate = successes / attempts
    ) %>%
    ggplot(aes(x = activity_type, y = success_rate, fill = guid)) +
    geom_col(position = "dodge") +
    labs(title = "Success Rates by Activity Type",
         x = "Activity Type",
         y = "Success Rate",
         fill = "Team Member") +
    theme_minimal() +
    theme(axis.text.x = element_text(angle = 45, hjust = 1))
}

# 4. Activity Completion Patterns
# This shows which types of activities team members tend to complete vs abort
activity_completion_analysis <- function(mission_data) {
  mission_data %>%
    pivot_longer(
      cols = ends_with(c("_started", "_completed", "_aborted")),
      names_to = "metric",
      values_to = "count"
    ) %>%
    mutate(
      activity_type = gsub("_started|_completed|_aborted", "", metric),
      action = gsub(".*_", "", metric)
    ) %>%
    filter(count > 0) %>%
    group_by(guid, activity_type, action) %>%
    summarize(total = sum(count)) %>%
    ggplot(aes(x = activity_type, y = total, fill = action)) +
    geom_col(position = "dodge") +
    facet_wrap(~guid) +
    labs(title = "Activity Completion Patterns by Team Member",
         x = "Activity Type",
         y = "Count",
         fill = "Action") +
    theme_minimal() +
    theme(axis.text.x = element_text(angle = 45, hjust = 1))
}

# 5. Word Learning Efficiency
# This examines how many attempts it takes to learn words
learning_efficiency_analysis <- function(words_learned_data) {
  # Parse the attempts column (assuming it's stored as a string representation of a list)
  # Adjust this based on the actual format in your data
  words_learned_data %>%
    mutate(avg_attempts = sapply(strsplit(attempts, ","), function(x) mean(as.numeric(x)))) %>%
    group_by(guid) %>%
    summarize(
      words_count = n(),
      avg_attempts_per_word = mean(avg_attempts, na.rm = TRUE)
    ) %>%
    ggplot(aes(x = guid, y = avg_attempts_per_word)) +
    geom_col(fill = "steelblue") +
    geom_text(aes(label = round(avg_attempts_per_word, 2)), vjust = -0.5) +
    labs(title = "Average Attempts Required to Learn Words",
         x = "Team Member",
         y = "Average Attempts") +
    theme_minimal()
}



name_mapping <- data.frame(
  guid = c("a555e91c-49aa-4888-b87d-e0a930388ed0", "f377fb20-4c29-4c14-9336-f1678bfca296", "c5eab1c5-facb-4a90-839b-aafcb6da125f", "8ccca471-dae9-4754-960b-2f7c7877da24", "3cffe8d0-6ca8-411f-a188-128cdb5a51b5"),  # Replace with actual GUIDs
  name = c("Hope", "Janet", "Michael", "Vanessa", "Yan")   # Replace with actual names
)

# Example of how to use this mapping in your analyses
# For data frame operations, use left_join
# playtime_with_names <- playtime_data %>%
#   left_join(name_mapping, by = "guid") %>%
# #   Replace guid with name in the data
#   mutate(team_member = name) %>%
#   select(-guid)  # Remove the original guid column if desired

# playtime_with_names <- merge(playtime_data, name_mapping, by = "guid", all.x = TRUE, all.y = TRUE)
# playtime_with_names <- playtime_with_names %>% mutate(team_member = name)

playtime_summary <- playtime_analysis(playtime_data)
print(playtime_summary)