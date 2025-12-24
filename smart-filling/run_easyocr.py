import os
import json
import re
from pdf2image import convert_from_path
import easyocr

# ---------------- INITIAL SETUP ----------------
reader = easyocr.Reader(['en'])
file_path = "data/trial/eg_aadhar_kani.jpeg"  # replace with your document
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

# ---------------- OCR FUNCTION ----------------
def process_image(img_path):
    results = reader.readtext(img_path)
    return [res[1].strip() for res in results]

# ---------------- GENERIC FIELD EXTRACTION ----------------
def extract_generic_fields(text_lines):
    data = {
        "name": None,
        "date": None,        # DOB / Issue Date
        "gender": None,
        "id_number": None,
        "document_type": None
    }

    ignore_words = [
        "GOVERNMENT", "INDIA", "REPUBLIC", "UNIQUE",
        "IDENTIFICATION", "AUTHORITY", "ELECTION",
        "COMMISSION", "CERTIFICATE", "AADHAAR", "BIRTH",
        "COMMUNITY", "VOTER"
    ]

    # ---------- PREPROCESS LINES ----------
    clean_lines = []
    for line in text_lines:
        clean_line = line.strip().replace('O', '0').replace('I','1').replace('l','1').replace('|','1')
        clean_lines.append(clean_line)

    # ---------- DETECT FIELDS ----------
    possible_names = []
    for line in clean_lines:
        upper = line.upper()

        # Document Type
        if "AADHAAR" in upper:
            data["document_type"] = "Aadhaar"
        elif "ELECTION" in upper or "VOTER" in upper:
            data["document_type"] = "Election ID"
        elif "BIRTH" in upper:
            data["document_type"] = "Birth Certificate"
        elif "COMMUNITY" in upper or "CASTE" in upper:
            data["document_type"] = "Community Certificate"

        # Gender
        gender = line.replace(" ", "").lower()
        if gender in ["male", "female", "other"]:
            data["gender"] = gender.capitalize()

        # Date (DOB / Issue Date)
        date_match = re.search(r'(\d{2}[\/\-]\d{2}[\/\-]\d{4})', line)
        if date_match and not data["date"]:
            data["date"] = date_match.group()

        # ID Number (Aadhaar or generic numbers)
        id_candidate = line.replace(" ", "")
        if re.fullmatch(r'\d{12}', id_candidate):  # Aadhaar 12 digits
            data["id_number"] = f"{id_candidate[:4]} {id_candidate[4:8]} {id_candidate[8:]}"
        elif re.fullmatch(r'[A-Z]{3}\d{7}', id_candidate):  # Voter ID
            data["id_number"] = id_candidate
        elif re.fullmatch(r'\d{6,12}', id_candidate) and not data["id_number"]:
            data["id_number"] = id_candidate

        # Name (possible)
        if line.isupper() and line.replace(" ", "").isalpha():
            words = line.split()
            if 1 <= len(words) <= 3 and not any(word in ignore_words for word in words):
                possible_names.append(line)

    # Pick the last suitable name (usually below title)
    if possible_names:
        data["name"] = possible_names[-1]

    return data

# ---------------- MAIN EXECUTION ----------------
all_text = []
from PIL import Image, ImageFilter

if file_path.lower().endswith(".pdf"):
    # Convert PDF to high-res images
    pages = convert_from_path(file_path, dpi=400)  # High DPI for better OCR

    for i, page in enumerate(pages):
        # Convert to grayscale
        page = page.convert('L')
        # Sharpen the image
        page = page.filter(ImageFilter.SHARPEN)
        
        # Save processed image
        img_path = os.path.join(output_dir, f"page_{i+1}.jpg")
        page.save(img_path, "JPEG")
        
        # Run OCR on processed image
        all_text.extend(process_image(img_path))

else:
    all_text.extend(process_image(file_path))

# Save raw OCR text
with open(os.path.join(output_dir, "ocr_raw.json"), "w", encoding="utf-8") as f:
    json.dump(all_text, f, indent=4, ensure_ascii=False)

# Extract structured fields
structured_data = extract_generic_fields(all_text)

with open(os.path.join(output_dir, "structured_output.json"), "w", encoding="utf-8") as f:
    json.dump(structured_data, f, indent=4, ensure_ascii=False)

print("✅ OCR completed")
print("✅ Structured data saved")
print(structured_data)
