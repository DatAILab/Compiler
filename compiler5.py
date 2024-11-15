import streamlit as st
import pandas as pd
from supabase import create_client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase = create_client(
    supabase_url=os.getenv('SUPABASE_URL'),
    supabase_key=os.getenv('SUPABASE_KEY')
)


# Function to initialize the database with sample data
def initialize_database():
    try:
        # Create tables using SQL
        # Note: Supabase automatically creates id column as primary key
        supabase.query('''
            CREATE TABLE IF NOT EXISTS employees (
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                department TEXT,
                salary DECIMAL(10,2),
                hire_date DATE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
            )
        ''').execute()

        supabase.query('''
            CREATE TABLE IF NOT EXISTS departments (
                dept_name TEXT NOT NULL,
                location TEXT,
                budget DECIMAL(15,2),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
            )
        ''').execute()

        # Sample data for employees
        employees_data = [
            {'first_name': 'John', 'last_name': 'Doe', 'department': 'IT', 'salary': 75000, 'hire_date': '2020-01-15'},
            {'first_name': 'Jane', 'last_name': 'Smith', 'department': 'HR', 'salary': 65000,
             'hire_date': '2019-06-20'},
            {'first_name': 'Bob', 'last_name': 'Johnson', 'department': 'IT', 'salary': 80000,
             'hire_date': '2018-03-10'},
            {'first_name': 'Alice', 'last_name': 'Williams', 'department': 'Finance', 'salary': 70000,
             'hire_date': '2021-02-28'},
            {'first_name': 'Charlie', 'last_name': 'Brown', 'department': 'HR', 'salary': 62000,
             'hire_date': '2020-11-15'}
        ]

        # Insert employees data
        supabase.table('employees').upsert(employees_data).execute()

        # Sample data for departments
        departments_data = [
            {'dept_name': 'IT', 'location': 'New York', 'budget': 500000},
            {'dept_name': 'HR', 'location': 'Chicago', 'budget': 300000},
            {'dept_name': 'Finance', 'location': 'Boston', 'budget': 400000}
        ]

        # Insert departments data
        supabase.table('departments').upsert(departments_data).execute()

        return "Database initialized with sample data."
    except Exception as e:
        return f"An error occurred: {str(e)}"


# Function to execute SQL queries
@st.cache_data(ttl=600)  # Cache results for 10 minutes
def execute_query(query):
    try:
        result = supabase.query(query).execute()

        # Convert result to DataFrame
        if result.data:
            df = pd.DataFrame(result.data)
            return df
        else:
            return "Query executed successfully."
    except Exception as e:
        return f"An error occurred: {str(e)}"


# Streamlit UI
st.title("Cloud Database Query Executor")
st.caption("Connected to Supabase Database")

# Connection status
if st.sidebar.button("Test Connection"):
    try:
        # Test query
        supabase.query("SELECT 1").execute()
        st.sidebar.success("Successfully connected to Supabase!")
    except Exception as e:
        st.sidebar.error(f"Connection failed: {str(e)}")

# Initialize database button
if st.button("Initialize Database with Sample Data"):
    result = initialize_database()
    st.success(result)

# Sample queries section
st.subheader("Sample Queries")
sample_queries = {
    "Select All Employees": "SELECT * FROM employees",
    "Distinct Departments": "SELECT DISTINCT department FROM employees",
    "Average Salary": """
        SELECT department, 
        ROUND(AVG(salary)::numeric, 2) as avg_salary 
        FROM employees 
        GROUP BY department
    """,
    "Min & Max Salary": """
        SELECT 
            MIN(salary) as min_salary, 
            MAX(salary) as max_salary 
        FROM employees
    """,
    "Join Example": """
        SELECT 
            e.first_name, 
            e.last_name, 
            e.department, 
            d.location, 
            d.budget
        FROM employees e
        JOIN departments d ON e.department = d.dept_name
    """,
    "Complex Query": """
        SELECT 
            d.dept_name,
            COUNT(e.*) as employee_count,
            ROUND(AVG(e.salary)::numeric, 2) as avg_salary,
            d.budget,
            ROUND((d.budget / COUNT(e.*))::numeric, 2) as budget_per_employee
        FROM departments d
        LEFT JOIN employees e ON d.dept_name = e.department
        GROUP BY d.dept_name, d.budget
        HAVING COUNT(e.*) > 1
        ORDER BY avg_salary DESC
    """
}

selected_query = st.selectbox("Choose a sample query:", ["Custom Query"] + list(sample_queries.keys()))

# Text area for SQL query input
if selected_query == "Custom Query":
    user_query = st.text_area("Enter your SQL query:", height=150)
else:
    user_query = st.text_area("SQL Query:", value=sample_queries[selected_query], height=150)

# Display options
display_option = st.radio(
    "Choose display format:",
    ["Static Table", "Interactive Table"],
    horizontal=True
)

# Execute query button
if st.button("Execute Query"):
    if user_query:
        with st.spinner("Executing query..."):
            result = execute_query(user_query)

        if isinstance(result, pd.DataFrame):
            st.write("Query Results:")
            if not result.empty:
                if display_option == "Static Table":
                    st.table(result)
                else:
                    st.dataframe(result, use_container_width=True)
                st.write(f"Total rows: {len(result)}")
            else:
                st.info("Query returned no results.")
        else:
            st.success(result)
    else:
        st.warning("Please enter a SQL query.")

# Performance metrics in sidebar
with st.sidebar:
    st.subheader("Performance Metrics")
    st.metric("Cached Queries", "10 minutes")
    if st.button("Clear Cache"):
        st.cache_data.clear()
        st.success("Cache cleared!")

# Documentation
with st.expander("Supabase Features & Limitations", expanded=False):
    st.markdown("""
    ### Supabase PostgreSQL Features:

    #### Supported Operations:
    - Full SQL support
    - Real-time capabilities
    - Row Level Security
    - Foreign Keys
    - Indexes
    - JSON support

    #### Free Tier Limits:
    - 500MB Database
    - Unlimited API requests
    - 50,000 monthly active users
    - Daily backups
    - Social OAuth providers

    #### Best Practices:
    1. Use prepared statements for better security
    2. Create indexes for frequently queried columns
    3. Use appropriate data types
    4. Implement row level security for production
    """)