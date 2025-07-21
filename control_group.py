import pandas as pd

# Example assumes you have a 'gain_score' column (post - pre)

student_metrics = pd.read_csv("during_study/results/june11/student_metrics.csv")
second_graders = pd.read_csv('pre_tests/Second_Grading_results.csv')
student_scores = pd.read_csv("test_metrics.csv")

# Get students in student_scores but not in student_metrics
missing_students = student_scores[~student_scores['id'].isin(student_metrics['service_id'])]

missing_second_graders = second_graders[~second_graders['id'].isin(student_metrics['service_id'])]
# Count them
count = len(missing_students)
print(f"Students in scores but not in metrics: {count}")
print(f"Second graders in pretest but not in metrics: {len(missing_second_graders)}")

# Save to new file
missing_students.to_csv("students_missing_from_metrics.csv", index=False)
missing_second_graders.to_csv("second_grade_missing.csv", index=False)