import streamlit as st
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = "https://ihpywjpyklpcyspoqabm.supabase.co"  # Replace with your Supabase URL
SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlocHl3anB5a2xwY3lzcG9xYWJtIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczMTU4ODU0OSwiZXhwIjoyMDQ3MTY0NTQ5fQ.Rxz7HfLatgFFQRngWtFsmTR23nvOgbP5K2kznoxPX6E"  # Replace with your Supabase API key

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_API_KEY)

# Streamlit app title
st.title("SQL Code Executor")

# SQL input
sql_code = st.text_area("Enter your SQL code:", height=200)

# Execute button
if st.button("Execute SQL"):
    if sql_code.strip():
        try:
            # Execute the SQL query
            response = supabase.rpc("execute_sql", {"query": sql_code}).execute()
            st.success(f"Query executed successfully: {response.data}")
        except Exception as e:
            st.error(f"Error executing query: {str(e)}")
    else:
        st.warning("Please enter some SQL code.")

# Create a button to validate SQL
if st.button("Validate SQL"):
    if sql_code.strip():
        # This is a placeholder for validation logic
        # In a production scenario, you would implement actual validation
        st.info("SQL validation placeholder: Your SQL syntax seems correct!")
    else:
        st.warning("Please enter some SQL code to validate.")