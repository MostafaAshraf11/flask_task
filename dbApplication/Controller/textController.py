from textblob import TextBlob
import spacy
from sklearn.manifold import TSNE
from sklearn.feature_extraction.text import TfidfVectorizer
import matplotlib.pyplot as plt
import io
from flask import jsonify

# Initialize the NLP model
nlp = spacy.load("en_core_web_sm")

def summarize_text(text):
    # Process the text with spaCy
    doc = nlp(text)

    # Extract sentences with named entities or keywords (basic extractive summarization)
    summary = [sent.text for sent in doc.sents if len(sent.ents) > 0]
    summary_text = ' '.join(summary[:3])  # Return top 3 sentences

    return summary_text

def extract_keywords(text):
    try:
        # Process the text using spaCy
        doc = nlp(text)

        # Extract keywords (Nouns and Proper Nouns)
        keywords = [token.text for token in doc if token.pos_ in ('NOUN', 'PROPN')]

        # Return unique keywords
        return list(set(keywords))

    except Exception as e:
        raise Exception(f"Error extracting keywords: {str(e)}")

def analyze_sentiment(text):
    try:
        # Perform sentiment analysis using TextBlob
        blob = TextBlob(text)
        sentiment = {
            'polarity': blob.sentiment.polarity,  # Range: [-1.0, 1.0]
            'subjectivity': blob.sentiment.subjectivity  # Range: [0.0, 1.0]
        }

        return sentiment
    except Exception as e:
        raise Exception(f"Error analyzing sentiment: {str(e)}")

def preprocess_text(text):
    # Process the text using spaCy
    doc = nlp(text.lower())
    
    # Filter out stopwords and non-alphabetic tokens, then lemmatize
    filtered_words = [token.lemma_ for token in doc if not token.is_stop and token.is_alpha]
    
    # Join the processed tokens back into a string
    return " ".join(filtered_words)

def generate_tsne_plot(texts):
    try:
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

        return buffer
    except Exception as e:
        raise Exception(f"Error generating t-SNE plot: {str(e)}")
