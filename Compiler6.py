from supabase import create_client, Client
import streamlit as st
import re
import pandas as pd
from typing import Tuple, Union, List, Dict, Any

# Comprehensive list of SQL keywords and potential table/column names
SQL_KEYWORDS = [
    'SELECT', 'FROM', 'WHERE', 'AND', 'OR', 'NOT', 'INSERT', 'UPDATE', 'DELETE',
    'CREATE', 'DROP', 'TABLE', 'VIEW', 'JOIN', 'LEFT', 'RIGHT', 'INNER', 'OUTER',
    'GROUP BY', 'ORDER BY', 'HAVING', 'LIMIT', 'OFFSET', 'DISTINCT', 'AS',
    'COUNT', 'SUM', 'AVG', 'MIN', 'MAX'
]

# Initialize Supabase client
url = "https://tjgmipyirpzarhhmihxf.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRqZ21pcHlpcnB6YXJoaG1paHhmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzE2NzQ2MDEsImV4cCI6MjA0NzI1MDYwMX0.LNMUqA0-t6YtUKP6oOTXgVGYLu8Tpq9rMhH388SX4bI"
supabase: Client = create_client(url, key)


def fetch_questions():
    """
    Fetch questions from Supabase
    """
    try:
        response = supabase.table("questions").select("question").execute()
        if hasattr(response, 'data') and response.data:
            return [q['question'] for q in response.data]
        return []
    except Exception as e:
        st.error(f"Erreur lors de la récupération des questions : {str(e)}")
        return []


def get_table_and_column_names(supabase: Client):
    """
    Fetch table and column names from the database with fallback
    """
    tables = []
    columns = []
    try:
        # Fetch table names from questions table
        response = supabase.table("questions").select("question").execute()
        if hasattr(response, 'data'):
            # Extract potential table and column keywords from questions
            for item in response.data:
                words = item['question'].lower().split()
                tables.extend([word for word in words if word.isalnum()])

        # Add predefined tables and columns as fallback
        tables.extend(['users', 'products', 'orders', 'customers'])
        columns.extend([
            'id', 'name', 'email', 'price', 'quantity',
            'date', 'status', 'category', 'total'
        ])
    except Exception as e:
        st.error(f"Error fetching suggestions: {e}")

    return list(set(SQL_KEYWORDS + tables + columns))


def sql_autocomplete(query: str, supabase: Client):
    """
    Provide comprehensive autocomplete suggestions for SQL queries based on the first letter
    """
    # Get dynamic suggestions
    dynamic_suggestions = get_table_and_column_names(supabase)

    # Split the current query and get the last word
    words = query.split()
    last_word = words[-1] if words else ""

    # Comprehensive suggestion mapping
    comprehensive_suggestions = {
        's': ['select', 'sum', 'substring'],
        'f': ['from', 'first'],
        'w': ['where', 'with'],
        'a': ['and', 'avg', 'as'],
        'o': ['order by', 'or'],
        'g': ['group by'],
        'h': ['having'],
        'l': ['left join', 'limit', 'like'],
        'i': ['inner join', 'insert', 'is'],
        'j': ['join'],
        'u': ['update', 'union']
    }

    # Combine dynamic and predefined suggestions
    suggestions = []

    # If last word is empty or a single letter, use comprehensive suggestions
    if not last_word or len(last_word) == 1:
        first_letter = last_word.lower()
        suggestions = comprehensive_suggestions.get(first_letter, [])

    # Add dynamic suggestions that start with the last word
    suggestions.extend([
        sug for sug in dynamic_suggestions
        if sug.lower().startswith(last_word.lower())
    ])

    # Remove duplicates while preserving order
    suggestions = list(dict.fromkeys(suggestions))

    return suggestions


def compare_query_results(user_result: List[Dict], solution_result: List[Dict]) -> Tuple[bool, str]:
    """
    Compare two query results for equality, focusing on data content rather than structure.
    Returns (is_equal, message)
    """
    try:
        # Convert results to DataFrames
        df_user = pd.DataFrame(user_result)
        df_solution = pd.DataFrame(solution_result)

        # If either result is empty, check if both are empty
        if df_user.empty and df_solution.empty:
            return True, "Les résultats sont identiques (aucune donnée)"
        elif df_user.empty or df_solution.empty:
            return False, "Un résultat est vide alors que l'autre ne l'est pas"

        # Convert DataFrames to sets of tuples for value comparison
        user_values = set(tuple(x) for x in df_user.values.tolist())
        solution_values = set(tuple(x) for x in df_solution.values.tolist())

        if user_values == solution_values:
            return True, "Les résultats correspondent exactement!"
        else:
            missing = len(solution_values - user_values)
            extra = len(user_values - solution_values)

            message = "Différences trouvées: "
            if missing > 0:
                message += f"{missing} lignes manquantes. "
            if extra > 0:
                message += f"{extra} lignes en trop."

            return False, message

    except Exception as e:
        return False, f"Erreur lors de la comparaison: {str(e)}"


def is_safe_query(query: str) -> Tuple[bool, str]:
    """
    Validate if the query is safe to execute.
    """
    query_upper = query.strip().upper()
    if re.search(r'\bDROP\b', query_upper):
        return False, "Les requêtes DROP ne sont pas autorisées pour des raisons de sécurité."
    return True, "La requête est sécurisée"


def highlight_sql(query: str) -> str:
    """
    Highlight SQL keywords in the query
    """
    sql_keywords = SQL_KEYWORDS

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


def normalize_query(query: str) -> str:
    """
    Normalize query for strict comparison
    """
    normalized = query.lower()
    normalized = re.sub(r'\s+', '', normalized)
    normalized = normalized.rstrip(';').strip()
    return normalized


def execute_query(query: str) -> Tuple[bool, Union[List[Dict], str], bool]:
    """
    Execute a query and return results
    """
    try:
        is_select = query.strip().upper().startswith("SELECT")
        is_create_view = query.strip().upper().startswith("CREATE VIEW")

        if is_create_view:
            response = supabase.rpc("execute_non_returning_sql", {"query_text": query}).execute()
            return True, "Vue créée avec succès", False
        elif is_select:
            response = supabase.rpc("execute_returning_sql", {"query_text": query}).execute()
            if not hasattr(response, 'data'):
                return True, [], True

            # Handle single-column results
            if response.data and len(response.data[0].keys()) == 1:
                key = list(response.data[0].keys())[0]
                result = [{"result": row[key]} for row in response.data]
            else:
                result = response.data

            return True, result, True
        else:
            response = supabase.rpc("execute_non_returning_sql", {"query_text": query}).execute()
            return True, "Requête exécutée avec succès", False
    except Exception as e:
        return False, str(e), is_select


def is_query_correct(user_query: str, selected_question: str) -> Tuple[bool, str]:
    """
    Enhanced query verification
    """
    try:
        # Get the solution query
        response = supabase.table("questions").select("solution").eq("question", selected_question).execute()
        if not hasattr(response, 'data') or not response.data:
            return False, "Solution non trouvée"

        solution_query = response.data[0]['solution']

        # Handle CREATE VIEW queries
        if user_query.strip().upper().startswith("CREATE VIEW"):
            normalized_user = normalize_query(user_query)
            normalized_solution = normalize_query(solution_query)
            return normalized_user == normalized_solution, "Vérification syntaxique uniquement pour CREATE VIEW"

        # Handle SELECT queries
        success_user, result_user, is_select_user = execute_query(user_query)
        if not success_user:
            return False, f"Erreur dans votre requête: {result_user}"

        success_solution, result_solution, is_select_solution = execute_query(solution_query)
        if not success_solution:
            return False, f"Erreur dans la solution: {result_solution}"

        if is_select_user and is_select_solution:
            return compare_query_results(result_user, result_solution)

        return False, "Type de requête non supporté pour la comparaison"

    except Exception as e:
        return False, f"Erreur lors de la vérification: {str(e)}"


# Enhanced Custom CSS
st.markdown("""
    <style>
        .stApp {
            background-color: #f4f6f9;
            font-family: 'Inter', 'Segoe UI', Roboto, sans-serif;
        }

        .title {
            color: #2c3e50;
            text-align: center;
            font-weight: 700;
            margin-bottom: 20px;
            background: linear-gradient(90deg, #3498db, #2980b9);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .autocomplete-container {
            position: relative;
            width: 100%;
        }
        .autocomplete-dropdown {
            position: absolute;
            top: 100%;
            left: 0;
            width: 100%;
            max-height: 200px;
            overflow-y: auto;
            background-color: white;
            border: 1px solid #ddd;
            z-index: 1000;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .autocomplete-item {
            padding: 8px 12px;
            cursor: pointer;
            background-color: white;
        }
        .autocomplete-item:hover {
            background-color: #f0f0f0;
        }
    </style>
""", unsafe_allow_html=True)

# Main application layout
st.markdown('<h1 class="title">Data AI Lab - Éditeur de requêtes SQL</h1>', unsafe_allow_html=True)

# Initialize session state
if 'submitted_queries' not in st.session_state:
    st.session_state.submitted_queries = []
if 'query' not in st.session_state:
    st.session_state.query = ""

# Fetch and display questions
questions = fetch_questions()
selected_question = st.selectbox(
    "Sélectionnez une question :",
    ["Choisissez une question"] + questions
)

# Query input
query = st.text_area(
    "Entrez votre requête SQL :",
    value=st.session_state.query,
    height=200,
    help="Écrivez votre requête SQL ici. Soyez attentif aux opérations sensibles."
)

# Get autocomplete suggestions
suggestions = sql_autocomplete(query, supabase)

# Display autocomplete dropdown if suggestions exist
if suggestions:
    st.markdown('<div class="autocomplete-dropdown">', unsafe_allow_html=True)
    cols = st.columns(len(suggestions))
    for i, suggestion in enumerate(suggestions):
        with cols[i]:
            if st.button(suggestion, key=f"autocomplete_{suggestion}"):
                # Replace the last word with the selected suggestion
                words = query.split()
                if words:
                    words[-1] = suggestion
                    new_query = ' '.join(words)
                    st.session_state.query = new_query
                    st.experimental_rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# Display highlighted query
if query:
    st.markdown(f"""
        <div class="sql-editor">
            {highlight_sql(query)}
        </div>
    """, unsafe_allow_html=True)

# Test query button
if st.button("Testez la requête"):
    if selected_question == "Choisissez une question":
        st.warning("Veuillez sélectionner une question.")
    else:
        is_safe, safety_message = is_safe_query(query)
        if not is_safe:
            st.error(safety_message)
        else:
            is_correct, message = is_query_correct(query, selected_question)

            # Display result status
            if is_correct:
                st.success(f"✅ Requête correcte! {message}")
            else:
                st.error(f"❌ Requête incorrecte: {message}")

            # Execute and show results
            success, result, is_select = execute_query(query)
            if success:
                if isinstance(result, list):
                    st.write("Résultat de votre requête:")
                    st.table(result)
                else:
                    st.info(result)
            else:
                st.error(f"Erreur d'exécution: {result}")

# Submit query button
if st.button("Soumettre la requête"):
    is_safe, message = is_safe_query(query)
    if not is_safe:
        st.error(message)
    else:
        try:
            st.session_state.submitted_queries.append(query)
            st.success("✅ La requête a été envoyée !")
        except Exception as e:
            st.error(f"Erreur dans l'envoi de la requête : {str(e)}")

# Display submitted queries
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

# Clear submitted queries button
if st.button("Effacer les requêtes soumises"):
    st.session_state.submitted_queries = []
    st.rerun()

st.markdown('<div class="footer">Data AI Lab © 2024</div>', unsafe_allow_html=True)