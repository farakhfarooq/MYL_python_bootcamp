import os
import zipfile
import requests
import pandas as pd
import streamlit as st
from bs4 import BeautifulSoup
from io import BytesIO
from urllib.parse import urljoin  # Import for handling relative URLs

# Streamlit App Title
st.title("🌐 Web Scraper App")
st.subheader("Scrape Text, Images, or Attributes from Any Website")

# User Inputs
url = st.text_input("Enter Website URL:", "https://example.com")
tag = st.text_input("Enter HTML Tag to Scrape:", "img")
class_name = st.text_input("Enter Class Name (optional):", "")
value_type = st.selectbox("Select Data Type:", ["Text", "Image", "Attribute"])
attribute = st.text_input("Enter Attribute (if applicable, e.g., 'src' for images)", "")

if st.button("Scrape Data"):
    if not url.strip():
        st.error("Please enter a valid website URL")
    else:
        # Send HTTP request
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            st.error("Failed to fetch the webpage.")
        else:
            soup = BeautifulSoup(response.text, "html.parser")
            
            if class_name.strip():
                elements = soup.find_all(tag, class_=class_name)
            else:
                elements = soup.find_all(tag)
            
            data = []
            image_urls = []
            
            if value_type == "Image":
                os.makedirs("scraped_images", exist_ok=True)
                
                for index, element in enumerate(elements):
                    if element.has_attr(attribute):
                        img_url = element[attribute]
                        img_url = urljoin(url, img_url)  # Ensure absolute URL
                        title = element.get("alt", "No Title")  # Get alt text as title
                        data.append({"Image URL": img_url, "Title": title})
                        image_urls.append((img_url, f"image_{index}.jpg"))
                
                # Show Preview in Streamlit
                st.write("### Scraped Image URLs Preview:")
                st.dataframe(pd.DataFrame(data).head())
                
                # Download images as ZIP
                zip_buffer = BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zipf:
                    for img_url, filename in image_urls:
                        response = requests.get(img_url, stream=True)
                        if response.status_code == 200:
                            with zipf.open(filename, "w") as f:
                                f.write(response.content)
                zip_buffer.seek(0)
                
                st.success("Images Scraped Successfully!")
                st.download_button("Download Images as ZIP", zip_buffer, "scraped_images.zip", "application/zip")
            else:
                for element in elements:
                    if value_type == "Text":
                        data.append({"Scraped Data": element.get_text(strip=True)})
                    elif value_type == "Attribute" and attribute:
                        data.append({"Scraped Data": element.get(attribute, "N/A")})
                
                # Convert to DataFrame
                df = pd.DataFrame(data)
                
                # Show Preview in Streamlit
                st.write("### Scraped Data Preview:")
                st.dataframe(df.head())
                
                # Save to Excel
                excel_buffer = BytesIO()
                df.to_excel(excel_buffer, index=False)
                excel_buffer.seek(0)
                
                st.success("Data Scraped Successfully!")
                st.download_button("Download Data as Excel", excel_buffer, "scraped_data.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
