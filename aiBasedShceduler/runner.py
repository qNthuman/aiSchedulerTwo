import streamlit as st
import pandas as pd
import os
from datetime import datetime
import pandas as pd
import json
import os
from datetime import datetime, date

# Ensure data directory exists
if not os.path.exists("data"):
    os.makedirs("data")

# Paths
schedule_path = "data/schedule.json"
marks_path = "data/marks.csv"
plan_path = "data/study_plan.json"
todo_path = "data/todo.json"

# Optimized function to load marks data with error handling
@st.cache_data
def load_marks_data():
    file_path = 'marks_data.csv'
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        st.error(f"The file '{file_path}' is missing!")
        return pd.DataFrame()  # Return an empty DataFrame or handle it appropriately

# Function to add task to the To-Do list and schedule it
def add_task_to_todo_and_schedule(task, date, task_type):
    to_do_list.append({
        'Task': task,
        'Date': date,
        'Task Type': task_type
    })
    if date not in task_schedule:
        task_schedule[date] = []
    task_schedule[date].append(task)
    save_data()

# Function to delete task from To-Do list and schedule
def delete_task_from_todo_and_schedule(task):
    global to_do_list
    to_do_list = [item for item in to_do_list if item['Task'] != task]
    for date in task_schedule:
        if task in task_schedule[date]:
            task_schedule[date].remove(task)
    save_data()
def load_json(path, default):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return default
def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# Function to save data to CSV
def save_data():
    # Save the to-do list data
    to_do_df = pd.DataFrame(to_do_list)
    to_do_df.to_csv('to_do_list.csv', index=False)
    # Save the task schedule
    schedule_df = pd.DataFrame([(date, task) for date in task_schedule for task in task_schedule[date]], columns=['Date', 'Task'])
    schedule_df.to_csv('task_schedule.csv', index=False)
schedule= load_json(schedule_path, [])
study_plan= load_json(plan_path, {})
todo_list=  load_json(todo_path, [])
marks_df=  pd.read_csv(marks_path) if os.path.exists(marks_path) else pd.DataFrame(columns=["Date", "Subject", "Test Type", "Score", "Total", "Notes"])

# Load existing data (if any)
def load_existing_data():
    global to_do_list, task_schedule
    
    
    if os.path.exists('to_do_list.csv'):
        to_do_list = pd.read_csv('to_do_list.csv').to_dict(orient='records')
    else:
        to_do_list = []
    if os.path.exists('task_schedule.csv'):
        task_schedule = pd.read_csv('task_schedule.csv').groupby('Date')['Task'].apply(list).to_dict()
    else:
        task_schedule = {}

# Initialize data storage
to_do_list = []
task_schedule = {}

load_existing_data()

# Streamlit app UI
def app_ui():
    st.title("Personal AI Study Assistant - Lite")
menu = st.sidebar.radio("Menu", ["Schedule", "Test Tracker", "AI Suggestions", "Study Manager ➕", "To-Do Tracker"])

# Schedule Page
if menu == "Schedule":
    st.header("Study Schedule")
    with st.form("Add Task"):
        d = st.date_input("Date")
        task = st.text_input("Task")
        if st.form_submit_button("Add Task"):
            schedule.append({"date": str(d), "task": task})
            save_json(schedule_path, schedule)
            st.success("Task added!")
    
    st.subheader("Upcoming Tasks")
    for idx, item in enumerate(schedule):
        col1, col2 = st.columns([6, 1])
        col1.write(f"**{item['date']}**: {item['task']}")
        if col2.button("❌", key=f"remove_schedule_{idx}"):
            schedule.pop(idx)
            save_json(schedule_path, schedule)
            st.rerun()

# Test Tracker Page
elif menu == "Test Tracker":
    st.header("Test Performance Tracker")

    with st.form("Add Score"):
        test_date = st.date_input("Test Date")
        subject = st.selectbox("Subject", ["Physics", "Chemistry", "Maths", "Biology"])
        test_type = st.selectbox("Test Type", ["Mock Test", "Unit Test", "Board Practice", "Others"])
        score = st.number_input("Score Obtained", min_value=0)
        total = st.number_input("Total Marks", min_value=1)
        notes = st.text_area("Notes (optional)")
        submitted = st.form_submit_button("Log Score")
        if submitted:
            new_row = {
                "Date": str(test_date),
                "Subject": subject,
                "Test Type": test_type,
                "Score": score,
                "Total": total,
                "Notes": notes
            }
            marks_df = pd.concat([marks_df, pd.DataFrame([new_row])], ignore_index=True)
            marks_df.to_csv(marks_path, index=False)
            st.success("Score logged!")

    st.subheader("Test Scores")
    if not marks_df.empty:
        marks_df["Date"] = pd.to_datetime(marks_df["Date"])
        unique_dates = sorted(marks_df["Date"].dt.strftime('%Y-%m-%d').unique())
        selected_date = st.selectbox("Filter by Test Date", ["All"] + unique_dates)
        
        # Ensure Test Type is a string before sorting
        selected_type = st.selectbox("Filter by Test Type", ["All"] + sorted(marks_df["Test Type"].astype(str).unique()))

        filtered_df = marks_df.copy()
        if selected_date != "All":
            filtered_df = filtered_df[filtered_df["Date"].dt.strftime('%Y-%m-%d') == selected_date]
        if selected_type != "All":
            filtered_df = filtered_df[filtered_df["Test Type"] == selected_type]

        st.dataframe(filtered_df[["Date", "Subject", "Test Type", "Score", "Total", "Notes"]])

        filtered_df["Score %"] = (filtered_df["Score"] / filtered_df["Total"]) * 100
        score_chart = filtered_df.groupby(["Date", "Subject"])["Score %"].mean().unstack()
        st.line_chart(score_chart)

        st.subheader("📊 Performance Breakdown")
        acc_chart = filtered_df.groupby("Subject")["Score %"].mean().sort_values()
        st.bar_chart(acc_chart)

        st.markdown("**Overall Stats:**")
        total_tests = len(filtered_df)
        avg_accuracy = round(filtered_df["Score %"].mean(), 2)
        best_score = filtered_df["Score"].max()
        worst_score = filtered_df["Score"].min()

        st.info(f"Total Tests: {total_tests}")
        st.success(f"Average Score: {avg_accuracy}%")
        st.info(f"Best Score: {best_score}")
        st.warning(f"Lowest Score: {worst_score}")

    # Remove Test Entry
    for idx, row in filtered_df.iterrows():
        col1, col2 = st.columns([6, 1])
        col1.write(f"**{row['Date']}**: {row['Subject']} - {row['Score']}/{row['Total']}")
        if col2.button(f"❌ Remove Test {idx}", key=f"remove_test_{idx}"):
            marks_df.drop(idx, inplace=True)
            marks_df.to_csv(marks_path, index=False)
            st.rerun()
    
# AI Suggestions Page
elif menu == "AI Suggestions":
    st.header("AI-Based Topic Suggestions")
    if marks_df.empty:
        st.info("Please log some test scores to get suggestions.")
    else:
        marks_df["Percentage"] = (marks_df["Score"] / marks_df["Total"]) * 100
        subject_avg = marks_df.groupby("Subject")["Percentage"].mean().sort_values()
        st.subheader("Subject-wise Performance")
        st.bar_chart(subject_avg)

        weak = subject_avg[subject_avg < 60].index.tolist()
        strong = subject_avg[subject_avg >= 85].index.tolist()

        st.markdown("### Suggestions:")
        st.error(f"Focus on: {', '.join(weak)}") if weak else st.success("No weak subjects detected!")
        st.info(f"Strong in: {', '.join(strong)}") if strong else st.warning("No strong subjects yet.")

# Study Manager Page
elif menu == "Study Manager ➕":
    st.header("Daily Study Plan Manager")
    selected_date = str(st.date_input("Select Date for Planning"))
    study_plan.setdefault(selected_date, [])

    with st.form("Add Plan"):
        subject = st.selectbox("Subject", ["Physics", "Chemistry", "Maths", "Biology", "English", "CS"])
        topic = st.text_input("Topic/Chapter")
        duration = st.number_input("Duration (in hours)", min_value=0.0, step=0.5)
        if st.form_submit_button("Add to Plan"):
            entry = {"subject": subject, "topic": topic, "duration": duration}
            study_plan[selected_date].append(entry)
            save_json(plan_path, study_plan)
            
            # Add the plan to the To-Do List
            todo_list.append({"task": f"{subject} - {topic} ({duration} hrs)", "done": False})
            save_json(todo_path, todo_list)
            st.success("Study plan added and synced with To-Do list!")

    st.subheader(f"Plan for {selected_date}")
    for idx, entry in enumerate(study_plan[selected_date]):
        col1, col2 = st.columns([6, 1])
        col1.write(f"**{entry['subject']}** - {entry['topic']} ({entry['duration']} hrs)")
        if col2.button("❌", key=f"remove_{idx}"):
            study_plan[selected_date].pop(idx)
            save_json(plan_path, study_plan)
            st.rerun()
    
    
# To-Do Tracker Page
elif menu == "To-Do Tracker":
    st.header("To-Do Tracker")

    with st.form("Add To-Do"):
        task = st.text_input("Task")
        if st.form_submit_button("Add") and task:
            todo_list.append({"task": task, "done": False})
            save_json(todo_path, todo_list)
            st.success("Task added!")

    def toggle_task(index):
        todo_list[index]["done"] = not todo_list[index]["done"]
        save_json(todo_path, todo_list)

    def remove_task(index):
        todo_list.pop(index)
        save_json(todo_path, todo_list)
        st.rerun()

    st.subheader("Your Tasks")
    for i, item in enumerate(todo_list):
        col1, col2, col3 = st.columns([5, 1, 1])
        col1.checkbox(label=item["task"], value=item["done"], key=i, on_change=toggle_task, args=(i,))
        if col2.button("🗑️", key=f"remove_todo_{i}"):
            remove_task(i)

# Run the app
if __name__ == "__main__":
    app_ui()
