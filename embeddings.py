import os
import argparse
import logging
import asyncio
from typing import List

from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from google import genai
from supabase import create_client, Client

from config import settings
from exceptions import RAGSearchError

# Configure basic logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Initialize Supabase client lazily
_supabase_client = None

def get_supabase() -> Client:
    global _supabase_client
    if _supabase_client is None:
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            raise ValueError("Supabase URL and Key must be set in the environment.")
        _supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    return _supabase_client

async def create_embedding(text: str) -> List[float]:
    client = genai.Client(api_key=settings.GOOGLE_API_KEY)
    from google.genai import types 
    
    result = client.models.embed_content(
        model="gemini-embedding-2",
        contents=text,
        config=types.EmbedContentConfig(output_dimensionality=768) # Shrinks it!
    )
    return result.embeddings[0].values

def check_supabase_connection():
    """Verifies that the required table exists in Supabase."""
    supabase = get_supabase()
    try:
        supabase.table("business_docs").select("id").limit(1).execute()
        logging.info("Supabase connection verified. Table 'business_docs' exists.")
    except Exception as e:
        error_msg = f"""
        FAILED to connect to Supabase or the 'business_docs' table is missing.
        Error: {str(e)}

        Please run this SQL in your Supabase project's SQL Editor:

        CREATE EXTENSION IF NOT EXISTS vector;
        CREATE TABLE business_docs (
          id BIGSERIAL PRIMARY KEY,
          business_id TEXT NOT NULL,
          content TEXT NOT NULL,
          embedding VECTOR(768),
          created_at TIMESTAMP DEFAULT NOW()
        );
        CREATE INDEX ON business_docs
        USING ivfflat (embedding vector_cosine_ops);
        """
        logging.error(error_msg)
        print(error_msg)
        raise e

async def embed_file(business_id: str, file_path: str, clear: bool = False) -> int:
    """
    Processes a file, chunks it, generates embeddings, and uploads to Supabase.
    Returns the number of chunks uploaded.
    """
    check_supabase_connection()
    supabase = get_supabase()

    if clear:
        logging.info(f"Clearing existing documents for business_id: {business_id}")
        supabase.table("business_docs").delete().eq("business_id", business_id).execute()

    logging.info(f"Loading file: {file_path}")
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
    elif ext in [".docx", ".doc"]:
        loader = Docx2txtLoader(file_path)
    elif ext == ".txt":
        loader = TextLoader(file_path)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")

    docs = loader.load()
    logging.info(f"Loaded {len(docs)} documents.")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len
    )
    chunks = text_splitter.split_documents(docs)
    logging.info(f"Split into {len(chunks)} chunks.")

    upload_data = []
    for i, chunk in enumerate(chunks):
        logging.info(f"Generating embedding for chunk {i+1}/{len(chunks)}...")
        embedding = await create_embedding(chunk.page_content)
        upload_data.append({
            "business_id": business_id,
            "content": chunk.page_content,
            "embedding": embedding
        })

    if upload_data:
        logging.info("Uploading chunks to Supabase...")
        supabase.table("business_docs").insert(upload_data).execute()
        logging.info("Upload complete.")
    else:
        logging.info("No chunks to upload.")

    return len(upload_data)

async def main():
    parser = argparse.ArgumentParser(description="Upload and embed business documents.")
    parser.add_argument("--business_id", type=str, required=True, help="The business ID")
    parser.add_argument("--file", type=str, required=True, help="Path to the document to process")
    parser.add_argument("--clear", action="store_true", help="Clear existing embeddings for the business before re-uploading")

    args = parser.parse_args()

    try:
        chunks_uploaded = await embed_file(args.business_id, args.file, args.clear)
        print(f"Successfully uploaded {chunks_uploaded} chunks for {args.business_id}.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())