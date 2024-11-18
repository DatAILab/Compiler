import streamlit as st
import sqlite3
import pandas as pd
import hashlib
from datetime import datetime
import os

# Ensure database directory exists
DB_DIRECTORY = 'user_databases'
os.makedirs(DB_DIRECTORY, exist_ok=True)


def get_user_database_path(username):
    """Generate a unique database path for each user"""
    # Use hash to create a consistent, unique filename
    username_hash = hashlib.md5(username.encode()).hexdigest()
    return os.path.join(DB_DIRECTORY, f"{username_hash}.db")


def init_session_state():
    """Initialize session state variables"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'query_history' not in st.session_state:
        st.session_state.query_history = []
    if 'last_executed_query' not in st.session_state:
        st.session_state.last_executed_query = None
    if 'execution_time' not in st.session_state:
        st.session_state.execution_time = None
    if 'query_input' not in st.session_state:
        st.session_state.query_input = ""


def add_to_history(query, success):
    """Add query to history with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Limit history to last 10 queries
    st.session_state.query_history.append({
        'timestamp': timestamp,
        'query': query,
        'status': 'Success' if success else 'Failed'
    })
    if len(st.session_state.query_history) > 10:
        st.session_state.query_history = st.session_state.query_history[-10:]


def execute_select_query(connection, query):
    """Execute a SELECT query and return results as DataFrame"""
    cursor = connection.cursor()
    cursor.execute(query)
    column_names = [description[0] for description in cursor.description]
    results = cursor.fetchall()
    return pd.DataFrame(results, columns=column_names)


def execute_query(query):
    # Ensure user is logged in
    if not st.session_state.logged_in:
        st.error("Please log in first.")
        return None

    # Get user-specific database path
    db_path = get_user_database_path(st.session_state.username)

    start_time = datetime.now()
    connection = sqlite3.connect(db_path)
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


def login():
    """Login functionality"""
    st.title("SQL Query Executor - Login")

    username = st.text_input("Email Address", placeholder="user@company.com")

    if st.button("Login"):
        if username and '@' in username:
            # Simple email validation
            st.session_state.logged_in = True
            st.session_state.username = username
            # Reset query input and history
            st.session_state.query_input = ""
            st.session_state.query_history = []
            # Use st.rerun() instead of experimental_rerun()
            st.rerun()
        else:
            st.error("Please enter a valid email address")


def logout():
    """Logout functionality"""
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.query_history = []
    st.session_state.query_input = ""
    # Use st.rerun() instead of experimental_rerun()
    st.rerun()


# Initialize session state
init_session_state()


# Main app logic
def main():
    # Check if user is logged in
    if not st.session_state.logged_in:
        login()
        return

    # Streamlit UI
    st.title(f"SQLite Query Executor - {st.session_state.username}")

    # Logout button
    if st.button("Logout"):
        logout()
        return

    # Sidebar for history
    with st.sidebar:
        st.header("Query History")
        if st.button("Clear History"):
            st.session_state.query_history = []

        if st.session_state.query_history:
            for idx, item in enumerate(reversed(st.session_state.query_history[-5:])):  # Show last 5 queries
                with st.expander(f"Query {len(st.session_state.query_history) - idx}"):
                    st.text(f"Time: {item['timestamp']}")
                    st.text(f"Status: {item['status']}")
                    if st.button("Rerun", key=f"rerun_{idx}"):
                        st.session_state.query_input = item['query']
                    st.code(item['query'])
        else:
            st.info("No query history yet.")

    # Main area
    col1, col2 = st.columns([3, 1])
    with col1:
        # SQL query input
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
            # Store the current query in session state
            st.session_state.query_input = user_query

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

        ### Multi-User Features:
        - Each user has a separate SQLite database
        - Databases are stored securely and uniquely
        - Query history is user-specific
        """)


# Run the main app
if __name__ == "__main__":
    main()