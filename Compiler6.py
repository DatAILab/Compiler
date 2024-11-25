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

# SQL Keywords for Autocomplete
SQL_KEYWORDS = [
    'SELECT', 'FROM', 'WHERE', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'TABLE',
    'INTO', 'VALUES', 'AND', 'OR', 'NOT', 'NULL', 'AS', 'JOIN', 'LEFT', 'RIGHT', 'INNER',
    'OUTER', 'GROUP BY', 'ORDER BY', 'HAVING', 'LIMIT', 'OFFSET', 'UNION', 'ALL',
    'VIEW', 'DISTINCT', 'COUNT', 'SUM', 'AVG', 'MIN', 'MAX'
]

def fetch_questions():
    """Fetch questions from Supabase"""
    try:
        response = supabase.table("questions").select("question").execute()
        if hasattr(response, 'data') and response.data:
            return [q['question'] for q in response.data]
        return []
    except Exception as e:
        st.error(f"Erreur lors de la récupération des questions : {str(e)}")
        return []

def autocomplete_query(query: str) -> str:
    """Suggest SQL keywords based on user input"""
    suggestions = [kw for kw in SQL_KEYWORDS if kw.lower().startswith(query.lower())]
    return suggestions

# Main application layout
st.markdown('<h1 class="title">Data AI Lab - Éditeur de requêtes SQL</h1>', unsafe_allow_html=True)

# Initialize session state
if 'submitted_queries' not in st.session_state:
    st.session_state.submitted_queries = []

# Fetch and display questions
questions = fetch_questions()
selected_question = st.selectbox(
    "Sélectionnez une question :",
    ["Choisissez une question"] + questions
)

# Query input with autocomplete
query = st.text_input(
    "Entrez votre requête SQL :",
    help="Écrivez votre requête SQL ici. Soyez attentif aux opérations sensibles."
)

# Display autocomplete suggestions
if query:
    suggestions = autocomplete_query(query)
    if suggestions:
        st.markdown("### Suggestions:")
        for suggestion in suggestions:
            st.markdown(f"- {suggestion}")

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