import csv
import pandas as pd
# File checking how many students answered multi-select questions with only one answer
if __name__ == "__main__":
    original = 'pre_tests/Second_Renamed_Columns_v2.csv'
    df = pd.read_csv(original)
    all_count = 0
    
    # Iterate over rows using iterrows() or itertuples()
    for index, row in df.iterrows():
        count = 0
        for i in range(13, 19):  # columns 13, 14, 15, 16, 17, 18
            # Check if the column exists and contains "|"
            if i < len(df.columns) and pd.notna(row.iloc[i]) and "|" not in str(row.iloc[i]):
                # print(row["id"])  # Assuming "id" is a valid column name
                count += 1
            
        if count == 6:
            all_count += 1
    
    print(f"Total rows with 6 matching columns: {all_count} out of {len(df)}")