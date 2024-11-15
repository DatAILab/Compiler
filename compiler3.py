import streamlit as st
import sqlite3

# Function to execute SQL queries
def execute_query(query):
    # Connect to the SQLite database (or create it if it doesn't exist)
    connection = sqlite3.connect('example.db')
    cursor = connection.cursor()
    
    try:
        # Execute the SQL query
        cursor.execute(query)
        
        # If the query is a SELECT statement, fetch and return the results
        if query.strip().upper().startswith("SELECT"):
            results = cursor.fetchall()
            return results
        else:
            # Commit changes for INSERT, UPDATE, DELETE
            connection.commit()
            return "Query executed successfully."
    except sqlite3.Error as e:
        return f"An error occurred: {e}"
    finally:
        # Close the connection
        connection.close()

# Streamlit application layout
st.title("SQLite Query Executor")
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