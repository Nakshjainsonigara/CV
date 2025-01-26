const express = require("express");
const bodyParser = require("body-parser");
const OpenAI = require("openai");
const app = express();
const port = 3000;

// Increase payload size limit (e.g., 50MB)
app.use(bodyParser.json({ limit: "50mb" }));
app.use(bodyParser.urlencoded({ limit: "50mb", extended: true }));

// Configuration
const token = "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";
const endpoint = "https://models.inference.ai.azure.com";
const modelName = "gpt-4o";

// Emission factors (kg CO₂ per kg of material)
const EMISSION_FACTORS = {
    plastic: 6.0,
    cotton: 8.0,
    glass: 1.2,
    aluminum: 8.1,
    paper: 1.4,
    steel: 2.8,
    default: 5.0
};

// Initialize OpenAI client
const openai = new OpenAI({
    baseURL: endpoint,
    apiKey: token,
});

// Route to handle image analysis
app.post("/analyze", async (req, res) => {
    const base64Image = req.body.image;

    if (!base64Image) {
        return res.status(400).json({ error: "No image provided" });
    }

    try {
        console.log("Received image:", base64Image.slice(0, 50) + "..."); // Log first 50 chars of base64

        const response = await openai.chat.completions.create({
            model: modelName,
            messages: [
                {
                    role: "system",
                    content: `You are an environmental analyst. Extract product details from images and calculate carbon footprint.
                              Return JSON with: 
                              - materials (list)
                              - weight_kg (convert to kg)
                              - origin (country)
                              - co2_kg
                              - confidence (0-100)
                              - alternatives (list of 3 eco-friendly PRODUCT alternatives with name, co2_kg, and savings)
                              Use defaults if data missing: materials=["plastic"], weight_kg=0.5, origin="China".`
                },
                {
                    role: "user",
                    content: [
                        {
                            type: "text",
                            text: `Analyze this product and calculate CO2 emissions using:
                                   ${JSON.stringify(EMISSION_FACTORS, null, 2)}
                                   - Assume liquid products: 1L = 1kg
                                   - For ambiguous materials, choose worst-case scenario
                                   - Manufacturing bonus: +0.5kg if from India/China
                                   - Suggest 3 eco-friendly PRODUCT alternatives (e.g., soda → juice, plastic bottle → glass bottle)
                                   Return ONLY valid JSON, no commentary.`
                        },
                        {
                            type: "image_url",
                            image_url: {
                                url: `data:image/jpeg;base64,${base64Image}`,
                                detail: "high"
                            }
                        }
                    ]
                }
            ],
            temperature: 0.1  // Keep responses factual
        });

        console.log("OpenAI response:", response);

        // Extract and parse JSON from response
        const responseText = response.choices[0].message.content;
        const jsonStr = responseText.slice(responseText.indexOf("{"), responseText.lastIndexOf("}") + 1);
        const data = JSON.parse(jsonStr);

        res.json(data);
    } catch (error) {
        console.error("Error:", error.message);
        if (error.response) {
            console.error("Response data:", error.response.data);
        }
        res.status(500).json({ error: "Failed to analyze image", details: error.message });
    }
});

// Serve the frontend
app.get("/", (req, res) => {
    res.sendFile(__dirname + "/index.html");
});

// Start the server
app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});