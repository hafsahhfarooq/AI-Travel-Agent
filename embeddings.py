import faiss
import numpy as np
from fastapi import APIRouter, Query
from sentence_transformers import SentenceTransformer

embeddings_router = APIRouter()

# Initialize Sentence Transformer model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Precomputed embeddings for popular places
places = ["Eiffel Tower, Paris", "Statue of Liberty, New York", "Colosseum, Rome"]
place_embeddings = np.array([model.encode(place) for place in places])

# Initialize FAISS index
dimension = place_embeddings.shape[1]  # Vector size of embeddings
index = faiss.IndexFlatL2(dimension)
index.add(place_embeddings)
place_dict = {i: place for i, place in enumerate(places)}

# Function to generate embeddings
def get_embedding(text: str):
    return model.encode(text)

# Function to search similar places
def search_similar_places(query: str, k: int = 3):
    query_embedding = get_embedding(query).reshape(1, -1)
    distances, indices = index.search(query_embedding, k)
    return [place_dict[i] for i in indices[0]]

# FastAPI endpoint to search similar places
@embeddings_router.get("/search_places/")
def search_places(query: str = Query(..., description="Enter a place or landmark"),
                  k: int = Query(3, description="Number of results")):
    results = search_similar_places(query, k)
    return {"query": query, "similar_places": results}
