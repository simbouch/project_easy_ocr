import easyocr
import numpy as np
from PIL import Image, ImageOps
import re
from fuzzywuzzy import fuzz

def initialize_reader(languages=None):
    if languages is None:
        languages = ['fr']
    return easyocr.Reader(languages, gpu=False)

def preprocess_image(image: Image.Image, grayscale: bool = True, threshold: bool = False) -> Image.Image:
    if grayscale:
        image = ImageOps.grayscale(image)
    if threshold:
        image = image.point(lambda x: 0 if x < 128 else 255, '1')
    return image

def perform_ocr(image: Image.Image, reader=None, detail: int = 1) -> list:
    if reader is None:
        reader = initialize_reader()
    image_np = np.array(image)
    result = reader.readtext(image_np, detail=detail)
    return result

def group_lines_by_row(ocr_data, y_threshold=10) -> list:
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
    
    merged_lines = []
    for line in sorted(lines, key=lambda x: x['y']):
        merged_text = " ".join(txt for txt, _ in line['items'])
        merged_lines.append(merged_text)
    return merged_lines

def extract_total(merged_lines) -> float:
    total_keywords = ["total", "montant total", "à payer", "somme", "net à payer", "total ttc"]
    number_pattern = r"(\d+\s*[,.\s]\s*\d{1,2}|\d+)"
    
    # Debug: Afficher les lignes pour vérification
    print("Lignes OCR reçues :")
    for line in merged_lines:
        print(f"- {line}")
    
    for i, line in enumerate(merged_lines):
        line_lower = line.lower().strip()
        for keyword in total_keywords:
            if fuzz.partial_ratio(keyword, line_lower) > 70:
                match = re.search(number_pattern, line)
                if match:
                    total_str = match.group(0).replace(" ", "").replace(",", ".")
                    print(f"Total trouvé dans la ligne '{line}': {total_str}")
                    try:
                        return float(total_str)
                    except ValueError:
                        continue
                if i + 1 < len(merged_lines):
                    next_line = merged_lines[i + 1]
                    match = re.search(number_pattern, next_line)
                    if match:
                        total_str = match.group(0).replace(" ", "").replace(",", ".")
                        print(f"Total trouvé dans la ligne suivante '{next_line}': {total_str}")
                        try:
                            return float(total_str)
                        except ValueError:
                            continue
    
    numbers = []
    for line in merged_lines[-5:]:
        matches = re.findall(number_pattern, line)
        for match in matches:
            total_str = match.replace(" ", "").replace(",", ".")
            try:
                numbers.append(float(total_str))
            except ValueError:
                continue
    
    if numbers:
        filtered_numbers = [n for n in numbers if n > 10]
        if filtered_numbers:
            total = max(filtered_numbers)
            print(f"Total estimé (fallback) : {total}")
            return total
    
    print("Aucun total détecté.")
    return None

def store_total(total: float, storage_list: list = None, filename: str = "totals.txt"):
    if total is None:
        print("Rien à stocker : total est None")
        return
    
    print(f"Stockage du total : {total}")
    if storage_list is not None:
        storage_list.append(total)
    
    with open(filename, "a") as f:
        f.write(f"{total:.2f}\n")