import streamlit as st
import pandas as pd
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

                # Check if the response has data
                if response.data is not None:
                    st.success("Query executed successfully!")

                    # Convert the JSON data to a DataFrame
                    df = pd.DataFrame(response.data)

                    # Display the DataFrame as a table
                    st.dataframe(df)  # Display results as a DataFrame for better interactivity
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

