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

totals_history = []

def main():
    st.title("OCR avec Easy OCR, essayons-le : téléchargez des reçus et extrayez le texte.")
    uploaded_file = st.file_uploader("Téléchargez une image de reçu", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        image = show_uploaded_image(uploaded_file)
        if image is None:
            st.stop()

        preprocessed_image = preprocess_image(image, grayscale=True, threshold=False)
        st.image(preprocessed_image, caption="Image prétraitée", use_column_width=True)

        if st.button("Extraire le texte"):
            with st.spinner("Extraction du texte en cours..."):
                reader = initialize_reader(['fr'])
                ocr_result = perform_ocr(preprocessed_image, reader=reader, detail=1)
                merged_lines = group_lines_by_row(ocr_result, y_threshold=10)
                total = extract_total(merged_lines)
                store_total(total, storage_list=totals_history, filename="totals.txt")
                display_ocr_data(merged_lines, total)

            if totals_history:
                st.subheader("Historique des totaux")
                st.write([f"{t:.2f} €" for t in totals_history])
            else:
                st.write("Aucun total dans l'historique.")

if __name__ == "__main__":
    main()