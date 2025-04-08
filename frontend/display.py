import streamlit as st
from PIL import Image

def show_uploaded_image(uploaded_file, caption="Image téléchargée") -> Image.Image:
    """
    Affiche l'image téléchargée dans l'application Streamlit.
    
    Args:
        uploaded_file: Fichier téléchargé via l'uploader.
        caption (str): Légende à afficher sous l'image.
    
    Returns:
        PIL.Image.Image: L'image ouverte ou None en cas d'erreur.
    """
    try:
        image = Image.open(uploaded_file)
        st.image(image, caption=caption, use_column_width=True)
        return image
    except Exception as e:
        st.error(f"Erreur lors de l'ouverture de l'image : {e}")
        return None

def display_ocr_data(merged_lines):
    """
    Affiche les résultats OCR sous forme de texte formaté dans Streamlit.
    
    Args:
        merged_lines (list): Liste des lignes de texte fusionnées.
    """
    st.subheader("Texte extrait")
    if merged_lines:
        text_output = "\n".join(merged_lines)
        st.markdown("```text\n" + text_output + "\n```")
    else:
        st.write("Aucun texte extrait.")