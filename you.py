import streamlit as st
import requests
from datetime import datetime, timedelta
import isodate

# YouTube API endpoints and key
API_KEY = st.text_input("AIzaSyDE7pUZFUQa200OKUvkbEeEQDCtoNgk7-o:").strip()
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"

st.title("YouTube Viral Topics Tool")

# Input Fields
days = st.number_input("Enter Days to Search (1-30):", min_value=1, max_value=30, value=5)
category_input = st.text_input("Enter YouTube Category (e.g., Music, Gaming or numeric ID):").strip()
country = st.text_input("Enter Country Code (e.g., US, IN, GB):").strip().upper()

# New optional filters (set to 0 to ignore)
min_views = st.number_input("Minimum Video Views (optional):", min_value=0, value=0)
max_views = st.number_input("Maximum Video Views (optional, 0 for no limit):", min_value=0, value=0)
min_subs = st.number_input("Minimum Channel Subscribers (optional):", min_value=0, value=0)
max_subs = st.number_input("Maximum Channel Subscribers (optional, 0 for no limit):", min_value=0, value=0)
min_duration = st.number_input("Minimum Video Duration (minutes, optional):", min_value=0, value=0)
max_duration = st.number_input("Maximum Video Duration (minutes, optional, 0 for no limit):", min_value=0, value=0)

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

# Convert the input into a valid numeric category ID if possible
def get_category_id(cat_input):
    if not cat_input:
        return None
    if cat_input.isdigit():
        return cat_input
    cat_lower = cat_input.lower()
    return category_mapping.get(cat_lower)

category_id = get_category_id(category_input)

# Validate inputs
def validate_inputs():
    if not API_KEY:
        st.error("API Key is required.")
        return False
    if category_input and (category_id is None):
        st.error("Invalid category. Enter a numeric category ID or a valid category name (e.g., Music, Gaming).")
        return False
    if country and len(country) != 2:
        st.error("Invalid country code. Use a 2-letter ISO code (e.g., US).")
        return False
    return True

# Function to convert ISO 8601 duration to minutes
def duration_to_minutes(duration_str):
    try:
        duration = isodate.parse_duration(duration_str)
        return duration.total_seconds() / 60
    except Exception as e:
        return 0

# Fetch and filter data
if st.button("Fetch Data") and validate_inputs():
    try:
        start_date = (datetime.utcnow() - timedelta(days=days)).isoformat("T") + "Z"
        video_items = []
        next_page_token = None
        max_videos = 300  # adjust as needed
        
        # Fetch results in a loop (pagination)
        while True:
            search_params = {
                "part": "snippet",
                "type": "video",
                "order": "viewCount",
                "publishedAfter": start_date,
                "maxResults": 50,
                "key": API_KEY,
            }
            if country:
                search_params["regionCode"] = country
            if category_id:
                search_params["videoCategoryId"] = category_id
            if next_page_token:
                search_params["pageToken"] = next_page_token

            response = requests.get(YOUTUBE_SEARCH_URL, params=search_params)
            data = response.json()
            
            if "error" in data:
                st.error(f"API Error: {data['error'].get('message', 'Invalid request parameters.')}")
                break
            
            items = data.get("items", [])
            video_items.extend(items)
            
            if ("nextPageToken" in data) and (len(video_items) < max_videos):
                next_page_token = data["nextPageToken"]
            else:
                break
        
        if not video_items:
            st.warning("No results found. Check your filters and API key permissions.")
        else:
            # Get video IDs and channel IDs from search results
            video_ids = [item.get("id", {}).get("videoId") for item in video_items if item.get("id", {}).get("videoId")]
            channel_ids = list({item["snippet"].get("channelId") for item in video_items if item["snippet"].get("channelId")})
            
            # Fetch video details (contentDetails & statistics)
            video_details = {}
            for i in range(0, len(video_ids), 50):
                batch_ids = video_ids[i:i+50]
                vid_params = {
                    "part": "contentDetails,statistics,snippet",
                    "id": ",".join(batch_ids),
                    "key": API_KEY,
                }
                vid_resp = requests.get(YOUTUBE_VIDEOS_URL, params=vid_params)
                vid_data = vid_resp.json().get("items", [])
                for vid in vid_data:
                    video_details[vid["id"]] = vid
            
            # Fetch channel details (statistics)
            channel_details = {}
            for i in range(0, len(channel_ids), 50):
                batch_cids = channel_ids[i:i+50]
                ch_params = {
                    "part": "statistics",
                    "id": ",".join(batch_cids),
                    "key": API_KEY,
                }
                ch_resp = requests.get(YOUTUBE_CHANNEL_URL, params=ch_params)
                ch_data = ch_resp.json().get("items", [])
                for ch in ch_data:
                    channel_details[ch["id"]] = ch
            
            # Filter results based on optional parameters
            filtered_results = []
            for item in video_items:
                video_id = item.get("id", {}).get("videoId")
                if not video_id or video_id not in video_details:
                    continue
                vid = video_details[video_id]
                # Filter by video views
                view_count = int(vid["statistics"].get("viewCount", 0))
                if min_views and view_count < min_views:
                    continue
                if max_views and view_count > max_views:
                    continue
                
                # Filter by video duration (in minutes)
                duration_str = vid["contentDetails"].get("duration", "PT0M")
                duration_minutes = duration_to_minutes(duration_str)
                if min_duration and duration_minutes < min_duration:
                    continue
                if max_duration and duration_minutes > max_duration:
                    continue
                
                # Filter by channel subscribers
                channel_id = item["snippet"].get("channelId")
                subs = 0
                if channel_id in channel_details:
                    subs = int(channel_details[channel_id]["statistics"].get("subscriberCount", 0))
                if min_subs and subs < min_subs:
                    continue
                if max_subs and subs > max_subs:
                    continue
                
                # If passes all filters, add to results
                filtered_results.append({
                    "video_id": video_id,
                    "title": vid["snippet"].get("title", "N/A"),
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "views": view_count,
                    "duration": round(duration_minutes, 2),
                    "channel_id": channel_id,
                    "subscribers": subs
                })
            
            if not filtered_results:
                st.warning("No videos matched your filters.")
            else:
                st.success(f"Found {len(filtered_results)} matching videos!")
                for res in filtered_results:
                    st.markdown(f"**Title:** {res['title']}\n**URL:** [Watch Video]({res['url']})\n**Views:** {res['views']}  |  **Duration (min):** {res['duration']}  |  **Subscribers:** {res['subscribers']}")
                    st.write("---")
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
