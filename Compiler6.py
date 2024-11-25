import streamlit as st
from supabase import create_client, Client
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
    Provide autocomplete suggestions for SQL queries
    """
    # Get dynamic suggestions
    dynamic_suggestions = get_table_and_column_names(supabase)

    # Split the current query and get the last word
    words = query.split()
    last_word = words[-1] if words else ""

    # Filter suggestions that start with the last word
    suggestions = [
        sug for sug in dynamic_suggestions
        if sug.lower().startswith(last_word.lower())
    ]

    return suggestions


# Rest of the original functions remain the same (compare_query_results, is_safe_query,
# highlight_sql, normalize_query, execute_query, is_query_correct, fetch_questions)

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

        /* Previous CSS styles remain the same */
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

# Query input with autocomplete
query_input_container = st.empty()
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