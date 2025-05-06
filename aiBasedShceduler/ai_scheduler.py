import streamlit as st
import os
import json
from datetime import datetime
import pandas as pd

# File to store notes, reflections, and test scores
data_file = "curious_data.json"

# Initialize data file if it doesn't exist
def init_data():
    if not os.path.exists(data_file):
        with open(data_file, 'w') as f:
            json.dump({"notes": [], "reflections": [], "test_scores": []}, f)

def load_data():
    try:
        with open(data_file, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        init_data()
        return {"notes": [], "reflections": [], "test_scores": []}

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
    # Validate the test score and accuracy
    if not (0 <= score <= 300):  # Assuming max score is 300
        return "❌ Score must be between 0 and 300."
    if not (0 <= accuracy <= 100):
        return "❌ Accuracy must be between 0 and 100."
    
    data = load_data()
    test_score = {
        "score": score,
        "accuracy": accuracy,
        "date": date
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

def get_performance_analysis():
    # Load and convert test scores to a DataFrame for analysis
    data = load_data()
    if not data["test_scores"]:
        return "No test scores to analyze."
    
    test_scores_df = pd.DataFrame(data["test_scores"])
    
    # Calculate average score and accuracy
    avg_score = test_scores_df["score"].mean()
    avg_accuracy = test_scores_df["accuracy"].mean()

    # Generate basic suggestions
    suggestions = []
    if avg_accuracy < 70:
        suggestions.append("❗ Your accuracy is below 70%. Focus on reviewing weak areas.")
    if avg_score < 60:
        suggestions.append("❗ Your score is low overall. Consider adjusting your study approach.")

    # Analyze trends in scores (last 3 scores comparison)
    if len(test_scores_df) > 2:
        recent_scores = test_scores_df.tail(3)
        score_trend = recent_scores["score"].mean()
        if score_trend < avg_score:
            suggestions.append("📉 Your recent scores are lower than the average. Revisit previous topics.")
    
    return f"🧑‍🏫 **Average Score**: {avg_score:.2f} | **Average Accuracy**: {avg_accuracy:.2f}%\n\n" + "\n".join(suggestions)

# Initialize and load data
st.set_page_config(page_title="Curious Manager", layout="centered")
st.title("🧠 Curious Manager")
st.markdown("Track your curious thoughts, reflections, and test scores.")

init_data()
data = load_data()

# Sidebar for navigation
page = st.sidebar.selectbox("Navigate", ["Add Entry", "View Notes", "View Reflections", "Add Test Score", "View Test Performance", "Performance Analysis"])

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
            if st.button(f"Delete Test Score {i}", key=f"delete_test_score_{i}"):
                result = delete_test_score(i)
                st.success(result)
                st.experimental_rerun()

elif page == "Performance Analysis":
    st.header("📊 Performance Analysis")
    analysis = get_performance_analysis()
    st.markdown(analysis)
