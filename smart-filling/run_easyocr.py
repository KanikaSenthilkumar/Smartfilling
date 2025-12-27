import easyocr
import cv2
import os
import re
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(BASE_DIR, "output")
os.makedirs(output_dir, exist_ok=True)


reader = easyocr.Reader(['en'], gpu=False)

def process_image(image_path):
    # Check if file exists
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at path: {image_path}")

    img = cv2.imread(image_path)

    if img is None:
        raise ValueError("Image exists but OpenCV cannot read it. Check format.")

    results = reader.readtext(img)
    return [text for (_, text, _) in results]

def extract_aadhaar_fields(text_lines):
    import re

    data = {
        "name": None,
        "dob": None,
        "gender": None,
        "aadhaar_number": None,
        "address": None,
        "phone_number": None
    }

    cleaned = [line.strip() for line in text_lines if len(line.strip()) > 2]

    ignore_words = [
        "GOVERNMENT", "INDIA", "UNIQUE", "IDENTIFICATION",
        "AUTHORITY", "DOB", "MALE", "FEMALE", "VID",
        "ENROLMENT", "SIGNATURE", "AADHAAR", "S/O", "D/O", "W/O"
    ]
# ---------------- Aadhaar Number (FIXED) ----------------
    for i, line in enumerate(cleaned):
        upper = line.upper()

        # Skip VID lines
        if "VID" in upper:
            continue

        # Aadhaar pattern
        match = re.search(r"\b\d{4}\s\d{4}\s\d{4}\b", line)
        if match:
            # Prefer Aadhaar mentioned near keyword
            if "AADHAAR" in upper or "AADHAAR NO" in upper:
                data["aadhaar_number"] = match.group()
                break

            # Otherwise pick first valid Aadhaar
            if data["aadhaar_number"] is None:
                data["aadhaar_number"] = match.group()


    # -------- DOB --------
    for line in cleaned:
        dob_match = re.search(r"\b\d{2}/\d{2}/\d{4}\b", line)
        if dob_match:
            data["dob"] = dob_match.group()

    # -------- Gender --------
    for line in cleaned:
        upper = line.upper()
        if "MALE" in upper:
            data["gender"] = "Male"
        elif "FEMALE" in upper:
            data["gender"] = "Female"

    # -------- Name (SMART LOGIC) --------
    for i, line in enumerate(cleaned):
        upper = line.upper()

        # skip unwanted lines
        if any(word in upper for word in ignore_words):
            continue

        # alphabet-only names
        if line.replace(" ", "").isalpha():
            words = line.split()
            if 1 <= len(words) <= 4:
                # name usually appears before DOB
                if i + 1 < len(cleaned) and "DOB" in cleaned[i + 1].upper():
                    data["name"] = line
                    break

                # or standalone name
                if data["name"] is None:
                    data["name"] = line
    # ---------------- ADDRESS EXTRACTION (NAME → PIN BASED) ----------------
    address_lines = []
    name_index = -1

    # find name index
    for i, line in enumerate(cleaned):
        if line.strip().lower() == data["name"].lower():
            name_index = i
            break

    # collect address after name until PIN
    if name_index != -1:
        for line in cleaned[name_index + 1:]:
            # skip relations
            if re.search(r"\bS/O\b|\bD/O\b|\bW/O\b", line, re.I):
                address_lines.append(line)
                continue

            address_lines.append(line)

            # stop at PIN
            if re.search(r"\b\d{6}\b", line):
                break

    # clean noise
    address_lines = [
        l for l in address_lines
        if not re.search(r"signature|aadhaar|vid|government", l, re.I)
    ]

    if address_lines:
        data["address"] = ", ".join(address_lines)

    # ---------------- PHONE NUMBER EXTRACTION ----------------
    for line in cleaned:
        phone_match = re.search(r"\b[6-9]\d{9}\b", line)
        if phone_match:
            data["phone_number"] = phone_match.group()
            break

    return data

if __name__ == "__main__":

    image_path = "data/trial/eg_aadhar_malli_page-0001.jpg"

    print("📷 Reading image from:", image_path)
    print("📂 Exists?", os.path.exists(image_path))

    extracted_text = process_image(image_path)

    print("\n--- OCR TEXT ---")
    for line in extracted_text:
        print(line)

    structured = extract_aadhaar_fields(extracted_text)

    print("\n--- STRUCTURED DATA ---")
    print(structured)

    # -------- SAVE RAW OCR TEXT --------
    ocr_path = os.path.join(output_dir, "ocr_raw.json")
    with open(ocr_path, "w", encoding="utf-8") as f:
        json.dump(extracted_text, f, indent=4, ensure_ascii=False)

    # -------- SAVE STRUCTURED AADHAAR DATA --------
    structured_path = os.path.join(output_dir, "aadhaar_structured.json")
    with open(structured_path, "w", encoding="utf-8") as f:
        json.dump(structured, f, indent=4, ensure_ascii=False)

    print("\n💾 Files saved successfully:")
    print(" -", ocr_path)
    print(" -", structured_path)
