import streamlit as st
import pandas as pd
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = "https://ihpywjpyklpcyspoqabm.supabase.co"
SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlocHl3anB5a2xwY3lzcG9xYWJtIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczMTU4ODU0OSwiZXhwIjoyMDQ3MTY0NTQ5fQ.Rxz7HfLatgFFQRngWtFsmTR23nvOgbP5K2kznoxPX6E"

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
           if sql_query.strip().upper().startswith("<span style='color:blue'>SELECT</span>"):
               response = supabase.rpc("execute_returning_sql", {"query": sql_query}).execute()

               if response.data is not None:
                   st.success("Query executed successfully!")
                   df = pd.DataFrame(response.data)
                   st.dataframe(df)
               else:
                   st.info("No results found.")
           else:
               response = supabase.rpc("execute_non_returning_sql", {"query": sql_query}).execute()
               if response.error is None:
                   st.success("Query executed successfully!")
               else:
                   st.error(f"Error executing query: {response.error}")
       except Exception as e:
           st.error(f"An error occurred: {str(e)}")
   else:
       st.warning("Please enter a SQL query.")