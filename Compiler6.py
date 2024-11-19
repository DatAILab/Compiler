from supabase import create_client, Client
import streamlit as st

# Initialize Supabase client
url = "https://tjgmipyirpzarhhmihxf.supabase.co"  # Replace with your Supabase URL
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRqZ21pcHlpcnB6YXJoaG1paHhmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzE2NzQ2MDEsImV4cCI6MjA0NzI1MDYwMX0.LNMUqA0-t6YtUKP6oOTXgVGYLu8Tpq9rMhH388SX4bI"  # Replace with your Supabase API key
supabase: Client = create_client(url, key)


# Function to execute SQL queries
def execute_query(query):
    try:
        # Execute the SQL query
        response = supabase.rpc("execute_sql", {"query": query}).execute()

        # Check for errors in the response
        if response.error:
            return f"An error occurred: {response.error.message}"

        # Return the results if it's a SELECT query
        return response.data if response.data else "Query executed successfully."
    except Exception as e:
        return f"An error occurred: {str(e)}"


# Streamlit application layout
st.title("Supabase SQL Executor")
st.write("Enter your SQL query below:")

# Text area for SQL query input
user_query = st.text_area("SQL Query", height=150)

# Button to execute the query
if st.button("Execute Query"):
    if user_query:
        result = execute_query(user_query)

        # Display the result
        if isinstance(result, list):
            st.write("Query Results:")
            for row in result:
                st.write(row)
        else:
            st.success(result)
    else:
        st.warning("Please enter a SQL query.")

# Optional: Display instructions
st.write("### Instructions:")
st.write("1. You can use SELECT, INSERT, UPDATE, DELETE statements.")
st.write("2. Type your SQL query in the text area and click 'Execute Query'.")