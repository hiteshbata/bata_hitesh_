import logging
from typing import List, Dict, Any

from embeddings import get_supabase, create_embedding
from config import settings
from exceptions import RAGSearchError

async def perform_rag_search(query: str, business_id: str, top_k: int = 5, similarity_threshold: float = 0.5) -> List[str]:
    """
    Embeds the user's query and searches the vector database for the most relevant context.
    Returns a list of matching chunks. Does not raise an error on empty results.
    """
    try:
        # Generate embedding for the query
        query_embedding = await create_embedding(query)

        supabase = get_supabase()

        # Use Postgres RPC function if defined, or manually query.
        # Here we assume a match_business_docs function exists, or we use Supabase's python-client syntax
        # Using a custom RPC is standard for pgvector with Supabase.
        # If match_business_docs is not created, you must create it.
        # But we can also use `.select()` if the table allows it.
        # The recommended way is an RPC for pgvector. We will assume the RPC 'match_business_docs'

        # We need an RPC to do cosine similarity search in Supabase.
        # Let's write the query using RPC.
        response = supabase.rpc(
            "match_business_docs",
            {
                "query_embedding": query_embedding,
                "filter_business_id": business_id,
                "match_threshold": similarity_threshold,
                "match_count": top_k
            }
        ).execute()

        # Check if the result has data
        if hasattr(response, 'data') and response.data:
            return [row['content'] for row in response.data]
        elif isinstance(response, list):
             return [row['content'] for row in response]
        return []

    except Exception as e:
        # If RPC is not available, we could throw RAGSearchError
        # or maybe the table is missing.
        if "Could not find the function" in str(e):
             logging.error("You need to create an RPC function 'match_business_docs' in Supabase for pgvector search. See README.")
        logging.error(f"RAG Search failed: {e}")
        # We don't raise an exception here to allow graceful fallback to model knowledge,
        # but we could. For safety, return empty list and log.
        return []
