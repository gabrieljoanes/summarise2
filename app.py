import streamlit as st
import json
from utils.summary import summarize_with_ratio

st.set_page_config(page_title="🗞️ Résumeur JSON Français", layout="centered")

st.title("🗞️ Résumeur JSON avec GPT-4 Turbo (sortie en français)")

uploaded_file = st.file_uploader("📂 Chargez un fichier JSON", type=["json"])

summary_percent = st.slider(
    "Choisissez la longueur du résumé (en pourcentage du texte original)",
    min_value=10,
    max_value=90,
    value=20,
    step=10
)

if uploaded_file:
    raw_data = uploaded_file.read()
    try:
        data = json.loads(raw_data)
    except json.JSONDecodeError:
        st.error("❌ Fichier JSON invalide.")
        st.stop()

    output_data = []

    with st.spinner("📚 Génération des résumés en cours…"):
        for entry in data:
            original_input = entry.get("input", "")
            original_transition = entry.get("output", "")
            summaries = summarize_with_ratio(original_input, summary_percent)

            summarized_input = "\n".join([s["text"] for s in summaries])

            output_data.append({
                "input": summarized_input,
                "transition": original_transition
            })

    st.success(f"✅ {len(output_data)} entrées traitées.")

    # Show preview
    for i, item in enumerate(output_data[:3]):
        st.subheader(f"Entrée {i+1}")
        st.text_area("Résumé généré", item["input"], height=150)
        st.markdown(f"**Transition :** _{item['transition']}_")

    # Download button
    summarized_json = json.dumps(output_data, ensure_ascii=False, indent=2)
    st.download_button(
        label="📥 Télécharger le JSON Résumé",
        data=summarized_json,
        file_name="resume_francais.json",
        mime="application/json"
    )
