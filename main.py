from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.flights import flights_router
from services.hotels import hotels_router
from services.attractions import attractions_router
from services.weather import weather_router
from embeddings import embeddings_router
from agents import agents_router

# Initialize FastAPI app
app = FastAPI(title="AI Travel Agent API 🚀")

# Enable CORS for Streamlit requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to ["http://localhost:8501"] if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Welcome to AI Travel Agent API 🚀"}

# Include routers
app.include_router(flights_router, prefix="/flights", tags=["flights"])
app.include_router(hotels_router, prefix="/hotels", tags=["hotels"])
app.include_router(attractions_router, prefix="/attractions", tags=["attractions"])
app.include_router(weather_router, prefix="/weather", tags=["weather"])
app.include_router(embeddings_router, prefix="/embeddings", tags=["embeddings"])
app.include_router(agents_router, prefix="/agents", tags=["travel agent"])
