import os
import base64
import json
import streamlit as st
from openai import OpenAI
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
from PIL import Image
import av
from dotenv import load_dotenv
load_dotenv()
# Configuration
token = os.getenv("token")
endpoint = "https://models.inference.ai.azure.com"
model_name = "gpt-4o"

# Emission factors (kg CO₂ per kg of material)
EMISSION_FACTORS = {
    "plastic": 6.0,
    "cotton": 8.0,
    "glass": 1.2,
    "aluminum": 8.1,
    "paper": 1.4,
    "steel": 2.8,
    "default": 5.0
}

def get_image_data_url(image_file) -> str:
    """Convert image file to base64 data URL"""
    try:
        return f"data:image/jpeg;base64,{base64.b64encode(image_file.read()).decode('utf-8')}"
    except Exception as e:
        st.error(f"Error: Could not process image file {e}")
        return None

def calculate_co2(materials: list, weight_kg: float, origin: str) -> float:
    """Calculate CO2 emissions based on materials and origin"""
    material_emissions = sum(EMISSION_FACTORS.get(m.lower(), EMISSION_FACTORS["default"]) * weight_kg 
                           for m in materials)
    
    # Add manufacturing bonus for coal-heavy countries
    manufacturing_bonus = 0.5 if origin.lower() in ["india", "china"] else 0
    return round(material_emissions + manufacturing_bonus, 2)

# Initialize OpenAI client
client = OpenAI(base_url=endpoint, api_key=token)

# Streamlit App
st.title("🌍 Carbon Footprint Scanner")
st.write("Capture an image using your camera or upload an existing image to calculate its carbon footprint.")

# Option to choose between camera and file upload
option = st.radio("Choose input method:", ("Use Camera", "Upload Image"))

image_data_url = None

if option == "Use Camera":
    # VideoProcessor class to capture frames from the camera
    class VideoProcessor(VideoTransformerBase):
        def __init__(self):
            self.frame = None

        def recv(self, frame):
            self.frame = frame.to_ndarray(format="bgr24")  # Convert frame to numpy array
            return frame

    # Start the WebRTC streamer
    ctx = webrtc_streamer(
        key="camera",
        video_processor_factory=VideoProcessor,
        rtc_configuration={
            "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]  # Add STUN server
        }
    )

    # Add a "Take Photo" button
    if ctx.video_processor:
        if st.button("Take Photo"):
            frame = ctx.video_processor.frame
            if frame is not None:
                # Convert the frame to a PIL image
                image = Image.fromarray(frame)
                st.image(image, caption='Captured Image.', use_column_width=True)
                st.write("Analyzing...")

                # Save the image temporarily to convert it to a data URL
                image.save("captured_image.jpg")
                with open("captured_image.jpg", "rb") as f:
                    image_data_url = get_image_data_url(f)

elif option == "Upload Image":
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        st.image(uploaded_file, caption='Uploaded Image.', use_column_width=True)
        st.write("Analyzing...")
        image_data_url = get_image_data_url(uploaded_file)

# Send the image to the model
if image_data_url:
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "system",
                "content": """You are an environmental analyst. Extract product details from images and calculate carbon footprint.
                              Return JSON with: 
                              - materials (list)
                              - weight_kg (convert to kg)
                              - origin (country)
                              - co2_kg
                              - confidence (0-100)
                              - alternatives (list of 3 eco-friendly PRODUCT alternatives with name, co2_kg, and savings)
                              Use defaults if data missing: materials=["plastic"], weight_kg=0.5, origin="China"."""
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"""Analyze this product and calculate CO2 emissions using:
                                   {json.dumps(EMISSION_FACTORS, indent=2)}
                                   - Assume liquid products: 1L = 1kg
                                   - For ambiguous materials, choose worst-case scenario
                                   - Manufacturing bonus: +0.5kg if from India/China
                                   - Suggest 3 eco-friendly PRODUCT alternatives (e.g., soda → juice, plastic bottle → glass bottle)
                                   Return ONLY valid JSON, no commentary."""
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_data_url,
                            "detail": "high"
                        }
                    }
                ]
            }
        ],
        temperature=0.1  # Keep responses factual
    )

    try:
        # Extract and parse JSON from response
        response_text = response.choices[0].message.content
        json_str = response_text[response_text.find("{"):response_text.rfind("}") + 1]
        data = json.loads(json_str)

        # Generate report
        report = f"""
        🌱 Carbon Emission Report
        --------------------------
        Materials: {', '.join(data['materials'])}
        Weight: {data['weight_kg']} kg
        Origin: {data['origin']}
        Estimated CO₂: {data['co2_kg']} kg
        Confidence: {data['confidence']}%
        """

        # Add alternatives if available
        if "alternatives" in data:
            report += "\n\n🍃 Eco-Friendly Alternatives:"
            for alt in data["alternatives"]:
                report += f"\n- {alt['name']}: {alt['co2_kg']} kg ({alt['savings']} savings)"
        else:
            report += "\n\n⚠️ No eco-friendly alternatives found."

        st.success(report)

    except json.JSONDecodeError:
        st.error("Error: Failed to parse model response")
        st.text("Raw response:")
        st.text(response_text)