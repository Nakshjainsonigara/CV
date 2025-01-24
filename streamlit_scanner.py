import streamlit as st
from PIL import Image
import numpy as np
from pyzbar.pyzbar import decode
import json
import av
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration
import cv2

st.set_page_config(
    page_title="Carbon Footprint Scanner",
    page_icon="🌱",
    layout="wide"
)

# RTC configuration for WebRTC
rtc_configuration = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

class QRCodeProcessor(VideoProcessorBase):
    def __init__(self):
        self.last_qr_data = None
        self.qr_detected = False

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        
        try:
            # Convert BGR to RGB
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            decoded_objects = decode(img_rgb)
            
            if decoded_objects and not self.qr_detected:
                for obj in decoded_objects:
                    try:
                        data = json.loads(obj.data.decode('utf-8'))
                        self.last_qr_data = data
                        self.qr_detected = True
                        # Draw rectangle around QR code
                        points = obj.polygon
                        if len(points) > 4:
                            hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
                            cv2.polylines(img, [hull], True, (0, 255, 0), 2)
                        else:
                            cv2.polylines(img, [np.array(points)], True, (0, 255, 0), 2)
                    except json.JSONDecodeError:
                        pass
            
            return av.VideoFrame.from_ndarray(img, format="bgr24")
        except Exception as e:
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
        try:
            webrtc_ctx = webrtc_streamer(
                key="qr-scanner",
                video_processor_factory=QRCodeProcessor,
                rtc_configuration=rtc_configuration,
                media_stream_constraints={"video": True, "audio": False},
            )
            
            if webrtc_ctx.video_processor:
                if webrtc_ctx.video_processor.qr_detected:
                    data = webrtc_ctx.video_processor.last_qr_data
                    if data:
                        display_product_info(data)
                        # Reset detection after displaying
                        webrtc_ctx.video_processor.qr_detected = False
        except Exception as e:
            st.error(f"Camera Error: {str(e)}")
            st.info("Please make sure you have granted camera permissions and are using HTTPS.")
    
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