from supabase import create_client, Client
import streamlit as st
import re

# Initialize Supabase client
url = "https://tjgmipyirpzarhhmihxf.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRqZ21pcHlpcnB6YXJoaG1paHhmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzE2NzQ2MDEsImV4cCI6MjA0NzI1MDYwMX0.LNMUqA0-t6YtUKP6oOTXgVGYLu8Tpq9rMhH388SX4bI"
supabase: Client = create_client(url, key)

# Enhanced Custom CSS and JavaScript for Instant Highlighting
st.markdown("""
    <style>
        .sql-editor {
            font-family: 'Fira Code', monospace;
            background-color: #f0f3f6;
            border: 1px solid #e0e4e8;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            white-space: pre-wrap;
            line-height: 1.6;
        }
    </style>
    <script>
        function highlightSQLKeywords() {
            const keywords = [
                'SELECT', 'FROM', 'WHERE', 'INSERT', 'UPDATE', 'DELETE', 
                'CREATE', 'DROP', 'TABLE', 'INTO', 'VALUES', 'AND', 'OR', 
                'NOT', 'NULL', 'AS', 'JOIN', 'LEFT', 'RIGHT', 'INNER', 
                'OUTER', 'GROUP BY', 'ORDER BY', 'HAVING', 'LIMIT', 
                'OFFSET', 'UNION', 'ALL', 'PROCEDURE', 'FUNCTION', 
                'RETURNS', 'RETURN', 'BEGIN', 'END', 'DECLARE', 'SET', 
                'IF', 'ELSE', 'WHILE', 'LANGUAGE', 'PLPGSQL', 'CALL'
            ];

            const input = document.getElementById('sql-input');
            const outputDiv = document.getElementById('sql-highlight');

            if (!input || !outputDiv) return;

            let text = input.value;

            // Escape HTML to prevent XSS
            text = text.replace(/&/g, '&amp;')
                       .replace(/</g, '&lt;')
                       .replace(/>/g, '&gt;');

            // Highlight keywords
            keywords.forEach(keyword => {
                const regex = new RegExp('\\b(' + keyword + ')\\b', 'gi');
                text = text.replace(regex, '<span style="color: #9c27b0; font-weight: bold;">$1</span>');
            });

            outputDiv.innerHTML = text;
        }

        // Add event listener after page load
        document.addEventListener('DOMContentLoaded', () => {
            const input = document.getElementById('sql-input');
            if (input) {
                input.addEventListener('input', highlightSQLKeywords);
            }
        });
    </script>
""", unsafe_allow_html=True)

# Streamlit application layout
st.markdown('<h1 class="title">Data AI Lab - Éditeur de requêtes SQL</h1>', unsafe_allow_html=True)

# Session state to store submitted queries
if 'submitted_queries' not in st.session_state:
    st.session_state.submitted_queries = []

# Create a container for the SQL input
st.markdown("""
    <div>
        <input 
            type="text" 
            id="sql-input" 
            placeholder="Entrez votre requête SQL" 
            style="width: 100%; padding: 10px; margin-bottom: 10px;"
        >
        <div id="sql-highlight" class="sql-editor" style="min-height: 50px;"></div>
    </div>
""", unsafe_allow_html=True)

# Hidden Streamlit input to capture the query
query = st.text_input("Hidden SQL Query Input", label_visibility="hidden", key="hidden_query")

# Columns for buttons with improved spacing
col1, col2 = st.columns([1, 1])

with col1:
    try_query = st.button("Testez la requête", help="Exécutez la requête pour voir les résultats")

with col2:
    submit_query = st.button("Soumettre la requête", help="Sauvegarder la requête pour révision")


def is_safe_query(query: str) -> tuple[bool, str]:
    """
    Validate if the query is safe to execute.
    Returns a tuple of (is_safe, message).
    """
    query_upper = query.strip().upper()
    if re.search(r'\bDROP\b', query_upper):
        return False, "Les requêtes DROP ne sont pas autorisées pour des raisons de sécurité."
    return True, "La requête est sécurisée"


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
                st.success("La requête a été exécutée avec succès !")
                st.table(response.data)
            else:
                st.success("La requête a été exécutée avec succès.")

        except Exception as e:
            st.error(f"Erreur : {str(e)}")
            st.write("Détails de la requête :")
            st.write(f"Tentative de requête : {query}")

# Submit Query functionality
if submit_query and query:
    is_safe, message = is_safe_query(query)
    if not is_safe:
        st.error(message)
    else:
        try:
            st.session_state.submitted_queries.append(query)
            st.success(f"La requête '{query}' a été envoyée !")

        except Exception as e:
            st.error(f"Erreur dans l'envoi de la requête : {str(e)}")

# Display submitted queries
if st.session_state.submitted_queries:
    st.markdown("### Requêtes envoyées")
    for idx, submitted_query in enumerate(st.session_state.submitted_queries, 1):
        st.markdown(f"""
            <div style="margin-bottom: 10px; padding: 10px; background-color: #f8f9fa; border-radius: 6px;">
                {idx}. <div class="sql-editor">
                    {submitted_query}
                </div>
            </div>
        """, unsafe_allow_html=True)

# Optional: Clear submitted queries
if st.button("Effacer les requêtes soumises"):
    st.session_state.submitted_queries = []
    st.rerun()

st.markdown('<div class="footer">Data AI Lab © 2024</div>', unsafe_allow_html=True)