# Load required packages
library(dplyr) # For data manipulation

# Read the datasets correctly
all_metrics <- read.csv("student_metrics_combined.csv", check.names = TRUE)
pretest <- read.csv("WT_Analyses/pre_tests/ANON_SecondGrade_PreTest.csv", check.names = TRUE)
# Function to convert fraction strings (like "12 / 30") to decimal values
# Improved function to handle potential errors in conversion
convert_fraction <- function(frac_str) {
    # Check if the value is NA or empty
    if (is.na(frac_str) || frac_str == "") {
        return(NA)
    }

    # Try to split the string by "/"
    parts <- tryCatch(
        {
            strsplit(as.character(frac_str), "/")[[1]]
        },
        error = function(e) {
            return(c(NA, NA))
        }
    )

    # If we don't have exactly two parts, return NA
    if (length(parts) != 2) {
        return(NA)
    }

    # Try to convert to numeric, handling errors
    numerator <- suppressWarnings(as.numeric(trimws(parts[1])))
    denominator <- suppressWarnings(as.numeric(trimws(parts[2])))

    # Check if either conversion failed
    if (is.na(numerator) || is.na(denominator) || denominator == 0) {
        return(NA)
    }

    # Return the decimal value
    return(numerator / denominator)
}

# Apply the conversion function to the score column
# Assuming the score is in a column - you'll need to replace "score_column_name" with the actual column name
pretest$score_decimal <- sapply(pretest$Column2, convert_fraction)

na_rows <- which(is.na(pretest$score_decimal))
if (length(na_rows) > 0) {
    # Print the original values that couldn't be converted
    print("These values couldn't be converted:")
    print(pretest$score_column_name[na_rows])
}
# Rename Column6 to service_id for merging
pretest <- pretest %>% rename(service_id = Column34)
# Select only the columns we need from pretest
pretest_subset <- pretest %>% select(service_id, score_decimal)

# Merge the datasets
merged_data <- left_join(all_metrics, pretest_subset, by = "service_id")

other_columns <- setdiff(names(merged_data), c("service_id", "score_decimal"))

# Create new dataframe with columns in desired order
merged_data <- merged_data %>%
    select(service_id, score_decimal, all_of(other_columns))

# View the first few rows to verify the merge
head(merged_data)

write.csv(merged_data, "WT_Analyses/all_metrics_all_time.csv", row.names = FALSE)
