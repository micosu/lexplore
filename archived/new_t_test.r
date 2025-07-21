# First, let's load the data
# Assuming your files are named "pretest.csv" and "posttest.csv"
pretest <- read.csv("WT_Analyses/pre_tests/Grading_Results.csv")
posttest <- read.csv("WT_Analyses/mid_tests/Grading_Results.csv")

# Check for "#N/D" IDs in both datasets
pre_missing_ids <- sum(pretest$id == "#N/D" | is.na(pretest$id) | pretest$id == "")
post_missing_ids <- sum(posttest$id == "#N/D" | is.na(posttest$id) | posttest$id == "")

cat("Pretest records with missing IDs (#N/D):", pre_missing_ids, "\n")
cat("Posttest records with missing IDs (#N/D):", post_missing_ids, "\n")

# Remove records with "#N/D" IDs before merging
pretest_clean <- pretest[pretest$id != "#N/D" & !is.na(pretest$id) & pretest$id != "", ]
posttest_clean <- posttest[posttest$id != "#N/D" & !is.na(posttest$id) & posttest$id != "", ]

# Count unique IDs in each dataset
pre_unique_ids <- length(unique(pretest_clean$id))
post_unique_ids <- length(unique(posttest_clean$id))

cat("Unique IDs in pretest:", pre_unique_ids, "\n")
cat("Unique IDs in posttest:", post_unique_ids, "\n")

cols_to_keep <- c(
    "id", "timestamp", "original_score", "possible_match",
    "total_correct", "total_questions", "percentage",
    "total_trained_correct", "total_trained_questions", "trained_percentage",
    "total_untrained_correct", "total_untrained_questions", "untrained_percentage"
)

pretest_subset <- pretest_clean[, cols_to_keep]
posttest_subset <- posttest_clean[, cols_to_keep]
# Merge the datasets by student ID
combined <- merge(pretest_subset, posttest_subset,
    by = "id",
    suffixes = c(".pre", ".post")
)

# Count how many students were successfully matched
matched_students <- nrow(combined)
cat("Students matched between pretest and posttest:", matched_students, "\n")
cat("Students in pretest but not in posttest:", pre_unique_ids - matched_students, "\n")
cat("Students in posttest but not in pretest:", post_unique_ids - matched_students, "\n")

# Continue with the analysis using the numeric score columns
pre_mean <- mean(combined$percentage.pre)
post_mean <- mean(combined$percentage.post)
pre_sd <- sd(combined$percentage.pre)
post_sd <- sd(combined$percentage.post)
improvement <- post_mean - pre_mean

# Display summary statistics
cat("Pretest mean proportion correct:", pre_mean, "(SD =", pre_sd, ")\n")
cat("Posttest mean proportion correct:", post_mean, "(SD =", post_sd, ")\n")
cat("Mean improvement in proportion:", improvement, "\n")

# Calculate percentage of students who improved
improved <- sum(combined$percentage.post > combined$percentage.pre)
percent_improved <- improved / nrow(combined) * 100
cat("Percentage of students who improved:", percent_improved, "%\n")

# Perform paired t-test
t_test_result <- t.test(combined$percentage.post, combined$percentage.pre, paired = TRUE)
print(t_test_result)

# Convert percentage strings to numeric if necessary
# (optional safety check if you're reading from CSV where values might be stored as text)
# combined$trained_percentage.pre <- as.numeric(combined$trained_percentage.pre)
# combined$trained_percentage.post <- as.numeric(combined$trained_percentage.post)
# combined$untrained_percentage.pre <- as.numeric(combined$untrained_percentage.pre)
# combined$untrained_percentage.post <- as.numeric(combined$untrained_percentage.post)

# Trained word improvement
trained_improvement <- combined$trained_percentage.post - combined$trained_percentage.pre
untrained_improvement <- combined$untrained_percentage.post - combined$untrained_percentage.pre



# Summary stats

cat("\n--- Trained Words Analysis ---\n")
cat("Pretest trained mean:", mean(combined$trained_percentage.pre), "\n")
cat("Posttest trained mean:", mean(combined$trained_percentage.post), "\n")
cat("Mean improvement in trained words:", mean(trained_improvement), "\n")

cat("\n--- Untrained Words Analysis ---\n")
cat("Pretest untrained mean:", mean(combined$untrained_percentage.pre), "\n")
cat("Posttest untrained mean:", mean(combined$untrained_percentage.post), "\n")
cat("Mean improvement in untrained words:", mean(untrained_improvement), "\n")

# Paired t-tests
trained_ttest <- t.test(combined$trained_percentage.post, combined$trained_percentage.pre, paired = TRUE)
untrained_ttest <- t.test(combined$untrained_percentage.post, combined$untrained_percentage.pre, paired = TRUE)

cat("\n--- T-Test Results ---\n")
cat("Trained words paired t-test:\n")
print(trained_ttest)

cat("Untrained words paired t-test:\n")
print(untrained_ttest)

# Optional: Test whether improvement in trained > untrained (i.e., interaction effect)
gain_diff <- trained_improvement - untrained_improvement
cat("\n--- Difference in Gains (Trained - Untrained) ---\n")
cat("Mean difference:", mean(gain_diff), "\n")
cat("T-test on difference in gain:\n")
print(t.test(gain_diff))

# --- Visualization of gains in trained vs untrained words ---
library(ggplot2)
library(tidyr)

# Melt data for plotting
gain_plot_data <- combined[, c(
    "id",
    "trained_percentage.pre", "trained_percentage.post",
    "untrained_percentage.pre", "untrained_percentage.post"
)]

gain_plot_long <- pivot_longer(gain_plot_data,
    cols = -id,
    names_to = c("word_type", "timepoint"),
    names_pattern = "(trained|untrained)_percentage\\.(pre|post)",
    values_to = "percentage"
)

p <- ggplot(gain_plot_long, aes(x = timepoint, y = percentage, group = id)) +
    geom_line(alpha = 0.3) +
    geom_point() +
    stat_summary(aes(group = word_type), fun = mean, geom = "line", size = 1.2, color = "red") +
    facet_wrap(~word_type) +
    theme_minimal() +
    labs(
        title = "Performance Change for Trained vs Untrained Words",
        x = "Timepoint", y = "Percent Correct"
    )

print(p)
