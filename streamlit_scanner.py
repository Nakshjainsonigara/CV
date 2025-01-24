import streamlit as st
from PIL import Image
import numpy as np
from pyzbar.pyzbar import decode
import json
import cv2

st.set_page_config(
    page_title="Carbon Footprint Scanner",
    page_icon="🌱",
    layout="wide"
)

def process_uploaded_qr_code(image):
    try:
        decoded_objects = decode(np.array(image))
        if decoded_objects:
            for obj in decoded_objects:
                data = json.loads(obj.data.decode('utf-8'))
                st.success("QR Code detected!")
                display_product_info(data)
        else:
            st.warning("No QR code found in the image")
    except Exception as e:
        st.error(f"Error processing QR code: {str(e)}")

def display_product_info(data):
    st.write("### Product Information")
    st.write(f"**Name:** {data.get('name', 'N/A')}")
    st.write(f"**Carbon Footprint:** {data.get('co2_kg', 'N/A')} kg CO2")
    st.write(f"**Category:** {data.get('category', 'N/A')}")
    st.write(f"**Tip:** {data.get('sustainability_tip', 'N/A')}")

def main():
    st.title("Carbon Footprint Scanner")
    
    # Initialize camera
    cap = cv2.VideoCapture(0)
    frame_placeholder = st.empty()
    info_placeholder = st.empty()
    stop_button = st.button("Stop Camera")
    
    while cap.isOpened() and not stop_button:
        ret, frame = cap.read()
        if not ret:
            st.error("Failed to read from camera")
            break
        
        # Convert frame to RGB for display
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process frame for QR codes
        decoded_objects = decode(frame_rgb)
        
        for obj in decoded_objects:
            try:
                # Draw rectangle around QR code
                points = obj.polygon
                if len(points) > 4:
                    hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
                    cv2.polylines(frame_rgb, [hull], True, (0, 255, 0), 3)
                else:
                    points = np.array(points, dtype=np.int32)
                    cv2.polylines(frame_rgb, [points], True, (0, 255, 0), 3)
                
                # Decode and display data
                data = json.loads(obj.data.decode('utf-8'))
                with info_placeholder.container():
                    display_product_info(data)
            except json.JSONDecodeError:
                pass
        
        # Display the frame
        frame_placeholder.image(frame_rgb, channels="RGB")
        
        # Add a small delay
        cv2.waitKey(1)
    
    # Release camera when stopped
    cap.release()
    
    st.markdown("""
    ### Instructions:
    1. Allow camera access when prompted
    2. Point your camera at a QR code
    3. The app will automatically scan and display product information
    4. Click 'Stop Camera' when done
    
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