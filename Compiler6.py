from supabase import create_client, Client
import streamlit as st
import re
import json

# Initialize Supabase client
url = "https://tjgmipyirpzarhhmihxf.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRqZ21pcHlpcnB6YXJoaG1paHhmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzE2NzQ2MDEsImV4cCI6MjA0NzI1MDYwMX0.LNMUqA0-t6YtUKP6oOTXgVGYLu8Tpq9rMhH388SX4bI"
supabase: Client = create_client(url, key)

# SQL Keywords for autocomplete
SQL_KEYWORDS = [
    'SELECT', 'FROM', 'WHERE', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'TABLE',
    'INTO', 'VALUES', 'AND', 'OR', 'NOT', 'NULL', 'AS', 'JOIN', 'LEFT', 'RIGHT', 'INNER',
    'OUTER', 'GROUP BY', 'ORDER BY', 'HAVING', 'LIMIT', 'OFFSET', 'UNION', 'ALL'
]

# Enhanced CSS for real-time highlighting and autocomplete
st.markdown("""
    <style>
        /* SQL Editor Styling */
        .sql-editor {
            font-family: 'Courier New', Courier, monospace;
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
            position: relative;
        }
        .stTextArea textarea {
            font-family: 'Courier New', Courier, monospace !important;
            line-height: 1.5 !important;
            padding: 10px !important;
            background-color: transparent !important;
            color: #000000 !important;
        }
        .sql-keyword {
            color: #0066cc;
            font-weight: bold;
        }
        .suggestion-box {
            position: absolute;
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 4px;
            max-height: 200px;
            overflow-y: auto;
            z-index: 1000;
        }
        .suggestion-item {
            padding: 5px 10px;
            cursor: pointer;
        }
        .suggestion-item:hover {
            background-color: #f0f0f0;
        }
        /* Real-time highlighting */
        .highlight-overlay {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            pointer-events: none;
            padding: 10px;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
    </style>
""", unsafe_allow_html=True)


def highlight_sql(query: str) -> str:
    """Enhanced SQL syntax highlighting with real-time updates"""
    highlighted = query
    for keyword in SQL_KEYWORDS:
        pattern = r'\b' + re.escape(keyword) + r'\b'
        highlighted = re.sub(
            pattern,
            f'<span class="sql-keyword">{keyword}</span>',
            highlighted,
            flags=re.IGNORECASE
        )
    return highlighted


def get_suggestions(partial_word: str) -> list:
    """Get keyword suggestions based on partial input"""
    if not partial_word:
        return []
    return [kw for kw in SQL_KEYWORDS if kw.lower().startswith(partial_word.lower())]


# Initialize session state
if 'query' not in st.session_state:
    st.session_state.query = ""
if 'cursor_pos' not in st.session_state:
    st.session_state.cursor_pos = 0

# Main application
st.title("Enhanced SQL Query Editor")

# Create columns for the editor and suggestions
col1, col2 = st.columns([3, 1])

with col1:
    # Query input with real-time highlighting
    query = st.text_area(
        "Enter your SQL query:",
        value=st.session_state.query,
        height=400,
        key="sql_input",
        on_change=lambda: None  # This triggers rerun on each keystroke
    )

    # Display highlighted version
    if query:
        st.markdown(f"""
            <div class="sql-editor">
                {highlight_sql(query)}
            </div>
        """, unsafe_allow_html=True)

with col2:
    # Keyword suggestions
    st.markdown("### SQL Keywords")
    if query:
        # Get the word under cursor
        words = query.split()
        if words:
            last_word = words[-1].strip()
            suggestions = get_suggestions(last_word)

            for suggestion in suggestions[:10]:  # Limit to 10 suggestions
                if st.button(suggestion, key=f"suggest_{suggestion}"):
                    # Insert the suggestion at cursor position
                    if st.session_state.query:
                        words[-1] = suggestion
                        st.session_state.query = " ".join(words) + " "
                    else:
                        st.session_state.query = suggestion + " "
                    st.experimental_rerun()

# Execute query buttons
col1, col2 = st.columns(2)

with col1:
    if st.button("Try Query"):
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

with col2:
    if st.button("Submit Query"):
        if not hasattr(st.session_state, 'submitted_queries'):
            st.session_state.submitted_queries = []
        st.session_state.submitted_queries.append(query)
        st.success("Query submitted successfully!")

# Display submitted queries
if hasattr(st.session_state, 'submitted_queries') and st.session_state.submitted_queries:
    st.write("### Submitted Queries:")
    for idx, submitted_query in enumerate(st.session_state.submitted_queries, 1):
        st.markdown(f"""
            {idx}. <div class="sql-editor">
                {highlight_sql(submitted_query)}
            </div>
        """, unsafe_allow_html=True)

# Clear submitted queries button
if st.button("Clear Submitted Queries"):
    st.session_state.submitted_queries = []