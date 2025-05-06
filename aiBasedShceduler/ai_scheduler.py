import streamlit as st
import os
import json
from datetime import datetime
import pandas as pd

# File to store JEE-related data
data_file = "jee_data.json"

# Initialize data file if it doesn't exist
def init_data():
    if not os.path.exists(data_file):
        with open(data_file, 'w') as f:
            json.dump({"study_progress": [], "mock_tests": [], "jee_performance": []}, f)

def load_data():
    try:
        with open(data_file, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        init_data()
        return {"study_progress": [], "mock_tests": [], "jee_performance": []}

def save_data(data):
    with open(data_file, 'w') as f:
        json.dump(data, f, indent=4)

def add_study_progress(topic, status):
    status = status.strip().lower()
    if not status or status not in ["completed", "in-progress", "not-started"]:
        return "❌ Invalid status. Please choose from: 'completed', 'in-progress', 'not-started'."
    
    data = load_data()
    progress = {
        "topic": topic,
        "status": status,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    data["study_progress"].append(progress)
    save_data(data)
    return "✅ Study progress updated successfully."

def delete_study_progress(index):
    data = load_data()
    if 0 <= index < len(data["study_progress"]):
        removed = data["study_progress"].pop(index)
        save_data(data)
        return f"🗑️ Deleted study progress for topic: {removed['topic']}"
    return "⚠️ Invalid index."

def add_mock_test_result(score, accuracy, date, time_taken):
    # Ensure that inputs are within valid ranges
    if not (0 <= score <= 300):  # Assuming max score is 300 for JEE Mains
        return "❌ Score must be between 0 and 300."
    if not (0 <= accuracy <= 100):
        return "❌ Accuracy must be between 0 and 100."
    
    data = load_data()
    mock_test = {
        "score": score,
        "accuracy": accuracy,
        "date": date.strftime('%Y-%m-%d'),
        "time_taken": time_taken
    }
    data["mock_tests"].append(mock_test)
    save_data(data)
    return "✅ Mock test result added successfully."

def delete_mock_test(index):
    data = load_data()
    if 0 <= index < len(data["mock_tests"]):
        removed = data["mock_tests"].pop(index)
        save_data(data)
        return f"🗑️ Deleted mock test result: {removed['score']} on {removed['date']}"
    return "⚠️ Invalid index."

def add_jee_performance(score, accuracy, time_taken, attempted, correct, incorrect, unattempted):
    # Ensure that inputs are within valid ranges
    if not (0 <= score <= 300):
        return "❌ Score must be between 0 and 300."
    if not (0 <= accuracy <= 100):
        return "❌ Accuracy must be between 0 and 100."
    
    data = load_data()
    jee_performance = {
        "score": score,
        "accuracy": accuracy,
        "time_taken": time_taken,
        "attempted": attempted,
        "correct": correct,
        "incorrect": incorrect,
        "unattempted": unattempted
    }
    data["jee_performance"].append(jee_performance)
    save_data(data)
    return "✅ JEE performance data added successfully."

def delete_jee_performance(index):
    data = load_data()
    if 0 <= index < len(data["jee_performance"]):
        removed = data["jee_performance"].pop(index)
        save_data(data)
        return f"🗑️ Deleted JEE performance data: {removed['score']} on {removed['date']}"
    return "⚠️ Invalid index."

def get_jee_performance_analysis():
    data = load_data()
    if not data["jee_performance"]:
        return "No JEE performance data available."
    
    jee_df = pd.DataFrame(data["jee_performance"])

    # Calculate average score, accuracy, and time taken
    avg_score = jee_df["score"].mean()
    avg_accuracy = jee_df["accuracy"].mean()
    avg_time = jee_df["time_taken"].mean()

    # Generate basic suggestions
    suggestions = []
    if avg_accuracy < 70:
        suggestions.append("❗ Your accuracy is below 70%. Focus on reviewing weak areas.")
    if avg_score < 180:
        suggestions.append("❗ Your score is below the expected range. Consider revising topics more deeply.")
    if avg_time > 180:
        suggestions.append("❗ Your time taken is above average. Focus on improving time management during practice tests.")

    return f"🧑‍🏫 **Average Score**: {avg_score:.2f} | **Average Accuracy**: {avg_accuracy:.2f}% | **Average Time Taken**: {avg_time:.2f} minutes\n\n" + "\n".join(suggestions)

# Initialize and load data
st.set_page_config(page_title="JEE Preparation Tracker", layout="centered")
st.title("📚 JEE Preparation Tracker")
st.markdown("Track your JEE Mains & Advanced progress, mock test results, and performance.")

init_data()
data = load_data()

# Sidebar for navigation
page = st.sidebar.selectbox("Navigate", ["Add Study Progress", "View Study Progress", "Add Mock Test Result", "View Mock Test Results", "Add JEE Performance", "View JEE Performance Analysis"])

if page == "Add Study Progress":
    st.header("➕ Add Study Progress")
    topic = st.text_input("Topic Name")
    status = st.radio("Status", ["completed", "in-progress", "not-started"], horizontal=True)
    if st.button("Add Progress"):
        if not topic:
            st.error("❌ Please enter a topic name.")
        else:
            result = add_study_progress(topic, status)
            st.success(result)

elif page == "View Study Progress":
    st.header("📒 Study Progress")
    if not data["study_progress"]:
        st.info("No study progress yet. Add some from the 'Add Study Progress' page.")
    else:
        for i, progress in enumerate(reversed(data["study_progress"])):
            index = len(data["study_progress"]) - 1 - i
            with st.expander(f"🕒 {progress['timestamp']} - {progress['topic']} ({progress['status']})"):
                if st.button("Delete", key=f"delete_progress_{index}"):
                    result = delete_study_progress(index)
                    st.success(result)
                    st.experimental_rerun()

elif page == "Add Mock Test Result":
    st.header("➕ Add Mock Test Result")
    score = st.number_input("Enter your score", min_value=0, max_value=300)
    accuracy = st.slider("Enter accuracy (%)", 0, 100, 0)
    time_taken = st.number_input("Time Taken (in minutes)", min_value=0)
    date = st.date_input("Mock Test Date")
    if st.button("Add Mock Test Result"):
        if score == 0:
            st.error("❌ Please enter a valid score.")
        else:
            result = add_mock_test_result(score, accuracy, date, time_taken)
            st.success(result)

elif page == "View Mock Test Results":
    st.header("📊 View Mock Test Results")
    if not data["mock_tests"]:
        st.info("No mock test results yet. Add some from the 'Add Mock Test Result' page.")
    else:
        for i, mock_test in enumerate(data["mock_tests"]):
            st.write(f"Test: {mock_test['date']} | Score: {mock_test['score']} | Accuracy: {mock_test['accuracy']}% | Time Taken: {mock_test['time_taken']} minutes")
            if st.button(f"Delete Mock Test {i}", key=f"delete_mock_test_{i}"):
                result = delete_mock_test(i)
                st.success(result)
                st.experimental_rerun()

elif page == "Add JEE Performance":
    st.header("➕ Add JEE Performance Data")
    score = st.number_input("Enter your JEE score", min_value=0, max_value=300)
    accuracy = st.slider("Enter accuracy (%)", 0, 100, 0)
    time_taken = st.number_input("Time Taken (in minutes)", min_value=0)
    attempted = st.number_input("Attempted Questions", min_value=0)
    correct = st.number_input("Correct Answers", min_value=0)
    incorrect = st.number_input("Incorrect Answers", min_value=0)
    unattempted = st.number_input("Unattempted Questions", min_value=0)
    if st.button("Add JEE Performance"):
        result = add_jee_performance(score, accuracy, time_taken, attempted, correct, incorrect, unattempted)
        st.success(result)

elif page == "View JEE Performance Analysis":
    st.header("📊 JEE Performance Analysis")
    analysis = get_jee_performance_analysis()
    st.markdown(analysis)
