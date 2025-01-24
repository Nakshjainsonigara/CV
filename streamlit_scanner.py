import streamlit as st
import cv2
import qrcode
import json
from pyzbar.pyzbar import decode
import numpy as np

class QRScanner:
    def __init__(self):
        self.product_db = {
            "organic_beef": {
                "name": "Organic Beef",
                "co2_kg": 27.0,
                "category": "meat",
                "sustainability_tip": "Consider plant-based alternatives to reduce emissions."
            },
            "plant_burger": {
                "name": "Plant-based Burger",
                "co2_kg": 3.5,
                "category": "vegetarian",
                "sustainability_tip": "Great choice! Plant-based foods generally have lower emissions."
            },
            "cola": {
                "name": "Coca Cola 330ml",
                "co2_kg": 0.5,
                "category": "beverages",
                "sustainability_tip": "Consider using reusable bottles and local drinks."
            }
        }

    def scan_qr(self, frame):
        decoded_objects = decode(frame)
        for obj in decoded_objects:
            try:
                data = json.loads(obj.data.decode('utf-8'))
                points = obj.polygon
                if len(points) == 4:
                    for i in range(4):
                        cv2.line(frame, 
                               (points[i].x, points[i].y),
                               (points[(i+1) % 4].x, points[(i+1) % 4].y),
                               (0, 255, 0), 3)
                return data
            except Exception as e:
                st.error(f"Error processing QR code: {e}")
        return None

def main():
    st.title("Carbon Footprint Scanner")
    
    scanner = QRScanner()
    
    # Create a placeholder for the camera feed
    camera_placeholder = st.empty()
    info_placeholder = st.empty()
    
    # Add start/stop button
    start_button = st.button("Start/Stop Camera")
    
    if 'camera_on' not in st.session_state:
        st.session_state.camera_on = False
    
    if start_button:
        st.session_state.camera_on = not st.session_state.camera_on
    
    if st.session_state.camera_on:
        cap = cv2.VideoCapture(0)
        
        try:
            while st.session_state.camera_on:
                ret, frame = cap.read()
                if not ret:
                    st.error("Failed to access camera")
                    break
                
                # Convert BGR to RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Scan for QR codes
                product_data = scanner.scan_qr(rgb_frame)
                
                # Display the frame
                camera_placeholder.image(rgb_frame, channels="RGB")
                
                # Display product information if found
                if product_data:
                    info_placeholder.markdown(f"""
                    ### Product Information
                    **Name:** {product_data['name']}
                    **Carbon Footprint:** {product_data['co2_kg']} kg CO2
                    **Tip:** {product_data['sustainability_tip']}
                    """)
                
        except Exception as e:
            st.error(f"Error: {str(e)}")
        finally:
            cap.release()
    else:
        camera_placeholder.empty()
        info_placeholder.empty()
    
    # Instructions
    st.markdown("""
    ### Instructions:
    1. Click 'Start/Stop Camera' to toggle the camera
    2. Show a QR code to the camera
    3. Product information will appear below
    """)

if __name__ == "__main__":
    main() 