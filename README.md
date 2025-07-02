# Lexplore Data Analysis

# First-time Setup Instructions

This guide will walk you through how to set up and try out the adaptive testing app locally. The following commands should be run in your terminal.

## 1. Clone the repo:

    ```bash
    git clone https://github.com/micosu/lexplore.git
    cd lexplore
    ```

## 2. Create and activate a virtual environment:

### On Mac

    ```bash
    python3 -m venv venv OR python -m venv venv (try both, see which works)
    source venv/bin/activate
    ```

### On Windows:

    ```bash
    python -m venv venv
    source venv\Scripts\activate
    ```

## 3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

# General Use

## Code for processing tests

convert_pretest.py : Code used to grade tests. Contains answer keys for each exam.  
** REQUIRED **

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

** Generates **

- File that renames questions to be 1-30 and grading results file that gives more details about trained and untrained questions
  Change this line to the location of the output files

```
renamed = 'mid_tests/Second_Renamed_Columns.csv'
results_name = 'mid_tests/Second_Grading_Results.csv'
```

## Code for analyzing tests

test_analysis.py : Code used to analyze tests and check performance from pret-test to post-tests
