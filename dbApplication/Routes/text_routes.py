from flask import Blueprint, Response, request, jsonify
from Controller.textController import (summarize_text, extract_keywords, analyze_sentiment, generate_tsne_plot)

text_routes = Blueprint('text_routes', __name__)

@text_routes.route('/summarize', methods=['POST'])
def summarize():
    data = request.json
    text = data.get('text')
    if not text:
        return jsonify({'error': 'No text provided'}), 400

    try:
        summary_text = summarize_text(text)
        return jsonify({'summary': summary_text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@text_routes.route('/keywords', methods=['POST'])
def extract_keywords_route():
    """
    Extract keywords from the provided text using spaCy.
    """
    data = request.json
    text = data.get('text')

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    try:
        keywords = extract_keywords(text)
        return jsonify({'keywords': keywords}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@text_routes.route('/sentiment', methods=['POST'])
def analyze_sentiment_route():
    """
    Perform basic sentiment analysis on the provided text.
    """
    data = request.json
    text = data.get('text')

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    try:
        sentiment = analyze_sentiment(text)
        return jsonify({'sentiment': sentiment}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@text_routes.route('/generate_tsne', methods=['POST'])
def generate_tsne():
    try:
        data = request.get_json()
        texts = data.get('texts')

        if not texts or len(texts) < 2:
            return jsonify({'error': 'Please provide at least two text inputs'}), 400

        buffer = generate_tsne_plot(texts)
        return Response(buffer, mimetype='image/png')

    except Exception as e:
        return jsonify({'error': str(e)}), 500
