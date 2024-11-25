from supabase import create_client, Client
import streamlit as st
import re
import pandas as pd
from typing import Tuple, Union, List, Dict, Any

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

        /* Results Table Styling */
        .dataframe {
            border-collapse: collapse;
            margin: 25px 0;
            font-size: 0.9em;
            font-family: sans-serif;
            min-width: 400px;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
        }

        .dataframe thead tr {
            background-color: #3498db;
            color: #ffffff;
            text-align: left;
        }

        .dataframe th,
        .dataframe td {
            padding: 12px 15px;
        }

        .dataframe tbody tr {
            border-bottom: 1px solid #dddddd;
        }

        .dataframe tbody tr:nth-of-type(even) {
            background-color: #f3f3f3;
        }

        .dataframe tbody tr:last-of-type {
            border-bottom: 2px solid #3498db;
        }
    </style>
""", unsafe_allow_html=True)


def compare_query_results(user_result: List[Dict], solution_result: List[Dict]) -> Tuple[bool, str]:
    """
    Compare two query results for equality.
    Returns (is_equal, message)
    """
    try:
        # Convert results to DataFrames for easier comparison
        df_user = pd.DataFrame(user_result)
        df_solution = pd.DataFrame(solution_result)

        # Sort both DataFrames to ensure consistent comparison
        if not df_user.empty and not df_solution.empty:
            df_user = df_user.sort_values(by=list(df_user.columns)).reset_index(drop=True)
            df_solution = df_solution.sort_values(by=list(df_solution.columns)).reset_index(drop=True)

        # Compare the DataFrames
        if df_user.equals(df_solution):
            return True, "Les résultats correspondent exactement!"
        else:
            differences = []
            if df_user.shape != df_solution.shape:
                differences.append(
                    f"Nombre de lignes/colonnes différent: Votre requête ({df_user.shape}) vs Solution ({df_solution.shape})")
            if list(df_user.columns) != list(df_solution.columns):
                differences.append("Colonnes différentes")
            elif not df_user.equals(df_solution):
                differences.append("Valeurs ou ordre des résultats différents")

            return False, "Différences trouvées: " + "; ".join(differences)
    except Exception as e:
        return False, f"Erreur lors de la comparaison: {str(e)}"


def is_safe_query(query: str) -> Tuple[bool, str]:
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
        'IF', 'ELSE', 'WHILE', 'LANGUAGE', 'PLPGSQL', 'CALL', 'VIEW'
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


def normalize_query(query: str) -> str:
    """
    Normalize query for strict comparison:
    1. Convert to lowercase
    2. Remove all whitespaces
    3. Remove semicolons
    """
    normalized = query.lower()  # Convert to lowercase
    normalized = re.sub(r'\s+', '', normalized)  # Remove all whitespaces
    normalized = normalized.rstrip(';').strip()
    return normalized


def execute_query(query: str) -> Tuple[bool, Union[List[Dict], str], bool]:
    """
    Execute a query and return (success, result/error_message, is_select)
    """
    try:
        is_select = query.strip().upper().startswith("SELECT")
        is_create_view = query.strip().upper().startswith("CREATE VIEW")

        if is_create_view:
            # Execute CREATE VIEW without comparison
            response = supabase.rpc("execute_non_returning_sql", {"query_text": query}).execute()
            return True, "Vue créée avec succès", False
        elif is_select:
            response = supabase.rpc("execute_returning_sql", {"query_text": query}).execute()
            return True, response.data if hasattr(response, 'data') else [], True
        else:
            response = supabase.rpc("execute_non_returning_sql", {"query_text": query}).execute()
            return True, "Requête exécutée avec succès", False
    except Exception as e:
        return False, str(e), is_select


def is_query_correct(user_query: str, selected_question: str) -> Tuple[bool, str]:
    """
    Enhanced query verification that checks both syntax and results
    """
    try:
        # Get the solution query
        response = supabase.table("questions").select("solution").eq("question", selected_question).execute()
        if not hasattr(response, 'data') or not response.data:
            return False, "Solution non trouvée"

        solution_query = response.data[0]['solution']

        # For CREATE VIEW queries, just check normalized text
        if user_query.strip().upper().startswith("CREATE VIEW"):
            normalized_user = normalize_query(user_query)
            normalized_solution = normalize_query(solution_query)
            return normalized_user == normalized_solution, "Vérification syntaxique uniquement pour CREATE VIEW"

        # For SELECT queries, execute both and compare results
        success_user, result_user, is_select_user = execute_query(user_query)
        if not success_user:
            return False, f"Erreur dans votre requête: {result_user}"

        success_solution, result_solution, is_select_solution = execute_query(solution_query)
        if not success_solution:
            return False, f"Erreur dans la solution: {result_solution}"

        if is_select_user and is_select_solution:
            is_equal, message = compare_query_results(result_user, result_solution)
            return is_equal, message

        return False, "Type de requête non supporté pour la comparaison"

    except Exception as e:
        return False, f"Erreur lors de la vérification: {str(e)}"


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


# Main application layout
st.markdown('<h1 class="title">Data AI Lab - Éditeur de requêtes SQL</h1>', unsafe_allow_html=True)

# Session state initialization
if 'submitted_queries' not in st.session_state:
    st.session_state.submitted_queries = []

# Fetch and display questions
questions = fetch_questions()
selected_question = st.selectbox(
    "Sélectionnez une question :",
    ["Choisissez une question"] + questions
)

# Query input area
query = st.text_area("Entrez votre requête SQL :", height=200, key="sql_input",
                     help="Écrivez votre requête SQL ici. Soyez attentif aux opérations sensibles.")

# Display highlighted version of the query
if query:
    st.markdown(f"""
        <div class="sql-editor">
            {highlight_sql(query)}
        </div>
    """, unsafe_allow_html=True)

# Try Query button
if st.button("Testez la requête", help="Exécutez la requête pour voir les résultats"):
    if selected_question == "Choisissez une question":
        st.warning("Veuillez sélectionner une question.")
    else:
        # Check if query is safe
        is_safe, safety_message = is_safe_query(query)
        if not is_safe:
            st.error(safety_message)
        else:
            # Execute and verify the query
            is_correct, message = is_query_correct(query, selected_question)
            if is_correct:
                st.success(f"Requête correcte! {message}")
            else:
                st.error(f"Requête incorrecte: {message}")

            # Execute and show results
            success, result, is_select = execute_query(query)
            if success:
                if isinstance(result, list):
                    st.table(result)
                else:
                    st.info(result)
            else:
                st.error(f"Erreur d'exécution: {result}")

# Submit Query button
if st.button("Soumettre la requête", help="Sauvegarder la requête pour révision"):
    is_safe, message = is_safe_query(query)
    if not is_safe:
        st.error(message)
    else:
        try:
            st.session_state.submitted_queries.append(query)
            st.success(f"La requête a été envoyée !")
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
if st.button("Éffacer les requêtes soumises"):
    st.session_state.submitted_queries = []
    st.rerun()

st.markdown('<div class="footer">Data AI Lab © 2024</div>', unsafe_allow_html=True)