import streamlit as st
import sqlite3
import pandas as pd


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
            # Get column names
            column_names = [description[0] for description in cursor.description]
            # Fetch results
            results = cursor.fetchall()
            # Create DataFrame with column names
            df = pd.DataFrame(results, columns=column_names)
            return df
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

# Add display options
display_option = st.radio(
    "Choose display format:",
    ["Static Table", "Interactive Table"],
    horizontal=True
)

# Button to execute the query
if st.button("Execute Query"):
    if user_query:
        result = execute_query(user_query)

        # Display the result
        if isinstance(result, pd.DataFrame):
            st.write("Query Results:")
            if not result.empty:
                if display_option == "Static Table":
                    st.table(result)  # Static table
                else:
                    st.dataframe(result)  # Interactive table with sorting capabilities
                st.write(f"Total rows: {len(result)}")
            else:
                st.info("Query returned no results.")
        else:
            st.success(result)
    else:
        st.warning("Please enter a SQL query.")

# Optional: Display instructions
with st.expander("Instructions", expanded=False):
    st.write("### Instructions:")
    st.write("1. You can use SELECT, INSERT, UPDATE, DELETE statements.")
    st.write("2. Type your SQL query in the text area and click 'Execute Query'.")
    st.write("3. Choose between static and interactive table display:")
    st.write("   - Static Table: Simple, clean table view")
    st.write("   - Interactive Table: Sortable columns and more interactive features")