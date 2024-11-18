import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime


def init_session_state():
    """Initialize session state variables"""
    if 'username' not in st.session_state:
        st.session_state.username = st.text_input("Enter your username:", key="username_input")

    if 'query_history' not in st.session_state:
        st.session_state.query_history = []


def add_to_history(query, success):
    """Add query to history with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.query_history.append({
        'timestamp': timestamp,
        'query': query,
        'status': 'Success' if success else 'Failed'
    })


def execute_select_query(connection, query):
    """Execute a SELECT query and return results as DataFrame"""
    cursor = connection.cursor()
    cursor.execute(query)
    column_names = [description[0] for description in cursor.description]
    results = cursor.fetchall()
    return pd.DataFrame(results, columns=column_names)


def execute_query(query):
    """Execute a SQL query and return results or success status"""
    db_filename = "shared_database.db"  # Single shared database
    connection = sqlite3.connect(db_filename)
    cursor = connection.cursor()
    success = True

    # Prefix table names with username
    if st.session_state.username:
        if query.strip().upper().startswith("CREATE TABLE"):
            table_name = query.split()[2]  # Get table name
            prefixed_table_name = f"{st.session_state.username}_{table_name}"  # Prefix with username
            query = query.replace(table_name, prefixed_table_name)

        if query.strip().upper().startswith("SELECT"):
            try:
                result = execute_select_query(connection, query)
                return result
            except sqlite3.Error as e:
                st.error(f"An error occurred: {e}")
                success = False
        else:
            try:
                cursor.execute(query)
                connection.commit()
                st.success("Query executed successfully.")
            except sqlite3.Error as e:
                st.error(f"An error occurred: {e}")
                success = False

    add_to_history(query, success)
    connection.close()


# Initialize session state
init_session_state()

# Streamlit UI
st.title("SQLite Query Executor")

# Input for username
if st.session_state.username:
    st.success(f"Welcome, {st.session_state.username}!")

# Sidebar for history
with st.sidebar:
    st.header("Query History")
    if st.button("Clear History"):
        st.session_state.query_history = []

    for idx, item in enumerate(reversed(st.session_state.query_history[-5:])):  # Show last 5 queries
        st.write(f"Time: {item['timestamp']}, Status: {item['status']}")
        st.code(item['query'])

# Main area
user_query = st.text_area("Enter your SQL query:", height=150)

# Execute query button
if st.button("Execute Query"):
    if user_query:
        result = execute_query(user_query)

        if isinstance(result, pd.DataFrame):
            st.write("Query Results:")
            if not result.empty:
                st.table(result)
                st.write(f"Total rows: {len(result)}")
            else:
                st.info("Query returned no results.")
    else:
        st.warning("Please enter a SQL query.")