from langgraph.graph import StateGraph
from langchain.schema import SystemMessage, HumanMessage
from langchain.memory import ConversationBufferMemory
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import json
from fastapi import APIRouter
from fastapi import HTTPException
from pydantic import BaseModel
from services.flights import get_flight_prices
from services.hotels import search_hotels
from services.attractions import get_top_destinations
from services.weather import get_weather
from embeddings import search_similar_places

agents_router = APIRouter()

# Load TinyLlama for local inference
MODEL_NAME = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float32,
    device_map="cpu"
)


class TravelState(BaseModel):
    user_input: str = ""
    trip_details: dict = {}
    recommendations: str = ""
    feedback: str = ""


memory = ConversationBufferMemory()
graph = StateGraph(TravelState)


# Function to generate AI-based recommendations
def generate_text(prompt: str, max_tokens: int = 300):
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(**inputs, max_new_tokens=max_tokens)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)


# Extract structured details from user input
def parse_user_query(state: TravelState):
    prompt = f"Extract key travel details (destination, dates, preferences) from: {state.user_input}."
    response = generate_text(prompt, max_tokens=100)

    try:
        state.trip_details = json.loads(response)  # Safe parsing
    except json.JSONDecodeError:
        state.trip_details = {"destination": "Paris"}  # Default fallback

    return state


graph.add_node("query_parser", parse_user_query)


# Fetch real-time travel data
def fetch_travel_data(state: TravelState):
    details = state.trip_details
    city = details.get("destination", "Paris")
    departure = details.get("departure_city", "NYC")
    depart_date = details.get("depart_date", "2025-05-01")
    return_date = details.get("return_date", "2025-05-10")

    flights_data = get_flight_prices(departure, city, depart_date, return_date)
    hotels_data = search_hotels(city)
    attractions_data = get_top_destinations(city)
    weather_data = get_weather(city)

    state.trip_details.update({
        "flights": flights_data,
        "hotels": hotels_data,
        "attractions": attractions_data,
        "weather": weather_data
    })

    return state


graph.add_node("fetch_data", fetch_travel_data)
graph.add_edge("query_parser", "fetch_data")


# Generate AI-based travel recommendations
def generate_recommendations(state: TravelState):
    details = state.trip_details
    similar_places = search_similar_places(details.get("destination", "Paris"))

    prompt = f"""
    Create a personalized travel itinerary for {details['destination']} including:
    - Top attractions
    - Recommended hotels
    - Weather conditions
    - Flights information
    - Alternative places to visit: {similar_places}
    """

    state.recommendations = generate_text(prompt, max_tokens=500)
    return state


graph.add_node("recommend", generate_recommendations)
graph.add_edge("fetch_data", "recommend")


# Format final recommendations for structured output
def format_recommendations(state: TravelState):
    details = state.trip_details
    similar_places = search_similar_places(details.get("destination", "Paris"))

    response = f"""
    ✈️ **Destination:** {details.get("destination", "Paris")}
    🏨 **Hotels:** {details.get("hotels", "Not Found")}
    🏝 **Top Attractions:** {details.get("attractions", "Not Found")}
    ☀️ **Weather:** {details.get("weather", "Not Available")}
    🌍 **Similar Places to Explore:** {similar_places}
    """

    state.recommendations = response
    return state


graph.add_node("format_recommendations", format_recommendations)
graph.add_edge("recommend", "format_recommendations")


# Feedback loop to refine itinerary
def feedback_loop(state: TravelState):
    feedback_prompt = f"Adjust the itinerary based on this feedback: {state.feedback}"
    state.recommendations = generate_text(feedback_prompt, max_tokens=300)
    return state


graph.add_node("feedback_loop", feedback_loop)
graph.add_edge("format_recommendations", "feedback_loop")
graph.add_edge("feedback_loop", "recommend")  # Continuous loop for feedback

graph.set_entry_point("query_parser")
app = graph.compile()


# API Request Model
class TravelRequest(BaseModel):
    user_input: str
    user_feedback: str = ""


@agents_router.post("/travel_agent/", response_model=dict, status_code=200)
def run_travel_agent(request: TravelRequest):
    if not request.user_input:
        raise HTTPException(status_code=400, detail="User input is required")

    state = TravelState(user_input=request.user_input, feedback=request.user_feedback)

    try:
        result = app.invoke(state)
        return {"recommendations": result.recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")