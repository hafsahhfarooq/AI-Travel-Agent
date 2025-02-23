from fastapi import APIRouter, Query
from datetime import datetime, timedelta
from config import SERP_API_KEY
from serpapi import GoogleSearch

hotels_router = APIRouter()

@hotels_router.get("/")
def search_hotels(
    destination: str = Query(..., description="Hotel Location"),
    check_in: str = Query((datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d"), description="Check-in Date"),
    check_out: str = Query((datetime.today() + timedelta(days=2)).strftime("%Y-%m-%d"), description="Check-out Date"),
    adults: int = Query(2, description="Number of adults")
):
    params = {
        "engine": "google_hotels",
        "q": destination,
        "check_in_date": check_in,
        "check_out_date": check_out,
        "adults": str(adults),
        "currency": "USD",
        "gl": "us",
        "hl": "en",
        "api_key": SERP_API_KEY
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    return {"message": "Hotel search results", "data": results}
