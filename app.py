import streamlit as st
import requests
from datetime import datetime, timedelta

# Base API URL (Change if hosted remotely)
BASE_URL = "https://ai-travel-agent-0zxc.streamlit.app/"

# Streamlit App
st.set_page_config(page_title="AI Travel Agent", layout="wide")
st.title("✈️ AI Travel Agent")

# Sidebar Navigation
page = st.sidebar.selectbox(
    "Choose a Service",
    ["Flight Search", "Hotel Search", "Tourist Attractions", "Weather Info", "Travel Recommendations"]
)

# -----------------------------------
# 🛫 FLIGHT SEARCH
# -----------------------------------
if page == "Flight Search":
    st.header("Flight Search")

    with st.form("flight_search_form"):
        origin = st.text_input("Origin Airport Code (e.g., JFK):")
        destination = st.text_input("Destination Airport Code (e.g., LAX):")
        depart_date = st.date_input("Departure Date")
        return_date = st.date_input("Return Date")
        currency = st.selectbox("Currency:", ["USD", "EUR", "GBP"])
        submit = st.form_submit_button("Search Flights")

    if submit:
        params = {
            "origin": origin,
            "destination": destination,
            "depart_date": depart_date.strftime("%Y-%m-%d"),
            "return_date": return_date.strftime("%Y-%m-%d"),
            "currency": currency
        }

        response = requests.get(f"{BASE_URL}/flights/search", params=params)
        if response.status_code == 200:
            data = response.json()["data"]
            st.success("Flights Found!")
            st.json(data)
        else:
            st.error("No flights found or API error!")

# -----------------------------------
# 🏨 HOTEL SEARCH
# -----------------------------------
elif page == "Hotel Search":
    st.header("Hotel Search")

    with st.form("hotel_search_form"):
        destination = st.text_input("Hotel Location:")
        check_in = st.date_input("Check-in Date", min_value=datetime.today() + timedelta(days=1))
        check_out = st.date_input("Check-out Date", min_value=check_in + timedelta(days=1))
        adults = st.number_input("Number of Adults", min_value=1, value=2)
        submit = st.form_submit_button("Search Hotels")

    if submit:
        params = {
            "destination": destination,
            "check_in": check_in.strftime("%Y-%m-%d"),
            "check_out": check_out.strftime("%Y-%m-%d"),
            "adults": adults
        }

        response = requests.get(f"{BASE_URL}/hotels", params=params)
        if response.status_code == 200:
            data = response.json()["data"]
            st.success("Hotels Found!")
            st.json(data)
        else:
            st.error("No hotels found or API error!")

# -----------------------------------
# 🏝️ TOURIST ATTRACTIONS
# -----------------------------------
elif page == "Tourist Attractions":
    st.header("Top Tourist Attractions")

    with st.form("attractions_form"):
        city = st.text_input("Enter City Name:")
        submit = st.form_submit_button("Find Attractions")

    if submit:
        response = requests.get(f"{BASE_URL}/attractions", params={"city": city})
        if response.status_code == 200:
            attractions = response.json()["data"]
            st.success(f"Top attractions in {city}:")
            for attr in attractions:
                st.write(f"🔹 {attr['title']} - [Read More]({attr['link']})")
        else:
            st.error("No attractions found or API error!")

# -----------------------------------
# 🌤️ WEATHER INFORMATION
# -----------------------------------
elif page == "Weather Info":
    st.header("Current Weather Information")

    with st.form("weather_form"):
        city = st.text_input("Enter City Name:")
        submit = st.form_submit_button("Get Weather")

    if submit:
        response = requests.get(f"{BASE_URL}/weather", params={"city": city})
        if response.status_code == 200:
            data = response.json()
            st.success(f"Weather in {data['location']}, {data['country']}")
            st.write(f"🌡️ Temperature: {data['temperature']}°C")
            st.write(f"☁️ Condition: {data['condition']}")
            st.image(f"http:{data['icon']}", width=100)
        else:
            st.error("Could not fetch weather data!")

# -----------------------------------
# 🧳 TRAVEL RECOMMENDATIONS
# -----------------------------------
elif page == "Travel Recommendations":
    st.header("AI-Powered Travel Recommendations")

    with st.form("recommendations_form"):
        user_query = st.text_area("Describe your travel preferences (e.g., 'I want a tropical beach vacation with adventure sports.')")
        submit = st.form_submit_button("Get Recommendations")

    if submit:
        response = requests.get(f"{BASE_URL}/agents/recommendations", params={"user_query": user_query})
        if response.status_code == 200:
            recommendations = response.json()["recommendations"]
            st.success("Here are your personalized travel recommendations:")
            st.write(recommendations)
        else:
            st.error("Could not generate recommendations!")
