import streamlit as st
from PIL import Image
import numpy as np
from pyzbar.pyzbar import decode
import json

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

def main():
    st.title("Carbon Footprint Scanner")
    
    # File uploader
    uploaded_file = st.file_uploader("Upload an image with QR code", type=['jpg', 'jpeg', 'png'])
    
    if uploaded_file is not None:
        # Display uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Image', use_column_width=True)
        
        # Convert to numpy array for QR scanning
        image_np = np.array(image)
        
        # Scan for QR codes
        try:
            decoded_objects = decode(image_np)
            
            if decoded_objects:
                for obj in decoded_objects:
                    try:
                        # Decode QR data
                        data = json.loads(obj.data.decode('utf-8'))
                        
                        # Display results
                        st.success("QR Code detected!")
                        st.write("### Product Information")
                        st.write(f"**Name:** {data.get('name', 'N/A')}")
                        st.write(f"**Carbon Footprint:** {data.get('co2_kg', 'N/A')} kg CO2")
                        st.write(f"**Category:** {data.get('category', 'N/A')}")
                        st.write(f"**Tip:** {data.get('sustainability_tip', 'N/A')}")
                        
                    except json.JSONDecodeError:
                        st.error("Invalid QR code format")
                    except Exception as e:
                        st.error(f"Error processing QR code: {str(e)}")
            else:
                st.warning("No QR code found in the image")
                
        except Exception as e:
            st.error(f"Error scanning image: {str(e)}")
    
    # Instructions
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