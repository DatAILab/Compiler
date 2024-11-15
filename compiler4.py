import streamlit as st
import sqlite3
import pandas as pd

# Function to initialize the database with sample data
def initialize_database():
    connection = sqlite3.connect('example.db')
    cursor = connection.cursor()

    try:
        # Create sample tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                emp_id INTEGER PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                department TEXT,
                salary REAL,
                hire_date DATE
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS departments (
                dept_id INTEGER PRIMARY KEY,
                dept_name TEXT NOT NULL,
                location TEXT,
                budget REAL
            )
        ''')

        # Insert sample data into employees
        employees_data = [
            (1, 'John', 'Doe', 'IT', 75000, '2020-01-15'),
            (2, 'Jane', 'Smith', 'HR', 65000, '2019-06-20'),
            (3, 'Bob', 'Johnson', 'IT', 80000, '2018-03-10'),
            (4, 'Alice', 'Williams', 'Finance', 70000, '2021-02-28'),
            (5, 'Charlie', 'Brown', 'HR', 62000, '2020-11-15')
        ]

        cursor.executemany('''
            INSERT OR REPLACE INTO employees 
            (emp_id, first_name, last_name, department, salary, hire_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', employees_data)

        # Insert sample data into departments
        departments_data = [
            (1, 'IT', 'New York', 500000),
            (2, 'HR', 'Chicago', 300000),
            (3, 'Finance', 'Boston', 400000)
        ]

        cursor.executemany('''
            INSERT OR REPLACE INTO departments 
            (dept_id, dept_name, location, budget)
            VALUES (?, ?, ?, ?)
        ''', departments_data)

        connection.commit()
        return "Database initialized with sample data."
    except sqlite3.Error as e:
        return f"An error occurred: {e}"
    finally:
        connection.close()

# Function to execute SQL queries
def execute_query(query):
    connection = sqlite3.connect('example.db')
    cursor = connection.cursor()

    try:
        cursor.execute(query)

        # For SELECT queries, return results as DataFrame
        if query.strip().upper().startswith("SELECT"):
            column_names = [description[0] for description in cursor.description]
            results = cursor.fetchall()
            df = pd.DataFrame(results, columns=column_names)
            return df
        else:
            connection.commit()
            return "Query executed successfully."
    except sqlite3.Error as e:
        return f"An error occurred: {e}"
    finally:
        connection.close()

# Function to create a view
def create_view(view_name, select_query):
    create_view_query = f"CREATE VIEW IF NOT EXISTS {view_name} AS {select_query}"
    return execute_query(create_view_query)

# Streamlit UI
st.title("Advanced SQLite Query Executor")

# Initialize database button
if st.button("Initialize Database with Sample Data"):
    result = initialize_database()
    st.success(result)

# Sample queries section
st.subheader("Sample Queries")
sample_queries = {
    "Select All Employees": "SELECT * FROM employees",
    "Distinct Departments": "SELECT DISTINCT department FROM employees",
    "Average Salary": "SELECT department, AVG(salary) as avg_salary FROM employees GROUP BY department",
    "Min & Max Salary": "SELECT MIN(salary) as min_salary, MAX(salary) as max_salary FROM employees",
    "Join Example": """
        SELECT e.first_name, e.last_name, e.department, d.location, d.budget
        FROM employees e
        JOIN departments d ON e.department = d.dept_name
    """,
    "Count by Department": "SELECT department, COUNT(*) as emp_count FROM employees GROUP BY department",
    "High Salary Employees": "SELECT * FROM employees WHERE salary > (SELECT AVG(salary) FROM employees)",
    "Recent Hires": "SELECT * FROM employees WHERE hire_date >= '2020-01-01' ORDER BY hire_date DESC"
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

# Create View section
st.subheader("Create a View")
view_name = st.text_input("Enter the name for the new view:")
view_query = st.text_area("Enter the SELECT query for the view:", height=150)

if st.button("Create View"):
    if view_name and view_query:
        result = create_view(view_name, view_query)
        st.success(result)
    else:
        st.warning("Please enter both a view name and a SELECT query.")

# Documentation section
with st.expander("SQL Features Reference", expanded=False):
    st.markdown("""
    ### Supported SQL Features:

    #### Data Definition Language (DDL):
    - CREATE TABLE
    - DROP TABLE
    - ALTER TABLE
    - CREATE INDEX
    - CREATE VIEW

    #### Data Manipulation Language (DML):
    - INSERT INTO
    - UPDATE
    - DELETE
    - SELECT

    #### Query Clauses:
    - WHERE
    - GROUP BY
    - HAVING
    - ORDER BY
    - LIMIT

    #### Joins:
    - INNER JOIN
    - LEFT JOIN
    - RIGHT JOIN
    - FULL JOIN

    #### Aggregate Functions:
    - COUNT()
    - SUM()
    - AVG()
    - MIN()
    - MAX()

    #### Other Features:
    - DISTINCT
    - LIKE
    - IN
    - BETWEEN
    - Subqueries
    - UNION/UNION ALL
    - Case statements
    - Date/Time functions
    """)

# Additional SQL examples
with st.expander("More SQL Examples", expanded=False):
    st.code("""
-- Create a new table
CREATE TABLE projects (
    project_id INTEGER PRIMARY KEY,
    project_name TEXT,
    start_date DATE,
    budget REAL
);

-- Drop a table
DROP TABLE IF EXISTS old_table;

-- Alter table
ALTER TABLE employees ADD COLUMN email TEXT;

-- Subquery example
SELECT * FROM employees 
WHERE salary > (SELECT AVG(salary) FROM employees);

-- Complex JOIN with aggregation
SELECT 
    d.dept_name,
    COUNT(e.emp_id) as employee_count,
    AVG(e.salary) as avg_salary,
    d.budget
FROM departments d
LEFT JOIN employees e ON d.dept_name = e.department
GROUP BY d.dept_name
HAVING COUNT(e.emp_id) > 1;

-- CASE statement
SELECT 
    first_name,
    last_name,
    salary,
    CASE 
        WHEN salary < 65000 THEN 'Low'
        WHEN salary < 75000 THEN 'Medium'
        ELSE 'High'
    END as salary_category
FROM employees;

-- Window functions
SELECT 
    department,
    first_name,
    salary,
    AVG(salary) OVER (PARTITION BY department) as dept_avg_salary
FROM employees;
    """)
