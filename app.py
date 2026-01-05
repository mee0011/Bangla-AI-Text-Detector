import os
import torch
import torch.nn.functional as F
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from transformers import AutoTokenizer, AutoModelForSequenceClassification

app = Flask(__name__)
CORS(app)

MODEL_PATH = "model" 

try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
except Exception as e:
    print(f"Error: {e}")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        text = data.get("text", "")

        if not text:
            return jsonify({"error": "Empty text"}), 400

        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        
        with torch.no_grad():
            outputs = model(**inputs)
            probs = F.softmax(outputs.logits, dim=1)

        ai_score = probs[0][1].item()
        human_score = probs[0][0].item()

        if ai_score > human_score:
            result = "AI"
            confidence_value = ai_score * 100
        else:
            result = "Human"
            confidence_value = human_score * 100

        confidence_str = f"{confidence_value:.1f}"

        return jsonify({
            "result": result,
            "confidence": confidence_str,
            "message": f"এটি {result}-এর লেখা। (Confidence: {confidence_str}%)"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7860)