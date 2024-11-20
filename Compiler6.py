from supabase import create_client, Client
import streamlit as st
import re

# Initialize Supabase client
url = "https://tjgmipyirpzarhhmihxf.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRqZ21pcHlpcnB6YXJoaG1paHhmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzE2NzQ2MDEsImV4cCI6MjA0NzI1MDYwMX0.LNMUqA0-t6YtUKP6oOTXgVGYLu8Tpq9rMhH388SX4bI"
supabase: Client = create_client(url, key)

# Enhanced Custom CSS for Professional Design
st.markdown("""
    <style>
        /* Global Styling */
        .stApp {
            background-color: #f4f6f9;
            font-family: 'Inter', 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
        }

        /* Title Styling */
        .title {
            color: #2c3e50;
            text-align: center;
            font-weight: 700;
            margin-bottom: 20px;
            background: linear-gradient(90deg, #3498db, #2980b9);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        /* SQL Editor Styling */
        .sql-editor {
            font-family: 'Fira Code', 'Courier New', monospace;
            background-color: #ffffff;
            border: 1px solid #e0e4e8;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            white-space: pre-wrap;
        }

        /* SQL Keyword Highlighting */
        .sql-keyword {
            color: #2980b9;
            font-weight: 600;
        }

        /* Button Styling */
        .stButton>button {
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 6px;
            transition: all 0.3s ease;
            font-weight: 600;
            padding: 10px 20px;
        }

        .stButton>button:hover {
            background-color: #2980b9;
            transform: translateY(-2px);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        /* Submitted Queries Styling */
        .submitted-query {
            margin-bottom: 10px;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 6px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        /* Improved Navigation Bar */
        .navbar {
            background-color: #2c3e50;
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 20px;
        }

        .navbar a {
            color: #ecf0f1;
            text-decoration: none;
            font-weight: 600;
            margin-right: 15px;
        }

        .navbar a:hover {
            color: #3498db;
        }

        /* Footer Styling */
        .footer {
            text-align: center;
            font-size: 12px;
            color: #95a5a6;
            margin-top: 20px;
        }
    </style>
""", unsafe_allow_html=True)


def is_safe_query(query: str) -> tuple[bool, str]:
    """
    Validate if the query is safe to execute.
    Returns a tuple of (is_safe, message).
    """
    query_upper = query.strip().upper()
    if re.search(r'\bDROP\b', query_upper):
        return False, "Les requêtes DROP ne sont pas autorisées pour des raisons de sécurité."
    return True, "La requête est sécurisée"


def highlight_sql(query: str) -> str:
    """
    Highlight SQL keywords in the query
    """
    sql_keywords = [
        'SELECT', 'FROM', 'WHERE', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'TABLE',
        'INTO', 'VALUES', 'AND', 'OR', 'NOT', 'NULL', 'AS', 'JOIN', 'LEFT', 'RIGHT', 'INNER',
        'OUTER', 'GROUP BY', 'ORDER BY', 'HAVING', 'LIMIT', 'OFFSET', 'UNION', 'ALL',
        'PROCEDURE', 'FUNCTION', 'RETURNS', 'RETURN', 'BEGIN', 'END', 'DECLARE', 'SET',
        'IF', 'ELSE', 'WHILE', 'LANGUAGE', 'PLPGSQL', 'CALL'
    ]

    highlighted_query = query
    for keyword in sql_keywords:
        pattern = r'\b' + re.escape(keyword) + r'\b'
        highlighted_query = re.sub(
            pattern,
            f'<span class="sql-keyword">{keyword}</span>',
            highlighted_query,
            flags=re.IGNORECASE
        )

    return highlighted_query


# Streamlit application layout
st.markdown('<div class="navbar"><a href="#home">Home</a><a href="#features">Features</a><a href="#about">About</a></div>', unsafe_allow_html=True)
st.markdown('<h1 class="title">Data AI Lab - SQL Query Editor</h1>', unsafe_allow_html=True)

# Session state to store submitted queries
if 'submitted_queries' not in st.session_state:
    st.session_state.submitted_queries = []

# Text area for SQL queries with syntax highlighting
query = st.text_area("Enter your SQL Query:", height=200, key="sql_input",
                     help="Write your SQL query here. Be careful with sensitive operations.")

# Display highlighted version of the query
if query:
    st.markdown(f"""
        <div class="sql-editor">
            {highlight_sql(query)}
        </div>
    """, unsafe_allow_html=True)

# Columns for buttons with improved spacing
col1, col2 = st.columns([1, 1])

with col1:
    try_query = st.button("Test Query", help="Execute the query to see results")

with col2:
    submit_query = st.button("Submit Query", help="Save the query for review")

# Try Query functionality
if try_query and query:
    is_safe, message = is_safe_query(query)
    if not is_safe:
        st.error(message)
    else:
        try:
            if query.strip().upper().startswith("SELECT"):
                response = supabase.rpc("execute_returning_sql", {"query_text": query}).execute()
            else:
                response = supabase.rpc("execute_non_returning_sql", {"query_text": query}).execute()

            if hasattr(response, 'data') and response.data:
                st.success("Query executed successfully!")
                st.table(response.data)
            else:
                st.success("Query executed successfully.")

        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.write("Query details:")
            st.write(f"Attempted query: {query}")

# Submit Query functionality
if submit_query and query:
    is_safe, message = is_safe_query(query)
    if not is_safe:
        st.error(message)
    else:
        try:
            st.session_state.submitted_queries.append(query)
            st.success(f"Query '{query}' has been submitted!")

        except Exception as e:
            st.error(f"Error submitting query: {str(e)}")

# Display submitted queries with syntax highlighting
if st.session_state.submitted_queries:
    st.markdown("### Submitted Queries")
    for idx, submitted_query in enumerate(st.session_state.submitted_queries, 1):
        st.markdown(f"""
            <div class="submitted-query">
                {idx}. <div class="sql-editor">
                    {highlight_sql(submitted_query)}
                </div>
            </div>
        """, unsafe_allow_html=True)

# Optional: Clear submitted queries
if st.button("Clear Submitted Queries"):
    st.session_state.submitted_queries = []
    st.experimental_rerun()

# Footer
st.markdown('<div class="footer">Data AI Lab © 2024</div>', unsafe_allow_html=True)
