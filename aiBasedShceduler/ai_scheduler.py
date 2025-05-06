
import pandas as pd
import random
import streamlit as st
import os
import json

# Ensure data directory exists
if not os.path.exists("data"):
    os.makedirs("data")

# Paths

schedule_path = "data/schedule.json"
plan_path = "data/study_plan.json"
todo_path = "data/todo.json"
quotes = "data/quotes.csv"
marks_path = "data/marks.csv"
# Sample Data (Replace with actual dynamic data sources like DB or CSVs)
marks_df = pd.read_csv(marks_path) if os.path.exists(marks_path) else pd.DataFrame(columns=["Date", "Subject", "Test Type", "Score", "Total", "Notes"])
 # Replace with actual data source
daily_schedule = [{"task": "Math Revision", "date": "2025-05-03"}, {"task": "Physics Mock Test", "date": "2025-05-04"}]  # Example
upcoming_tests = [{"name": "Mock Test 1", "date": "2025-05-10"}, {"name": "Final Exam", "date": "2025-06-01"}]  # Example
def load_json(path, default):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# Load data
schedule = load_json(schedule_path, [])
study_plan = load_json(plan_path, {})
todo_list = load_json(todo_path, [])
marks_df = pd.read_csv(marks_path) if os.path.exists(marks_path) else pd.DataFrame(columns=["Date", "Subject", "Test Type", "Score", "Total", "Notes"])



# Function to generate AI suggestions based on user's progress, schedule, and tests
def generate_suggestions(marks_df, daily_schedule, upcoming_tests):
    suggestions = []

    # Suggest study areas based on weak subjects
    required_cols = {'Subject', 'Score %'}
    if not required_cols.issubset(marks_df.columns):
        st.write("missing")

    weak_subjects = marks_df.groupby('Subject')['Score %'].mean().sort_values().head(3).index.tolist()
    for subject in weak_subjects:
        suggestions.append(f"Review and practice concepts in {subject} to improve your score.")

    # Suggest upcoming tasks or exams
    upcoming = []
    for test in upcoming_tests:
        test_date = pd.to_datetime(test["date"])
        if test_date < pd.to_datetime("today"):
            upcoming.append(f"Prepare for the {test['name']} scheduled on {test_date.strftime('%Y-%m-%d')}.")
    
    # Suggest optimized study plans based on progress
    if len(daily_schedule) > 0:
        recent_task = daily_schedule[-1]
        suggestions.append(f"Based on your recent task ({recent_task}), focus on similar tasks for better performance.")
    
    # Motivational prompt

# Step 1: Read the file and store its contents in a list
    file_path = 'qts.txt'  # Replace with your file path
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Step 2: Select random elements from the list
    num_elements = 1
    motivational_quotes = random.sample(lines, num_elements)
    
      # Number of random elements you want to select
    for element in motivational_quotes:
        mt = element.strip()
        suggestions.append(mt)
    
    # Automated To-Do List suggestions
    overdue_tasks = [task for task in daily_schedule if pd.to_datetime(task["date"]) < pd.to_datetime("today")]
    if overdue_tasks:
        suggestions.append("You have some overdue tasks. It's a good idea to catch up on them today.")

    return suggestions

# Display the AI suggestions UI in the Streamlit app
def ai_suggestions_ui():
    st.header("AI Suggestions")
    
    suggestions = generate_suggestions(marks_df, daily_schedule, upcoming_tests)
    
    for suggestion in suggestions:
        st.write(f"- {suggestion}")

# Streamlit layout: Update the app structure
def app_ui():
    st.title("Curious Manager")

    # Sidebar for navigation (Example)
    menu = ["Home", "Test Tracker","Study Manager", "Schedule", "AI Suggestions", "To-Do List"]
    choice = st.sidebar.selectbox("may i help you ?", menu)



    # Display sections based on user choice
    if choice == "AI Suggestions":
        ai_suggestions_ui()  # Display AI suggestions

    elif choice == "Schedule":
        # Include schedule management logic here
        st.subheader("Schedule")
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

        
        # Your logic to display or add schedules goes here
        
    elif choice == "Test Tracker":
        # Include test tracking logic here
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
                if marks_df is None:
                    marks_df = pd.DataFrame()
                marks_df = pd.concat([marks_df, pd.DataFrame([new_row])], ignore_index=True)
                marks_df.to_csv(marks_path, index=False)
                st.success("Score logged!")

        st.subheader("Test Scores")
        marks_df = None  # or pd.DataFrame() depending on your use case

        if isinstance(marks_df, pd.DataFrame):
    # then safe to do marks_df.empty
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
                # Your logic to manage tests goes here

    elif choice == "To-Do List":
        # Include to-do list management logic here
        st.subheader("To-Do List")

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




        # Your logic to display or add to-do list tasks goes here
    elif choice == "Study Manager":
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
    
    
    else:
        st.subheader("Welcome to your AI Scheduler!")

# Main function to run the app
if __name__ == "__main__":
    app_ui()
