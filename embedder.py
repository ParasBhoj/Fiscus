import numpy as np
from openai import AsyncOpenAI
import config

# Initialize Async client based on config
client = AsyncOpenAI(
    api_key=config.LLM_API_KEY,
    base_url=config.LLM_BASE_URL if config.LLM_BASE_URL else None
)

async def generate_embedding(text: str) -> bytes:
    """
    Generates a vector embedding for the given text using the configured LLM API.
    Returns the embedding as a bytes BLOB suitable for SQLite storage.
    """
    if not text:
        return b""
        
    try:
        # If using Gemini's OpenAI compat endpoint, the model is usually gemini-embedding-2
        # If OpenAI, it's usually text-embedding-3-small or text-embedding-ada-002
        embedding_model = "gemini-embedding-2" if "generativelanguage" in str(config.LLM_BASE_URL) else "text-embedding-3-small"
        
        response = await client.embeddings.create(
            input=[text],
            model=embedding_model
        )
        
        # Get the float array
        vector = response.data[0].embedding
        
        # Convert to numpy array of float32, then to bytes for SQLite BLOB storage
        vector_np = np.array(vector, dtype=np.float32)
        return vector_np.tobytes()
        
    except Exception as e:
        print(f"[!] Embedding generation error: {e}")
        return b""

def compute_cosine_similarity(vec1_bytes: bytes, vec2_bytes: bytes) -> float:
    """
    Utility function to compute cosine similarity between two BLOB embeddings.
    """
    if not vec1_bytes or not vec2_bytes:
        return 0.0
        
    v1 = np.frombuffer(vec1_bytes, dtype=np.float32)
    v2 = np.frombuffer(vec2_bytes, dtype=np.float32)
    
    # Catch dimension mismatch (e.g. between mock 1536d data and live 3072d data)
    if len(v1) != len(v2):
        print(f"[!] Dimension mismatch in embeddings: {len(v1)} vs {len(v2)}")
        return 0.0
        
    # Compute cosine similarity
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    
    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0
        
    return float(dot_product / (norm_v1 * norm_v2))
