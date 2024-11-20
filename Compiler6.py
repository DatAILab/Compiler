import streamlit as st
import sqlite3
import re
import pandas as pd


def init_database():
    """Initialize SQLite database with sample data"""
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()

    # Create sample tables
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            age INTEGER
        )
    ''')

    cursor.execute('''
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            product TEXT,
            amount REAL
        )
    ''')

    # Insert sample data
    users_data = [
        (1, 'John Doe', 'john@example.com', 30),
        (2, 'Jane Smith', 'jane@example.com', 25),
        (3, 'Bob Johnson', 'bob@example.com', 45)
    ]

    orders_data = [
        (1, 1, 'Laptop', 1200.50),
        (2, 1, 'Mouse', 50.00),
        (3, 2, 'Keyboard', 100.00),
        (4, 3, 'Monitor', 300.75)
    ]

    cursor.executemany('INSERT INTO users VALUES (?,?,?,?)', users_data)
    cursor.executemany('INSERT INTO orders VALUES (?,?,?,?)', orders_data)

    conn.commit()
    return conn


def is_safe_query(query: str) -> tuple[bool, str]:
    """
    Validate if the query is safe to execute.
    """
    query_upper = query.strip().upper()

    # Enhanced security checks
    unsafe_keywords = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE', 'GRANT', 'REVOKE']
    for keyword in unsafe_keywords:
        if re.search(fr'\b{keyword}\b', query_upper):
            return False, f"Les requêtes {keyword} ne sont pas autorisées pour des raisons de sécurité."

    return True, "La requête est sécurisée"


def highlight_sql(query: str) -> str:
    """
    Highlight SQL keywords in the query
    """
    sql_keywords = [
        'SELECT', 'FROM', 'WHERE', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'TABLE',
        'INTO', 'VALUES', 'AND', 'OR', 'NOT', 'NULL', 'AS', 'JOIN', 'LEFT', 'RIGHT', 'INNER'
    ]

    highlighted_query = query
    for keyword in sql_keywords:
        pattern = r'\b' + re.escape(keyword) + r'\b'
        highlighted_query = re.sub(
            pattern,
            f'<span style="color: #2980b9; font-weight: bold;">{keyword}</span>',
            highlighted_query,
            flags=re.IGNORECASE
        )

    return highlighted_query


def execute_query(conn, query):
    """
    Execute SQL query and return results
    """
    try:
        return pd.read_sql_query(query, conn)
    except Exception as e:
        st.error(f"Query execution error: {e}")
        return None


def main():
    # Page configuration
    st.set_page_config(page_title="SQL Query Editor", page_icon=":computer:", layout="wide")

    # Custom CSS
    st.markdown("""
    <style>
        .stApp { background-color: #f0f2f6; }
        .stTextArea textarea { 
            background-color: white; 
            border: 2px solid #3498db; 
            border-radius: 8px; 
        }
        .stButton>button {
            background-color: #3498db;
            color: white;
            border-radius: 6px;
        }
        .stButton>button:hover {
            background-color: #2980b9;
        }
    </style>
    """, unsafe_allow_html=True)

    # Title
    st.title("🖥️ Data AI Lab - SQL Query Editor")

    # Initialize database
    conn = init_database()

    # Session state for queries
    if 'submitted_queries' not in st.session_state:
        st.session_state.submitted_queries = []

    # Example schemas
    with st.expander("Database Schema"):
        st.markdown("""
        ### Users Table
        - id (INTEGER)
        - name (TEXT)
        - email (TEXT)
        - age (INTEGER)

        ### Orders Table
        - id (INTEGER)
        - user_id (INTEGER)
        - product (TEXT)
        - amount (REAL)
        """)

    # Query input
    query = st.text_area(
        "Enter your SQL Query:",
        height=200,
        help="Example queries: 'SELECT * FROM users' or 'SELECT name, age FROM users WHERE age > 25'"
    )

    # Columns for buttons
    col1, col2 = st.columns(2)

    with col1:
        test_query = st.button("Test Query")

    with col2:
        submit_query = st.button("Submit Query")

    # Test Query functionality
    if test_query and query:
        is_safe, message = is_safe_query(query)

        if not is_safe:
            st.error(message)
        else:
            try:
                results = execute_query(conn, query)

                if results is not None and not results.empty:
                    st.success("Query executed successfully!")
                    st.dataframe(results)
                elif results is not None:
                    st.info("Query executed, but returned no results.")

            except Exception as e:
                st.error(f"Error executing query: {e}")

    # Submit Query functionality
    if submit_query and query:
        is_safe, message = is_safe_query(query)

        if not is_safe:
            st.error(message)
        else:
            st.session_state.submitted_queries.append(query)
            st.success("Query submitted successfully!")

    # Display submitted queries
    if st.session_state.submitted_queries:
        st.subheader("Submitted Queries")
        for idx, submitted_query in enumerate(st.session_state.submitted_queries, 1):
            st.markdown(f"""
            <div style="background-color: white; border: 1px solid #e0e0e0; 
                        border-radius: 8px; padding: 10px; margin-bottom: 10px;">
                {idx}. {highlight_sql(submitted_query)}
            </div>
            """, unsafe_allow_html=True)

    # Clear queries button
    if st.button("Clear Submitted Queries"):
        st.session_state.submitted_queries = []
        st.experimental_rerun()


if __name__ == "__main__":
    main()