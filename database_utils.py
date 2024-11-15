import streamlit as st
import pandas as pd
from supabase import Client, create_client
import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

# Function to create a new Supabase database
def create_database(database_name):
    try:
        url = f"{os.getenv('SUPABASE_URL')}/rest/v1/database"
        headers = {
            "apikey": os.getenv('SUPABASE_KEY'),
            "Content-Type": "application/json"
        }
        data = {"name": database_name}
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return f"Database '{database_name}' created successfully."
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Function to execute SQL queries
@st.cache_data(ttl=600)
def execute_query(query):
    try:
        result = supabase.query(query).execute()
        if result.data:
            df = pd.DataFrame(result.data)
            return df
        else:
            return "Query executed successfully."
    except Exception as e:
        return f"An error occurred: {str(e)}"