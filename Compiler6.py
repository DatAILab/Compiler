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
            white-space: pre-wrap; /* Preserve whitespace */
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
st.title("Editeur de requêtes SQL de Data AI Lab")

# Session state to store submitted queries
if 'submitted_queries' not in st.session_state:
    st.session_state.submitted_queries = []

# Text area for SQL queries with syntax highlighting
query = st.text_area("Entrez votre requête SQL :", height=200, key="sql_input")

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
    try_query = st.button("Essayez la requête")

with col2:
    submit_query = st.button("Soumettre la requête")

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
                st.write("Query Results:")
                st.table(response.data)
            else:
                st.success("La requête a été exécutée avec succès.")

        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.write("Debug info:")
            st.write(f"Query attempted: {query}")

# Submit Query functionality
if submit_query and query:
    is_safe, message = is_safe_query(query)
    if not is_safe:
        st.error(message)
    else:
        try:
            st.session_state.submitted_queries.append(query)
            st.success(f"Requête '{query}' a été envoyée!")

        except Exception as e:
            st.error(f"Erreur dans l'envoi de la requête : {str(e)}")

# Display submitted queries with syntax highlighting
if st.session_state.submitted_queries:
    st.write("### Requêtes envoyées:")
    for idx, submitted_query in enumerate(st.session_state.submitted_queries, 1):
        st.markdown(f"""
            {idx}. <div class="sql-editor">
                {highlight_sql(submitted_query)}
            </div>
        """, unsafe_allow_html=True)

# Optional: Clear submitted queries
if st.button("Effacer les requêtes envoyées"):
    st.session_state.submitted_queries = []