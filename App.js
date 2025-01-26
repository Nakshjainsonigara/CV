import React, { useState, useEffect } from 'react';
import { StyleSheet, View, Text, Alert } from 'react-native';
import { Camera, useCameraDevices } from 'react-native-vision-camera';
import { useScanBarcodes, BarcodeFormat } from 'vision-camera-code-scanner';

function App() {
  const [hasPermission, setHasPermission] = useState(false);
  const [scannedBarcode, setScannedBarcode] = useState(null);
  const devices = useCameraDevices();
  const device = devices.back;

  // Request camera permission
  useEffect(() => {
    (async () => {
      const status = await Camera.requestCameraPermission();
      setHasPermission(status === 'authorized');
    })();
  }, []);

  // Barcode scanner setup
  const [frameProcessor, barcodes] = useScanBarcodes([BarcodeFormat.ALL], {
    checkInverted: true,
  });

  // Handle scanned barcode
  useEffect(() => {
    if (barcodes.length > 0) {
      setScannedBarcode(barcodes[0].displayValue);
    }
  }, [barcodes]);

  // Fetch product data using the scanned barcode
  const fetchProductData = async (barcode) => {
    try {
      const response = await fetch(
        `https://world.openfoodfacts.org/api/v0/product/${barcode}.json`
      );
      const data = await response.json();
      const productName = data.product.product_name;
      const co2PerKg = data.product.ecoscore_data?.agribalyse?.co2_total; // May not exist
      return { productName, co2PerKg };
    } catch (error) {
      console.error(error);
      return null;
    }
  };

  // Display product data
  useEffect(() => {
    if (scannedBarcode) {
      (async () => {
        const productData = await fetchProductData(scannedBarcode);
        if (productData) {
          Alert.alert(`${productData.productName}: ${productData.co2PerKg} kg CO₂`);
        } else {
          Alert.alert("Product not found in our database.");
        }
      })();
    }
  }, [scannedBarcode]);

  if (!hasPermission) {
    return <Text>No access to camera</Text>;
  }

  if (!device) {
    return <Text>Loading camera...</Text>;
  }

  return (
    <View style={StyleSheet.absoluteFill}>
      <Camera
        style={StyleSheet.absoluteFill}
        device={device}
        isActive={true}
        frameProcessor={frameProcessor}
        frameProcessorFps={5}
      />
      {/* Add a UI overlay for scanning */}
    </View>
  );
}

export default App;
