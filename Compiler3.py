import streamlit as st
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = "https://ihpywjpyklpcyspoqabm.supabase.co"  # Replace with your Supabase URL
SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlocHl3anB5a2xwY3lzcG9xYWJtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzE1ODg1NDksImV4cCI6MjA0NzE2NDU0OX0.V-Vpxx63VoT-tdjCOV1y2BPpRWbVtxp9aMhV7DCo2oM"  # Replace with your Supabase API key

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_API_KEY)

# Streamlit app title
st.title("Supabase SQL Executor")

# SQL input area
sql_query = st.text_area("Write your SQL query here:", height=200)

# Execute button
if st.button("Execute SQL"):
    if sql_query.strip():
        try:
            # Check if the query is a SELECT statement
            if sql_query.strip().upper().startswith("SELECT"):
                response = supabase.rpc("execute_returning_sql", {"query": sql_query}).execute()

                # Check if the response has data
                if response.data is not None:
                    st.success("Query executed successfully!")
                    # Display the result in a more readable format
                    for row in response.data:
                        st.write(row)  # Display each row's result
                else:
                    st.info("No results found.")
            else:
                # For non-SELECT queries (like CREATE, INSERT, UPDATE, DELETE)
                response = supabase.rpc("execute_non_returning_sql", {"query": sql_query}).execute()
                if response.error is None:
                    st.success("Query executed successfully!")
                else:
                    st.error(f"Error executing query: {response.error}")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    else:
        st.warning("Please enter a SQL query.")

# Section for displaying previous queries or results
st.header("Previous Queries")
# You can implement a feature to save and display previous queries if needed