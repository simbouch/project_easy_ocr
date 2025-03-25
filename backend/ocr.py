# backend/ocr.py

import easyocr
import numpy as np
from PIL import Image, ImageOps
import re

def initialize_reader(languages=None):
    """
    Initialize the EasyOCR Reader with specified languages.
    Defaults to French if no languages are provided.
    """
    if languages is None:
        languages = ['fr']  # default to French, change as needed
    return easyocr.Reader(languages)

def preprocess_image(image: Image.Image, grayscale: bool = True, threshold: bool = False) -> Image.Image:
    """
    Optionally preprocess the image to improve OCR results.
    
    Args:
        image (PIL.Image.Image): The input image.
        grayscale (bool): Convert to grayscale if True.
        threshold (bool): Apply a simple threshold if True.
    
    Returns:
        PIL.Image.Image: Preprocessed image.
    """
    # Convert to grayscale if needed
    if grayscale:
        image = ImageOps.grayscale(image)

    # Apply a simple binary threshold if needed (adjust 128 as necessary)
    if threshold:
        image = image.point(lambda x: 0 if x < 128 else 255, '1')
    
    return image

def perform_ocr(image: Image.Image, reader=None, detail: int = 1):
    """
    Perform OCR on a given PIL image using EasyOCR.
    
    Args:
        image (PIL.Image.Image): The input image.
        reader (easyocr.Reader): An initialized EasyOCR reader. 
                                 If None, a default French reader is used.
        detail (int, optional): 0 = text only, 1 = (bbox, text, confidence).
    
    Returns:
        list: OCR result. If detail=1, returns a list of (bbox, text, confidence).
    """
    if reader is None:
        reader = initialize_reader()  # default to ['fr']
    
    image_np = np.array(image)
    result = reader.readtext(image_np, detail=detail)
    return result

def group_lines_by_row(ocr_data, y_threshold=10):
    """
    Group recognized text lines by their approximate y-coordinate to merge split lines.
    
    Args:
        ocr_data (list): List of (bbox, text, confidence) tuples.
        y_threshold (int): Max distance in pixels to consider text on the same row.
    
    Returns:
        list of dict: Each dict contains { 'y': <average_y>, 'text': <merged_text>, 'confidence': <average_conf> }
    """
    # We'll store lines as: [{'y': some_value, 'items': [(text, conf), ...]}]
    lines = []
    
    for (bbox, text, conf) in ocr_data:
        # bbox is typically [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
        # We'll use the average y of the bounding box as the line position
        ys = [point[1] for point in bbox]
        avg_y = sum(ys) / len(ys)
        
        # Try to find an existing line group close to avg_y
        matched_line = None
        for line in lines:
            if abs(line['y'] - avg_y) <= y_threshold:
                matched_line = line
                break
        
        if matched_line:
            matched_line['items'].append((text, conf))
            # Optionally, update the line's y to be an average
            matched_line['y'] = (
                matched_line['y'] * (len(matched_line['items']) - 1) + avg_y
            ) / len(matched_line['items'])
        else:
            lines.append({
                'y': avg_y,
                'items': [(text, conf)]
            })
    
    # Merge text items for each line
    merged_lines = []
    for line in lines:
        # Sort items by text order (optional) if bounding box x-coordinates matter
        # For simplicity, we'll just join them as recognized
        merged_text = " ".join([txt for (txt, _) in line['items']])
        avg_conf = sum([c for (_, c) in line['items']]) / len(line['items'])
        
        merged_lines.append({
            'y': line['y'],
            'text': merged_text,
            'confidence': avg_conf
        })
    
    # Sort merged lines by y-coordinate
    merged_lines.sort(key=lambda x: x['y'])
    
    return merged_lines

def parse_merged_lines(merged_lines):
    """
    Parse merged lines into structured data, e.g., item/price pairs or totals.
    
    Args:
        merged_lines (list): List of {'y': float, 'text': str, 'confidence': float}
    
    Returns:
        dict: A dictionary containing parsed sections, e.g., {
            'items': [(item_name, price), ...],
            'totals': [...],
            'others': [...]
        }
    """
    data = {
        'items': [],
        'totals': [],
        'others': []
    }
    
    # Basic regex patterns (adapt as needed)
    price_pattern = re.compile(r"\d+[.,]\d{2}")
    total_keywords = ["TOTAL", "TICKET", "PAYER", "EUR", "TVA", "ESPECES"]
    
    for line in merged_lines:
        text_upper = line['text'].upper()
        
        # Check if line contains a price
        prices = price_pattern.findall(line['text'])
        
        # Check if line might be a total or summary line
        if any(kw in text_upper for kw in total_keywords):
            data['totals'].append(line['text'])
        elif prices:
            # If there's a price, we assume it's an item line
            # For simplicity, let's assume there's only one price per line
            item_price = prices[-1]
            # The rest is item name
            item_name = line['text'].replace(item_price, "").strip()
            data['items'].append((item_name, item_price))
        else:
            data['others'].append(line['text'])
    
    return data
