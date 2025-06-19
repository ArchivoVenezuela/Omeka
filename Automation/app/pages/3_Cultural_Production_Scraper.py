import streamlit as st
import pandas as pd
import datetime
import io
import sys
import os
from scrapers.youtube_api import scrape_youtube_api
from scrapers.google_books import scrape_google_books
from scrapers.soundcloud import scrape_soundcloud
from scrapers.spotify import scrape_spotify





# 👇 Allow import from web-scraper folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../web-scraper')))

from scrapers.goodreads import scrape_goodreads
# from scrapers.spotify import scrape_spotify  # We'll create this soon

st.set_page_config(page_title="Cultural Scraper", layout="wide")
st.title("🌍 Venezuelan Cultural Production Scraper")

# Platform selection
platform = st.selectbox("Choose a platform:", [
    "Goodreads", "YouTube", "Google Books","Spotify",
])




# Keyword input
query = st.text_input("Enter search keyword (e.g., 'Venezuela')", value="Venezuela")

if st.button("🔍 Start Scraping"):
    with st.spinner(f"Scraping {platform} for '{query}'..."):
        if platform == "Goodreads":
            results = scrape_goodreads(query)
        elif platform == "YouTube":
            YOUTUBE_API_KEY = "AIzaSyAalRfVNk-YQljZpedIlsDh7KO4fmqf2YY"  # TEMPORARY: later use env
            results = scrape_youtube_api(query, YOUTUBE_API_KEY)
        elif platform == "Google Books":
            results = scrape_google_books(query)
        elif platform == "Spotify":
            results = scrape_spotify(query)
        
        







        filtered = [r for r in results if isinstance(r, dict) and r.get("title")]

        if filtered:
            df = pd.DataFrame(filtered)
            st.success(f"✅ Found {len(filtered)} items.")
            st.dataframe(df)

            # Download CSV
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False, encoding="utf-8-sig")

            st.download_button(
                label="⬇️ Download CSV",
                data=csv_buffer.getvalue(),
                file_name=f"{platform.lower()}_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M')}.csv",
                mime="text/csv"
                )

        else:
            st.warning("❌ No results found or scraping failed.")
