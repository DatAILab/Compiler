import streamlit as st
from database_utils import create_database, execute_query
import pandas as pd

# Streamlit UI
st.title("Supabase Database Creator")
st.caption("Create and Manage Supabase Databases")

# Test connection
try:
    # Test query
    execute_query("SELECT 1")
    st.sidebar.success("Successfully connected to Supabase!")
except Exception as e:
    st.sidebar.error(f"Connection failed: {str(e)}")

# Create database section
st.subheader("Create a New Database")
database_name = st.text_input("Enter a name for the new database:", "")

if st.button("Create Database"):
    if database_name:
        result = create_database(database_name)
        st.success(result)
    else:
        st.warning("Please enter a database name.")

# SQL Query Executor section
st.subheader("SQL Query Executor")
user_query = st.text_area("Enter your SQL query:", height=150)

# Display options
display_option = st.radio(
    "Choose display format:",
    ["Static Table", "Interactive Table"],
    horizontal=True
)

# Execute query button
if st.button("Execute Query"):
    if user_query:
        with st.spinner("Executing query..."):
            result = execute_query(user_query)

        if isinstance(result, pd.DataFrame):
            st.write("Query Results:")
            if not result.empty:
                if display_option == "Static Table":
                    st.table(result)
                else:
                    st.dataframe(result, use_container_width=True)
                st.write(f"Total rows: {len(result)}")
            else:
                st.info("Query returned no results.")
        else:
            st.error(result)
    else:
        st.warning("Please enter a SQL query.")

# Performance metrics in sidebar
with st.sidebar:
    st.subheader("Performance Metrics")
    st.metric("Cached Queries", "10 minutes")
    if st.button("Clear Cache"):
        st.cache_data.clear()
        st.success("Cache cleared!")

# Documentation
with st.expander("Supabase Features & Limitations", expanded=False):
    st.markdown("""
    ### Supabase PostgreSQL Features:

    #### Supported Operations:
    - Full SQL support
    - Real-time capabilities
    - Row Level Security
    - Foreign Keys
    - Indexes
    - JSON support

    #### Free Tier Limits:
    - 500MB Database
    - Unlimited API requests
    - 50,000 monthly active users
    - Daily backups
    - Social OAuth providers

    #### Best Practices:
    1. Use prepared statements for better security
    2. Create indexes for frequently queried columns
    3. Use appropriate data types
    4. Implement row level security for production
    """)