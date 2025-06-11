import math
import openai
import os

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MIN_WORDS = 30  # To ensure readability even at low % summaries

def count_words(text):
    return len(text.strip().split())

def call_gpt_summary(text, target_word_count):
    # Ensure target word count isn't lower than the readability threshold
    target = max(target_word_count, MIN_WORDS)

    prompt = (
        f"Tu es un assistant de presse. Résume très fidèlement le texte suivant en français en maximum {target} mots. "
        f"N'ajoute aucune interprétation. Sois synthétique, clair et factuel. Aucune introduction ou conclusion, seulement le résumé.\n\n"
        f"Texte à résumer :\n{text}\n\n"
        f"Résumé (maximum {target} mots) :"
    )

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return response.choices[0].message.content.strip()

def summarize_section(section_text, ratio):
    word_count = count_words(section_text)
    target_word_count = math.ceil(word_count * ratio)
    summary_text = call_gpt_summary(section_text, target_word_count)
    return {"text": summary_text}

def summarize_with_ratio(input_text, summary_percent):
    sections = input_text.split("\n")
    ratio = summary_percent / 100.0
    return [summarize_section(section, ratio) for section in sections if section.strip()]
