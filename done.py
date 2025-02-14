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
category_input = st.text_input("Enter YouTube Category (e.g., Music, Gaming or numeric ID):").strip()
country = st.text_input("Enter Country Code (e.g., US, IN, GB):").strip().upper()

# Mapping of common category names to numeric IDs
category_mapping = {
    "film & animation": "1",
    "autos & vehicles": "2",
    "music": "10",
    "pets & animals": "15",
    "sports": "17",
    "short movies": "18",
    "travel & events": "19",
    "gaming": "20",
    "videoblogging": "21",
    "people & blogs": "22",
    "comedy": "23",
    "entertainment": "24",
    "news & politics": "25",
    "howto & style": "26",
    "education": "27",
    "science & technology": "28",
    "nonprofits & activism": "29",
}

# Convert the input into a valid numeric category ID
def get_category_id(cat_input):
    # if the input is numeric, return it
    if cat_input.isdigit():
        return cat_input
    # else, try to map the name to a numeric ID (case-insensitive)
    cat_lower = cat_input.lower()
    return category_mapping.get(cat_lower)

category_id = get_category_id(category_input)

# Validation Checks
def validate_inputs():
    if not API_KEY:
        st.error("API Key is required.")
        return False
    if not category_id:
        st.error("Invalid category. Enter a numeric category ID or a valid category name (e.g., Music, Gaming).")
        return False
    if len(country) != 2:
        st.error("Invalid country code. Use a 2-letter ISO code (e.g., US).")
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
            "videoCategoryId": category_id,
            "publishedAfter": start_date,
            "maxResults": 10,
            "key": API_KEY,
        }
        
        response = requests.get(YOUTUBE_SEARCH_URL, params=search_params)
        data = response.json()

        if "error" in data:
            st.error(f"API Error: {data['error'].get('message', 'Invalid request parameters.')}")
        elif not data.get("items"):
            st.warning("No results found. Check category, country code, or API key permissions.")
        else:
            for video in data["items"]:
                video_id = video.get("id", {}).get("videoId")
                title = video["snippet"].get("title", "N/A")
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                st.markdown(f"**Title:** {title}  \n**URL:** [Watch Video]({video_url})")
                st.write("---")
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
