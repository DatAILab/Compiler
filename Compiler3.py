import streamlit as st
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = "https://ihpywjpyklpcyspoqabm.supabase.co"  # Replace with your Supabase URL
SUPABASE_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlocHl3anB5a2xwY3lzcG9xYWJtIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczMTU4ODU0OSwiZXhwIjoyMDQ3MTY0NTQ5fQ.Rxz7HfLatgFFQRngWtFsmTR23nvOgbP5K2kznoxPX6E"  # Replace with your Supabase API key

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_API_KEY)

# Streamlit app title
st.title("Supabase Database Management")

# Section for adding a new item
st.header("Add New Item")
name = st.text_input("Item Name")
description = st.text_area("Item Description")

if st.button("Add Item"):
    if name:
        response = supabase.table("items").insert({"name": name, "description": description}).execute()
        if response.status_code == 201:
            st.success("Item added successfully!")
        else:
            st.error("Error adding item.")

# Section for retrieving items
st.header("Retrieve Items")
if st.button("Retrieve All Items"):
    response = supabase.table("items").select("*").execute()
    items = response.data
    if items:
        for item in items:
            st.write(f"**ID**: {item['id']}, **Name**: {item['name']}, **Description**: {item['description']}")
    else:
        st.info("No items found.")

# Section for creating a new table (example)
st.header("Create New Table")
new_table_name = st.text_input("New Table Name")

if st.button("Create Table"):
    if new_table_name:
        query = f"CREATE TABLE {new_table_name} (id SERIAL PRIMARY KEY, name TEXT NOT NULL);"
        response = supabase.rpc("execute_sql", {"query": query}).execute()
        if response.status_code == 200:
            st.success(f"Table '{new_table_name}' created successfully!")
        else:
            st.error("Error creating table.")