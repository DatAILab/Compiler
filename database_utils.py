import streamlit as st
import pandas as pd
from supabase import Client, create_client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

# Function to execute SQL queries
@st.cache_data(ttl=600)
def execute_query(query):
    try:
        result = supabase.rpc("execute_sql", {"query": query}).execute()  # Use a stored procedure or RPC for executing SQL
        if result.data:
            df = pd.DataFrame(result.data)
            return df
        else:
            return "Query executed successfully."
    except Exception as e:
        return f"An error occurred: {str(e)}"