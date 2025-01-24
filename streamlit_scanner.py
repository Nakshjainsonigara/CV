import streamlit as st
from PIL import Image
import numpy as np
from pyzbar.pyzbar import decode
import json
import av
import cv2
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase

st.set_page_config(
    page_title="Carbon Footprint Scanner",
    page_icon="🌱",
    layout="wide"
)

class QRCodeProcessor(VideoProcessorBase):
    def __init__(self):
        self.qr_data = None
        self.last_detection = None

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        
        # Process the frame for QR codes
        try:
            decoded_objects = decode(img)
            if decoded_objects:
                for obj in decoded_objects:
                    try:
                        # Draw rectangle around QR code
                        points = obj.polygon
                        if len(points) > 4:
                            hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
                            cv2.polylines(img, [hull], True, (0, 255, 0), 3)
                        else:
                            points = np.array(points, dtype=np.int32)
                            cv2.polylines(img, [points], True, (0, 255, 0), 3)
                        
                        # Try to decode QR data
                        data = json.loads(obj.data.decode('utf-8'))
                        if data != self.last_detection:  # Only update if new QR code
                            self.qr_data = data
                            self.last_detection = data
                            
                        # Add text overlay
                        cv2.putText(img, "QR Code Detected!", 
                                  (points[0][0], points[0][1] - 10),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                            
                    except json.JSONDecodeError:
                        pass
                        
        except Exception as e:
            pass

        return av.VideoFrame.from_ndarray(img, format="bgr24")

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
    
    tab1, tab2 = st.tabs(["📸 Live Scanner", "📁 File Upload"])
    
    with tab1:
        st.write("### Live QR Code Scanner")
        
        # Create placeholder for product info
        info_placeholder = st.empty()
        
        # Initialize WebRTC streamer
        ctx = webrtc_streamer(
            key="qr-scanner",
            video_processor_factory=QRCodeProcessor,
            media_stream_constraints={"video": True, "audio": False},
        )
        
        # Check for QR code data
        if ctx.video_processor:
            if ctx.video_processor.qr_data:
                with info_placeholder.container():
                    display_product_info(ctx.video_processor.qr_data)
    
    with tab2:
        st.write("### File Upload")
        uploaded_file = st.file_uploader("Upload an image with QR code", type=['jpg', 'jpeg', 'png'])
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption='Uploaded Image', use_column_width=True)
            process_uploaded_qr_code(image)
    
    st.markdown("""
    ### Instructions:
    1. Choose either Live Scanner or File Upload tab
    2. For Live Scanner: Allow camera access and point your camera at a QR code
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