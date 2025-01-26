import cv2
import streamlit as st
import pytesseract
import numpy as np
import json

# Specify the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Update this path if necessary

def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    return thresh

# Load harmful ingredients database
with open('ingredients.json') as f:
    harmful_ingredients = json.load(f)

uploaded_file = st.file_uploader("Upload an ingredient list:")
if uploaded_file:
    image = cv2.imdecode(np.frombuffer(uploaded_file.read(), np.uint8), 1)
    processed = preprocess_image(image)
    text = pytesseract.image_to_string(processed)
    
    st.write("Extracted Text:", text)  # Add this line to see the OCR output
    
    # Check ingredients against JSON and display
    found = []
    for ingredient, details in harmful_ingredients.items():
        if ingredient in text.lower():
            found.append({**details, "ingredient": ingredient})
    
    if found:
        st.write("🚨 Harmful Ingredients Found:")
        for item in found:
            st.write(f"**{item['ingredient']}**: {item['impact']}. Swap with: {item['alternatives']}")
    else:
        st.write("No harmful ingredients found.")
