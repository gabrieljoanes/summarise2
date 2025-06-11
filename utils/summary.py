from transformers import pipeline
import math

# Load model once
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Minimum number of words to ensure readability
MIN_NEWS_WORDS = 30

def split_text_by_newline(text: str) -> list[str]:
    """Split text into sections by newlines."""
    return [part.strip() for part in text.split('\n') if part.strip()]

def summarize_with_ratio(text: str, ratio: float) -> list[dict]:
    """
    Summarize each section from the input text.

    Each section is reduced to ratio * word count, but no less than MIN_NEWS_WORDS.

    Returns:
        list of dicts with keys: text, used_words, used_words_source
    """
    sections = split_text_by_newline(text)
    summarized_output = []

    for section in sections:
        word_count = len(section.split())
        requested_words = math.ceil(word_count * ratio)

        if requested_words < MIN_NEWS_WORDS:
            target_word_count = MIN_NEWS_WORDS
            source = "minimum"
        else:
            target_word_count = requested_words
            source = "ratio"

        result = summarizer(
            section,
            min_length=5,
            max_length=target_word_count,
            do_sample=False
        )

        summarized_output.append({
            "text": result[0]['summary_text'],
            "used_words": target_word_count,
            "used_words_source": source
        })

    return summarized_output
