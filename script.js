// 🌾 Handle image upload preview
function handleImageUpload(event) {
    const file = event.target.files[0];
    if (file) {
        const preview = document.getElementById('imagePreview');
        preview.src = URL.createObjectURL(file);
        preview.style.display = 'block';
    }
}

// 🔍 Handle detection for uploaded image
async function detectDisease() {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    const resultDiv = document.getElementById('result');

    if (!file) {
        alert('Please select an image first');
        return;
    }

    const formData = new FormData();
    formData.append('image', file);

    try {
        const response = await fetch('/detect', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.error) {
            resultDiv.innerHTML = `<p style="color: red;">Error: ${data.error}</p>`;
        } else {
            resultDiv.innerHTML = formatResult(data);
        }
        resultDiv.style.display = 'block';

    } catch (error) {
        resultDiv.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
        resultDiv.style.display = 'block';
    }
}

// 🎥 Setup webcam
const webcam = document.getElementById('webcam');
navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        webcam.srcObject = stream;
    })
    .catch(err => {
        console.error("Webcam not accessible", err);
    });

// 📸 Handle webcam capture and send for detection
document.getElementById('captureBtn').addEventListener('click', () => {
    const canvas = document.getElementById('canvas');
    const context = canvas.getContext('2d');
    canvas.width = webcam.videoWidth;
    canvas.height = webcam.videoHeight;
    context.drawImage(webcam, 0, 0);

    // Convert to blob and send
    canvas.toBlob(async (blob) => {
        const formData = new FormData();
        formData.append('image', blob, 'webcam_capture.jpg');

        const resultDiv = document.getElementById('result');

        try {
            const response = await fetch('/detect', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.error) {
                resultDiv.innerHTML = `<p style="color: red;">Error: ${data.error}</p>`;
            } else {
                resultDiv.innerHTML = formatResult(data);
            }

            resultDiv.style.display = 'block';

        } catch (error) {
            resultDiv.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
            resultDiv.style.display = 'block';
        }

    }, 'image/jpeg');
});

// 🧠 Format result to display
function formatResult(data) {
    return `
        <h3>🧪 Detection Results:</h3>
        <p><strong>Disease:</strong> ${data.disease}</p>
        <p><strong>Confidence:</strong> ${(data.confidence * 100).toFixed(2)}%</p>
        <p><strong>Description:</strong> ${data.description}</p>
        <p><strong>Symptoms:</strong> ${data.symptoms}</p>
        <p><strong>Treatment:</strong> ${data.treatment}</p>
    `;
}
