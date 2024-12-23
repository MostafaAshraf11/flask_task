from spacy.language import Language
from scipy import spatial
from textblob import TextBlob
import spacy
from sklearn.manifold import TSNE
from sklearn.feature_extraction.text import TfidfVectorizer
import matplotlib.pyplot as plt
import io


# Initialize the NLP model
nlp = spacy.load("en_core_web_sm")

def summarize_text(text):
    """
    Summarize the input text by extracting sentences with named entities.

    This method performs basic extractive summarization by processing the input text using spaCy
    and extracting sentences that contain named entities. The top 3 sentences with named entities
    are returned as the summary.

    Technologies used:
        - spaCy (for NLP processing)

    Input:
        text (str): Input text to summarize.

    Output:
        str: Summary consisting of the top 3 sentences containing named entities.
    """
    doc = nlp(text)

    # Extract sentences with named entities or keywords (basic extractive summarization)
    summary = [sent.text for sent in doc.sents if len(sent.ents) > 0]
    summary_text = ' '.join(summary[:3])  # Return top 3 sentences

    return summary_text

def extract_keywords(text):
    """
    Extract keywords (nouns and proper nouns) from the input text.

    This method processes the input text using spaCy and extracts keywords, which are defined as
    nouns and proper nouns. The result is a list of unique keywords.

    Technologies used:
        - spaCy (for NLP processing)

    Input:
        text (str): Input text to extract keywords from.

    Output:
        list: A list of unique keywords (nouns and proper nouns) extracted from the text.
    """
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
    """
    Analyze the sentiment of the input text.

    This method uses TextBlob to perform sentiment analysis on the input text. It returns
    a dictionary containing two values: polarity (sentiment score) and subjectivity (subjective
    nature of the text).

    Technologies used:
        - TextBlob (for sentiment analysis)

    Input:
        text (str): Input text to analyze sentiment.

    Output:
        dict: A dictionary with two keys: 'polarity' and 'subjectivity', representing
              the sentiment polarity and subjectivity score of the text.
    """
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
    """
    Preprocess the input text by lowering case, removing stopwords, non-alphabetic tokens, and lemmatizing.

    This method processes the input text using spaCy by converting it to lowercase, removing stopwords,
    removing non-alphabetic tokens, and lemmatizing the remaining words. The processed text is returned as a string.

    Technologies used:
        - spaCy (for text processing and lemmatization)

    Input:
        text (str): The text to preprocess.

    Output:
        str: The preprocessed text with stopwords removed, non-alphabetic tokens filtered, and lemmatized.
    """
    doc = nlp(text.lower())

    filtered_words = [token.lemma_ for token in doc if not token.is_stop and token.is_alpha]

    return " ".join(filtered_words)

def generate_tsne_plot(texts):
    """
    Generate a t-SNE plot for visualizing high-dimensional text data.

    This method converts a list of texts into TF-IDF features, applies t-SNE for dimensionality reduction to 2D,
    and then generates a scatter plot of the result. The plot is saved as a PNG image in a bytes buffer, which is returned.

    Technologies used:
        - scikit-learn (for TF-IDF and t-SNE)
        - matplotlib (for plotting)

    Input:
        texts (list[str]): A list of text documents to analyze.

    Output:
        io.BytesIO: A bytes buffer containing the generated t-SNE plot as a PNG image.
    """
    try:
        # Convert texts to TF-IDF features
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(texts)


        n_samples = tfidf_matrix.shape[0]

        # Set perplexity to 30 or less than n_samples
        perplexity = min(n_samples - 1, 30)  

        # Apply t-SNE for dimensionality reduction
        tsne = TSNE(n_components=2, random_state=42, perplexity=perplexity)
        X_tsne = tsne.fit_transform(tfidf_matrix.toarray())

 
        plt.figure(figsize=(8, 6))
        plt.scatter(X_tsne[:, 0], X_tsne[:, 1], marker='o', c='blue') 
        plt.title('t-SNE Visualization of Texts')
        plt.xlabel('Component 1')
        plt.ylabel('Component 2')

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')  
        buffer.seek(0) 
        plt.close()

        return buffer
    except Exception as e:
        raise Exception(f"Error generating t-SNE plot: {str(e)}")

    
"""""
@Language.component("set_custom_boundaries")  # Register the component
def setCustomBoundaries(doc):
    for token in doc[:-1]:
        if token.text == ';':
            doc[token.i + 1].is_sent_start = True
        if token.text == ".":
            doc[token.i + 1].is_sent_start = False
    return doc

# Function to create SpaCy document object from input text
def getSpacyDocument(text):
    return nlp(text)

# Method to find cosine similarity between two vectors
def cosineSimilarity(vect1, vect2):
    return 1 - spatial.distance.cosine(vect1, vect2)

# Function to create keyword vectors using SpaCy
def createKeywordsVectors(keyword):
    doc = nlp(keyword)
    return doc.vector

# Method to find similar words based on a keyword
def getSimilarWords(keyword):
    similarity_list = []

    keyword_vector = createKeywordsVectors(keyword)

    for tokens in nlp.vocab:
        if tokens.has_vector:
            if tokens.is_lower and tokens.is_alpha:
                similarity_list.append((tokens, cosineSimilarity(keyword_vector, tokens.vector)))

    similarity_list = sorted(similarity_list, key=lambda item: -item[1])[:30]
    top_similar_words = [item[0].text for item in similarity_list]

    top_similar_words.append(keyword)
    for token in nlp(keyword):
        top_similar_words.insert(0, token.lemma_)

    top_similar_words = list(set(top_similar_words))
    return ", ".join(top_similar_words)

# Function to search for keyword in the document
def search_for_keyword(keyword, doc_obj):
    phrase_matcher = PhraseMatcher(nlp.vocab)
    phrase_list = [nlp(keyword)]
    phrase_matcher.add("Text Extractor", None, *phrase_list)

    matched_items = phrase_matcher(doc_obj)

    matched_text = []
    for match_id, start, end in matched_items:
        span = doc_obj[start:end]
        matched_text.append(span.sent.text)

    return matched_text
"""