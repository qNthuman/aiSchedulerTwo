# planner/data_handler.py

import json
import os
from datetime import datetime

# Define the path where user data will be stored
DATA_FILE = "user_data.json"

# Function to load user data from the file
def load_user_data():
    """
    Load user data from a JSON file (if exists).
    If no data exists, return a dictionary with default structure.
    """
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as file:
                user_data = json.load(file)
            return user_data
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading user data: {str(e)}")
            return {}
    else:
        print("No previous user data found. Starting fresh.")
        return {"username": "User", "plans": {}, "history": []}

# Function to save user data to a file
def save_user_data(data):
    """
    Save user data to a JSON file.
    """
    try:
        with open(DATA_FILE, "w") as file:
            json.dump(data, file, indent=4)
        print("User data saved successfully!")
    except IOError as e:
        print(f"Error saving user data: {str(e)}")

# Function to add history entry (optional for tracking)
def add_history_entry(user_data, action, details):
    """
    Add an entry to the user's history log.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    history_entry = {"timestamp": timestamp, "action": action, "details": details}
    user_data["history"].append(history_entry)
    save_user_data(user_data)

# Function to clear user data (if needed, for resets)
def clear_user_data():
    """
    Clear user data and reset to default.
    """
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
    print("User data cleared.")

