import streamlit as st
import os
import json
from datetime import datetime
import openai  # Assuming you're using OpenAI API for suggestions

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
    data = load_data()
    test_score = {
        "score": score,
        "accuracy": accuracy,
        "date": date
    }
    data["test_scores"].append(test_score)
    save_data(data)

def get_suggestions():
    # Gather user's reflections and performance
    data = load_data()
    reflections = " ".join([entry["text"] for entry in data["reflections"]])
    test_scores = data["test_scores"]
    
    # Assuming OpenAI GPT model for generating suggestions based on reflections and performance
    openai.api_key = "your_openai_api_key"
    
    prompt = f"""
    Based on the following reflections and past test scores, provide study suggestions:
    Reflections: {reflections}
    Test Scores: {test_scores}
    """
    
    response = openai.Completion.create(
        engine="text-davinci-003",  # You can use the GPT engine of your choice
        prompt=prompt,
        max_tokens=150
    )
    
    suggestions = response.choices[0].text.strip()
    return suggestions

# Initialize and load data
st.set_page_config(page_title="Curious Manager", layout="centered")
st.title("🧠 Curious Manager")
st.markdown("Track your curious thoughts, reflections, and test scores.")

init_data()
data = load_data()

# Sidebar for navigation
page = st.sidebar.selectbox("Navigate", ["Add Entry", "View Notes", "View Reflections", "Add Test Score", "View Test Performance", "AI Suggestions"])

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
        add_test_score(score, accuracy, date)
        st.success("✅ Test score added successfully.")

elif page == "View Test Performance":
    st.header("📈 Test Performance")
    if not data["test_scores"]:
        st.info("No test scores yet. Add some from the 'Add Test Score' page.")
    else:
        total_scores = sum([score["score"] for score in data["test_scores"]])
        total_tests = len(data["test_scores"])
        average_score = total_scores / total_tests if total_tests > 0 else 0
        st.write(f"Average Score: {average_score}")
        
        # Display test scores
        for score in data["test_scores"]:
            st.write(f"Score: {score['score']} | Accuracy: {score['accuracy']}% | Date: {score['date']}")

elif page == "AI Suggestions":
    st.header("🤖 AI Study Suggestions")
    suggestions = get_suggestions()
    if suggestions:
        st.write(suggestions)
    else:
        st.info("No suggestions available at the moment. Add more reflections and test scores to get personalized recommendations.")
