import cv2
import qrcode
import os
import json
from pyzbar.pyzbar import decode
from PIL import Image

class CarbonFootprintScanner:
    def __init__(self):
        # Product database
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
        
        # Create QR codes directory if it doesn't exist
        if not os.path.exists('qrcodes'):
            os.makedirs('qrcodes')
            
        # Generate QR codes
        self.generate_qr_codes()
        
    def generate_qr_codes(self):
        print("Generating QR codes...")
        for product_id, data in self.product_db.items():
            # Create QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            
            # Add data as JSON string
            qr.add_data(json.dumps(data))
            qr.make(fit=True)
            
            # Create and save QR code image
            qr_image = qr.make_image(fill_color="black", back_color="white")
            qr_image.save(f"qrcodes/{product_id}.png")
            print(f"Generated QR code for {data['name']}")
            
    def scan_qr_codes(self):
        print("Starting camera... Press 'q' to quit")
        
        # Start camera
        cap = cv2.VideoCapture(0)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame")
                break
                
            # Try to decode QR codes in frame
            decoded_objects = decode(frame)
            
            # Process any QR codes found
            for obj in decoded_objects:
                try:
                    # Decode the QR code data
                    data = json.loads(obj.data.decode('utf-8'))
                    
                    # Draw rectangle around QR code
                    points = obj.polygon
                    if len(points) == 4:
                        for i in range(4):
                            cv2.line(frame, 
                                   (points[i].x, points[i].y),
                                   (points[(i+1) % 4].x, points[(i+1) % 4].y),
                                   (0, 255, 0), 3)
                    
                    # Display product information
                    text_lines = [
                        f"Product: {data['name']}",
                        f"Carbon Footprint: {data['co2_kg']} kg CO2",
                        f"Tip: {data['sustainability_tip']}"
                    ]
                    
                    # Position text
                    y_position = 30
                    for line in text_lines:
                        cv2.putText(frame, line, (10, y_position), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.7, 
                                  (0, 255, 0), 2)
                        y_position += 30
                        
                except json.JSONDecodeError:
                    print("Invalid QR code data")
                except Exception as e:
                    print(f"Error processing QR code: {e}")
            
            # Show the frame
            cv2.imshow('Carbon Footprint Scanner', frame)
            
            # Break loop on 'q' press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
        # Clean up
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    # Create scanner instance
    scanner = CarbonFootprintScanner()
    
    print("\nQR codes have been generated in the 'qrcodes' folder.")
    print("You can print these or show them on another device.")
    input("Press Enter to start scanning...")
    
    # Start scanning
    scanner.scan_qr_codes() 