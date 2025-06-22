# Import necessary libraries
import argparse  # For parsing command-line arguments
import os  # For interacting with the operating system (e.g., checking for file paths)
import shutil  # For file system operations like deleting directories
from langchain_community.document_loaders import PyPDFDirectoryLoader  # To load PDF documents from a directory
from langchain_text_splitters import RecursiveCharacterTextSplitter  # To split documents into smaller chunks
from langchain_core.documents import Document  # The basic data structure for a document
from get_embedding_function import get_embedding_function  # A custom function to get the embedding model
from langchain_chroma import Chroma  # The Chroma vector store


# Define constant paths for the ChromaDB database and the data directory
CHROMA_PATH = "chroma"
DATA_PATH = "data"


def main():
    """
    The main function of the script. It handles command-line arguments for resetting the database,
    loads documents from PDF files, splits them into manageable chunks, and adds them to the ChromaDB vector store.
    """
    # Create a parser for command-line arguments
    parser = argparse.ArgumentParser()
    # Add an argument to allow resetting the database
    parser.add_argument("--reset", action="store_true", help="Reset the database.")
    args = parser.parse_args()

    # If the --reset flag is used, clear the existing database
    if args.reset:
        print("✨ Clearing Database")
        clear_database()

    # Load the documents from the specified data path
    documents = load_documents()
    # Split the loaded documents into smaller chunks
    chunks = split_documents(documents)
    # Add the generated chunks to the ChromaDB database
    add_to_chroma(chunks)


def load_documents():
    """
    Loads all PDF documents from the directory specified by DATA_PATH.

    Returns:
        list[Document]: A list of loaded documents.
    """
    # Initialize the PDF loader with the path to the data directory
    document_loader = PyPDFDirectoryLoader(DATA_PATH)
    # Load and return the documents
    return document_loader.load()


def split_documents(documents: list[Document]):
    """
    Splits the provided documents into smaller chunks using a text splitter.

    Args:
        documents (list[Document]): The list of documents to split.

    Returns:
        list[Document]: A list of document chunks.
    """
    # Initialize the text splitter with specific parameters
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,  # The maximum size of each chunk (in characters)
        chunk_overlap=80,  # The number of characters to overlap between chunks
        length_function=len,  # The function to measure the length of the text
        is_separator_regex=False,  # Specifies that the separators are not regular expressions
    )
    # Split the documents and return the resulting chunks
    return text_splitter.split_documents(documents)


def add_to_chroma(chunks: list[Document]):
    """
    Adds document chunks to the ChromaDB database, avoiding duplicates.

    Args:
        chunks (list[Document]): The list of document chunks to add.
    """
    # Initialize the ChromaDB client with the persistent directory and the embedding function
    db = Chroma(
        persist_directory=CHROMA_PATH, embedding_function=get_embedding_function()
    )

    # Generate unique IDs for each chunk based on its source and position
    chunks_with_ids = calculate_chunk_ids(chunks)

    # Get the IDs of all documents that already exist in the database
    existing_items = db.get(include=[])  # By default, getting items includes their IDs
    existing_ids = set(existing_items["ids"])
    print(f"Number of existing documents in DB: {len(existing_ids)}")

    # Filter out chunks that are already in the database
    new_chunks = []
    for chunk in chunks_with_ids:
        # Check if the chunk's unique ID is not in the set of existing IDs
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)

    # If there are new chunks to add, add them to the database
    if len(new_chunks):
        print(f"👉 Adding new documents: {len(new_chunks)}")
        # Extract the IDs for the new chunks
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        # Add the new documents to the database with their unique IDs
        db.add_documents(new_chunks, ids=new_chunk_ids)
        # Persist the changes to disk
        db.persist()
    else:
        # If no new chunks were found, print a message
        print("✅ No new documents to add")


def calculate_chunk_ids(chunks):
    """
    Generates a unique ID for each document chunk based on its source file, page number, and chunk index.
    Example ID: "data/monopoly.pdf:6:2" (Source:Page:ChunkIndex)

    Args:
        chunks (list[Document]): The list of document chunks.

    Returns:
        list[Document]: The list of chunks with the 'id' added to their metadata.
    """
    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        # Create an ID for the current page
        current_page_id = f"{source}:{page}"

        # If the page ID is the same as the last one, it means we are on the same page,
        # so we increment the chunk index.
        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            # If it's a new page, reset the chunk index to 0.
            current_chunk_index = 0

        # Create the final unique chunk ID
        chunk_id = f"{current_page_id}:{current_chunk_index}"
        # Update the last page ID for the next iteration
        last_page_id = current_page_id
        # Add the unique ID to the chunk's metadata
        chunk.metadata["id"] = chunk_id

    return chunks


def clear_database():
    """
    Deletes the ChromaDB directory if it exists, effectively clearing the database.
    """
    # Check if the ChromaDB path exists
    if os.path.exists(CHROMA_PATH):
        # Remove the directory and all its contents
        shutil.rmtree(CHROMA_PATH)


# This ensures that the main() function is called only when the script is executed directly
if __name__ == "__main__":
    main()
