from flask import Flask, render_template
import qrcode
import os

app = Flask(__name__)

# Create directories if they don't exist
if not os.path.exists('static'):
    os.makedirs('static')
if not os.path.exists('static/qrcodes'):
    os.makedirs('static/qrcodes')

# Product database
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

# Generate QR codes for each product
def generate_qr_codes(base_url):
    for barcode in PRODUCT_DB.keys():
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(f"{base_url}/product/{barcode}")
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(f"static/qrcodes/{barcode}.png")

@app.route('/')
def index():
    return render_template('index.html', products=PRODUCT_DB)

@app.route('/product/<barcode>')
def product(barcode):
    if barcode in PRODUCT_DB:
        return render_template('product.html', product=PRODUCT_DB[barcode])
    return "Product not found", 404

if __name__ == '__main__':
    # Generate QR codes with localhost URL
    generate_qr_codes('http://localhost:5000')
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True) 