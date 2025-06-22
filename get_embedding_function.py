# from langchain_community.embeddings.ollama import OllamaEmbeddings
from langchain_ollama import OllamaEmbeddings
# from langchain_aws import BedrockEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings

# from langchain_community.embeddings.bedrock import BedrockEmbeddings


# def get_embedding_function():
#     embeddings = OpenAIEmbeddings(openai_api_key="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")
#     return embeddings

# def get_embedding_function():
#     model_name = "sentence-transformers/all-MiniLM-L6-v2"  # Free and fast
#     embeddings = HuggingFaceEmbeddings(model_name=model_name)
#     return embeddings



def get_embedding_function():
    # embeddings = BedrockEmbeddings(
    #     credentials_profile_name="default", region_name="us-east-1"
    # )
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    return embeddings
