from fastapi import APIRouter, Query, HTTPException
from serpapi import GoogleSearch
from config import SERP_API_KEY

attractions_router = APIRouter()

@attractions_router.get("/")
def get_top_destinations(city: str = Query(..., description="City Name")):
    try:
        if not SERP_API_KEY:
            raise HTTPException(status_code=500, detail="SerpAPI key is missing")

        params = {
            "engine": "google",
            "q": f"Top tourist attractions in {city}",
            "hl": "en",
            "gl": "us",
            "api_key": SERP_API_KEY
        }

        search = GoogleSearch(params)
        results = search.get_dict()

        # Extract attraction results
        if "organic_results" in results:
            attractions = results["organic_results"][:10]  # Get top 10 results
        else:
            raise HTTPException(status_code=404, detail="No attractions found")

        return {"message": "Top attractions found", "data": attractions}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
