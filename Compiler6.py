import streamlit as st
import streamlit.components.v1 as components

# HTML and JavaScript for CodeMirror
code_mirror_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>SQL Editor</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.5/codemirror.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.5/codemirror.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.5/mode/sql/sql.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.5/addon/hint/show-hint.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.5/addon/hint/show-hint.min.css">
    <style>
        .CodeMirror {
            border: 1px solid #eee;
            height: auto;
        }
    </style>
</head>
<body>
    <textarea id="code" name="code"></textarea>
    <script>
        var editor = CodeMirror.fromTextArea(document.getElementById("code"), {
            mode: "text/x-sql",
            lineNumbers: true,
            extraKeys: {"Ctrl-Space": "autocomplete"},
            hintOptions: {tables: {
                users: ["name", "score", "birthDate"],
                countries: ["name", "population", "size"]
            }}
        });
        editor.on("change", function() {
            const code = editor.getValue();
            const event = new CustomEvent("codeChange", { detail: code });
            window.dispatchEvent(event);
        });
    </script>
</body>
</html>
"""

# Streamlit app
st.title("SQL Query Editor with Syntax Highlighting")

# Create a Streamlit component for CodeMirror
component_value = components.html(code_mirror_html, height=300, width=700, scrolling=False)

# Display the current SQL query
st.write("Current SQL Query:")
st.code(component_value, language='sql')