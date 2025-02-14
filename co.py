import streamlit as st
import requests
from datetime import datetime, timedelta

# YouTube API Key
API_KEY = st.text_input("AIzaSyAI57lPDf9y3DDn_kmRzkR0ATTkYDnDgpg:").strip()
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"

# Streamlit App Title
st.title("YouTube Viral Topics Tool")

# Input Fields
days = st.number_input("Enter Days to Search (1-30):", min_value=1, max_value=30, value=5)
category = st.text_input("Enter YouTube Category ID (e.g., 10 for Music, 20 for Gaming):").strip()
country = st.text_input("Enter Country Code (e.g., US, IN, GB):").strip().upper()

# Validation Checks
def validate_inputs():
    if not API_KEY:
        st.error("API Key is required.")
        return False
    if not category.isdigit():
        st.error("Invalid category ID. Must be numeric.")
        return False
    if len(country) != 2:
        st.error("Invalid country code. Use a 2-letter ISO code.")
        return False
    return True

# Fetch Data Button
if st.button("Fetch Data") and validate_inputs():
    try:
        start_date = (datetime.utcnow() - timedelta(days=days)).isoformat("T") + "Z"
        search_params = {
            "part": "snippet",
            "type": "video",
            "order": "viewCount",
            "regionCode": country,
            "videoCategoryId": category,
            "publishedAfter": start_date,
            "maxResults": 10,
            "key": API_KEY,
        }

        response = requests.get(YOUTUBE_SEARCH_URL, params=search_params)
        data = response.json()

        if "error" in data:
            st.error(f"API Error: {data['error'].get('message', 'Invalid request parameters.')}")
        elif not data.get("items"):
            st.warning("No results found. Check category ID, country code, or API key permissions.")
        else:
            for video in data["items"]:
                video_id = video.get("id", {}).get("videoId")
                title = video["snippet"].get("title", "N/A")
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                st.markdown(f"**Title:** {title}  \n**URL:** [Watch]({video_url})")
                st.write("---")
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
