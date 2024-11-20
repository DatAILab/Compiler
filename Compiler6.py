from supabase import create_client, Client
import streamlit as st
import re
import streamlit.components.v1 as components

# Initialize Supabase client
url = "https://tjgmipyirpzarhhmihxf.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRqZ21pcHlpcnB6YXJoaG1paHhmIiwicm9zZSI6ImFub24iLCJpYXQiOjE3MzE2NzQ2MDEsImV4cCI6MjA0NzI1MDYwMX0.LNMUqA0-t6YtUKP6oOTXgVGYLu8Tpq9rMhH388SX4bI"
supabase: Client = create_client(url, key)

# HTML and JavaScript for CodeMirror
code_mirror_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>SQL Editor</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.5/codemirror.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.5/codemirror.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.5/mode/sql/sql.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.5/addon/hint/show-hint.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.5/addon/hint/show-hint.min.css">
    <style>
        .CodeMirror {
            border: 1px solid #eee;
            height: auto;
        }
    </style>
</head>
<body>
    <textarea id="code" name="code"></textarea>
    <script>
        var editor = CodeMirror.fromTextArea(document.getElementById("code"), {
            mode: "text/x-sql",
            lineNumbers: true,
            extraKeys: {"Ctrl-Space": "autocomplete"},
            hintOptions: {tables: {
                users: ["name", "score", "birthDate"],
                countries: ["name", "population", "size"]
            }}
        });
        editor.on("change", function() {
            const code = editor.getValue();
            const event = new CustomEvent("codeChange", { detail: code });
            window.dispatchEvent(event);
        });
    </script>
</body>
</html>
"""

def is_safe_query(query: str) -> tuple[bool, str]:
    """
    Validate if the query is safe to execute.
    Returns a tuple of (is_safe, message).
    """
    query_upper = query.strip().upper()
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
st.title("SQL Query Editor with Syntax Highlighting")

# Create a Streamlit component for CodeMirror
component_value = components.html(code_mirror_html, height=300, width=700, scrolling=False)

# Session state to store submitted queries
if 'submitted_queries' not in st.session_state:
    st.session_state.submitted_queries = []

# Display the current SQL query
st.write("Current SQL Query:")
if component_value:
    st.code(component_value, language='sql')

# Columns for buttons
col1, col2 = st.columns(2)

with col1:
    try_query = st.button("Try Query")

with col2:
    submit_query = st.button("Submit Query")

# Try Query functionality
if try_query and component_value:
    is_safe, message = is_safe_query(component_value)
    if not is_safe:
        st.error(message)
    else:
        try:
            if component_value.strip().upper().startswith("SELECT"):
                response = supabase.rpc("execute_returning_sql", {"query_text": component_value}).execute()
            else:
                response = supabase.rpc("execute_non_returning_sql", {"query_text": component_value}).execute()

            if hasattr(response, 'data') and response.data:
                st.write("Query Results:")
                st.table(response.data)
            else:
                st.success("Query executed successfully.")

        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.write("Debug info:")
            st.write(f"Query attempted: {component_value}")

# Submit Query functionality
if submit_query and component_value:
    is_safe, message = is_safe_query(component_value)
    if not is_safe:
        st.error(message)
    else:
        try:
            st.session_state.submitted_queries.append(component_value)
            st.success(f"Query '{component_value}' has been submitted!")

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