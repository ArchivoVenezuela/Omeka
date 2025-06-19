import streamlit as st
import pandas as pd
from omeka_fetcher import fetch_all_omeka_items, omeka_items_to_dataframe
from utils.link_checker import check_links
from utils.image_checker import validate_images
from utils.completeness_checker import validate_metadata

st.title("🔍 Validate Live Metadata from Omeka")

API_URL = "https://archivovenezuela.com/raagya/api/items"

if st.button("📥 Fetch Metadata from Omeka"):
    with st.spinner("Fetching data..."):
        items = fetch_all_omeka_items(API_URL)
        if not items:
            st.error("❌ No items found or API call failed.")
        else:
            df = omeka_items_to_dataframe(items)
            st.success(f"✅ {len(df)} metadata items fetched.")
            st.dataframe(df)

            # Save for session use
            st.session_state["omeka_df"] = df

# If data is available, show checkers
if "omeka_df" in st.session_state:
    df = st.session_state["omeka_df"]

    st.subheader("🧪 Run Validations")

    if st.button("🔗 Check Link Validity"):
        link_df, df = check_links(df)
        st.write(link_df)
        st.download_button("⬇ Download Link Report", link_df.to_csv(index=False), file_name="omeka_link_report.csv")

    if st.button("🖼️ Validate Image URLs"):
        image_df, df = validate_images(df)
        st.write(image_df)
        st.download_button("⬇ Download Image Report", image_df.to_csv(index=False), file_name="omeka_image_report.csv")

    if st.button("✅ Check Metadata Completeness"):
        complete_df, df = validate_metadata(df)
        
        st.subheader("🧾 Completeness Summary")
        num_complete = sum(complete_df['Complete'] == '✅')
        total = len(complete_df)
        st.write(f"✅ Complete: {num_complete} / {total} items")
        st.dataframe(complete_df)
        
         # ✅ ENCODE in utf-8-sig to make Excel-friendly CSV
        completeness_csv = complete_df.to_csv(index=False).encode('utf-8-sig')
        updated_csv = df.to_csv(index=False).encode('utf-8-sig')
        
        st.download_button("⬇ Download Completeness Report", completeness_csv, file_name="omeka_completeness_report.csv")
        st.download_button("⬇ Download Updated Metadata", updated_csv, file_name="omeka_metadata_checked.csv")

    