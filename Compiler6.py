import streamlit as st
import re
import os
from supabase import create_client, Client


def init_supabase():
    """
    Initialize Supabase client using environment variables
    """
    try:
        url = st.secrets.get("SUPABASE_URL")
        key = st.secrets.get("SUPABASE_KEY")

        if not url or not key:
            st.error("Supabase credentials not configured.")
            return None

        return create_client(url, key)
    except Exception as e:
        st.error(f"Error initializing Supabase: {e}")
        return None


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
    # Custom Page Config
    st.set_page_config(
        page_title="SQL Query Editor",
        page_icon=":computer:",
        layout="wide"
    )

    # Add custom CSS
    st.markdown("""
    <style>
        .stApp {
            background-color: #f0f2f6;
        }
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

    # Initialize Supabase
    supabase = init_supabase()
    if supabase is None:
        return

    # Session state for queries
    if 'submitted_queries' not in st.session_state:
        st.session_state.submitted_queries = []

    # Query input
    query = st.text_area(
        "Enter your SQL Query:",
        height=200,
        help="Write your SQL query carefully"
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
                # Placeholder for actual query execution
                st.warning("Query testing is disabled in this demo version.")
                # Uncomment and modify the following when you have actual database connection
                # if query.strip().upper().startswith("SELECT"):
                #     response = supabase.rpc("execute_returning_sql", {"query_text": query}).execute()
                # else:
                #     response = supabase.rpc("execute_non_returning_sql", {"query_text": query}).execute()

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