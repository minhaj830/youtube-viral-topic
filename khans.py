import streamlit as st
import requests
from datetime import datetime, timedelta

# YouTube API Key
API_KEY = st.text_input("AIzaSyAI57lPDf9y3DDn_kmRzkR0ATTkYDnDgpg:")
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"

# Streamlit App Title
st.title("YouTube Viral Topics Tool")

# Input Fields
days = st.number_input("Enter Days to Search (1-30):", min_value=1, max_value=30, value=5)
category = st.text_input("Enter YouTube Category ID (e.g., 10 for Music, 20 for Gaming):")
country = st.text_input("Enter Country Code (e.g., US, IN, GB):")

# Fetch Data Button
if st.button("Fetch Data"):
    if not API_KEY:
        st.error("API Key is required.")
    else:
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
                st.warning("No results found. Check the category ID and country code.")
            else:
                for video in data["items"]:
                    title = video["snippet"].get("title", "N/A")
                    video_url = f"https://www.youtube.com/watch?v={video['id']['videoId']}"
                    st.markdown(f"**Title:** {title}  \n**URL:** [Watch]({video_url})")
                    st.write("---")
        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")
