from keras.models import load_model
import numpy as np
import cv2
import base64
import io
from PIL import Image
import os

# ✅ Rename model.txt back to model.h5 if needed
if not os.path.exists("model.h5") and os.path.exists("model.txt"):
    os.rename("model.txt", "model.h5")

# ✅ Load model safely
model = load_model("model.h5", compile=False)

# Labels (update if you have different ones)
class_labels = ["Late Blight", "Leaf Mold", "Bacterial Spot", "Healthy"]

def preprocess_image(image_data):
    image_data = image_data.split(",")[1]
    img_bytes = base64.b64decode(image_data)
    img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
    img = img.resize((224, 224))
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

def predict_disease(image_data):
    try:
        img_array = preprocess_image(image_data)
        prediction = model.predict(img_array)[0]
        confidence = float(np.max(prediction))
        label_index = int(np.argmax(prediction))
        label = class_labels[label_index]

        disease_info = {
            "Late Blight": {
                "description": "Serious fungal disease of potatoes and tomatoes.",
                "symptoms": "Dark lesions, white fuzz under leaves.",
                "treatment": "Apply fungicide, remove affected plants."
            },
            "Leaf Mold": {
                "description": "Fungal disease common in humid areas.",
                "symptoms": "Yellow spots on upper leaves, mold on bottom.",
                "treatment": "Use copper-based fungicides, increase airflow."
            },
            "Bacterial Spot": {
                "description": "Bacterial disease affecting leaves and fruit.",
                "symptoms": "Small, water-soaked spots that turn brown.",
                "treatment": "Use resistant varieties, apply copper sprays."
            },
            "Healthy": {
                "description": "No visible disease symptoms.",
                "symptoms": "Leaves appear normal.",
                "treatment": "No treatment necessary."
            }
        }

        result = disease_info.get(label, {})
        return {
            "disease": label,
            "confidence": confidence,
            "description": result.get("description", "N/A"),
            "symptoms": result.get("symptoms", "N/A"),
            "treatment": result.get("treatment", "N/A")
        }

    except Exception as e:
        print("Prediction error:", e)
        return {
            "disease": "Unknown",
            "confidence": 0.0,
            "description": "Prediction failed.",
            "symptoms": "N/A",
            "treatment": "N/A"
        }
