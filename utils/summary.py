from transformers import pipeline
import math

# Load summarizer model once
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def split_text_by_newline(text: str) -> list[str]:
    """Split text into sections by newlines."""
    return [part.strip() for part in text.split('\n') if part.strip()]

def summarize_with_ratio(text: str, ratio: float) -> list[str]:
    """
    Summarize each section in the input text down to a ratio of the original word count.
    
    Args:
        text (str): Full input text with sections separated by \\n
        ratio (float): Target length as a percentage (e.g., 0.2 = 20%)

    Returns:
        list[str]: List of summarized strings
    """
    sections = split_text_by_newline(text)
    summaries = []

    for section in sections:
        word_count = len(section.split())
        target_len = max(5, math.ceil(word_count * ratio))

        result = summarizer(
            section,
            min_length=5,
            max_length=target_len,
            do_sample=False
        )
        summaries.append(result[0]['summary_text'])

    return summaries
