import streamlit as st
import sqlite3
import pandas as pd
import os

def get_connection(username):
    # Create a unique database for each user
    db_file = f"{username}.db"
    return sqlite3.connect(db_file)

def execute_query(query, username):
    connection = get_connection(username)
    cursor = connection.cursor()

    try:
        # Execute the query
        cursor.execute(query)

        # Handle CREATE statements
        if query.strip().upper().startswith("CREATE"):
            if query.strip().upper().startswith("CREATE TABLE"):
                st.success("Table created successfully.")
            elif query.strip().upper().startswith("CREATE VIEW"):
                st.success("View created successfully.")
            elif query.strip().upper().startswith("CREATE PROCEDURE"):
                procedure_name = query.strip().split(" ")[2]
                st.success(f"Stored procedure '{procedure_name}' created successfully.")
            else:
                st.success("Statement executed successfully.")
            return None  # Return None for CREATE statements

        # Handle SELECT queries
        elif query.strip().upper().startswith("SELECT"):
            column_names = [description[0] for description in cursor.description]
            results = cursor.fetchall()
            df = pd.DataFrame(results, columns=column_names)
            return df

        # Handle other queries
        else:
            connection.commit()
            st.success("Query executed successfully.")
            return None  # Return None for non-SELECT queries

    except sqlite3.Error as e:
        st.error(f"An error occurred: {e}")
        return None
    finally:
        connection.close()

# Streamlit UI
st.title("SQLite Query Executor")

# Initialize session state for submitted queries if not exists
if 'submitted_queries' not in st.session_state:
    st.session_state.submitted_queries = []

# User input for username
username = st.text_input("Enter your username:", "")

if username:
    # SQL query input
    user_query = st.text_area("Enter your SQL query:", height=150)

    # Columns for buttons
    col1, col2 = st.columns(2)

    with col1:
        try_query = st.button("Try Query")

    with col2:
        submit_query = st.button("Submit Query")

    # Display options
    display_option = st.radio(
        "Choose display format:",
        ["Static Table", "Interactive Table"],
        horizontal=True
    )

    # Try Query functionality
    if try_query and user_query:
        result = execute_query(user_query, username)

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

    # Submit Query functionality
    if submit_query and user_query:
        try:
            # Add query to submitted queries list
            st.session_state.submitted_queries.append(user_query)
            st.success(f"Query '{user_query}' has been submitted!")
        except Exception as e:
            st.error(f"Error submitting query: {str(e)}")

    # Display submitted queries
    if st.session_state.submitted_queries:
        st.write("### Submitted Queries:")
        for idx, submitted_query in enumerate(st.session_state.submitted_queries, 1):
            st.write(f"{idx}. {submitted_query}")

    # Optional: Clear submitted queries
    if st.button("Clear Submitted Queries"):
        st.session_state.submitted_queries = []
else:
    st.warning("Please enter a username to proceed.")