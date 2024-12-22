import io
from flask import Blueprint, Response, request, jsonify
from textblob import TextBlob
import spacy
from sklearn.manifold import TSNE
from sklearn.feature_extraction.text import TfidfVectorizer
import matplotlib.pyplot as plt


text_routes = Blueprint('text_routes', __name__)

nlp = spacy.load("en_core_web_sm")

@text_routes.route('/summarize', methods=['POST'])
def summarize():
    data = request.json
    text = data.get('text')
    if not text:
        return jsonify({'error': 'No text provided'}), 400

    # Process the text with spaCy
    doc = nlp(text)

    # Extract sentences with named entities or keywords (basic extractive summarization)
    summary = [sent.text for sent in doc.sents if len(sent.ents) > 0]
    summary_text = ' '.join(summary[:3])  # Return top 3 sentences

    return jsonify({'summary': summary_text})

@text_routes.route('/keywords', methods=['POST'])
def extract_keywords():
    """
    Extract keywords from the provided text using spaCy.
    """
    data = request.json
    text = data.get('text')

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    try:
        # Process the text using spaCy
        doc = nlp(text)

        # Extract keywords (Nouns and Proper Nouns)
        keywords = [token.text for token in doc if token.pos_ in ('NOUN', 'PROPN')]

        # Return unique keywords
        return jsonify({'keywords': list(set(keywords))}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@text_routes.route('/sentiment', methods=['POST'])
def analyze_sentiment():
    """
    Perform basic sentiment analysis on the provided text.
    """
    data = request.json
    text = data.get('text')

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    try:
        # Perform sentiment analysis using TextBlob
        blob = TextBlob(text)
        sentiment = {
            'polarity': blob.sentiment.polarity,  # Range: [-1.0, 1.0]
            'subjectivity': blob.sentiment.subjectivity  # Range: [0.0, 1.0]
        }

        return jsonify({'sentiment': sentiment}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

def preprocess_text(text):
    # Process the text using spaCy
    doc = nlp(text.lower())
    
    # Filter out stopwords and non-alphabetic tokens, then lemmatize
    filtered_words = [token.lemma_ for token in doc if not token.is_stop and token.is_alpha]
    
    # Join the processed tokens back into a string
    return " ".join(filtered_words)

@text_routes.route('/generate_tsne', methods=['POST'])
def generate_tsne():
    try:
        data = request.get_json()
        texts = data.get('texts')

        if not texts or len(texts) < 2:
            return jsonify({'error': 'Please provide at least two text inputs'}), 400

        # Convert texts to TF-IDF features
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(texts)

        # Get number of samples
        n_samples = tfidf_matrix.shape[0]

        # Set perplexity to a value less than the number of samples
        perplexity = min(n_samples - 1, 30)  # Set perplexity to 30 or less than n_samples

        # Apply t-SNE for dimensionality reduction
        tsne = TSNE(n_components=2, random_state=42, perplexity=perplexity)
        X_tsne = tsne.fit_transform(tfidf_matrix.toarray())

        # Plotting the t-SNE result
        plt.figure(figsize=(8, 6))
        plt.scatter(X_tsne[:, 0], X_tsne[:, 1], marker='o', c='blue')  # Optionally, you can color by clusters if needed
        plt.title('t-SNE Visualization of Texts')
        plt.xlabel('Component 1')
        plt.ylabel('Component 2')

        # Save the plot to a bytes buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')  # Save the figure as a PNG image
        buffer.seek(0)  # Rewind the buffer to the beginning
        plt.close()  # Close the plot to free resources

        # Return the plot as a response
        return Response(buffer, mimetype='image/png')

    except Exception as e:
        return jsonify({'error': str(e)}), 500