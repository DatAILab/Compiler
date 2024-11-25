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
            line-height: 1.6;
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



# Function to normalize and compare two SELECT queries
def compare_select_queries(query1: str, query2: str) -> bool:
    # Normalize queries: remove whitespaces, convert to lowercase
    def normalize_query(query: str) -> str:
        normalized = query.lower()
        normalized = re.sub(r'\s+', '', normalized)
        normalized = normalized.rstrip(';').strip()
        return normalized

    # Normalize both queries
    normalized_query1 = normalize_query(query1)
    normalized_query2 = normalize_query(query2)

    # Compare normalized queries
    return normalized_query1 == normalized_query2

# Function to execute and compare outputs of two SELECT queries using Supabase
def execute_and_compare(query1: str, query2: str) -> bool:
    try:
        # Execute the first query
        response1 = supabase.rpc("execute_returning_sql", {"query_text": query1}).execute()
        result1 = response1.data if hasattr(response1, 'data') else []

        # Execute the second query
        response2 = supabase.rpc("execute_returning_sql", {"query_text": query2}).execute()
        result2 = response2.data if hasattr(response2, 'data') else []

        # Compare the outputs (assuming both are lists of dicts)
        return result1 == result2

    except Exception as e:
        st.error(f"Error executing queries: {str(e)}")
        return False

# Function to determine if a query is SELECT or CREATE VIEW
def is_select_or_create_view(query: str) -> str:
    query_upper = query.strip().upper()
    if query_upper.startswith("SELECT"):
        return "SELECT"
    elif query_upper.startswith("CREATE VIEW"):
        return "CREATE VIEW"
    return "OTHER"

# Streamlit application layout
st.markdown('<h1 class="title">Data AI Lab - Éditeur de requêtes SQL</h1>', unsafe_allow_html=True)

# Placeholder for fetching questions (you can implement your logic here)
def fetch_questions():
    return ["Question 1", "Question 2", "Question 3"]  # Replace with actual fetching logic

# Fetch questions at the start
questions = fetch_questions()

# Dropdown for selecting questions
selected_question = st.selectbox(
    "Sélectionnez une question :",
    ["Choisissez une question"] + questions
)

# Text area for SQL queries
query = st.text_area("Entrez votre requête SQL :", height=200, key="sql_input",
                     help="Écrivez votre requête SQL ici. Soyez attentif aux opérations sensibles.")

# Example second query for comparison (this could be fetched from a database or user input)
second_query = st.text_area("Entrez la deuxième requête SQL pour comparaison :", height=200, key="sql_input_comparison",
                             help="Entrez une autre requête SQL à comparer avec la première.")

# Check if query is SELECT or CREATE VIEW and apply logic accordingly
query_type = is_select_or_create_view(query)
if query_type == "SELECT":
    if compare_select_queries(query, second_query):
        st.success("Les requêtes SELECT sont structurellement identiques!")
    else:
        if execute_and_compare(query, second_query):
            st.success("Les sorties des requêtes SELECT sont identiques!")
        else:
            st.error("Les sorties des requêtes SELECT sont différentes.")
elif query_type == "CREATE VIEW":
    st.info("Les requêtes CREATE VIEW ne sont pas modifiées ou comparées.")
else:
    st.warning("Les requêtes qui ne sont ni SELECT ni CREATE VIEW ne sont pas traitées.")

# The rest of the code continues unchanged


# Streamlit application layout
st.markdown('<h1 class="title">Data AI Lab - Éditeur de requêtes SQL</h1>', unsafe_allow_html=True)

# Session state to store submitted queries
if 'submitted_queries' not in st.session_state:
    st.session_state.submitted_queries = []

# Fetch questions at the start
questions = fetch_questions()

# Dropdown for selecting questions
selected_question = st.selectbox(
    "Sélectionnez une question :",
    ["Choisissez une question"] + questions
)

# Text area for SQL queries with syntax highlighting
query = st.text_area("Entrez votre requête SQL :", height=200, key="sql_input",
                     help="Écrivez votre requête SQL ici. Soyez attentif aux opérations sensibles.")

# Display highlighted version of the query
if query:
    st.markdown(f"""
        <div class="sql-editor">
            {highlight_sql(query)}
        </div>
    """, unsafe_allow_html=True)

# Try Query functionality
if st.button("Testez la requête", help="Exécutez la requête pour voir les résultats"):
    # Check if a question is selected
    if selected_question == "Choisissez une question":
        st.warning("Veuillez sélectionner une question.")
    else:
        # Check if query is correct
        if is_query_correct(query, selected_question):
            st.success("Requête correcte !")
        else:
            st.error("La requête ne correspond pas à la solution attendue.")

        # Execute the query
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
                    st.table(response.data)

            except Exception as e:
                st.error(f"Erreur : {str(e)}")

# Submit Query functionality
if st.button("Soumettre la requête", help="Sauvegarder la requête pour révision"):
    is_safe, message = is_safe_query(query)
    if not is_safe:
        st.error(message)
    else:
        try:
            st.session_state.submitted_queries.append(query)
            st.success(f"La requête '{query}' a été envoyée !")

        except Exception as e:
            st.error(f"Erreur dans l'envoi de la requête : {str(e)}")

# Display submitted queries with syntax highlighting
if st.session_state.submitted_queries:
    st.markdown("### Requêtes envoyées")
    for idx, submitted_query in enumerate(st.session_state.submitted_queries, 1):
        st.markdown(f"""
            <div class="submitted-query">
                {idx}. <div class="sql-editor">
                    {highlight_sql(submitted_query)}
                </div>
            </div>
        """, unsafe_allow_html=True)

# Optional: Clear submitted queries
if st.button("Éffacer les requêtes soumises"):
    st.session_state.submitted_queries = []
    st.rerun()

st.markdown('<div class="footer">Data AI Lab © 2024</div>', unsafe_allow_html=True)