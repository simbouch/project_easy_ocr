import streamlit as st
from PIL import Image
from backend.ocr import (
    initialize_reader,
    preprocess_image,
    perform_ocr,
    group_lines_by_row
)
from frontend.display import show_uploaded_image, display_ocr_data

def main():
    """Lance l'application OCR pour reçus français avec EasyOCR dans Streamlit."""
    st.title("OCR avec Easy OCR, essayons-le : téléchargez des reçus et extrayez le texte.")

    # Téléchargeur de fichier
    uploaded_file = st.file_uploader("Téléchargez une image de reçu", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        # Afficher l'image originale
        image = show_uploaded_image(uploaded_file)
        if image is None:
            st.stop()

        # Prétraiter l'image
        preprocessed_image = preprocess_image(image, grayscale=True, threshold=False)
        st.image(preprocessed_image, caption="Image prétraitée", use_column_width=True)

        # Bouton pour déclencher l'OCR
        if st.button("Extraire le texte"):
            with st.spinner("Extraction du texte en cours..."):
                # Initialiser le lecteur et effectuer l'OCR
                reader = initialize_reader(['fr'])
                ocr_result = perform_ocr(preprocessed_image, reader=reader, detail=1)

                # Regrouper les lignes
                merged_lines = group_lines_by_row(ocr_result, y_threshold=10)

                # Afficher les résultats
                display_ocr_data(merged_lines)

if __name__ == "__main__":
    main()