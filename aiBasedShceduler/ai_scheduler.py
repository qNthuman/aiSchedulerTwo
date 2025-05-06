import streamlit as st
import os
import json
from datetime import datetime
import pandas as pd

# File to store notes, reflections, test scores, and IAT mocks
data_file = "curious_data.json"

# Initialize data file if it doesn't exist
def init_data():
    if not os.path.exists(data_file):
        with open(data_file, 'w') as f:
            json.dump({"notes": [], "reflections": [], "test_scores": [], "iat_mocks": []}, f)

def load_data():
    try:
        with open(data_file, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        init_data()
        return {"notes": [], "reflections": [], "test_scores": [], "iat_mocks": []}

def save_data(data):
    with open(data_file, 'w') as f:
        json.dump(data, f, indent=4)

def add_entry(entry_type, text):
    text = text.strip()
    if not text:
        return "❌ Cannot add empty entry."
    if entry_type not in ["notes", "reflections"]:
        return "❌ Invalid entry type."

    data = load_data()
    entry = {
        "text": text,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    data[entry_type].append(entry)
    save_data(data)
    return "✅ Entry added successfully."

def delete_entry(entry_type, index):
    data = load_data()
    if entry_type in data and 0 <= index < len(data[entry_type]):
        removed = data[entry_type].pop(index)
        save_data(data)
        return f"🗑️ Deleted: {removed['text']}"
    return "⚠️ Invalid index."

def add_test_score(score, accuracy, date):
    if not (0 <= score <= 300):  # Assuming max score is 300
        return "❌ Score must be between 0 and 300."
    if not (0 <= accuracy <= 100):
        return "❌ Accuracy must be between 0 and 100."
    
    if not isinstance(score, int) or not isinstance(accuracy, int):
        return "❌ Score and Accuracy must be integers."
    
    data = load_data()
    test_score = {
        "score": score,
        "accuracy": accuracy,
        "date": date.strftime('%Y-%m-%d')
    }
    data["test_scores"].append(test_score)
    save_data(data)
    return "✅ Test score added successfully."

def delete_test_score(index):
    data = load_data()
    if 0 <= index < len(data["test_scores"]):
        removed = data["test_scores"].pop(index)
        save_data(data)
        return f"🗑️ Deleted test score: {removed['score']} on {removed['date']}"
    return "⚠️ Invalid index."

def add_iat_mock(test_name, date, score, accuracy, time_taken, attempted, correct, incorrect, unattempted):
    # Validate inputs for IAT mock test
    if not (0 <= score <= 240):  # Assuming max score is 240 for IAT
        return "❌ Score must be between 0 and 240."
    if not (0 <= accuracy <= 100):
        return "❌ Accuracy must be between 0 and 100."
    
    if not isinstance(score, int) or not isinstance(accuracy, int):
        return "❌ Score and Accuracy must be integers."
    
    if not isinstance(time_taken, (int, float)) or time_taken < 0:
        return "❌ Time taken must be a valid positive number."
    
    data = load_data()
    iat_mock = {
        "test_name": test_name,
        "date": date.strftime('%Y-%m-%d'),
        "score": score,
        "accuracy": accuracy,
        "time_taken": time_taken,
        "attempted": attempted,
        "correct": correct,
        "incorrect": incorrect,
        "unattempted": unattempted
    }
    data["iat_mocks"].append(iat_mock)
    save_data(data)
    return "✅ IAT mock test added successfully."

def delete_iat_mock(index):
    data = load_data()
    if 0 <= index < len(data["iat_mocks"]):
        removed = data["iat_mocks"].pop(index)
        save_data(data)
        return f"🗑️ Deleted IAT mock test: {removed['test_name']} on {removed['date']}"
    return "⚠️ Invalid index."

def get_iat_performance_analysis():
    # Load and convert IAT mocks to a DataFrame for analysis
    data = load_data()
    if not data["iat_mocks"]:
        return "No IAT mock tests to analyze."
    
    iat_df = pd.DataFrame(data["iat_mocks"])
    
    # Handle cases where data is empty
    if iat_df.empty:
        return "No data available for analysis."

    # Calculate average score, accuracy, and time taken
    avg_score = iat_df["score"].mean()
    avg_accuracy = iat_df["accuracy"].mean()
    avg_time = iat_df["time_taken"].mean()

    # Generate basic suggestions
    suggestions = []
    if avg_accuracy < 70:
        suggestions.append("❗ Your accuracy is below 70%. Focus on reviewing weak areas.")
    if avg_score < 120:
        suggestions.append("❗ Your score is low overall. Consider adjusting your study approach.")
    if avg_time > 90:
        suggestions.append("❗ Your time taken is above average. Focus on time management during the test.")

    return f"🧑‍🏫 **Average Score**: {avg_score:.2f} | **Average Accuracy**: {avg_accuracy:.2f}% | **Average Time Taken**: {avg_time:.2f} minutes\n\n" + "\n".join(suggestions)

# Initialize and load data
st.set_page_config(page_title="Curious Manager", layout="centered")
st.title("🧠 Curious Manager")
st.markdown("Track your curious thoughts, reflections, test scores, and IAT mock results.")

init_data()
data = load_data()

# Sidebar for navigation
page = st.sidebar.selectbox("Navigate", ["Add Entry", "View Notes", "View Reflections", "Add Test Score", "View Test Performance", "Performance Analysis", "Add IAT Mock Test", "View IAT Mock Performance"])

if page == "Add Entry":
    st.header("➕ Add a New Entry")
    entry_type = st.radio("Entry Type", ["notes", "reflections"], horizontal=True)
    entry_text = st.text_area("What's on your mind?", height=150)
    if st.button("Add Entry"):
        result = add_entry(entry_type, entry_text)
        st.success(result)

elif page == "View Notes":
    st.header("📒 Notes")
    if not data["notes"]:
        st.info("No notes yet. Add some from the 'Add Entry' page.")
    else:
        for i, note in enumerate(reversed(data["notes"])):
            index = len(data["notes"]) - 1 - i
            with st.expander(f"🕒 {note['timestamp']}"):
                st.markdown(note["text"])
                if st.button("Delete", key=f"delete_note_{index}"):
                    result = delete_entry("notes", index)
                    st.success(result)
                    st.experimental_rerun()

elif page == "View Reflections":
    st.header("🪞 Reflections")
    if not data["reflections"]:
        st.info("No reflections yet. Add some from the 'Add Entry' page.")
    else:
        for i, reflection in enumerate(reversed(data["reflections"])):
            index = len(data["reflections"]) - 1 - i
            with st.expander(f"🕒 {reflection['timestamp']}"):
                st.markdown(reflection["text"])
                if st.button("Delete", key=f"delete_reflection_{index}"):
                    result = delete_entry("reflections", index)
                    st.success(result)
                    st.experimental_rerun()

elif page == "Add Test Score":
    st.header("📊 Add Test Score")
    score = st.number_input("Enter your score", min_value=0)
    accuracy = st.slider("Enter accuracy (%)", 0, 100, 0)
    date = st.date_input("Test Date")
    if st.button("Add Test Score"):
        if score == 0 or accuracy == 0:
            st.error("Please ensure both score and accuracy are entered correctly.")
        else:
            result = add_test_score(score, accuracy, date)
            st.success(result)

elif page == "View Test Performance":
    st.header("📈 Test Performance")
    if not data["test_scores"]:
        st.info("No test scores yet. Add some from the 'Add Test Score' page.")
    else:
        total_scores = sum([score["score"] for score in data["test_scores"]])
        total_tests = len(data["test_scores"])
        average_score = total_scores / total_tests if total_tests > 0 else 0
        st.write(f"Average Score: {average_score}")
        
        # Display test scores and allow removal
        for i, score in enumerate(data["test_scores"]):
            st.write(f"Score: {score['score']} | Accuracy: {score['accuracy']}% | Date: {score['date']}")
            if st.button(f"Delete Score {i}", key=f"delete_test_{i}"):
                result = delete_test_score(i)
                st.success(result)
                st.experimental_rerun()

elif page == "Performance Analysis":
    st.header("📊 IAT Mock Performance Analysis")
    analysis = get_iat_performance_analysis()
    st.markdown(analysis)

elif page == "Add IAT Mock Test":
    st.header("➕ Add IAT Mock Test")
    test_name = st.text_input("Test Name")
    date = st.date_input("Test Date")
    score = st.number_input("Enter your score", min_value=0)
    accuracy = st.slider("Enter accuracy (%)", 0, 100, 0)
    time_taken = st.number_input("Time Taken (in minutes)", min_value=0)
    attempted = st.number_input("Attempted Questions", min_value=0)
    correct = st.number_input("Correct Answers", min_value=0)
    incorrect = st.number_input("Incorrect Answers", min_value=0)
    unattempted = st.number_input("Unattempted Questions", min_value=0)
    
    if st.button("Add IAT Mock Test"):
        result = add_iat_mock(test_name, date, score, accuracy, time_taken, attempted, correct, incorrect, unattempted)
        st.success(result)

elif page == "View IAT Mock Performance":
    st.header("📊 View IAT Mock Performance")
    if not data["iat_mocks"]:
        st.info("No IAT mock tests yet. Add some from the 'Add IAT Mock Test' page.")
    else:
        for i, iat_mock in enumerate(data["iat_mocks"]):
            st.write(f"Test: {iat_mock['test_name']} | Date: {iat_mock['date']} | Score: {iat_mock['score']} | Accuracy: {iat_mock['accuracy']}%")
            if st.button(f"Delete IAT Mock {i}", key=f"delete_iat_mock_{i}"):
                result = delete_iat_mock(i)
                st.success(result)
                st.experimental_rerun()
