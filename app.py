import streamlit as st
import json
import io
from utils.summary import summarize_with_ratio, MIN_NEWS_WORDS

st.set_page_config(page_title="Adjustable News Summariser", layout="wide")
st.title("🗞️ JSON Input Summariser with Smart Length Adjustment")

uploaded_file = st.file_uploader("Upload a JSON file", type="json")

summary_percent = st.slider(
    "Select summary output length (as a percentage of original word count)",
    min_value=10, max_value=90, value=20, step=5
) / 100  # Convert to float

if uploaded_file:
    raw_data = json.load(uploaded_file)
    summarized_data = []

    st.info(
        f"Each section will be summarized to {int(summary_percent * 100)}% of the original word count, "
        f"but will always be at least {MIN_NEWS_WORDS} words to maintain readability."
    )

    for entry in raw_data:
        original_input = entry.get("input", "")
        transition_output = entry.get("output", "")
        summaries = summarize_with_ratio(original_input, summary_percent)

        summarized_data.append({
            "input": original_input,
            "summaries": summaries,
            "original_output": transition_output
        })

    st.success(f"Processed {len(summarized_data)} entries.")

    for i, item in enumerate(summarized_data, 1):
        st.markdown(f"---\n### Entry {i}")
        st.markdown("#### Original Input")
        st.text(item['input'])

        st.markdown("#### Summarized Sections")
        for idx, section in enumerate(item['summaries'], 1):
            used = section['used_words']
            source = "ratio" if section['used_words_source'] == "ratio" else f"minimum enforced ({MIN_NEWS_WORDS} words)"
            st.markdown(f"**Section {idx}** — *{used} words used ({source})*")
            st.write(section['text'])

        st.markdown("#### Original Transition Output")
        st.text(item['original_output'])

    # Downloadable JSON
    output_json = json.dumps(summarized_data, ensure_ascii=False, indent=2)
    st.download_button(
        label="📥 Download Summarized JSON",
        data=io.StringIO(output_json),
        file_name="summarized_output.json",
        mime="application/json"
    )
