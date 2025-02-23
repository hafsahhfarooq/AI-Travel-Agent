from fastapi import APIRouter, HTTPException, Query
from serpapi import GoogleSearch
from config import flights_secret_key  # Ensure this is correctly set up

flights_router = APIRouter()

@flights_router.get("/search", tags=["flights"])
def get_flight_prices(
    origin: str = Query(..., description="Departure Airport Code (e.g., JFK)"),
    destination: str = Query(..., description="Arrival Airport Code (e.g., LAX)"),
    depart_date: str = Query(..., description="Departure Date (YYYY-MM-DD)"),
    return_date: str = Query(..., description="Return Date (YYYY-MM-DD)"),
    currency: str = Query("USD", description="Currency (default: USD)")
):
    try:
        params = {
            "engine": "google_flights",
            "departure_id": origin,
            "arrival_id": destination,
            "outbound_date": depart_date,
            "return_date": return_date,
            "currency": currency,
            "hl": "en",
            "api_key": flights_secret_key,
        }

        search = GoogleSearch(params)
        results = search.get_dict()

        # Debugging: Print API response
        print("SerpAPI Response:", results)

        if "error" in results:
            raise HTTPException(status_code=400, detail=results["error"])

        return {"message": "Flight search results", "data": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
