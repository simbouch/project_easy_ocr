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
    return reader.readtext(image_np, detail=detail)

def group_lines_by_row(ocr_data, y_threshold=10) -> list:
    lines = []
    for (bbox, text, conf) in ocr_data:
        ys = [pt[1] for pt in bbox]
        avg_y = sum(ys) / len(ys)
        # find matching row
        for row in lines:
            if abs(row['y'] - avg_y) <= y_threshold:
                row['items'].append((text, conf))
                row['y'] = (row['y'] * (len(row['items']) - 1) + avg_y) / len(row['items'])
                break
        else:
            lines.append({'y': avg_y, 'items': [(text, conf)]})
    # merge text
    merged = [" ".join(txt for txt, _ in sorted(r['items'], key=lambda x: x[0])) 
              for r in sorted(lines, key=lambda x: x['y'])]
    return merged

def extract_total(merged_lines) -> float:
    total_keywords = ["total", "montant total", "à payer", "somme", "net à payer", "total ttc"]
    num_pat = r"(\d+\s*[,.\s]\s*\d{1,2}|\d+)"
    for i, line in enumerate(merged_lines):
        low = line.lower()
        if any(fuzz.partial_ratio(k, low) > 70 for k in total_keywords):
            # try same line
            m = re.search(num_pat, line)
            if m:
                s = m.group(0).replace(" ", "").replace(",", ".")
                try: return float(s)
                except: pass
            # try next line
            if i+1 < len(merged_lines):
                m = re.search(num_pat, merged_lines[i+1])
                if m:
                    s = m.group(0).replace(" ", "").replace(",", ".")
                    try: return float(s)
                    except: pass
    # fallback: largest number in last 5 lines
    nums = []
    for line in merged_lines[-5:]:
        for m in re.findall(num_pat, line):
            s = m.replace(" ", "").replace(",", ".")
            try: nums.append(float(s))
            except: pass
    if nums:
        cand = [n for n in nums if n > 10]
        return max(cand) if cand else max(nums)
    return None

def store_total(total: float, storage_list: list = None, filename: str = "totals.txt"):
    if total is None:
        return
    if storage_list is not None:
        storage_list.append(total)
    with open(filename, "a") as f:
        f.write(f"{total:.2f}\n")
