import math
import re
import streamlit as st
from openai import OpenAI

# Load OpenAI client using Streamlit secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

MIN_NEWS_WORDS = 30
RETRY_INCREMENT = 20

def split_text_by_newline(text: str) -> list[str]:
    return [part.strip() for part in text.split('\n') if part.strip()]

def is_summary_incomplete(text: str) -> bool:
    """Detect if the summary might be cut off or unusable."""
    if len(text.split()) < 8:
        return True
    if not re.search(r'[.!?]$', text.strip()):
        return True
    return False

def call_gpt_summary(section: str, word_limit: int) -> str:
    prompt = (
        f"Tu es journaliste pour un site d'actualités régionales.\n"
        f"Résume le texte ci-dessous en français, en **maximum {word_limit} mots**. "
        f"Ton résumé doit être fluide, lisible, naturel et refléter toutes les informations importantes. "
        f"Rédige comme un article de presse professionnel — sans phrases incomplètes, sans puces, sans style télégraphique.\n\n"
        f"Texte à résumer :\n{section}"
    )
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )
    return response.choices[0].message.content.strip()

def summarize_section(section: str, ratio: float) -> dict:
    word_count = len(section.split())
    requested_words = math.ceil(word_count * ratio)
    target_word_count = max(MIN_NEWS_WORDS, requested_words)
    used_source = "ratio" if requested_words >= MIN_NEWS_WORDS else "minimum"

    summary_text = call_gpt_summary(section, target_word_count)
    retried = False

    if is_summary_incomplete(summary_text):
        retried = True
        retry_words = target_word_count + RETRY_INCREMENT
        summary_text = call_gpt_summary(section, retry_words)
        target_word_count = retry_words

    return {
        "text": summary_text,
        "used_words": len(summary_text.split()),
        "used_words_source": used_source,
        "retried": retried
    }

def summarize_with_ratio(text: str, ratio: float) -> list[dict]:
    sections = split_text_by_newline(text)
    return [summarize_section(section, ratio) for section in sections]
