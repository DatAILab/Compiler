from supabase import create_client, Client
import streamlit as st
import re
import pandas as pd
from typing import Tuple, Union, List, Dict, Any
import uuid

# Initialize Supabase client
url = "https://tjgmipyirpzarhhmihxf.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRqZ21pcHlpcnB6YXJoaG1paHhmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzE2NzQ2MDEsImV4cCI6MjA0NzI1MDYwMX0.LNMUqA0-t6YtUKP6oOTXgVGYLu8Tpq9rMhH388SX4bI"
supabase: Client = create_client(url, key)

# Set page configuration
st.set_page_config(layout="wide", page_title="Data AI Lab - SQL Query Editor", page_icon="🔍")

# Initialize user session
if 'user_id' not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())
if 'submitted_queries' not in st.session_state:
    st.session_state.submitted_queries = []

# Enhanced Custom CSS
st.markdown("""
    <style>
        .stApp {
            background-color: #f4f6f9;
            font-family: 'Inter', 'Segoe UI', Roboto, sans-serif;
        }

        .stSelectbox > div > div > div {
            min-height: 60px;
            font-size: 16px;
            display: flex;
            align-items: center;
        }

        .question-container {
            background-color: #ffffff;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
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

        .sql-keyword {
            color: #2980b9;
            font-weight: 600;
        }
    </style>
""", unsafe_allow_html=True)


def compare_query_results(user_result: List[Dict], solution_result: List[Dict]) -> Tuple[bool, str]:
    """Compare two query results for equality."""
    try:
        df_user = pd.DataFrame(user_result)
        df_solution = pd.DataFrame(solution_result)

        if df_user.empty and df_solution.empty:
            return True, "Les résultats sont identiques (aucune donnée)"
        elif df_user.empty or df_solution.empty:
            return False, "Un résultat est vide alors que l'autre ne l'est pas"

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
    """Validate if the query is safe to execute."""
    query_upper = query.strip().upper()
    forbidden_keywords = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'GRANT', 'REVOKE']
    for keyword in forbidden_keywords:
        if re.search(fr'\b{keyword}\b', query_upper):
            return False, f"Les requêtes {keyword} ne sont pas autorisées pour des raisons de sécurité."
    return True, "La requête est sécurisée"


def highlight_sql(query: str) -> str:
    """Highlight SQL keywords in the query."""
    sql_keywords = [
        'SELECT', 'FROM', 'WHERE', 'INSERT', 'UPDATE', 'CREATE', 'TABLE',
        'INTO', 'VALUES', 'AND', 'OR', 'NOT', 'NULL', 'AS', 'JOIN',
        'LEFT', 'RIGHT', 'INNER', 'OUTER', 'GROUP BY', 'ORDER BY',
        'HAVING', 'LIMIT', 'OFFSET', 'UNION', 'DISTINCT', 'COUNT',
        'SUM', 'AVG', 'MIN', 'MAX'
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


def execute_query(query: str, **kwargs) -> Tuple[bool, Union[List[Dict], str], bool]:
    """Execute a query and return results."""
    try:
        user_id = kwargs.get('user_id')
        query_upper = query.strip().upper()

        is_create_view = query_upper.startswith("CREATE VIEW")

        if is_create_view:
            view_name = query.split()[2]
            if user_id:
                user_specific_view_name = f"{user_id}_{view_name}"
                query = query.replace(view_name, user_specific_view_name, 1)
                view_name = user_specific_view_name

            response = supabase.rpc("execute_non_returning_sql", {"query_text": query}).execute()
            return True, f"Vue {view_name} créée avec succès", False

        elif query_upper.startswith("SELECT"):
            response = supabase.rpc("execute_returning_sql", {"query_text": query}).execute()
            if not hasattr(response, 'data'):
                return True, [], True

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
        return False, str(e), is_create_view


def is_query_correct(user_query: str, selected_question: str, user_id: str = None) -> Tuple[bool, str]:
    """Verify if the query is correct."""
    try:
        # Get the solution query
        response = supabase.table("questions").select("solution").eq("question", selected_question).execute()
        if not hasattr(response, 'data') or not response.data:
            return False, "Solution non trouvée"

        solution_query = response.data[0]['solution']

        # Pass user_id to execute_query if available
        execute_kwargs = {"user_id": user_id} if user_id else {}
        success_user, result_user, is_select_user = execute_query(user_query, **execute_kwargs)
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


def fetch_questions():
    """Fetch questions from Supabase."""
    try:
        response = supabase.table("questions").select("question").execute()
        if hasattr(response, 'data') and response.data:
            return [q['question'] for q in response.data]
        return []
    except Exception as e:
        st.error(f"Erreur lors de la récupération des questions : {str(e)}")
        return []


def main():
    # Title
    st.markdown('<h1 class="title">Data AI Lab - Éditeur de requêtes SQL</h1>', unsafe_allow_html=True)

    # Columns for layout
    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown('<div class="question-container">', unsafe_allow_html=True)
        # Fetch and display questions
        questions = fetch_questions()
        selected_question = st.selectbox(
            "Sélectionnez une question :",
            ["Choisissez une question"] + questions,
            help="Choisissez la question SQL que vous souhaitez résoudre"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        # Query input
        query = st.text_area(
            "Entrez votre requête SQL :",
            height=300,
            help="Écrivez votre requête SQL ici. Soyez attentif aux opérations sensibles."
        )

        # Display highlighted query
        if query:
            st.markdown(f"""
                <div class="sql-editor">
                    {highlight_sql(query)}
                </div>
            """, unsafe_allow_html=True)

        # Button row
        col_test, col_submit, col_clear = st.columns(3)

        with col_test:
            # Test query button
            if st.button("Testez la requête"):
                if selected_question == "Choisissez une question":
                    st.warning("Veuillez sélectionner une question.")
                else:
                    is_safe, safety_message = is_safe_query(query)
                    if not is_safe:
                        st.error(safety_message)
                    else:
                        is_correct, message = is_query_correct(query, selected_question, st.session_state.user_id)

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

        with col_submit:
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

        with col_clear:
            # Clear submitted queries button
            if st.button("Effacer les requêtes"):
                st.session_state.submitted_queries = []
                st.rerun()

    # Display submitted queries section
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

    st.markdown('<div class="footer">Data AI Lab © 2024</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()