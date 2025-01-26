import tkinter as tk
from barcode import EAN13
from barcode.writer import ImageWriter
from PIL import Image, ImageTk
import io
import os

class CarbonFootprintDisplay:
    def __init__(self):
        # Create barcodes directory first
        if not os.path.exists('barcodes'):
            os.makedirs('barcodes')
            print("Created barcodes directory")

        # Initialize product database
        self.product_db = {
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
        
        # Generate all barcodes at startup
        self.generate_all_barcodes()
        self.setup_gui()
        
    def generate_all_barcodes(self):
        print("Generating barcodes...")
        for barcode_num in self.product_db.keys():
            try:
                ean = EAN13(barcode_num, writer=ImageWriter())
                filename = f"barcodes/{barcode_num}"
                ean.save(filename)
                print(f"Generated barcode: {filename}")
            except Exception as e:
                print(f"Error generating barcode {barcode_num}: {e}")

    def generate_barcode(self, barcode_num):
        try:
            # Use existing barcode file
            filename = f"barcodes/{barcode_num}.png"
            if not os.path.exists(filename):
                # Generate if doesn't exist
                ean = EAN13(barcode_num, writer=ImageWriter())
                ean.save(f"barcodes/{barcode_num}")
                
            # Open and resize the image
            image = Image.open(filename)
            image = image.resize((500, 300), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(image)
            
        except Exception as e:
            print(f"Error with barcode {barcode_num}: {e}")
            return None

    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("Carbon Footprint Scanner")
        
        # Instructions
        instructions = "Click on a product to display its barcode"
        self.instructions = tk.Label(self.root, text=instructions, pady=10)
        self.instructions.pack()
        
        # Barcode display area
        self.barcode_frame = tk.Frame(self.root)
        self.barcode_frame.pack(pady=20)
        
        # Product info
        self.product_label = tk.Label(self.root, text="", font=('Arial', 14))
        self.product_label.pack()
        
        self.emission_label = tk.Label(self.root, text="", font=('Arial', 12))
        self.emission_label.pack()
        
        self.tip_label = tk.Label(self.root, text="", wraplength=400)
        self.tip_label.pack(pady=10)
        
        # Create buttons for each product
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        
        for barcode, data in self.product_db.items():
            btn = tk.Button(
                button_frame,
                text=data['name'],
                command=lambda b=barcode, d=data: self.display_barcode(b, d)
            )
            btn.pack(side=tk.LEFT, padx=5)

    def display_barcode(self, barcode, product_data):
        barcode_image = self.generate_barcode(barcode)
        
        if barcode_image is None:
            self.product_label.config(text="Error: Could not generate barcode", fg="red")
            return
            
        # Clear previous barcode
        for widget in self.barcode_frame.winfo_children():
            widget.destroy()
            
        # Display new barcode
        label_image = tk.Label(self.barcode_frame, image=barcode_image)
        label_image.image = barcode_image  # Keep a reference!
        label_image.pack()
        
        # Update product info
        self.product_label.config(text=f"Product: {product_data['name']}")
        self.emission_label.config(
            text=f"Carbon Footprint: {product_data['co2_kg']} kg CO₂",
            fg="red" if product_data['co2_kg'] > 10 else "green"
        )
        self.tip_label.config(text=f"Sustainability Tip: {product_data['sustainability_tip']}")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = CarbonFootprintDisplay()
    app.run() 