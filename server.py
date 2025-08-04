import os
import sqlite3
from flask import Flask, render_template, request, jsonify, redirect, session
from werkzeug.utils import secure_filename
from keras.models import load_model
from keras.preprocessing.image import load_img, img_to_array
import numpy as np
import json
from datetime import datetime

# Hide TensorFlow logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

app = Flask(__name__)
app.secret_key = 'sridhar_secret_123'

# Load model and disease info
model = load_model("model.h5", compile=False)
disease_info = json.load(open("disease_info.json"))

# Upload folder setup
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# DB init
DB_FILE = "predictions.db"
conn = sqlite3.connect(DB_FILE)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT,
    disease TEXT,
    confidence REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)''')
conn.commit()
conn.close()

@app.route('/')
def login_page():
    return render_template("login.html")

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    if username == "farmer" and password == "1234":
        session['logged_in'] = True
        return redirect("/home")
    return "❌ Invalid credentials. <a href='/'>Try again</a>"

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/home')
def home():
    if not session.get('logged_in'):
        return redirect('/')
    return render_template("index.html")

@app.route('/detect', methods=['POST'])
def detect():
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"})

    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No selected file"})

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    try:
        # ✅ Ensure the image is RGB
        img = load_img(filepath, target_size=(224, 224), color_mode='rgb')
        img_array = img_to_array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        # ✅ Model Prediction
        prediction = model.predict(img_array)[0]
        predicted_index = np.argmax(prediction)
        confidence = float(prediction[predicted_index])
        disease_name = list(disease_info.keys())[predicted_index]
        details = disease_info[disease_name]

        # ✅ Debug output
        print("📸 Prediction:", prediction)
        print("🔍 Predicted Index:", predicted_index)
        print("📊 Confidence:", confidence)

        # ✅ Threshold check (Relaxed from 0.4 to 0.25)
        if confidence < 0.25:
            return jsonify({
                "disease": "Unknown",
                "confidence": 0.0,
                "description": "Prediction confidence too low. Try again with a clearer image.",
                "symptoms": "N/A",
                "treatment": "N/A"
            })

        # ✅ Save prediction to DB
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO predictions (filename, disease, confidence) VALUES (?, ?, ?)",
                  (filename, disease_name, confidence))
        conn.commit()
        conn.close()

        # ✅ Return success response
        return jsonify({
            "disease": disease_name,
            "confidence": confidence,
            "description": details["description"],
            "symptoms": details["symptoms"],
            "treatment": details["treatment"]
        })

    except Exception as e:
        print("❌ Error during detection:", str(e))
        return jsonify({
            "disease": "Unknown",
            "confidence": 0.0,
            "description": "Error during detection.",
            "symptoms": "N/A",
            "treatment": "N/A"
        })

@app.route('/history')
def history():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT filename, disease, confidence, timestamp FROM predictions ORDER BY timestamp DESC")
    rows = c.fetchall()
    conn.close()
    return render_template("history.html", predictions=rows)

if __name__ == '__main__':
    print("🌐 AgriGuardians for Smart India server started...")
    app.run(debug=True)
