import pandas as pd

# Read the data
words_learned = pd.read_csv(f"flag_files/june11/words_learned.csv")
words_df = pd.read_csv('/Users/yaboi/Desktop/Lexplore/adaptivetestapp/adaptivetest/only_lexile_all_columns.csv')

# Check for required columns
required_word_cols = ['word_id', 'word']
missing_cols = [col for col in required_word_cols if col not in words_df.columns]
if missing_cols:
    print(f"Error: Missing required columns in words_df: {missing_cols}")
    exit()

# Create a mapping dictionary from word_id to word
word_mapping = dict(zip(words_df['word_id'].astype(str), words_df['word']))

# Replace word_id with actual words in words_learned
words_learned['word_id'] = words_learned['word_id'].astype(str)
words_learned['word'] = words_learned['word_id'].map(word_mapping)

# Check for any unmapped word IDs
unmapped_ids = words_learned[words_learned['word'].isna()]['word_id']
if not unmapped_ids.empty:
    print(f"Warning: Could not find words for these IDs: {unmapped_ids.tolist()}")

# Display the results
print("Words learned with actual words:")
print(words_learned[['word_id', 'word']].head(10))

# Optional: Save the updated DataFrame
words_learned.to_csv("flag_files/june11/updated_words_learned.csv", index=False)