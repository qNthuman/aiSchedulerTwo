import streamlit as st
import os
import json
from datetime import datetime

# File to store notes and reflections
DATA_FILE = "curious_data.json"

# Initialize data file if it doesn't exist
def init_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as f:
            json.dump({"notes": [], "reflections": [], "tests": []}, f)

def load_data():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        init_data()
        return {"notes": [], "reflections": [], "tests": []}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
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

def add_test(score, total):
    try:
        score = float(score)
        total = float(total)
    except ValueError:
        return "❌ Score and total must be numeric."

    if score < 0 or total <= 0 or score > total:
        return "⚠️ Invalid test data."

    data = load_data()
    accuracy = round((score / total) * 100, 2)
    entry = {
        "score": score,
        "total": total,
        "accuracy": accuracy,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    data["tests"].append(entry)
    save_data(data)
    return f"✅ Test added. Accuracy: {accuracy}%"

def delete_entry(entry_type, index):
    data = load_data()
    if entry_type in data and 0 <= index < len(data[entry_type]):
        removed = data[entry_type].pop(index)
        save_data(data)
        return f"🗑️ Deleted: {removed.get('text', 'test entry')}"
    return "⚠️ Invalid index."

# Initialize and load data
st.set_page_config(page_title="Curious Manager", layout="centered")
st.title("🧠 Curious Manager")
st.markdown("Track your curious thoughts, reflections, and test performance.")

init_data()
data = load_data()

# Sidebar for navigation
page = st.sidebar.selectbox("Navigate", ["Add Entry", "View Notes", "View Reflections", "Add Test Score", "View Performance"])

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
    st.header("🧪 Add Test Score")
    score = st.text_input("Score")
    total = st.text_input("Total Marks")
    if st.button("Submit Test Score"):
        result = add_test(score, total)
        st.success(result)

elif page == "View Performance":
    st.header("📊 Performance Overview")
    if not data["tests"]:
        st.info("No test data available. Add some from the 'Add Test Score' page.")
    else:
        accuracies = []
        for i, test in enumerate(reversed(data["tests"])):
            st.write(f"🕒 {test['timestamp']} - Score: {test['score']} / {test['total']} → Accuracy: {test['accuracy']}%")
            accuracies.append(test['accuracy'])

        avg_accuracy = round(sum(accuracies) / len(accuracies), 2)
        st.markdown(f"**📈 Average Accuracy:** {avg_accuracy}%")
