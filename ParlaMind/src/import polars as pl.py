from tqdm import tqdm
import polars as pl
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk

# Download required NLTK resources if you haven't already
nltk.download('vader_lexicon')
nltk.download('punkt')
nltk.download('stopwords')

# Initialize VADER sentiment analyzer
sid = SentimentIntensityAnalyzer()

# Load the dataset
df = pl.read_parquet("../../../../bundestags_daten.parquet")


def analyze_sentiment(text):
    """Analyzes the sentiment of a given text and returns a dictionary of scores."""
    if text is None or not isinstance(text, str):  # Handle nulls or non-string data
        return {'neg': None, 'neu': None, 'pos': None, 'compound': None}

    scores = sid.polarity_scores(text)
    return scores


def preprocess_text(text):
    """Basic preprocessing to potentially improve sentiment analysis accuracy."""
    if text is None or not isinstance(text, str):
        return ""  # Return empty string if text is missing

    tokens = word_tokenize(text)
    stop_words = set(stopwords.words('german'))  # Use German stopwords
    filtered_tokens = [w for w in tokens if not w.lower() in stop_words and w.isalnum()]  # Remove stopwords and punctuation
    return " ".join(filtered_tokens)


def apply_with_progress(series, func):
    """Apply a function to a Pandas series with a progress bar using tqdm."""
    return [func(item) for item in tqdm(series, desc=f'Processing')]


# Convert 'speechContent' column to a list for processing
speech_contents = df['speechContent'].to_list()

# Apply the analyze_sentiment function with progress
sentiment_scores = apply_with_progress(speech_contents, analyze_sentiment)
df = df.with_columns(pl.DataFrame(sentiment_scores).unnest(""))

# Preprocess text with progress
preprocessed_texts = apply_with_progress(speech_contents, preprocess_text)
df = df.with_column(pl.Series('preprocessed_text', preprocessed_texts))

# Apply sentiment analysis again on preprocessed text
preprocessed_sentiment_scores = apply_with_progress(preprocessed_texts, analyze_sentiment)
df = df.with_columns(pl.DataFrame(preprocessed_sentiment_scores).unnest("preprocessed_"))

# Print DataFrame
df.write_parquet("processed_bundestags_daten.parquet")
print(df)