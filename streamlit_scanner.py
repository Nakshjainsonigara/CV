import streamlit as st
from PIL import Image
import numpy as np
from pyzbar.pyzbar import decode
import json

st.set_page_config(
    page_title="Carbon Footprint Scanner",
    page_icon="🌱",
    layout="wide"
)

def process_qr_code(image):
    try:
        decoded_objects = decode(np.array(image))
        if decoded_objects:
            for obj in decoded_objects:
                data = json.loads(obj.data.decode('utf-8'))
                st.success("QR Code detected!")
                st.write("### Product Information")
                st.write(f"**Name:** {data.get('name', 'N/A')}")
                st.write(f"**Carbon Footprint:** {data.get('co2_kg', 'N/A')} kg CO2")
                st.write(f"**Category:** {data.get('category', 'N/A')}")
                st.write(f"**Tip:** {data.get('sustainability_tip', 'N/A')}")
        else:
            st.warning("No QR code found in the image")
    except Exception as e:
        st.error(f"Error processing QR code: {str(e)}")

def main():
    st.title("Carbon Footprint Scanner")
    
    uploaded_file = st.file_uploader("Upload an image with QR code", type=['jpg', 'jpeg', 'png'])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Image', use_column_width=True)
        process_qr_code(image)
    
    st.markdown("""
    ### Instructions:
    1. Upload an image containing a QR code
    2. The app will automatically scan the QR code
    3. Product information will appear below
    
    ### Sample QR Code Format:
    ```json
    {
        "name": "Product Name",
        "co2_kg": 27.0,
        "category": "Category",
        "sustainability_tip": "Tip text"
    }
    ```
    """)

if __name__ == "__main__":
    main() 