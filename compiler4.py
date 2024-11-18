import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime


def init_session_state():
    """Initialize session state variables"""
    if 'query_history' not in st.session_state:
        st.session_state.query_history = []
    if 'last_executed_query' not in st.session_state:
        st.session_state.last_executed_query = None
    if 'execution_time' not in st.session_state:
        st.session_state.execution_time = None


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
    start_time = datetime.now()
    connection = sqlite3.connect('example.db')
    cursor = connection.cursor()
    success = True

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
            result = execute_select_query(connection, query)
            end_time = datetime.now()
            st.session_state.execution_time = (end_time - start_time).total_seconds()
            return result

        # Handle other queries
        else:
            cursor.execute(query)
            connection.commit()
            st.success("Query executed successfully.")

    except sqlite3.Error as e:
        st.error(f"An error occurred: {e}")
        success = False
        return None
    finally:
        connection.close()
        end_time = datetime.now()
        st.session_state.execution_time = (end_time - start_time).total_seconds()
        st.session_state.last_executed_query = query
        add_to_history(query, success)


# Initialize session state
init_session_state()

# Streamlit UI
st.title("SQLite Query Executor")

# Sidebar for history
with st.sidebar:
    st.header("Query History")
    if st.button("Clear History"):
        st.session_state.query_history = []

    for idx, item in enumerate(reversed(st.session_state.query_history[-5:])):  # Show last 5 queries
        with st.expander(f"Query {len(st.session_state.query_history) - idx}"):
            st.text(f"Time: {item['timestamp']}")
            st.text(f"Status: {item['status']}")
            if st.button("Rerun", key=f"rerun_{idx}"):
                st.session_state.query_input = item['query']
            st.code(item['query'])

# Main area
col1, col2 = st.columns([3, 1])
with col1:
    # SQL query input
    if 'query_input' not in st.session_state:
        st.session_state.query_input = ""

    user_query = st.text_area(
        "Enter your SQL query:",
        value=st.session_state.query_input,
        height=150,
        key="query_area"
    )

with col2:
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
                if st.session_state.execution_time is not None:
                    st.write(f"Query execution time: {st.session_state.execution_time:.3f} seconds")
            else:
                st.info("Query returned no results.")
    else:
        st.warning("Please enter a SQL query.")

