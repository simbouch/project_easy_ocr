import streamlit as st
from PIL import Image
from backend.ocr import (
    initialize_reader,
    preprocess_image,
    perform_ocr,
    group_lines_by_row,
    extract_total,
    store_total
)
from frontend.display import show_uploaded_image, display_ocr_data

# session state for history
if "history" not in st.session_state:
    st.session_state.history = []

@st.cache_resource
def get_reader():
    return initialize_reader(['fr'])

def main():
    st.set_page_config(
        page_title="OCR Reçus 🇫🇷",
        layout="centered",
        initial_sidebar_state="auto"
    )
    st.title("🧾 Extraction de Total depuis un Reçu")
    st.write("Téléchargez une photo de reçu et récupérez automatiquement le montant total.")

    uploaded = st.file_uploader("Choisir une image :", type=["png","jpg","jpeg"])
    if not uploaded:
        st.info("En attente d'un reçu…")
        return

    img = show_uploaded_image(uploaded)
    if img is None:
        return

    # preprocess toggles
    col1, col2 = st.columns(2)
    with col1:
        gray = st.checkbox("Niveaux de gris", value=True)
    with col2:
        thr = st.checkbox("Seuillage binaire", value=False)

    pre = preprocess_image(img, grayscale=gray, threshold=thr)
    st.image(pre, caption="Image prétraitée", use_container_width=True)

    if st.button("🔍 Extraire le texte & total"):
        with st.spinner("Analyse en cours…"):
            reader = get_reader()
            ocr_raw = perform_ocr(pre, reader, detail=1)
            merged = group_lines_by_row(ocr_raw)
            total = extract_total(merged)
            store_total(total, storage_list=st.session_state.history)
        display_ocr_data(merged, total)

    # show history
    if st.session_state.history:
        st.subheader("📊 Historique des Totaux")
        st.table(
            [{"Tour": i+1, "Total (€)": f"{t:.2f}"} 
             for i,t in enumerate(st.session_state.history)]
        )
        # download CSV
        import pandas as pd
        df = pd.DataFrame(st.session_state.history, columns=["Total"])
        csv = df.to_csv(index=False)
        st.download_button("Télécharger l'historique (CSV)", data=csv,
                           file_name="history.csv", mime="text/csv")

if __name__ == "__main__":
    main()
