import streamlit as st
import pandas as pd
from supabase import create_client, Client
import re

# Supabase configuration
SUPABASE_URL = "https://ihpywjpyklpcyspoqabm.supabase.co"  # Replace with your Supabase URL
SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlocHl3anB5a2xwY3lzcG9xYWJtIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczMTU4ODU0OSwiZXhwIjoyMDQ3MTY0NTQ5fQ.Rxz7HfLatgFFQRngWtFsmTR23nvOgbP5K2kznoxPX6E"  # Replace with your Supabase API key

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_API_KEY)

# Streamlit app title
st.title("Supabase SQL Executor")

# SQL input area
sql_query = st.text_area("Write your SQL query here:", height=200)

# Function to highlight SQL keywords
def highlight_sql_keywords(query):
    keywords = ["SELECT", "FROM", "WHERE", "UPDATE", "DELETE", "INSERT", "INTO", "VALUES", "SET", "JOIN", "ON", "ORDER BY", "GROUP BY"]
    for keyword in keywords:
        query = re.sub(r'\b' + keyword + r'\b', f"<span style='color:blue'>{keyword}</span>", query, flags=re.IGNORECASE)
    return query

# Display the highlighted SQL query
if sql_query.strip():
    highlighted_query = highlight_sql_keywords(sql_query)
    st.markdown(highlighted_query, unsafe_allow_html=True)

# Execute button
if st.button("Execute SQL"):
    if sql_query.strip():
        try:
            # Check if the query is a SELECT statement
            if sql_query.strip().upper().startswith("SELECT"):
                response = supabase.rpc("execute_returning_sql", {"query": sql_query}).execute()

                if response.data is not None:
                    st.success("Query executed successfully!")
                    df = pd.DataFrame(response.data)  # Convert JSON response to DataFrame
                    st.dataframe(df)  # Display DataFrame as an interactive table
                else:
                    st.info("No results found.")
            else:
                response = supabase.rpc("execute_non_returning_sql", {"query": sql_query}).execute()

                # Check if the response indicates success
                if response.status_code == 200:  # Assuming 200 indicates success
                    st.success("Query executed successfully!")
                else:
                    st.error(f"Error executing query: {response.message}")  # Adjust based on actual response structure
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    else:
        st.warning("Please enter a SQL query.")
