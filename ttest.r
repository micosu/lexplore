# First, let's load the data
# Assuming your files are named "pretest.csv" and "posttest.csv"
pretest <- read.csv("WT_Analyses/pre_tests/ANON_SecondGrade_PreTest.csv")
posttest <- read.csv("WT_Analyses/mid_tests/ANON_Second_Grade_WT_Pretest_2.csv")

# Function to convert score strings like "16 / 30" to numeric values
convert_score <- function(score_str) {
    # Check if the score is a string in the format "X / Y"
    if (is.character(score_str) && grepl(" / ", score_str)) {
        # Extract the numbers before and after the slash
        parts <- strsplit(score_str, " / ")[[1]]
        numerator <- as.numeric(parts[1])
        denominator <- as.numeric(parts[2])

        # Return the fraction
        return(numerator / denominator)
    } else {
        # If it's already numeric or in another format, try to convert directly
        return(as.numeric(score_str))
    }
}

# Apply the conversion function to score columns
pretest$score_numeric <- sapply(pretest$Score, convert_score)
posttest$score_numeric <- sapply(posttest$Score, convert_score)

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

# Merge the datasets by student ID
combined <- merge(pretest_clean, posttest_clean,
    by = "id",
    suffixes = c(".pre", ".post")
)

# Count how many students were successfully matched
matched_students <- nrow(combined)
cat("Students matched between pretest and posttest:", matched_students, "\n")
cat("Students in pretest but not in posttest:", pre_unique_ids - matched_students, "\n")
cat("Students in posttest but not in pretest:", post_unique_ids - matched_students, "\n")

# Continue with the analysis using the numeric score columns
pre_mean <- mean(combined$score_numeric.pre)
post_mean <- mean(combined$score_numeric.post)
pre_sd <- sd(combined$score_numeric.pre)
post_sd <- sd(combined$score_numeric.post)
improvement <- post_mean - pre_mean

# Display summary statistics
cat("Pretest mean proportion correct:", pre_mean, "(SD =", pre_sd, ")\n")
cat("Posttest mean proportion correct:", post_mean, "(SD =", post_sd, ")\n")
cat("Mean improvement in proportion:", improvement, "\n")

# Calculate percentage of students who improved
improved <- sum(combined$score_numeric.post > combined$score_numeric.pre)
percent_improved <- improved / nrow(combined) * 100
cat("Percentage of students who improved:", percent_improved, "%\n")

# Perform paired t-test
t_test_result <- t.test(combined$score_numeric.post, combined$score_numeric.pre, paired = TRUE)
print(t_test_result)

# Create a visualization of individual changes
boxplot(combined$score_numeric.pre, combined$score_numeric.post,
    names = c("Pretest", "Posttest"),
    main = "Comparison of Pretest and Posttest Scores",
    ylab = "Score (proportion correct)"
)

# For a more detailed visualization with individual student trajectories
library(ggplot2)
library(reshape2)

# Restructure data for ggplot
plot_data <- melt(combined[, c("id", "score_numeric.pre", "score_numeric.post")],
    id.vars = "id",
    variable.name = "test",
    value.name = "score"
)

# Fix the labels for better readability
plot_data$test <- factor(plot_data$test,
    levels = c("score_numeric.pre", "score_numeric.post"),
    labels = c("Pretest", "Posttest")
)

# Create a more advanced plot
ggplot(plot_data, aes(x = test, y = score, group = id)) +
    geom_line(alpha = 0.3) +
    geom_point() +
    stat_summary(aes(group = 1), fun = mean, geom = "line", size = 1, color = "red") +
    theme_minimal() +
    labs(
        title = "Student Score Changes from Pretest to Posttest",
        x = "Test", y = "Score (proportion correct)"
    )
