import streamlit as st
import requests
from gtts import gTTS
from io import BytesIO
from deep_translator import GoogleTranslator
from textblob import TextBlob  # Sentiment analysis

# Function to fetch news (always in English for consistency)
def fetch_news(api_key, category):
    base_url = "https://newsapi.org/v2/top-headlines"
    params = {
        'category': category,
        'apiKey': api_key,
        'language': 'en',   # Always English
        'pageSize': 5
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json().get("articles", [])
    else:
        st.error(f"Error fetching news: {response.status_code}")
        return []

# Function to translate text
def translate_text(text, lang):
    try:
        if text and text.strip() and lang != "en":
            return GoogleTranslator(source="auto", target=lang).translate(text)
        return text
    except Exception:
        return text

# Function for sentiment analysis
def analyze_sentiment(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity  # -1 (negative) → +1 (positive)
    if polarity > 0.1:
        return "😊 Positive"
    elif polarity < -0.1:
        return "😞 Negative"
    else:
        return "😐 Neutral"

# Map Streamlit language options → gTTS codes
gtts_lang_map = {
    "en": "en",
    "fr": "fr",
    "es": "es",
    "de": "de",
    "it": "it",
    "ru": "ru",
    "ar": "ar",
    "hi": "hi",
    "ta": "ta"  # Tamil
}

# Streamlit UI
st.title("📰 News Aggregator")
st.write("Fetch the latest news articles based on your preferences.")

api_key = "226e3dde4bea489586c585251cb7b293"  # Your API key

# Language options supported
language = st.selectbox("Select language:",
                        ["en", "fr", "es", "de", "it", "ru", "ar", "hi", "ta"])  # Added Tamil

# Categories
category = st.selectbox("Select a category:",
                        ["business", "entertainment", "general", "health", "science", "sports", "technology"])

if st.button("Get News"):
    articles = fetch_news(api_key, category)

    if articles:
        for i, article in enumerate(articles):
            # English text (fix: force fallback if None)
            title_en = article.get("title") or "No Title"
            desc_en = article.get("description") or "No description available"

            # Translate if needed
            title = translate_text(title_en, language)
            desc = translate_text(desc_en, language)

            # Show news
            st.subheader(title)
            st.write(desc)
            st.write(f"[Read more]({article.get('url', '')})")

            # Sentiment analysis (safe concatenation)
            sentiment = analyze_sentiment(f"{title_en} {desc_en}")
            st.write(f"🧠 Sentiment: {sentiment}")

            # Listen button with in-memory audio
            if st.button(f"🔊 Listen {i+1}", key=f"listen_{i}"):
                text_to_read = f"{title}. {desc}"
                if text_to_read.strip():
                    try:
                        tts_lang = gtts_lang_map.get(language, "en")
                        tts = gTTS(text=text_to_read, lang=tts_lang)

                        # Save to memory instead of file
                        audio_buffer = BytesIO()
                        tts.write_to_fp(audio_buffer)
                        audio_buffer.seek(0)

                        # Play directly
                        st.audio(audio_buffer, format="audio/mp3")

                    except Exception as e:
                        st.error(f"TTS Error: {e}")

            st.write("---")
    else:
        st.warning("No news found. Try another category.")