import streamlit as st
import pandas as pd
from supabase import Client, create_client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

# Function to initialize the database with sample data
def initialize_database():
    try:
        # Create tables using SQL
        # Note: Supabase automatically creates id column as primary key
        supabase.table("employees").insert([
            {"first_name": "John", "last_name": "Doe", "department": "IT", "salary": 75000, "hire_date": "2020-01-15"},
            {"first_name": "Jane", "last_name": "Smith", "department": "HR", "salary": 65000, "hire_date": "2019-06-20"},
            {"first_name": "Bob", "last_name": "Johnson", "department": "IT", "salary": 80000, "hire_date": "2018-03-10"},
            {"first_name": "Alice", "last_name": "Williams", "department": "Finance", "salary": 70000, "hire_date": "2021-02-28"},
            {"first_name": "Charlie", "last_name": "Brown", "department": "HR", "salary": 62000, "hire_date": "2020-11-15"}
        ]).execute()

        supabase.table("departments").insert([
            {"dept_name": "IT", "location": "New York", "budget": 500000},
            {"dept_name": "HR", "location": "Chicago", "budget": 300000},
            {"dept_name": "Finance", "location": "Boston", "budget": 400000}
        ]).execute()

        return "Database initialized with sample data."
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Function to execute SQL queries
@st.cache_data(ttl=600)
def execute_query(query):
    try:
        result = supabase.table("employees").select("*").execute()
        if result.data:
            df = pd.DataFrame(result.data)
            return df
        else:
            return "Query executed successfully."
    except Exception as e:
        return f"An error occurred: {str(e)}"