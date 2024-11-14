import streamlit as st
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = "https://ihpywjpyklpcyspoqabm.supabase.co"  # Replace with your Supabase URL
SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlocHl3anB5a2xwY3lzcG9xYWJtIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczMTU4ODU0OSwiZXhwIjoyMDQ3MTY0NTQ5fQ.Rxz7HfLatgFFQRngWtFsmTR23nvOgbP5K2kznoxPX6E"  # Replace with your Supabase API key

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
                if response.status_code == 200:
                    st.success("Query executed successfully!")
                    # Display the result in a more readable format
                    if response.data:
                        for row in response.data:
                            st.write(row)  # Display each row's result
                    else:
                        st.info("No results found.")
                else:
                    st.error(f"Error executing query: {response.error}")
            else:
                # For non-SELECT queries (like CREATE, INSERT, UPDATE, DELETE)
                response = supabase.rpc("execute_non_returning_sql", {"query": sql_query}).execute()
                if response.status_code == 200:
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