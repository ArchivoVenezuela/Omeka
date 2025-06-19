import streamlit as st
import pandas as pd
from utils.link_checker import check_links
from utils.image_checker import validate_images
from utils.completeness_checker import validate_metadata

st.title("📋 Metadata Quality Check")

uploaded_file = st.file_uploader("Upload a metadata CSV file", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("Preview of Uploaded Data:")
    st.dataframe(df.head())

    st.subheader("🧪 Run Checks")

    if st.button("🔗 Check Link Validity"):
        link_df, updated_df = check_links(df)
        st.subheader("🔎 Link Check Report")
        st.write(link_df)
        
        st.download_button("⬇ Download Link Report", link_df.to_csv(index=False), file_name="link_check_report.csv")
        st.download_button("⬇ Download Updated Metadata File", updated_df.to_csv(index=False), file_name="updated_metadata_with_links.csv")


    if st.button("🖼️ Validate Image URLs"):
        image_df, updated_df = validate_images(df)
        st.subheader("🧾 Image Validation Report")
        st.write(image_df)
        
        st.download_button("⬇ Download Image Report", image_df.to_csv(index=False), file_name="image_validation_report.csv")
        st.download_button("⬇ Download Updated Metadata File", updated_df.to_csv(index=False), file_name="updated_metadata_with_images.csv")


    if st.button("✅ Check Metadata Completeness"):
        complete_df, updated_df = validate_metadata(df)
        st.subheader("🧾 Metadata Completeness Report")
        st.write(complete_df)
        
        st.download_button("⬇ Download Completeness Report", complete_df.to_csv(index=False), file_name="metadata_completeness_report.csv")
        st.download_button("⬇ Download Updated Metadata File", updated_df.to_csv(index=False), file_name="updated_metadata_with_completeness.csv")

