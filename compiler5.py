import streamlit as st
from database_utils import initialize_database, execute_query
import pandas as pd

# Streamlit UI
st.title("Cloud Database Query Executor")
st.caption("Connected to Supabase Database")

# Connection status
if st.sidebar.button("Test Connection"):
    try:
        # Test query
        execute_query("SELECT 1")
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
    "Average Salary": "SELECT department, ROUND(AVG(salary)::numeric, 2) as avg_salary FROM employees GROUP BY department",
    "Min & Max Salary": "SELECT MIN(salary) as min_salary, MAX(salary) as max_salary FROM employees",
    "Join Example": "SELECT e.first_name, e.last_name, e.department, d.location, d.budget FROM employees e JOIN departments d ON e.department = d.dept_name",
    "Complex Query": "SELECT d.dept_name, COUNT(e.*) as employee_count, ROUND(AVG(e.salary)::numeric, 2) as avg_salary, d.budget, ROUND((d.budget / COUNT(e.*))::numeric, 2) as budget_per_employee FROM departments d LEFT JOIN employees e ON d.dept_name = e.department GROUP BY d.dept_name, d.budget HAVING COUNT(e.*) > 1 ORDER BY avg_salary DESC"
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