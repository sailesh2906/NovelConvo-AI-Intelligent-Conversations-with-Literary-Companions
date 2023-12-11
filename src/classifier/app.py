from flask import Flask, request, jsonify
from transformers import pipeline
import numpy as np

app = Flask(__name__)

#classifier = pipeline("zero-shot-classification", model="MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli")
classifier = pipeline("zero-shot-classification", model="MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli")

@app.route('/classify', methods=['POST'])
def classify():
    # Extract data from request
    data = request.json

    sequence_to_classify = data['sequence_to_classify']
    candidate_labels = data['candidate_labels']

    try:
        multi_label = data['multi_label']
    except KeyError:
        multi_label = None

    if not multi_label:
        result = classifier(sequence_to_classify, candidate_labels, multi_label=False)
        labels = result['labels']
        scores = result['scores']
        output = {'label' : labels[np.argmax(scores)]}
        return jsonify(output)
    else:
        result = classifier(sequence_to_classify, candidate_labels, multi_label=True)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)


