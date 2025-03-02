# Import necessary libraries
import streamlit as st
import pandas as pd
import numpy as np
from pulp import LpMinimize, LpProblem, LpVariable, lpSum

# Streamlit App Title
st.title("Optimization-Based Timetable Scheduler")
st.subheader("Enter Course, Teacher, and Time Slot Constraints")

# User Inputs
num_courses = st.number_input("Enter Number of Courses", min_value=1, step=1, value=4)
num_teachers = st.number_input("Enter Number of Teachers", min_value=1, step=1, value=3)
num_slots = st.number_input("Enter Number of Time Slots", min_value=1, step=1, value=5)

# Availability Matrix Input
data = []
st.write("Enter course-teacher preference matrix (1 if available, 0 otherwise)")
for i in range(num_courses):
    row = []
    for j in range(num_teachers):
        value = st.number_input(f"Course {i+1}, Teacher {j+1}", min_value=0, max_value=1, step=1)
        row.append(value)
    data.append(row)
availability_matrix = np.array(data)

# Optimization Button
if st.button("Generate Optimal Timetable"):
    # Define LP Problem
    model = LpProblem("Timetable_Optimization", LpMinimize)

    # Decision Variables
    x = {(i, j, k): LpVariable(f"x_{i}_{j}_{k}", cat="Binary")
         for i in range(num_courses) for j in range(num_teachers) for k in range(num_slots)}

    # Objective Function: Minimize vacant slots
    model += lpSum(x[i, j, k] for i in range(num_courses) for j in range(num_teachers) for k in range(num_slots))

    # Constraints
    for i in range(num_courses):
        model += lpSum(x[i, j, k] for j in range(num_teachers) for k in range(num_slots)) == 1  # Each course assigned once
    
    for j in range(num_teachers):
        for k in range(num_slots):
            model += lpSum(x[i, j, k] for i in range(num_courses)) <= 1  # Each teacher has one course per slot

    for i in range(num_courses):
        for j in range(num_teachers):
            if availability_matrix[i, j] == 0:
                for k in range(num_slots):
                    model += x[i, j, k] == 0  # Respect availability

    # Solve Model
    model.solve()
    
    # Display Results
    timetable = []
    for i in range(num_courses):
        for j in range(num_teachers):
            for k in range(num_slots):
                if x[i, j, k].value() == 1:
                    timetable.append([f"Course {i+1}", f"Teacher {j+1}", f"Slot {k+1}"])
    
    df = pd.DataFrame(timetable, columns=["Course", "Teacher", "Time Slot"])
    st.write("### Optimized Timetable")
    st.dataframe(df)
    st.download_button("Download Timetable", data=df.to_csv().encode('utf-8'), file_name="timetable.csv", mime="text/csv")
