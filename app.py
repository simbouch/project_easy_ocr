# app.py

import streamlit as st
from PIL import Image
from backend.ocr import (
    initialize_reader, 
    preprocess_image, 
    perform_ocr, 
    group_lines_by_row, 
    parse_merged_lines
)
from frontend.display import show_uploaded_image, display_ocr_data

st.title("Enhanced OCR for French Receipts")

# 1. File uploader
uploaded_file = st.file_uploader("Upload a receipt image", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    # 2. Display the original image
    image = show_uploaded_image(uploaded_file)
    if image is None:
        st.stop()  # If there's an error opening the image, stop here

    # 3. Optional preprocessing (e.g., grayscale + threshold)
    preprocessed_image = preprocess_image(image, grayscale=True, threshold=False)
    st.image(preprocessed_image, caption="Preprocessed Image", use_column_width=True)

    # 4. Perform OCR
    #    You can reuse the same reader for multiple images if needed
    reader = initialize_reader(['fr'])  
    ocr_result = perform_ocr(preprocessed_image, reader=reader, detail=1)

    # 5. Group lines by row
    merged_lines = group_lines_by_row(ocr_result, y_threshold=10)

    # 6. Parse merged lines into structured data
    parsed_data = parse_merged_lines(merged_lines)

    # 7. Display final output
    display_ocr_data(merged_lines, parsed_data)
