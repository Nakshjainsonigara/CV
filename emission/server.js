const express = require('express');
const multer = require('multer');
const fs = require('fs');
const path = require('path');
const OpenAI = require('openai'); // Ensure you have this installed
const app = express();
const port = 3000;

// Set up storage for uploaded images
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, 'uploads/'); // Save to uploads folder
    },
    filename: (req, file, cb) => {
        cb(null, Date.now() + path.extname(file.originalname)); // Append timestamp to filename
    }
});

const upload = multer({ storage: storage });

// Serve the front.html file at the root URL
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'front.html'));
});

// Initialize OpenAI client
const openai = new OpenAI({
    apiKey: "YOUR_API_KEY", // Replace with your actual OpenAI API key
});

// Endpoint to handle image upload
app.post('/upload', upload.single('image'), async (req, res) => {
    const imagePath = req.file.path; // Path to the saved image

    // Call your analyzeProduct function with the imagePath
    try {
        const result = await analyzeProduct(imagePath);
        res.json(result);
    } catch (error) {
        console.error("Error:", error);
        res.status(500).json({ error: "An error occurred while processing the image." });
    }
});

// Function to analyze the product using OpenAI
async function analyzeProduct(imagePath) {
    // Your OpenAI API call logic here
    // For demonstration, let's return a mock response
    return {
        message: 'Image uploaded successfully',
        imagePath: imagePath,
        // Add more fields as needed
    };
}

// Serve static files
app.use(express.static('.'));

app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});
