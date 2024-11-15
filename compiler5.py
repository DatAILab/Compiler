import streamlit as st
from database_utils import execute_query
import pandas as pd

# Streamlit UI
st.title("Supabase Database Manager")
st.caption("Manage your Supabase Databases")

# Test connection
try:
    # Test query
    execute_query("SELECT 1")
    st.sidebar.success("Successfully connected to Supabase!")
except Exception as e:
    st.sidebar.error(f"Connection failed: {str(e)}")

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