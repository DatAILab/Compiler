from supabase import create_client, Client
import streamlit as st
import re
import pandas as pd

# Initialize Supabase client
url = "https://tjgmipyirpzarhhmihxf.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRqZ21pcHlpcnB6YXJoaG1paHhmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzE2NzQ2MDEsImV4cCI6MjA0NzI1MDYwMX0.LNMUqA0-t6YtUKP6oOTXgVGYLu8Tpq9rMhH388SX4bI"
supabase: Client = create_client(url, key)

# Page configuration
st.set_page_config(page_title="Data AI Lab - SQL Query Editor", page_icon=":computer:", layout="wide")

# Enhanced Custom CSS for Professional Design
st.markdown("""
    <style>
        .stApp { 
            background-color: #f4f6f9; 
            font-family: 'Inter', 'Segoe UI', Roboto, sans-serif;
        }
        .stTextArea textarea { 
            background-color: white; 
            border: 2px solid #3498db; 
            border-radius: 8px; 
            font-family: 'Fira Code', 'Courier New', monospace;
        }
        .stButton>button {
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 6px;
            transition: all 0.3s ease;
            font-weight: 600;
        }
        .stButton>button:hover {
            background-color: #2980b9;
            transform: translateY(-2px);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .sql-editor {
            font-family: 'Fira Code', 'Courier New', monospace;
            background-color: #ffffff;
            border: 1px solid #e0e4e8;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            white-space: pre-wrap;
            line-height: 1.6;
        }
        .sql-keyword {
            color: #2980b9;
            font-weight: 600;
        }
    </style>
""", unsafe_allow_html=True)

# Title with gradient effect
st.markdown(
    '<h1 style="text-align: center; color: #2c3e50; background: linear-gradient(90deg, #3498db, #2980b9); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Data AI Lab - SQL Query Editor</h1>',
    unsafe_allow_html=True)


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


def main():
    # Session state for queries
    if 'submitted_queries' not in st.session_state:
        st.session_state.submitted_queries = []

    # Query input
    query = st.text_area(
        "Enter your SQL Query:",
        height=200,
        help="Example queries: 'SELECT * FROM Car' or 'SELECT name FROM Car WHERE condition'"
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
                response = supabase.table('Car').select('*').execute()

                if response.data:
                    st.success("Query executed successfully!")
                    st.dataframe(response.data)
                else:
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
            <div style="background-color: white; border: 1px solid #e0e4e8; 
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