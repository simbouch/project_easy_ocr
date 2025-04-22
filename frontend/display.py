import streamlit as st
from PIL import Image
import io

def show_uploaded_image(uploaded_file, caption="Image téléchargée") -> Image.Image:
    try:
        img = Image.open(uploaded_file)
        st.image(img, caption=caption, use_container_width=True)
        return img
    except Exception as e:
        st.error(f"Erreur d'ouverture d'image : {e}")
        return None

def display_ocr_data(merged_lines: list, total: float):
    # Total metric
    if total is not None:
        st.metric(label="Total détecté", value=f"{total:.2f} €")
    else:
        st.warning("Aucun montant total détecté.")

    # Raw OCR
    with st.expander("Voir toutes les lignes OCR"):
        for i, line in enumerate(merged_lines, 1):
            st.write(f"{i}. {line}")

    # Download button for merged lines
    txt = "\n".join(merged_lines)
    st.download_button(
        "Télécharger le texte complet",
        data=txt,
        file_name="ocr_output.txt",
        mime="text/plain"
    )
