import streamlit as st
from PIL import Image
import numpy as np
from pyzbar.pyzbar import decode
import json
from io import BytesIO

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
    
    # Add a tab selection for camera or file upload
    tab1, tab2 = st.tabs(["📸 Camera", "📁 File Upload"])
    
    with tab1:
        st.write("### Camera Scanner")
        # Add camera input
        camera_image = st.camera_input("Take a picture of a QR code")
        
        if camera_image is not None:
            # Process the camera image
            image = Image.open(camera_image)
            process_qr_code(image)
    
    with tab2:
        st.write("### File Upload")
        uploaded_file = st.file_uploader("Upload an image with QR code", type=['jpg', 'jpeg', 'png'])
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption='Uploaded Image', use_column_width=True)
            process_qr_code(image)
    
    st.markdown("""
    ### Instructions:
    1. Choose either Camera or File Upload tab
    2. For Camera: Allow camera access and take a picture of a QR code
    3. For File Upload: Upload an image containing a QR code
    4. The app will automatically scan and display product information
    
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