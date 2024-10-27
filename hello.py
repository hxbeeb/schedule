import streamlit as st
from pymongo import MongoClient
from datetime import datetime, timedelta

# MongoDB connection string
mongo_uri = 'mongodb+srv://Abraar:Abraar@cluster0.pyk9f.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'
client = MongoClient(mongo_uri)
db = client['test']
departments_collection = db['departments']

# Define conflict matrix and priorities
conflict_matrix = {
    "roads & buildings department": ["ma&ud department", "phed", "electricity department", "irrigation and cad department"],
    "ma&ud department": ["roads & buildings department"],
    "phed": ["roads & buildings department", "ma&ud department"],
    "electricity department": ["roads & buildings department"],
    "irrigation and cad department": ["roads & buildings department"],
    "transport department": [],
    "housing department": ["roads & buildings department", "ma&ud department"],
    "environment and forest department": ["roads & buildings department"],
}

department_priorities = {
    "ma&ud department": 1,
    "phed": 2,
    "electricity department": 3,
    "roads & buildings department": 4,
    "irrigation and cad department": 5,
    "transport department": 6,
    "housing department": 7,
    "environment and forest department": 8,
}

# Function to generate alternative dates
def suggest_alternative_dates(start_date, end_date, duration_days):
    alternative_dates = []
    # Check dates around the conflict range for alternatives
    for i in range(1, 15):  # Suggest up to 14 days later
        new_start_date = start_date + timedelta(days=i)
        new_end_date = new_start_date + timedelta(days=duration_days)
        alternative_dates.append((new_start_date, new_end_date))

    return alternative_dates

# Streamlit App
st.title("Department Project Scheduler")

# Form for user input
with st.form("scheduler_form"):
    department = st.selectbox("Select Department", options=list(conflict_matrix.keys()))
    start_date = st.date_input("Start Date")
    end_date = st.date_input("End Date")
    submitted = st.form_submit_button("Check Schedule")

if submitted:
    start_date = datetime.strptime(str(start_date), '%Y-%m-%d')
    end_date = datetime.strptime(str(end_date), '%Y-%m-%d')
    duration_days = (end_date - start_date).days + 1

    conflicting_depts = []
    priority_info = []

    # Fetching department projects from MongoDB
    departments = departments_collection.find({})
    for dept in departments:
        dept_name = dept['name'].lower()  # Ensure the department name is in lowercase
        if dept_name in conflict_matrix.get(department.lower(), []):  # Convert input to lowercase
            for project in dept.get('projects', []):
                project_start_date = datetime.strptime(project['start_date'], '%Y-%m-%d')
                project_end_date = datetime.strptime(project['end_date'], '%Y-%m-%d')
                if start_date <= project_end_date and end_date >= project_start_date:
                    conflicting_depts.append(dept_name)
                    priority_info.append(f"{dept_name} (Priority {department_priorities[dept_name]})")

    # Displaying results
    if conflicting_depts:
        st.subheader("Scheduling Conflict")
        st.write("Conflicting Departments:", conflicting_depts)
        
        # Suggest alternative dates for rescheduling
        alternative_dates = suggest_alternative_dates(start_date, end_date, duration_days)
        st.subheader("Alternative Dates for Rescheduling")
        for new_start, new_end in alternative_dates:
            st.write(f"* New Start: {new_start.date()}, New End: {new_end.date()}")
    else:
        st.success("No conflicts detected.")
