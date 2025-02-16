import streamlit as st
import requests
from datetime import datetime, timedelta

# YouTube API Key
API_KEY = "AIzaSyAUnkZsuMgx9UaZthuG5rCvj3VUW1UVkqY"
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"

# Streamlit App Title
st.title("🚗 YouTube High-Performance Car & Truck Video Finder")

# Input Fields
days = st.number_input("Enter Days to Search (1-30):", min_value=1, max_value=30, value=7)

# High-Performance Automotive Keywords (Expanded)
keywords = [
    "2025 vehicle reviews", "Best trucks 2025", "Worst trucks 2025", "Pickup truck reviews",
    "Car buying advice", "Vehicle comparisons", "New car launches 2025", "Top SUVs 2025",
    "Luxury vehicle reviews", "Hybrid and electric trucks", "Affordable cars 2025",
    "2025 Ford Ranger", "2025 Honda Ridgeline", "2025 Ford F-150", "Pickup Truck Comparison",
    "New Trucks 2025", "Top 10 Cars 2025", "Truck Safety Ratings", "Luxury SUVs 2025",
    "Performance SUVs 2025", "Hybrid SUVs 2025", "Sports Cars 2025", "High-Tech SUVs 2025"
]

# Fetch Data Button
if st.button("Fetch Data"):
    try:
        # Calculate date range
        start_date = (datetime.utcnow() - timedelta(days=int(days))).isoformat("T") + "Z"
        all_results = []

        # Iterate over keywords
        for keyword in keywords:
            st.write(f"🔎 Searching for: **{keyword}**")

            # Define search parameters (Fetch 100+ results per keyword for better filtering)
            search_params = {
                "part": "snippet",
                "q": keyword,
                "type": "video",
                "order": "viewCount",
                "publishedAfter": start_date,
                "maxResults": 100,  # Fetching more data to filter
                "key": API_KEY,
            }

            # Fetch video data
            response = requests.get(YOUTUBE_SEARCH_URL, params=search_params)
            data = response.json()

            # Check API Response for Errors
            if "error" in data:
                st.error(f"🚨 YouTube API Error: {data['error']['message']}")
                break  # Stop execution if there's an API error

            # Check if "items" exist
            if "items" not in data or not data["items"]:
                st.warning(f"❌ No results for: {keyword}")
                continue

            videos = data["items"]
            video_ids = [video["id"]["videoId"] for video in videos if "id" in video and "videoId" in video["id"]]
            channel_ids = [video["snippet"]["channelId"] for video in videos if "snippet" in video and "channelId" in video["snippet"]]

            if not video_ids or not channel_ids:
                st.warning(f"⚠️ Skipping {keyword} - No valid video/channel data.")
                continue

            # Fetch video statistics
            stats_params = {"part": "statistics", "id": ",".join(video_ids), "key": API_KEY}
            stats_response = requests.get(YOUTUBE_VIDEO_URL, params=stats_params)
            stats_data = stats_response.json()

            # Fetch channel statistics
            channel_params = {"part": "statistics", "id": ",".join(channel_ids), "key": API_KEY}
            channel_response = requests.get(YOUTUBE_CHANNEL_URL, params=channel_params)
            channel_data = channel_response.json()

            if "items" not in stats_data or "items" not in channel_data:
                st.warning(f"⚠️ Data fetch failed for: {keyword}")
                continue

            stats = stats_data["items"]
            channels = channel_data["items"]

            # Filter only high-performance videos
            avg_views = sum(int(stat["statistics"].get("viewCount", 0)) for stat in stats) / len(stats) if stats else 0
            high_performance_threshold = avg_views * 10  # Videos must have 10x more views than the avg

            # **Dynamically filter only car-related videos**
            relevant_keywords = ["car", "truck", "suv", "vehicle", "review", "ford", "toyota", "tesla", "chevrolet"]
            
            for video, stat, channel in zip(videos, stats, channels):
                title = video["snippet"].get("title", "").lower()
                description = video["snippet"].get("description", "").lower()
                video_url = f"https://www.youtube.com/watch?v={video['id']['videoId']}"
                views = int(stat["statistics"].get("viewCount", 0))
                likes = int(stat["statistics"].get("likeCount", 0)) if "likeCount" in stat["statistics"] else 0
                comments = int(stat["statistics"].get("commentCount", 0)) if "commentCount" in stat["statistics"] else 0
                subs = int(channel["statistics"].get("subscriberCount", 0))
                engagement_rate = (likes + comments) / views if views > 0 else 0  # Engagement Rate

                # **Ensure videos match the niche by checking title/description**
                if (
                    views >= high_performance_threshold
                    and subs < 50000
                    and any(x in title or x in description for x in relevant_keywords)  # Ensures it’s car-related
                ):
                    all_results.append({
                        "Title": video["snippet"]["title"],
                        "Description": video["snippet"]["description"][:200],
                        "URL": video_url,
                        "Views": views,
                        "Likes": likes,
                        "Comments": comments,
                        "Subscribers": subs,
                        "Engagement Rate": round(engagement_rate * 100, 2)
                    })

        # Display results
        if len(all_results) >= 50:
            st.success(f"🎯 Found {len(all_results)} High-Performance Videos!")
            for result in all_results[:50]:  # Show top 50 results
                st.markdown(
                    f"**🎬 Title:** {result['Title']}  \n"
                    f"**📝 Description:** {result['Description']}  \n"
                    f"**🔗 URL:** [Watch Here]({result['URL']})  \n"
                    f"**👀 Views:** {result['Views']}  \n"
                    f"**👍 Likes:** {result['Likes']}  \n"
                    f"**💬 Comments:** {result['Comments']}  \n"
                    f"**📢 Subscribers:** {result['Subscribers']}  \n"
                    f"**📊 Engagement Rate:** {result['Engagement Rate']}%"
                )
                st.write("---")
        else:
            st.warning("😔 Not enough results. Try increasing the search days.")

    except Exception as e:
        st.error(f"🚨 Error: {e}")
