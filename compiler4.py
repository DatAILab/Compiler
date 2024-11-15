import streamlit as st
import sqlite3
import pandas as pd

def execute_query(query):
    connection = sqlite3.connect('example.db')
    cursor = connection.cursor()

    try:
        # Execute the query
        cursor.execute(query)

        # Handle CREATE statements
        if query.strip().upper().startswith("CREATE"):
            if query.strip().upper().startswith("CREATE TABLE"):
                st.success("Table created successfully.")
            elif query.strip().upper().startswith("CREATE VIEW"):
                # Create a new table for the view
                view_name = query.strip().split(" ")[2]
                view_query = " ".join(query.strip().split(" ")[4:])
                view_data = execute_query(view_query)
                view_data.to_sql(view_name, connection, index=False, if_exists="replace")
                st.success(f"View '{view_name}' created successfully.")
            elif query.strip().upper().startswith("CREATE PROCEDURE"):
                procedure_name = query.strip().split(" ")[2]
                st.success(f"Stored procedure '{procedure_name}' created successfully.")
            else:
                st.success("Statement executed successfully.")

        # Handle SELECT queries
        elif query.strip().upper().startswith("SELECT"):
            column_names = [description[0] for description in cursor.description]
            results = cursor.fetchall()
            df = pd.DataFrame(results, columns=column_names)
            return df

        # Handle other queries
        else:
            connection.commit()
            st.success("Query executed successfully.")

    except sqlite3.Error as e:
        st.error(f"An error occurred: {e}")
    finally:
        connection.close()

# Streamlit UI
st.title("SQLite Query Executor")

# SQL query input
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
        st.warning("Please enter a SQL query.")

# Documentation section
with st.expander("SQL Features Reference", expanded=False):
    st.markdown("""
    ### Supported SQL Features:
    - CREATE TABLE
    - CREATE VIEW
    - CREATE PROCEDURE
    - SELECT
    - INSERT
    - UPDATE
    - DELETE
    """)