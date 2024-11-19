from supabase import create_client, Client
import streamlit as st

# Initialize Supabase client
url = "https://tjgmipyirpzarhhmihxf.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRqZ21pcHlpcnB6YXJoaG1paHhmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzE2NzQ2MDEsImV4cCI6MjA0NzI1MDYwMX0.LNMUqA0-t6YtUKP6oOTXgVGYLu8Tpq9rMhH388SX4bI"
supabase: Client = create_client(url, key)

# Streamlit application layout
st.title("SQL Query Editor")

# Single input field for SQL queries
query = st.text_input("Enter your SQL query:")

if query:
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
        st.write("Debug info:")
        st.write(f"Query attempted: {query}")