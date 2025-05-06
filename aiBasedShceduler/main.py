import pandas as pd
import tkinter as tk
import numpy 
from tkinter import messagebox, ttk

import os
from datetime import datetime

# ---------- File Paths ----------
TODO_FILE = "to_do_list.csv"
SCHEDULE_FILE = "task_schedule.csv"
MARKS_FILE = "marks_data.csv"

# ---------- Data Storage ----------
to_do_list = []
task_schedule = {}

# ---------- Data Loaders ----------
def load_data():
    global to_do_list, task_schedule
    if os.path.exists(TODO_FILE):
        to_do_list.clear()
        to_do_list.extend(pd.read_csv(TODO_FILE).to_dict('records'))

    if os.path.exists(SCHEDULE_FILE):
        df = pd.read_csv(SCHEDULE_FILE)
        task_schedule.clear()
        for _, row in df.iterrows():
            date, task = row['Date'], row['Task']
            if date not in task_schedule:
                task_schedule[date] = []
            task_schedule[date].append(task)

# ---------- Data Saver ----------
def save_data():
    pd.DataFrame(to_do_list).to_csv(TODO_FILE, index=False)
    schedule_data = [(d, t) for d in task_schedule for t in task_schedule[d]]
    pd.DataFrame(schedule_data, columns=["Date", "Task"]).to_csv(SCHEDULE_FILE, index=False)

# ---------- Add Task ----------
def add_task():
    task = task_entry.get()
    date = date_entry.get()
    task_type = type_entry.get()
    if not task or not date:
        messagebox.showerror("Error", "Please enter both task and date")
        return

    to_do_list.append({"Task": task, "Date": date, "Task Type": task_type})
    if date not in task_schedule:
        task_schedule[date] = []
    task_schedule[date].append(task)
    save_data()
    update_display()
    task_entry.delete(0, tk.END)

# ---------- Delete Task ----------
def delete_selected():
    try:
        selected = todo_tree.selection()[0]
        task = todo_tree.item(selected)['values'][0]
        # Remove from to-do list
        to_do_list[:] = [t for t in to_do_list if t['Task'] != task]
        # Remove from schedule
        for date in list(task_schedule.keys()):
            if task in task_schedule[date]:
                task_schedule[date].remove(task)
                if not task_schedule[date]:
                    del task_schedule[date]
        save_data()
        update_display()
    except IndexError:
        messagebox.showerror("Error", "No task selected")

# ---------- Display Updater ----------
def update_display():
    todo_tree.delete(*todo_tree.get_children())
    for task in to_do_list:
        todo_tree.insert("", "end", values=(task['Task'], task['Date'], task['Task Type']))

# ---------- Load Marks File ----------
def load_marks():
    if os.path.exists(MARKS_FILE):
        df = pd.read_csv(MARKS_FILE)
        return df["Test Type"].unique().tolist()
    else:
        return []

# ---------- GUI Setup ----------
root = tk.Tk()
root.title("AI-Based Scheduler")
root.geometry("800x600")

# ========== Input Fields ==========
frame = tk.Frame(root)
frame.pack(pady=10)

tk.Label(frame, text="Task").grid(row=0, column=0, padx=5)
task_entry = tk.Entry(frame, width=30)
task_entry.grid(row=0, column=1)

tk.Label(frame, text="Date (YYYY-MM-DD)").grid(row=0, column=2, padx=5)
date_entry = tk.Entry(frame, width=15)
date_entry.grid(row=0, column=3)

tk.Label(frame, text="Task Type").grid(row=0, column=4, padx=5)
type_entry = tk.Entry(frame, width=15)
type_entry.grid(row=0, column=5)

tk.Button(frame, text="Add Task", command=add_task).grid(row=0, column=6, padx=5)

# ========== Task Table ==========
columns = ("Task", "Date", "Task Type")
todo_tree = ttk.Treeview(root, columns=columns, show="headings", height=10)
for col in columns:
    todo_tree.heading(col, text=col)
todo_tree.pack(pady=10, fill="x", padx=20)

tk.Button(root, text="Delete Selected Task", command=delete_selected).pack(pady=5)

# ========== AI Suggestions ==========
tk.Label(root, text="AI Suggestions", font=("Arial", 14)).pack()
ai_text = tk.Text(root, height=6, wrap="word", bg="#f0f0f0")
ai_text.pack(padx=20, pady=5, fill="x")
ai_text.insert(tk.END, "- Focus on revising Plant Reproduction\n- Practice Physics vector and integration problems\n- Avoid silly mistakes in Power Set and HCF/LCM\n- Maintain strong Chemistry performance\n- Try mock tests every 7 days")
ai_text.config(state='disabled')

# ========== Load Initial ==========
load_data()
update_display()

# ========== Start App ==========
root.mainloop()
