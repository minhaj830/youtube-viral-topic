import streamlit as st
import requests
from datetime import datetime, timedelta

# YouTube API Key
API_KEY = "AIzaSyAI57lPDf9y3DDn_kmRzkR0ATTkYDnDgpg"
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"

# Streamlit App Title
st.title("YouTube Viral Topics Tool")

# Input Fields
days = st.number_input("Enter Days to Search (1-30):", min_value=1, max_value=30, value=5)
category = st.text_input("Enter YouTube Category ID (e.g., 10 for Music, 20 for Gaming):")
country = st.text_input("Enter Country Code (e.g., US, IN, GB):")
min_subs = st.number_input("Minimum Subscribers:", min_value=0, value=0)
min_views = st.number_input("Minimum Views:", min_value=0, value=0)

# Fetch Data Button
if st.button("Fetch Data"):
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
        data = response.json().get("items", [])

        if not data:
            st.warning("No results found. Please check your inputs.")

        for video in data:
            title = video["snippet"].get("title", "N/A")
            video_url = f"https://www.youtube.com/watch?v={video['id']['videoId']}"
            st.markdown(f"**Title:** {title}  \n**URL:** [Watch]({video_url})")
            st.write("---")
    except Exception as e:
        st.error(f"An error occurred: {e}")
