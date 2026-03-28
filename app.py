
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import joblib, numpy as np, os

app = Flask(__name__)
CORS(app)

BASE     = os.path.dirname(os.path.abspath(__file__))

# ── Load models safely ──
try:
    ensemble = joblib.load(os.path.join(BASE, "models/ensemble_model.pkl"))
    scaler   = joblib.load(os.path.join(BASE, "models/scaler.pkl"))
    print("Models loaded successfully!")
except Exception as e:
    print(f"Model loading error: {e}")
    ensemble = None
    scaler   = None

LABELS = [
    "Normal",
    "Elevated",
    "High Blood Pressure Stage 1",
    "High Blood Pressure Stage 2"
]
ADVICE = {
    "Normal":                       "Your BP is healthy. Maintain a balanced diet and exercise regularly.",
    "Elevated":                     "Slightly elevated. Reduce sodium, avoid smoking, exercise daily.",
    "High Blood Pressure Stage 1":  "Consult a doctor. Lifestyle changes are critical.",
    "High Blood Pressure Stage 2":  "Seek immediate medical attention.",
}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/health", methods=["GET"])
def health():
    model_status = "loaded" if ensemble is not None else "not loaded"
    return jsonify({
        "status":       "ok",
        "models":       model_status,
        "flask":        "running"
    })

@app.route("/predict", methods=["POST"])
def predict():
    if ensemble is None or scaler is None:
        return jsonify({"error": "Models not loaded"}), 500
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({"error": "No data received"}), 400

        ht  = float(data["height"])
        wt  = float(data["weight"])
        bmi = wt / ((ht / 100) ** 2)

        features = np.array([[
            int(data["age"]),
            int(data["gender"]),
            ht, wt, bmi,
            float(data["ap_hi"]),
            float(data["ap_lo"]),
            int(data["cholesterol"]),
            int(data["gluc"]),
            int(data["smoke"]),
            int(data["alco"]),
            int(data["active"]),
        ]])

        scaled     = scaler.transform(features)
        pred_class = int(ensemble.predict(scaled)[0])
        proba      = ensemble.predict_proba(scaled)[0].tolist()
        label      = LABELS[pred_class]

        return jsonify({
            "prediction":    pred_class,
            "label":         label,
            "confidence":    round(max(proba) * 100, 2),
            "probabilities": dict(zip(LABELS, [round(p*100,2) for p in proba])),
            "advice":        ADVICE[label],
            "bmi":           round(bmi, 2)
        })

    except KeyError as e:
        return jsonify({"error": f"Missing field: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
