import streamlit as st
import sqlite3
import pandas as pd


def execute_select_query(connection, query):
    """Execute a SELECT query and return results as DataFrame"""
    cursor = connection.cursor()
    cursor.execute(query)
    column_names = [description[0] for description in cursor.description]
    results = cursor.fetchall()
    return pd.DataFrame(results, columns=column_names)


def execute_query(query):
    connection = sqlite3.connect('example.db')
    cursor = connection.cursor()

    try:
        # Handle CREATE VIEW separately
        if query.strip().upper().startswith("CREATE VIEW"):
            # Extract view name and underlying query
            parts = query.strip().split(" AS ", 1)
            view_name = parts[0].split()[-1]
            view_query = parts[1]

            # Create the view directly using SQLite
            cursor.execute(query)
            connection.commit()
            st.success(f"View '{view_name}' created successfully.")

        # Handle other CREATE statements
        elif query.strip().upper().startswith("CREATE"):
            cursor.execute(query)
            connection.commit()
            if query.strip().upper().startswith("CREATE TABLE"):
                st.success("Table created successfully.")
            elif query.strip().upper().startswith("CREATE PROCEDURE"):
                procedure_name = query.strip().split(" ")[2]
                st.success(f"Stored procedure '{procedure_name}' created successfully.")
            else:
                st.success("Statement executed successfully.")

        # Handle SELECT queries
        elif query.strip().upper().startswith("SELECT"):
            return execute_select_query(connection, query)

        # Handle other queries
        else:
            cursor.execute(query)
            connection.commit()
            st.success("Query executed successfully.")

    except sqlite3.Error as e:
        st.error(f"An error occurred: {e}")
        return None
    finally:
        connection.close()


# Streamlit UI
st.title("SQLite Query Executor")

# SQL query input
user_query = st.text_area("Enter your SQL query:", height=150)

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
        st.warning("Please enter a SQL query.")

# Documentation section
with st.expander("SQL Features Reference", expanded=False):
    st.markdown("""
    ### Supported SQL Features:
    - CREATE TABLE
    - CREATE VIEW
    - CREATE PROCEDURE
    - SELECT
    - INSERT
    - UPDATE
    - DELETE
    """)