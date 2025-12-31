import easyocr
import ollama
import json
import re
import os
from datetime import datetime

class UniversalIndianExtractor:
    def __init__(self):
        print("Initializing OCR (English only)...")
        try:
            self.reader = easyocr.Reader(['en'])
        except Exception as e:
            print(f"Error initializing OCR: {e}")
            raise

        if not os.path.exists('data/output'):
            os.makedirs('data/output')

    def extract_json_from_text(self, text):
        """Finds and parses the JSON block within the AI response."""
        try:
            start_idx = text.find('{')
            end_idx = text.rfind('}')
            if start_idx == -1 or end_idx == -1: return None
            json_str = text[start_idx:end_idx + 1]
            return json.loads(json_str)
        except Exception as e:
            print(f"JSON Parsing Error: {e}")
            return None

    def clean_id_logic(self, value):
        """Standardizes IDs: removes spaces, symbols, and fixes O to 0."""
        if not value: return ""
        # Convert to string, uppercase, remove spaces, change letter O to number 0
        val = str(value).upper().replace(" ", "").replace("O", "0")
        return val

    def post_process_data(self, data):
        """Applies strict validation for Indian document formats."""
        doc_type = data.get("DocumentType", "").upper()

        # 1. AADHAAR CARD (Strict 12 digits)
        if "AADHAAR" in doc_type or "ADHAR" in doc_type:
            raw_val = self.clean_id_logic(data.get("AadhaarNo", data.get("ID_Number", "")))
            clean_digits = re.sub(r'[^0-9]', '', raw_val)

            # If AI merged Aadhaar (12) + VID (16) = 28 digits
            if len(clean_digits) >= 28:
                data["AadhaarNo"] = clean_digits[:12]
                data["VID"] = clean_digits[12:28]
            else:
                data["AadhaarNo"] = clean_digits[:12] # Keep first 12 digits only

        # 2. PAN CARD (10 Chars: 5 Letters, 4 Digits, 1 Letter)
        elif "PAN" in doc_type:
            raw_val = self.clean_id_logic(data.get("PAN_Number", data.get("ID_Number", "")))
            clean_pan = "".join(re.findall(r'[A-Z0-9]', raw_val))
            data["PAN_Number"] = clean_pan[:10]

        # 3. VOTER ID (EPIC Number - 10 Chars)
        elif "VOTER" in doc_type:
            raw_val = self.clean_id_logic(data.get("EPIC_Number", data.get("ID_Number", "")))
            data["EPIC_Number"] = "".join(re.findall(r'[A-Z0-9]', raw_val))[:10]

        # 4. RATION CARD
        elif "RATION" in doc_type:
            raw_val = self.clean_id_logic(data.get("RationCardNo", data.get("ID_Number", "")))
            data["RationCardNo"] = re.sub(r'[^A-Z0-9]', '', raw_val)

        # 5. BIRTH CERTIFICATE
        elif "BIRTH" in doc_type:
            reg_no = str(data.get("RegistrationNo", ""))
            data["RegistrationNo"] = re.sub(r'[^A-Z0-9/]', '', reg_no.upper())

        return data

    def process_image(self, image_path):
        if not os.path.exists(image_path):
            print(f"Error: File '{image_path}' not found.")
            return

        # STEP 1: OCR Extraction
        print(f"\n--- Scanning: {os.path.basename(image_path)} ---")
        results = self.reader.readtext(image_path, detail=0)
        raw_text = " ".join(results)

        if not raw_text.strip():
            print("No text detected in image.")
            return

        # STEP 2: Llama 3 Processing
        print("Analyzing with Llama 3...")
        system_msg = (
            "You are an Indian Document Parser. Extract data into JSON.\n"
            "1. Detect 'DocumentType' (Aadhaar, PAN, VoterID, RationCard, BirthCertificate).\n"
            "2. Extract Name, DOB, Gender, ID Numbers, and Address.\n"
            "3. If text is in Hindi/Tamil/etc., use English for JSON keys, but keep values in original script.\n"
            "4. IMPORTANT: If Aadhaar is 12 digits and VID is 16 digits, keep them separate.\n"
            "5. Return ONLY valid JSON."
        )

        try:
            response = ollama.generate(
                model='llama3.2:1b',
                prompt=f"OCR Text: {raw_text}",
                format='json',
                system=system_msg
            )

            data = self.extract_json_from_text(response['response'])

            if data:
                # STEP 3: Validate and Format
                data = self.post_process_data(data)

                # STEP 4: Save to File
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                label = data.get("DocumentType", "Unknown").replace(" ", "_")
                save_path = f"data/output/{label}_{ts}.json"

                with open(save_path, "w", encoding="utf-8") as f:
                    # ensure_ascii=False ensures Hindi/Tamil text is saved correctly
                    json.dump(data, f, indent=4, ensure_ascii=False)

                print(f"SUCCESS: Data saved to {save_path}")
                return data
            else:
                print("Failed to structure data from AI response.")

        except Exception as e:
            print(f"An unexpected error occurred: {e}")

# Standalone function for easy importing
def process_image(image_path):
    """Process an image and return extracted data"""
    extractor = UniversalIndianExtractor()
    return extractor.process_image(image_path)

# --- MAIN RUN ---
if __name__ == "__main__":
    extractor = UniversalIndianExtractor()

    # Update the path below to your image file
    my_document = "data/eg_aadhar_malli_page-0001.jpg"

    final_data = extractor.process_image(my_document)

    if final_data:
        print("\nFinal Extracted JSON:")
        print(json.dumps(final_data, indent=4, ensure_ascii=False))