import streamlit as st
import sqlite3
import pandas as pd

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

# Streamlit UI
st.title("SQLite Query Executor")

# Single input area for queries, views, or stored procedures
user_query = st.text_area("Enter your SQL query, view creation, or stored procedure:", height=300)

# Execute query button
if st.button("Execute"):
    if user_query:
        result = execute_query(user_query)

        if isinstance(result, pd.DataFrame):
            st.write("Query Results:")
            if not result.empty:
                st.dataframe(result, use_container_width=True)
                st.write(f"Total rows: {len(result)}")
            else:
                st.info("Query returned no results.")
        else:
            st.success(result)
    else:
        st.warning("Please enter a SQL query.")

# Documentation section
with st.expander("SQL Features Reference", expanded=False):
    st.markdown("""
    ### Supported SQL Features:

    - **Data Definition Language (DDL)**: CREATE TABLE, DROP TABLE, ALTER TABLE, CREATE VIEW
    - **Data Manipulation Language (DML)**: INSERT INTO, UPDATE, DELETE, SELECT
    - **Query Clauses**: WHERE, GROUP BY, HAVING, ORDER BY, LIMIT
    - **Joins**: INNER JOIN, LEFT JOIN, RIGHT JOIN, FULL JOIN
    - **Aggregate Functions**: COUNT(), SUM(), AVG(), MIN(), MAX()
    - **Other Features**: DISTINCT, LIKE, IN, BETWEEN, Subqueries, UNION/UNION ALL, Case statements, Date/Time functions
    """)

# Additional SQL examples
with st.expander("More SQL Examples", expanded=False):
    st.code("""
-- Example of creating a view
CREATE VIEW high_salary_employees AS 
SELECT * FROM employees WHERE salary > 70000;

-- Example of a parameterized query
SELECT * FROM employees WHERE department = ?;

-- Example of a complex query
SELECT 
    e.first_name,
    e.last_name,
    d.dept_name,
    e.salary
FROM employees e
JOIN departments d ON e.department = d.dept_name
WHERE e.salary > 60000;
    """)