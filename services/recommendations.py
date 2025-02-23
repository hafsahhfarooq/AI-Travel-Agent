import faiss
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from fastapi import APIRouter, Query
from embeddings import get_embedding, search_similar_places

torch.device("cpu")  # Ensure the model runs on CPU

recommendations_router = APIRouter()

# Load TinyLlama model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("TinyLlama/TinyLlama-1.1B-Chat-v1.0")
model = AutoModelForCausalLM.from_pretrained("TinyLlama/TinyLlama-1.1B-Chat-v1.0")

def generate_recommendations(prompt: str, max_tokens: int = 300):
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(**inputs, max_new_tokens=max_tokens)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

@recommendations_router.get("/")
def get_recommendations(user_query: str = Query(..., description="Describe your travel preferences")):
    try:
        # Find similar places using FAISS
        similar_places = search_similar_places(user_query)

        # Generate travel recommendation prompt
        prompt = (
            f"Suggest a personalized travel itinerary for: {user_query}. "
            f"Include attractions, hotels, and activities. "
            f"Consider these places: {similar_places}"
        )

        # Generate recommendations using TinyLlama
        recommendations = generate_recommendations(prompt)

        return {"message": "Travel recommendations", "recommendations": recommendations}

    except Exception as e:
        return {"error": str(e)}
