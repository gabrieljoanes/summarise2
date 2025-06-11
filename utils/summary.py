from transformers import pipeline
import math
import re

# Load the model once
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Constants
MIN_NEWS_WORDS = 30
RETRY_INCREMENT = 20  # How many extra words to try if summary looks incomplete

def split_text_by_newline(text: str) -> list[str]:
    """Split text into non-empty sections."""
    return [part.strip() for part in text.split('\n') if part.strip()]

def is_summary_incomplete(summary: str) -> bool:
    """Heuristic to detect an incomplete summary."""
    # Ends with known bad signs
    bad_endings = (":", ",", "-", "(", "…", "—", "–")
    if summary.strip().endswith(bad_endings):
        return True
    if len(summary.split()) < 8:
        return True
    if not re.search(r"[.!?]$", summary.strip()):
        return True
    return False

def summarize_section(section: str, ratio: float) -> dict:
    word_count = len(section.split())
    requested_words = math.ceil(word_count * ratio)
    target_word_count = max(MIN_NEWS_WORDS, requested_words)
    used_source = "ratio" if requested_words >= MIN_NEWS_WORDS else "minimum"

    # First attempt
    result = summarizer(section, min_length=5, max_length=target_word_count, do_sample=False)
    summary_text = result[0]['summary_text']
    retried = False

    # Retry with extra length if summary looks incomplete
    if is_summary_incomplete(summary_text):
        retried = True
        retry_word_count = target_word_count + RETRY_INCREMENT
        result_retry = summarizer(section, min_length=5, max_length=retry_word_count, do_sample=False)
        summary_text = result_retry[0]['summary_text']
        target_word_count = retry_word_count

    return {
        "text": summary_text,
        "used_words": target_word_count,
        "used_words_source": used_source,
        "retried": retried
    }

def summarize_with_ratio(text: str, ratio: float) -> list[dict]:
    sections = split_text_by_newline(text)
    return [summarize_section(sec, ratio) for sec in sections]
