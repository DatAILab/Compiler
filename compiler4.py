import streamlit as st
import sqlite3
import pandas as pd

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
    finally:
        connection.close()

# Streamlit UI
st.title("SQLite Query Executor")

# User input for username
username = st.text_input("Enter your username:", "")

if username:
    # SQL query input
    user_query = st.text_area("Enter your SQL query:", height=150)

    # Execute query button
    if st.button("Execute Query"):
        if user_query:
            result = execute_query(user_query, username)
            if isinstance(result, pd.DataFrame):
                st.write("Query Results:")
                st.dataframe(result, use_container_width=True)
        else:
            st.warning("Please enter a SQL query.")
else:
    st.warning("Please enter a username to proceed.")