# query_data.py

# --- START of SQLite3 fix for ChromaDB ---
# This block must be at the very top of the file,
# before any imports that might use sqlite3 (e.g., langchain_chroma which imports chromadb)
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules['pysqlite3']
# --- END of SQLite3 fix for ChromaDB ---

import argparse
from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM

from get_embedding_function import get_embedding_function

CHROMA_PATH = "chroma"

PROMPT_TEMPLATE = """
If the user ask questions about dengue, answer based on the text below. if not, answer normally. 
Answer the question based only on the following context:

{context}

---

Answer the question based on the above in paragraph with concise answer as a dengue expert. context: {question}
"""


def main():
    # Create CLI.
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="The query text.")
    args = parser.parse_args()
    query_text = args.query_text
    query_rag(query_text)


def query_rag(query_text: str):
    # Prepare the DB.
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Search the DB.
    results = db.similarity_search_with_score(query_text, k=5)

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    # print(prompt) # Keep this commented unless you want to see the prompt in logs

    model = OllamaLLM(model="gemma3", base_url="https://5fa7-2001-d08-db-8378-7039-6ffd-6a24-f21a.ngrok-free.app ")
    response_text = model.invoke(prompt)

    sources = [doc.metadata.get("id", None) for doc, _score in results]
    formatted_response = f"Response: {response_text}\n\nSources: {sources}"
    print(formatted_response)
    return response_text


if __name__ == "__main__":
    main()
