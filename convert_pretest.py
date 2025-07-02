import pandas as pd
import csv

# Fourth Grade Pretest 1
pre_key_fourth = {
    "1": "Sturdy",
    "2": "Treacherous",
    "3": "Cunning",
    "4": "Luscious",
    "5": "Breathtaking",
    "6": "Diversity",
    "7": "Fragrance",
    "8": "Pandemonioum",  # Note: This might be misspelled "Pandemonium"
    "9": "Nuisance",
    "10": "Assist",
    "11": "Assemble",
    "12": "Consume",
    # For question 13 about "delirious", all three sentences are correct
    "13": {
        "correct_answers": [
            "After staying awake for two nights, Ryan became delirious and started babbling nonsense.",
            "She was delirious with excitement when her favorite band walked onto the stage.",
            "The high fever made him delirious, so he couldn't recognize anyone around him."
        ],
        "word": "delirious"
    },
    # For question 14 about "demonstrate", all three sentences are correct
    "14": {
        "correct_answers": [
            "Our teacher asked us to demonstrate the lab experiment in front of the class.",
            "The chef will demonstrate how to make homemade pasta from scratch.",
            "Could you demonstrate the proper way to wrap a bandage on my arm?"
        ],
        "word": 'demonstrate'
    },
    # For question 15 about "clarify", all four sentences are correct
    "15": {
        "correct_answers": [
            "The coach paused practice to clarify the new drill for the players.",
            "I asked my teacher to clarify how he would grade our homework before turning it in.",
            "Can you clarify the instructions for this game? I'm a bit confused about the rules.",
            "She called customer service to clarify the hidden fees on her bill"
        ],
        "word": "clarify"
    },
    # For question 16 about "evaluate", all four sentences are correct
    "16": {
        "correct_answers": [
            "The scientist wants to evaluate the data carefully before publishing the results.",
            "I need to evaluate the pros and cons of moving to a bigger apartment.",
            "The judges will evaluate each contestant's performance on creativity and skill.",
            "We should evaluate all the recipes before deciding which one to cook for dinner."
        ],
        "word": "evaluate"
    },
    # For question 17 about "opinionated", all three sentences are correct
    "17": {
        "correct_answers": [
            "The opinionated writer always writes articles that spark debate.",
            "She's very opinionated about fashion, arguing that bright colors are the only stylish choice.",
            "My uncle is so opinionated that he insists no one can grill burgers better than he can."
        ],
        "word": "opinionated"
    },
    # For question 18 about "scamper", both sentences are correct
    "18": {
        "correct_answers": [
            "The children scampered across the lawn when the ice cream truck arrived.",
            "I watched the chipmunk scamper under the fence to hide from the cat."
        ],
        "word": "scamper"
    },
    "19": "rebellious",
    "20": "intense",
    "21": "phenomenon",
    "22": "velocity",
    "23": "define",
    "24": "interpret",
    "25": "empathy",
    "26": "energetic",
    "27": "accumulate",
    "28": "celestial",
    "29": "precise",
    "30": "substantial"
}

# Fourth Grade Pretest 2
mid_key_fourth = {
    "1": "Glorious",
    "2": "Adventurous",
    "3": "Lethal",
    "4": "Rebellious",
    "5": "Celestial",
    "6": "Velocity",
    "7": "Empathy",
    "8": "Phenomenon",
    "9": "Energetic",
    "10": "Define",
    "11": "Contrast",
    "12": "Watchful",
    # For question 13 about "emphasis", all three sentences are correct
    "13": {
        "correct_answers": [
            "Our teacher placed special emphasis on punctuation during writing class today.",
            "The coach's emphasis on teamwork helped the players win the championship.",
            "When speaking, actors use emphasis to highlight important words or emotions."
        ],
        "word": "emphasis"
    },
    # For question 14 about "assist", all three sentences are correct
    "14": {
        "correct_answers": [
            "The nurse will assist the patient in walking down the hallway.",
            "The firefighter rushed over to assist the child trapped inside the building.",
            "My older brother offered to assist me with my difficult homework assignment."
        ],
       "word": "assist"
    },
    # For question 15 about "precise", all four sentences are correct
    "15": {
        "correct_answers": [
            "The chef gave precise instructions to her assistants about the cooking temperature.",
            "For the experiment to work, you must add precise amounts of each chemical.",
            "The architect drew precise plans so the builders knew exactly where each wall should go.",
            "The clock in the classroom is precise, always showing the correct time."
        ],
        "word": "precise"
    },
    # For question 16 about "wholesome", all four sentences are correct
    "16": {
        "correct_answers": [
            "She has a wholesome lifestyle, getting plenty of sleep and exercise every day.",
            "The doctor recommended eating wholesome snacks like apples and carrots.",
            "The park offers wholesome activities like hiking and birdwatching.",
            "My mom prepared a wholesome meal with fresh vegetables and grilled chicken."
        ],
        "word": "wholesome"
    },
    # For question 17 about "resentful", all three sentences are correct
    "17": {
        "correct_answers": [
            "He was resentful about getting in trouble for something he didn't do.",
            "Sarah felt resentful after her friend took credit for her idea.",
            "Amy became resentful when her brother received more attention than she did."
        ],
        "word": "resentful"
    },
    # For question 18 about "pandemonium", both sentences are correct
    "18": {
        "correct_answers": [
            "The fire alarm caused pandemonium as students rushed out of the school building.",
            "Pandemonium erupted in the stadium when the winning goal was scored."
        ],
        "word": "pandemonium"
    },
    "19": "assemble",
    "20": "clarify",
    "21": "accumulate",
    "22": "enhance",
    "23": "energetic",
    "24": "sturdy",
    "25": "luscious",
    "26": "superior",
    "27": "breathtaking",
    "28": "informal",
    "29": "substantial",
    "30": "conviction"
}

trained_fourth = {
    "accumulate",
    "adventurous",
    "assemble",
    "assist",
    "clarify",
    "contrast",
    "cunning",
    "define",
    "deforestation",
    "deliberate",
    "demonstrate",
    "diversity",
    "empathy",
    "evaluate",
    "fragrance",
    "glorious",
    "grudge",
    "justify",
    "lethal",
    "pandemonium",
    "pandemonioum", # incorrect spelling added to match quiz misspelling
    "phenomenon",
    "precise",
    "rebellious",
    "refer",
    "scamper",
    "sturdy",
    "treacherous",
    "twilight",
    "uncertain",
    "wholesome"
}

untrained_fourth = {
    "anticipation",
    "assume",
    "breathtaking",
    "celestial",
    "consume",
    "conviction",
    "deceitful",
    "delirious",
    "emphasis",
    "energetic",
    "enhance",
    "feud",
    "hostile",
    "informal",
    "intense",
    "interpret",
    "luscious",
    "mutter",
    "nuisance",
    "opinionated",
    "prejudice",
    "reliable",
    "resentful",
    "revolt",
    "substantial",
    "superior",
    "thorough",
    "tolerance",
    "velocity",
    "watchful"
}

pre_key_second = {
    "1": "Telescope",
    "2": "Delicious",
    "3": "Guide",
    "4": "Successful",
    "5": "Calm",
    "6": "Explore",
    "7": "Hollow",
    "8": "Ancient",
    "9": "Enormous",
    "10": "Habit",
    "11": "Defeat",
    "12": "Experiment",
    
    "13": {
        "correct_answers": [
            "This lotion uses only natural ingredients, like coconut oil.",
            "Volcanoes are natural features of the Earth's surface.",
            "She enjoys painting scenes of natural landscapes."
        ],
        "word": "natural"
    },
    
    "14": {
        "correct_answers": [
            "Our family decided to feast in celebration of Grandma's birthday.",
            "After the big harvest, the farmers would feast together.",
            "We plan to feast on turkey and pie for our holiday dinner."
        ],
        "word": "feast"
    },
   
    "15": {
        "correct_answers": [
            "We could see the effect of the strong wind on the swaying trees.",
            "The medicine took effect quickly, relieving my headache.",
            "The movie's special effects were impressive.",
            "The effect of her studying was a higher score on the test."
        ],
        "word": "effect"
    },
   
    "16": {
        "correct_answers": [
            "High water pressure can burst a pipe.",
            "I felt pressure to finish my assignment before the deadline.",
            "The doctor measured the pressure in my arm with a cuff.",
            "The soccer team faced pressure to win the championship."
        ],
        "word": "pressure"
    },
    
    "17": {
        "correct_answers": [
            "He practiced daily to complete the marathon next month.",
            "I spent hours trying to complete this puzzle.",
            "We must complete our chores before watching TV.",
            "The sandwich was complete with lettuce, tomato, and cheese."
        ],
        "word": "complete"
    },
    
    "18": {
        "correct_answers": [
            "The earthquake was a major disaster, leaving the city in ruins.",
            "The tornado destroyed the entire town, causing a real disaster."
        ],
        "word": "disaster"
    },
    "19": "important",
    "20": "improve",
    "21": "purpose",
    "22": "recover",
    "23": "ripe",
    "24": "struggle",
    "25": "overgrown",
    "26": "effort",
    "27": "invent",
    "28": "jealous",
    "29": "relax",
    "30": "patient"
}

mid_key_second = {
    "1": "Competition",
    "2": "Tropical",
    "3": "Recover",
    "4": "Unkind",
    "5": "Stormy",
    "6": "Balance",
    "7": "Peaceful",
    "8": "Ripe",
    "9": "Struggle",
    "10": "Delicious",
    "11": "Steep",
    "12": "Powerful",
    # For question 13 about "patient", all three sentences are correct
    "13": {
        "correct_answers": [
            "The teacher asked the class to be patient while she handed out papers.",
            "She was patient as she waited quietly for her turn on the slide.",
            "My dad was very patient when we stood in line for ice cream."
        ],
        "word": "patient"
    },
    # For question 14 about "guide", all three sentences are correct
    "14": {
        "correct_answers": [
            "My teacher will guide us through the museum.",
            "The map can guide you to the hidden treasure.",
            "Mom will guide me to bake my first cake."
        ],
        "word": "guide"
    },
    # For question 15 about "repair", all four sentences are correct
    "15": {
        "correct_answers": [
            "She helped repair the hole in my shirt.",
            "My dad will repair the broken bike today.",
            "My sister can repair our car tomorrow.",
            "I used glue to repair my favorite toy airplane."
        ],
        "word": "repair"
    },
    # For question 16 about "telescope", all four sentences are correct
    "16": {
        "correct_answers": [
            "At night, I use my telescope to see the bright stars.",
            "The telescope helps me see planets far away.",
            "Dad showed me how to use the telescope to look at stars.",
            "We looked at the moon through the telescope."
        ],
        "word": "telescope"
    },
    # For question 17 about "imagine", all three sentences are correct
    "17": {
        "correct_answers": [
            "I can imagine a giant ice cream cone as tall as a building!",
            "Close your eyes and imagine you're flying through the clouds.",
            "She likes to imagine herself as a princess in a castle."
        ],
        "word": "imagine"
    },
    # For question 18 about "habit", both sentences are correct
    "18": {
        "correct_answers": [
            "She has a habit of reading books every night before bed.",
            "Brushing your teeth every morning and night is a good habit."
        ],
        "word": "habit"
    },
    "19": "calm",
    "20": "important",
    "21": "improve",
    "22": "pressure",
    "23": "feast",
    "24": "comfort",
    "25": "overgrown",
    "26": "invent",
    "27": "complete",
    "28": "successful",
    "29": "conversation",
    "30": "relax"
}


trained_second = { "recover", "calm", "stormy", "struggle", "telescope", "disaster", "tropical", "delicious", "guide", "competition", "gentle", "improve", "pressure", "peaceful", "feast", "important", "communicate", "purpose", "repair", "howl", "comfort", "effect", "wreckage", "habit", "speechless", "ancient", "ripe", "hollow", "enormous", "unmistakable" }

untrained_second = { "explore", "jealous", "patient", "unusual", "scent", "opinion", "balance", "experiment", "complete", "imagine", "natural", "unkind", "powerful", "impatient", "comfortable", "successful", "gobble", "wise", "describe", "method", "invent", "defeat", "relax", "effort", "voyage", "conversation", "dreamy", "hearty", "steep", "overgrown" }


def rename_csv_columns(input_file, output_file):
    """
    Rename columns in CSV file to keep first 4 columns as-is and rename rest to 1, 2, 3, etc.
    
    Args:
        input_file (str): Path to input CSV file
        output_file (str): Path to output CSV file with renamed columns
    """
    # Read the CSV file
    df = pd.read_csv(input_file)
    
    # Get current column names
    current_columns = list(df.columns)
    
    # Create new column names
    new_columns = []
    
    # Keep first 4 columns as they are: Timestamp, Score, id, Possible match
    for i in range(min(4, len(current_columns))):
        new_columns.append(current_columns[i])
    
    # Rename remaining columns to numbers 1, 2, 3, ..., 30
    question_number = 1
    for i in range(4, len(current_columns)):
        new_columns.append(str(question_number))
        question_number += 1
    
    # Apply the new column names
    df.columns = new_columns
    
    # Save to new CSV file
    df.to_csv(output_file, index=False)
    
    print(f"Column renaming complete!")
    # print(f"Original columns: {current_columns}")
    # print(f"New columns: {new_columns}")
    print(f"File saved as: {output_file}")


def check_answer(student_answer, correct_data, question_num, trained, untrained):
    """
    Check if a student's answer matches the correct answer
    
    Args:
        student_answer: The student's response (string or list)
        correct_data: The correct answer data (string for single words, dict for sentences)
        question_num: Question number (for debugging)
    
    Returns:
        tuple: 
            tuple[0]: True if answer is correct, False otherwise
            tuple[1]: True is question is trained, False if untrained
    """
    # Handle empty or NaN answers
    if pd.isna(student_answer) or student_answer == "" or student_answer is None:
        assert(False)
        return False
    
    is_trained = False
    # For single word answers
    if isinstance(correct_data, str):
        if correct_data.strip().lower() in trained:
            is_trained = True
        else:
            assert(correct_data.strip().lower() in untrained)
        return str(student_answer).strip().lower() == correct_data.strip().lower(), is_trained
    
    # For sentence-based answers where students must select ALL correct options
    elif isinstance(correct_data, dict):
        # Parse the student's answer - this depends on how your CSV stores multiple selections
        # Common formats might be: "Option 1|Option 2|Option 3" or "Option 1; Option 2; Option 3"
        answer_string = str(student_answer).strip()
        student_answers_list = [ans.strip() for ans in answer_string.split("|") if ans.strip()]

        if correct_data["word"].strip().lower() in trained:
            is_trained = True
        else:
            assert(correct_data['word'].strip().lower() in untrained)
        
        def debug_set_comparison(student_set, correct_set):
            print("Student set:")
            for i, item in enumerate(sorted(student_set)):
                print(f"  {i}: '{item}' (len: {len(item)})")
            
            print("\nCorrect set:")
            for i, item in enumerate(sorted(correct_set)):
                print(f"  {i}: '{item}' (len: {len(item)})")
            
            print(f"\nStudent set size: {len(student_set)}")
            print(f"Correct set size: {len(correct_set)}")
            
            print("\nIn student but not correct:")
            for item in student_set - correct_set:
                print(f"  '{item}' (len: {len(item)})")
                print(f"  Repr: {repr(item)}")
            
            print("\nIn correct but not student:")
            for item in correct_set - student_set:
                print(f"  '{item}' (len: {len(item)})")
                print(f"  Repr: {repr(item)}")
            
            print(f"\nSets equal: {student_set == correct_set}")
        
        # Convert to sets for comparison (strip whitespace)
        student_set = {ans.strip().rstrip(".") for ans in student_answers_list if ans.strip()}
        correct_set = {ans.strip().rstrip(".") for ans in correct_data["correct_answers"]}
        # if question_num == "14":
        #     print("Student_answers_list ", student_set)
        #     print("Correct answer: ", correct_set)
        #     debug_set_comparison(student_set, correct_set)
            
        # assert(student_set == correct_set)
        
        # Student must have selected ALL correct answers and NO incorrect ones
        return student_set == correct_set, is_trained
    
    assert(False)

def grade_student_csv(csv_file, answer_key, trained, untrained, output_file=None):
    """
    Grade student responses from CSV file
    
    Args:
        csv_file (str): Path to CSV file with student responses
        answer_key (dict): Dictionary with correct answers
        output_file (str, optional): Path to save results. If None, returns results only.
    
    Returns:
        dict: Grading results for all students
    """
    # Read the CSV file
    df = pd.read_csv(csv_file)
    
    results = {}
    detailed_results = []
    
    for index, row in df.iterrows():
        # Get student identifier (use id column, or fall back to row index)
        id = row.get('id', f"Student_{index+1}")
        if pd.isna(id):
            id = f"Student_{index+1}"
        
        student_results = {
            'id': id,
            'timestamp': row.get('Timestamp', ''),
            'original_score': row.get('Score', ''),
            'possible_match': row.get('Possible match', ''),
            'questions': {},
            'total_correct': 0,
            # 'total_questions': len(answer_key),
            'percentage': 0.0,
            'total_trained_correct': 0,
            'total_trained_questions': 0,
            'trained_percentage': 0.0,
            'total_untrained_correct': 0,
            'total_untrained_questions': 0,
            'untrained_percentage': 0.0,
        }
        # Grade each question
        for question_num in answer_key.keys():
            # The column name is just the question number as a string
            column_name = question_num
            
            if column_name in df.columns:
                student_answer = row.get(column_name, "")
                # For second grade post test, skip question 24, since there is no correct answer
                # if question_num == "24":
                #     continue
                is_correct, is_trained = check_answer(student_answer, answer_key[question_num], question_num, trained, untrained)
                student_results['questions'][question_num] = {
                    'student_answer': student_answer,
                    'correct': is_correct,
                    'correct_answer': answer_key[question_num]
                }
                
                if is_trained:
                    student_results['total_trained_questions'] += 1
                else: 
                    student_results['total_untrained_questions'] += 1
                if is_correct:
                    student_results['total_correct'] += 1
                    if is_trained:
                        student_results['total_trained_correct'] += 1
                    else:
                        student_results['total_untrained_correct'] += 1
            else:
                # Question column not found
                assert(False)
                student_results['questions'][question_num] = {
                    'student_answer': 'COLUMN_NOT_FOUND',
                    'correct': False,
                    'correct_answer': answer_key[question_num]
                }
        student_results["total_questions"] = student_results["total_trained_questions"] + student_results["total_untrained_questions"]
        # Calculate percentage
        if student_results['total_questions'] > 0:
            student_results['percentage'] = (student_results['total_correct'] / student_results['total_questions']) * 100
            student_results['trained_percentage'] = (student_results['total_trained_correct'] / student_results['total_trained_questions']) * 100
            student_results['untrained_percentage'] = (student_results['total_untrained_correct'] / student_results['total_untrained_questions']) * 100

        
        results[id] = student_results
        detailed_results.append(student_results)
    
    # Print summary
    print(f"Graded {len(results)} students")
    print(f"Questions per student: {len(answer_key)}")
    
    # Calculate class statistics
    if detailed_results:
        percentages = [r['percentage'] for r in detailed_results]
        avg_percentage = sum(percentages) / len(percentages)
        print(f"Class average: {avg_percentage:.1f}%")
        print(f"Highest score: {max(percentages):.1f}%")
        print(f"Lowest score: {min(percentages):.1f}%")
    
    # Save results to file if requested
    if output_file:
        save_grading_results(detailed_results, output_file, answer_key)
    
    return results

def save_grading_results(detailed_results, output_file, answer_key):
    """
    Save detailed grading results to a CSV file
    
    Args:
        detailed_results: List of student result dictionaries
        output_file: Path to output CSV file
        answer_key: The answer key used for grading
    """
    # Prepare data for CSV output
    output_data = []
    
    for student in detailed_results:
        # sanity checks
        # assert(student['total_correct'] == int(student['original_score'].strip().split("/")[0]))
        if student['total_correct'] != int(student['original_score'].strip().split("/")[0]):
            print(student["id"], student['total_correct'], int(student['original_score'].split("/")[0].strip()))
            # assert(student['total_correct'] == int(student['original_score'].strip().split("/")[0]))
        assert(student['total_trained_questions'] + student['total_untrained_questions'] == 29)

        row = {
            'id': student['id'],
            'timestamp': student['timestamp'],
            'original_score': student['original_score'],
            'possible_match': student['possible_match'],
            'total_correct': student['total_correct'],
            'total_questions': student['total_questions'],
            'percentage': round(student['percentage'], 1),
            'total_trained_correct': student['total_trained_correct'],
            'total_trained_questions': student['total_trained_questions'],
            'trained_percentage': student['trained_percentage'],
            'total_untrained_correct': student['total_untrained_correct'],
            'total_untrained_questions': student['total_untrained_questions'],
            'untrained_percentage': student['untrained_percentage'],
        }
        
        # Add individual question results
        for q_num in sorted(answer_key.keys(), key=lambda x: int(x)):
            if q_num in student['questions']:
                row[f'Q{q_num}_correct'] = student['questions'][q_num]['correct']
                row[f'Q{q_num}_answer'] = student['questions'][q_num]['student_answer']
            else:
                row[f'Q{q_num}_correct'] = False
                row[f'Q{q_num}_answer'] = 'NO_ANSWER'
        
        output_data.append(row)
    
    # Save to CSV
    df_output = pd.DataFrame(output_data)
    df_output.to_csv(output_file, index=False)
    print(f"Detailed results saved to: {output_file}")

def analyze_question_performance(results, answer_key):
    """
    Analyze which questions were most/least difficult
    
    Args:
        results: Grading results from grade_student_csv
        answer_key: The answer key used
    
    Returns:
        dict: Question analysis
    """
    question_stats = {}
    
    for q_num in answer_key.keys():
        correct_count = 0
        total_count = 0
        
        for id, student_data in results.items():
            if q_num in student_data['questions']:
                total_count += 1
                if student_data['questions'][q_num]['correct']:
                    correct_count += 1
        
        if total_count > 0:
            percentage = (correct_count / total_count) * 100
            question_stats[q_num] = {
                'correct': correct_count,
                'total': total_count,
                'percentage': percentage,
                'difficulty': 'Easy' if percentage >= 80 else 'Medium' if percentage >= 60 else 'Hard'
            }
    
    # Sort by difficulty (lowest percentage first)
    sorted_questions = sorted(question_stats.items(), key=lambda x: x[1]['percentage'])
    
    print("\nQuestion Difficulty Analysis:")
    print("=" * 50)
    for q_num, stats in sorted_questions:
        print(f"Question {q_num}: {stats['correct']}/{stats['total']} ({stats['percentage']:.1f}%) - {stats['difficulty']}")
    
    return question_stats

# Usage examples:
if __name__ == "__main__":
    # Step 1: Create a new file with renamed columns
    # original = 'pre_tests/ANON_SecondGrade_PreTest.csv'
    # renamed = 'pre_tests/Second_Renamed_Columns.csv'
    # results_name = 'pre_tests/Second_Grading_Results.csv'

    original = 'mid_tests/ANON_Second_Grade_WT_Pretest_2.csv'
    renamed = 'mid_tests/Second_Renamed_Columns.csv'
    results_name = 'mid_tests/Second_Grading_Results.csv'

    rename_csv_columns(original, renamed)

    # Step 2: Use Answer Key to replace each Answer choice with Correct / Incorrect
    results = grade_student_csv(renamed, mid_key_second, trained_second, untrained_second, results_name)
    
    # Analyze question difficulty
    # question_analysis = analyze_question_performance(results, sample_answer_key)
    
    print("Grading system ready! Use the functions above with your actual data.")

    