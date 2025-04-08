import easyocr
import numpy as np
from PIL import Image, ImageOps

def initialize_reader(languages=None):
    """
    Initialise le lecteur EasyOCR avec les langues spécifiées.
    Par défaut en français si aucune langue n'est fournie.
    """
    if languages is None:
        languages = ['fr']  # Par défaut en français
    return easyocr.Reader(languages, gpu=False)  # gpu=True si GPU compatible

def preprocess_image(image: Image.Image, grayscale: bool = True, threshold: bool = False) -> Image.Image:
    """
    Prétraite l'image pour améliorer les résultats OCR.
    
    Args:
        image (PIL.Image.Image): L'image d'entrée.
        grayscale (bool): Convertit en niveaux de gris si True.
        threshold (bool): Applique un seuil binaire si True.
    
    Returns:
        PIL.Image.Image: Image prétraitée.
    """
    if grayscale:
        image = ImageOps.grayscale(image)
    if threshold:
        image = image.point(lambda x: 0 if x < 128 else 255, '1')
    return image

def perform_ocr(image: Image.Image, reader=None, detail: int = 1) -> list:
    """
    Effectue l'OCR sur une image PIL avec EasyOCR.
    
    Args:
        image (PIL.Image.Image): L'image d'entrée.
        reader (easyocr.Reader): Lecteur EasyOCR initialisé. Par défaut en français si None.
        detail (int): 0 = texte uniquement, 1 = (bbox, texte, confiance).
    
    Returns:
        list: Résultat OCR sous forme [(bbox, texte, confiance), ...] si detail=1.
    """
    if reader is None:
        reader = initialize_reader()  # Par défaut en français
    image_np = np.array(image)
    result = reader.readtext(image_np, detail=detail)
    return result

def group_lines_by_row(ocr_data, y_threshold=10) -> list:
    """
    Regroupe les lignes de texte reconnues par leur coordonnée y approximative.
    
    Args:
        ocr_data (list): Liste de tuples (bbox, texte, confiance).
        y_threshold (int): Distance max en pixels pour considérer un texte sur la même ligne.
    
    Returns:
        list: Liste de chaînes de texte fusionnées.
    """
    lines = []
    
    for (bbox, text, conf) in ocr_data:
        ys = [point[1] for point in bbox]
        avg_y = sum(ys) / len(ys)
        
        matched_line = None
        for line in lines:
            if abs(line['y'] - avg_y) <= y_threshold:
                matched_line = line
                break
        
        if matched_line:
            matched_line['items'].append((text, conf))
            matched_line['y'] = (
                matched_line['y'] * (len(matched_line['items']) - 1) + avg_y
            ) / len(matched_line['items'])
        else:
            lines.append({'y': avg_y, 'items': [(text, conf)]})
    
    # Fusionner les éléments de texte en chaînes simples
    merged_lines = []
    for line in sorted(lines, key=lambda x: x['y']):
        merged_text = " ".join(txt for txt, _ in line['items'])
        merged_lines.append(merged_text)
    
    return merged_lines