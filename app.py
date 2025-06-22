import streamlit as st
import subprocess
import os
import sys # Import sys module

# --- Configuration ---
# Define the base directory for your application in Streamlit Cloud
# os.getcwd() is generally correct for Streamlit Cloud deployments
APP_DIR = os.getcwd()

# Script is in the same directory as app.py
QUERY_SCRIPT_PATH = os.path.join(APP_DIR, "query_data.py")

# The working directory for the subprocess should be the APP_DIR
SUBPROCESS_CWD = APP_DIR

# --- IMPORTANT CHANGE HERE ---
# Use the exact Python executable that is running the current Streamlit app
PYTHON_EXECUTABLE = sys.executable

# --- Streamlit App ---
st.title("Ask a Question to Your Documentss")

# Input field for the user's question
user_question = st.text_input("Enter your question:")

if st.button("Get Answer"):
    if user_question:
        st.info("Processing your question...")

        # --- Enhanced Debugging Output ---
        st.write(f"App directory (configured): {APP_DIR}")
        st.write(f"Query script path (configured): {QUERY_SCRIPT_PATH}")
        st.write(f"Subprocess CWD (configured): {SUBPROCESS_CWD}")
        st.write(f"Python executable for subprocess: {PYTHON_EXECUTABLE}") # Display the exact executable path

        if not os.path.exists(QUERY_SCRIPT_PATH):
            st.error(f"Error: Script file not found at: {QUERY_SCRIPT_PATH}. Please check the path and if query_data.py is uploaded.")
        elif not os.path.isdir(SUBPROCESS_CWD):
            st.error(f"Error: Subprocess working directory not found at: {SUBPROCESS_CWD}. Please check the path.")
        else:
            try:
                process = subprocess.run(
                    [PYTHON_EXECUTABLE, QUERY_SCRIPT_PATH, user_question],
                    capture_output=True,
                    text=True,
                    check=True, # This will raise CalledProcessError if query_data.py fails
                    cwd=SUBPROCESS_CWD
                )
                result = process.stdout
                st.success("Answer:")
                st.markdown(result)

            except subprocess.CalledProcessError as e:
                st.error(f"Error running the query script (Exit Code: {e.returncode}):")
                st.code(f"STDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}") # Display both stdout and stderr
            except FileNotFoundError:
                st.error(f"Error: Could not find the Python executable '{PYTHON_EXECUTABLE}' or the script '{QUERY_SCRIPT_PATH}'.")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
