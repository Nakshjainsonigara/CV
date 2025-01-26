from flask import Flask, render_template, jsonify
from barcode import EAN13
from barcode.writer import ImageWriter
import os

app = Flask(__name__)

# Initialize product database
PRODUCT_DB = {
    "7376280645025": {
        "name": "Organic Beef",
        "co2_kg": 27.0,
        "category": "meat",
        "sustainability_tip": "Consider plant-based alternatives to reduce emissions."
    },
    "0417890019578": {
        "name": "Plant-based Burger",
        "co2_kg": 3.5,
        "category": "vegetarian",
        "sustainability_tip": "Great choice! Plant-based foods generally have lower emissions."
    },
    "0490000425668": {
        "name": "Coca Cola 330ml",
        "co2_kg": 0.5,
        "category": "beverages",
        "sustainability_tip": "Consider using reusable bottles and local drinks."
    }
}

# Create static/barcodes directory if it doesn't exist
if not os.path.exists('static/barcodes'):
    os.makedirs('static/barcodes')

# Generate barcodes
for barcode_num in PRODUCT_DB.keys():
    ean = EAN13(barcode_num, writer=ImageWriter())
    filename = f"static/barcodes/{barcode_num}.png"
    ean.save(filename, options={"module_width": 0.8, "module_height": 25})

@app.route('/')
def index():
    return render_template('index.html', products=PRODUCT_DB)

@app.route('/product/<barcode>')
def get_product(barcode):
    if barcode in PRODUCT_DB:
        return render_template('product.html', product=PRODUCT_DB[barcode], barcode=barcode)
    return "Product not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 