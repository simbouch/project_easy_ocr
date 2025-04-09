import streamlit as st
from PIL import Image

def show_uploaded_image(uploaded_file, caption="Image téléchargée") -> Image.Image:
    try:
        image = Image.open(uploaded_file)
        st.image(image, caption=caption, use_column_width=True)
        return image
    except Exception as e:
        st.error(f"Erreur lors de l'ouverture de l'image : {e}")
        return None

def display_ocr_data(merged_lines, total: float = None):
    st.subheader("Texte extrait")
    if merged_lines:
        text_output = "\n".join(merged_lines)
        st.markdown("```text\n" + text_output + "\n```")
    else:
        st.write("Aucun texte extrait.")
    
    st.subheader("Montant total extrait")
    if total is not None:
        st.write(f"**{total:.2f} €**")
    else:
        st.write("Aucun montant total détecté.")