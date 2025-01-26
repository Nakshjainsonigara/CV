import pytesseract
from PIL import Image
import re
import json

# Path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Update this path if necessary

def extract_text_from_image(image_path):
    # Open the image using Pillow
    img = Image.open(image_path)
    
    # Use Tesseract to do OCR on the image
    text = pytesseract.image_to_string(img)
    
    return text

def parse_product_data(text):
    # Clean text: remove special characters and normalize
    text = re.sub(r'[^a-zA-Z0-9%.,]', ' ', text).lower()
    
    # Initialize result dict with defaults
    result = {
        "materials": [],
        "weight_kg": None,
        "origin": "unknown",
        "certifications": []
    }

    # 1. Extract Weight/Volume --------------------------------------------
    weight_pattern = r'(\d+\.?\d*)\s*(g|kg|ml|l|lb|pound)'
    weight_match = re.search(weight_pattern, text)
    if weight_match:
        value, unit = weight_match.groups()
        value = float(value)
        # Convert all units to kg
        conversion = {
            "g": 0.001,
            "kg": 1,
            "ml": 0.001,  # Assuming water-like density
            "l": 1,
            "lb": 0.453592,
            "pound": 0.453592
        }
        result["weight_kg"] = value * conversion.get(unit, 1)  # Default to kg

    # 2. Extract Materials -------------------------------------------------
    material_keywords = ["cotton", "polyester", "plastic", "organic", "recycled"]
    material_pattern = r'(\d+%?\s*)?(' + '|'.join(material_keywords) + r')'
    result["materials"] = [m[1] for m in re.findall(material_pattern, text)]

    # 3. Extract Origin Country --------------------------------------------
    origin_match = re.search(r'(made|manufactured)\s*in\s+([a-z\s]+?)(?=\.|,|$)', text)
    if origin_match:
        result["origin"] = origin_match.group(2).strip()

    # 4. Extract Certifications --------------------------------------------
    cert_pattern = r'\b(organic|recycled|fairtrade|usda|gots|fsc)\b'
    result["certifications"] = re.findall(cert_pattern, text)

    return result

# Example usage
image_path = r'C:\Users\jainn\OneDrive\Desktop\Knowcode\CarbonFootprintScanner\emission\bisleri-10ltr-label-600x600.jpg'  # Update with your image path
extracted_text = extract_text_from_image(image_path)

# Print the raw extracted text for debugging
print("Extracted Text:")
print(extracted_text)

# Parse the extracted text to get structured data
parsed_data = parse_product_data(extracted_text)

# Print the result in JSON format
print(json.dumps(parsed_data, indent=4))