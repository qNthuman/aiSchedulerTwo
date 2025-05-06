# planner/scheduler.py

from ortools.sat.python import cp_model
import pandas as pd
import random

# Function to generate the study schedule using OR-Tools
def generate_schedule(ai_plan, hours_per_day, deadline_days):
    """
    Generate an optimized study schedule using OR-Tools for the given AI plan.

    Parameters:
        ai_plan (dict): Dictionary with topics and their breakdown from AI planner.
        hours_per_day (int): Number of hours available for study per day.
        deadline_days (int): Total days available to study.

    Returns:
        dict: Optimized study schedule (Day -> List of topics)
    """
    
    # Flatten the AI plan into a list of topics and their estimated hours
    tasks = []
    for topic, hours in ai_plan.items():
        for _ in range(hours):
            tasks.append(topic)
    
    total_hours_needed = len(tasks)
    
    # Create the model
    model = cp_model.CpModel()

    # Create variables: for each task, we will assign it to a specific day
    task_assignments = []
    for i in range(total_hours_needed):
        task_assignments.append(model.NewIntVar(0, deadline_days - 1, f"task_{i}"))
    
    # Add constraints: Ensure we don't exceed available study hours per day
    for day in range(deadline_days):
        model.Add(sum(task_assignments[i] == day for i in range(total_hours_needed)) <= hours_per_day)
    
    # Objective: Minimize the max day index (i.e., we want to spread tasks evenly)
    model.Minimize(max(task_assignments))
    
    # Solve the model
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 10
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        # Generate the final schedule
        schedule = {f"Day {day + 1}": [] for day in range(deadline_days)}
        for i in range(total_hours_needed):
            assigned_day = solver.Value(task_assignments[i])
            schedule[f"Day {assigned_day + 1}"].append(tasks[i])

        # Optionally randomize order of topics in each day to avoid monotony
        for day in schedule:
            random.shuffle(schedule[day])

        return schedule
    else:
        return {"error": "No feasible schedule found. Please adjust your constraints."}

