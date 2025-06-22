import streamlit as st
import subprocess
import os

# --- Configuration ---
# Define the base directory for your application in Colab
# This should be the directory where your app.py and query_data.py reside
# Example: If your app is in /content/gdrive/MyDrive/PSM_RAG_Chatbot/
APP_DIR = "/content/gdrive/MyDrive/PSM_RAG_Chatbot/"

# Script is in the same directory as app.py
QUERY_SCRIPT_PATH = os.path.join(APP_DIR, "query_data.py")

# The working directory for the subprocess should be the APP_DIR
SUBPROCESS_CWD = APP_DIR

PYTHON_EXECUTABLE = "python" # This should generally be fine in Colab

# --- Streamlit App ---
st.title("Ask a Question to Your Documents")

# Input field for the user's question
user_question = st.text_input("Enter your question:")

if st.button("Get Answer"):
    if user_question:
        st.info("Processing your question...")

        # --- Debugging Output (Keep these for now) ---
        st.write(f"App directory (configured): {APP_DIR}")
        st.write(f"Query script path (configured): {QUERY_SCRIPT_PATH}")
        st.write(f"Subprocess CWD (configured): {SUBPROCESS_CWD}")

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