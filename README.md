# Lexplore Data Analysis

# First-time Setup Instructions

This guide will walk you through how to set up and try out the adaptive testing app locally. The following commands should be run in your terminal.

## 1. Clone the repo:

```
git clone https://github.com/micosu/lexplore.git
cd lexplore
```

## 2. Create and activate a virtual environment:

### On Mac

```
python3 -m venv venv OR python -m venv venv (try both, see which works)
source venv/bin/activate
```

### On Windows:

```
python -m venv venv
source venv\Scripts\activate
```

## 3. Install dependencies:

    ```
    pip install -r requirements.txt
    ```

# General Use

## Code for processing tests

convert_pretest.py : Code used to grade tests. Contains answer keys for each exam.  
**REQUIRED**

- File for test to grade
  Change this line to the location of the test file

```
original = 'pre_tests/ANON_SecondGrade_PreTest.csv'
```

- Choose which answer key and what are the trained words
  Change this to use the correct answer key and trained / untrained word sets

```
results = grade_student_csv(renamed, mid_key_second, trained_second, untrained_second, results_name)
```

**Generates**

- File that renames questions to be 1-30 and grading results file that gives more details about trained and untrained questions
  Change this line to the location of the output files

```
renamed = 'mid_tests/Second_Renamed_Columns.csv'
results_name = 'mid_tests/Second_Grading_Results.csv'
```

## Code for analyzing tests

test_analysis.py : Code used to analyze tests and check performance from pret-test to post-tests

**REQUIRED**

- Files for the pretests and posttests to grade
  Change these lines to the locations of the test files

```
second_pretest = pd.read_csv("pre_tests/Second_Grading_Results.csv")
second_midtest = pd.read_csv("mid_tests/Second_Grading_Results.csv")

fourth_pretest = pd.read_csv("pre_tests/Fourth_Grading_Results.csv")
fourth_midtest = pd.read_csv("mid_tests/Fourth_Grading_Results.csv")
```

- Choose which answer key and what are the trained words
  Change this to use the correct answer key and trained / untrained word sets

```
results = grade_student_csv(renamed, mid_key_second, trained_second, untrained_second, results_name)
```

**Generates**

- Different metrics about the test data (performance change from pretest to posttest, and whether
  changes to performance were significant)

- File with metrics about change in performance (overall, trained, and untrained) for each student

```
tests.to_csv(f"test_metrics.csv", index=False)
```

- Different plots / visualizations for the test data

## Code for analyzing performance in Word Tag

during_study/alltime_calculations.py : Code used to analyze gameplay during study

**REQUIRED**

- In order to do these analyses, you need to download the following files from the bucket: - Playtime data - Words Learned - Interaction Events - Game Events
  These files should be in a folder of the date that you downloaded it.

```
date_var = "june11" # Replace with date of when you downloaded data.  This should be a folder

playtime_data = pd.read_csv(f"flag_files/{date_var}/wt_guid__wt_daycycle_event_date___playtime_000.csv")
word_data = pd.read_csv(f"flag_files/{date_var}/wt_guid__word_id___words_learned_000.csv")
interaction_data = pd.read_csv(f"flag_files/june11/updated_events.csv")
all_events_data = pd.read_csv(f"flag_files/{date_var}/int_game_events_000.csv")
```

**Generates**

- Student metrics

- File with metrics about gameplay (playtime, activities completed, days active, etc) for each student

```
student_metrics.to_csv(f"results/{date_var}/student_metrics.csv", index=False)
```

## Code for analyzing relationship between performance on test and gameplay

overall_analysis.py : Code used to analyze relationship between performance on test and gameplay

**REQUIRED**

- In order to do these analyses, you need the files for student metrics in game and on the test (provided).

```
student_metrics = pd.read_csv("during_study/results/june11/student_metrics.csv")
student_scores = pd.read_csv("test_metrics.csv")
```

**Generates**

- ANOVA test results of data based on different groups

- You can modify what groups are used, by changing what column of student metrics is used

```
all_metrics['exposure_group'] = pd.qcut(all_metrics['words_with_4plus_exposures'], q=3, labels=['low', 'med', 'high'])
```

- Finally you can run the ANOVA test with the group you choose

```
print("Words w/ 4+ exposures")
model = ols('overall_change ~ C(trained_with_4plus_group)', data=all_metrics).fit()
anova_table = sm.stats.anova_lm(model, typ=2)
print(anova_table)
```
