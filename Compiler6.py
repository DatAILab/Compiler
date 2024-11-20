from supabase import create_client, Client
import streamlit as st
import re

# Initialize Supabase client
url = "https://tjgmipyirpzarhhmihxf.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRqZ21pcHlpcnB6YXJoaG1paHhmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzE2NzQ2MDEsImV4cCI6MjA0NzI1MDYwMX0.LNMUqA0-t6YtUKP6oOTXgVGYLu8Tpq9rMhH388SX4bI"
supabase: Client = create_client(url, key)

# Custom CSS for SQL syntax highlighting
st.markdown("""
    <style>
        .sql-editor {
            font-family: 'Courier New', Courier, monospace;
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
        }
        .stTextArea textarea {
            font-family: 'Courier New', Courier, monospace !important;
            line-height: 1.5 !important;
        }
        .sql-keyword {
            color: #0066cc;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)


def is_safe_query(query: str) -> tuple[bool, str]:
    """
    Validate if the query is safe to execute.
    Returns a tuple of (is_safe, message).
    """
    # Convert to uppercase for consistent checking
    query_upper = query.strip().upper()

    # Check for DROP statements
    if re.search(r'\bDROP\b', query_upper):
        return False, "DROP queries are not allowed for security reasons."

    return True, "Query is safe"


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
st.title("SQL Query Editor")

# Session state to store submitted queries
if 'submitted_queries' not in st.session_state:
    st.session_state.submitted_queries = []

# Text area for SQL queries with syntax highlighting
query = st.text_area("Enter your SQL query:", height=400, key="sql_input")

# Display highlighted version of the query
if query:
    st.markdown(f"""
        <div class="sql-editor">
            {highlight_sql(query)}
        </div>
    """, unsafe_allow_html=True)

# Columns for buttons
col1, col2 = st.columns(2)

with col1:
    try_query = st.button("Try Query")

with col2:
    submit_query = st.button("Submit Query")

# Try Query functionality
if try_query and query:
    # Validate query before execution
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
                st.write("Query Results:")
                st.table(response.data)
            else:
                st.success("Query executed successfully.")

        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.write("Debug info:")
            st.write(f"Query attempted: {query}")

# Submit Query functionality
if submit_query and query:
    # Validate query before submission
    is_safe, message = is_safe_query(query)

    if not is_safe:
        st.error(message)
    else:
        try:
            # Add query to submitted queries list
            st.session_state.submitted_queries.append(query)
            st.success(f"Query '{query}' has been submitted!")

        except Exception as e:
            st.error(f"Error submitting query: {str(e)}")

# Display submitted queries with syntax highlighting
if st.session_state.submitted_queries:
    st.write("### Submitted Queries:")
    for idx, submitted_query in enumerate(st.session_state.submitted_queries, 1):
        st.markdown(f"""
            {idx}. <div class="sql-editor">
                {highlight_sql(submitted_query)}
            </div>
        """, unsafe_allow_html=True)

# Optional: Clear submitted queries
if st.button("Clear Submitted Queries"):
    st.session_state.submitted_queries = []