# frontend/display.py

import streamlit as st
from PIL import Image

def show_uploaded_image(uploaded_file, caption="Uploaded Image"):
    """
    Display the uploaded image in the Streamlit app.
    
    Args:
        uploaded_file: The uploaded file from the file uploader.
        caption (str): Caption to display below the image.
        
    Returns:
        PIL.Image.Image: The opened image.
    """
    try:
        image = Image.open(uploaded_file)
        st.image(image, caption=caption, use_column_width=True)
        return image
    except Exception as e:
        st.error(f"Error opening image: {e}")
        return None

def display_ocr_data(merged_lines, parsed_data):
    """
    Display both the merged lines and parsed data in the Streamlit UI.
    
    Args:
        merged_lines (list): List of merged lines from `group_lines_by_row`.
        parsed_data (dict): Structured data from `parse_merged_lines`.
    """
    st.subheader("Merged Lines (Post-Processing)")
    for line in merged_lines:
        st.write(f"**Line:** {line['text']} (Confidence: {line['confidence']:.2f})")

    st.subheader("Parsed Data")
    
    # Display items
    if parsed_data['items']:
        st.write("**Items & Prices:**")
        for item_name, price in parsed_data['items']:
            st.write(f"- {item_name} : {price}")
    else:
        st.write("No items found.")

    # Display totals
    if parsed_data['totals']:
        st.write("**Totals / Summary Lines:**")
        for total_line in parsed_data['totals']:
            st.write(f"- {total_line}")
    else:
        st.write("No totals found.")

    # Display other lines
    if parsed_data['others']:
        st.write("**Other Lines:**")
        for other_line in parsed_data['others']:
            st.write(f"- {other_line}")
    else:
        st.write("No other lines found.")
