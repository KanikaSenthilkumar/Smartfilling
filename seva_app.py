import streamlit as st
import easyocr
import ollama
import json
import re
import os
import gc
import numpy as np
from PIL import Image
from pdf2image import convert_from_path
from datetime import datetime

# --- SETTINGS ---
st.set_page_config(page_title="Seva Kendra AI Assistant", layout="wide", page_icon="🏛️")

# --- MEMORY & OCR MANAGEMENT ---
def clear_memory():
    """Clears OCR models from RAM to prevent the 'Size Mismatch' error."""
    if 'reader' in st.session_state:
        del st.session_state.reader
    gc.collect()

def get_reader(lang_code):
    """Initializes EasyOCR for English + One Regional Language."""
    # We use gpu=False because of the low system memory mentioned in your error
    return easyocr.Reader(['en', lang_code], gpu=False)

# --- BUSINESS LOGIC ---
class SevaEngine:
    @staticmethod
    def extract_json(text):
        try:
            start = text.find('{')
            end = text.rfind('}')
            if start != -1 and end != -1:
                return json.loads(text[start:end+1])
        except: return None

    @staticmethod
    def validate_data(data):
        """Standardizes IDs and cleans address confusion."""
        doc_type = str(data.get("DocumentType", "")).upper()
        
        # 1. CLEAN ID NUMBERS
        raw_id = str(data.get("AadhaarNo", data.get("PAN_Number", data.get("IDNumber", ""))))
        clean_id = raw_id.upper().replace(" ", "").replace("O", "0")
        
        if "AADHAAR" in doc_type:
            data["AadhaarNo"] = re.sub(r'[^0-9]', '', clean_id)[:12]
        elif "PAN" in doc_type:
            data["PAN_Number"] = re.sub(r'[^A-Z0-9]', '', clean_id)[:10]

        # 2. FIX ADDRESS CONFUSION (Remove Name/CareOf from Street/City)
        if "Address" in data:
            addr = data["Address"]
            forbidden_terms = [str(data.get("Name", "")).upper(), str(data.get("FatherName", "")).upper(), "S/O", "D/O", "W/O", "C/O"]
            
            for key in ["Street", "City", "Locality"]:
                val = str(addr.get(key, "")).upper()
                for term in forbidden_terms:
                    if term and len(term) > 2 and term in val:
                        addr[key] = "" # Wipe incorrect mapping
        return data

# --- USER INTERFACE ---
st.title("🏛️ AI Seva Kendra Assistant")
st.markdown("### Problem Statement 3: AI-Powered Form Filling for Citizen Services")

# Sidebar Configuration
st.sidebar.header("Document Settings")
lang_map = {
    "Hindi": "hi",
    "Tamil": "ta",
    "Telugu": "te",
    "Kannada": "kn",
    "Bengali": "bn",
    "Marathi": "mr"
}
selected_lang = st.sidebar.selectbox("Select Regional Language on Document", list(lang_map.keys()))
lang_code = lang_map[selected_lang]

if "current_lang" not in st.session_state:
    st.session_state.current_lang = lang_code

# If user switches language, wipe memory to prevent Size Mismatch crash
if st.session_state.current_lang != lang_code:
    clear_memory()
    st.session_state.current_lang = lang_code

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📁 1. Upload Document")
    file = st.file_uploader("Upload Image or PDF", type=["jpg", "png", "jpeg", "pdf"])
    
    if file:
        if file.type == "application/pdf":
            with open("temp.pdf", "wb") as f: f.write(file.getbuffer())
            img = convert_from_path("temp.pdf")[0]
        else:
            img = Image.open(file)
        
        st.image(img, caption="Document Preview", use_container_width=True)

        if st.button("🚀 Extract & Map Entities"):
            with st.spinner(f"Using Llama 3.2 (1B) & EasyOCR ({selected_lang})..."):
                # Run OCR
                reader = get_reader(lang_code)
                results = reader.readtext(np.array(img), detail=0)
                raw_text = " ".join(results)
                
                # LLM Entity Extraction
                # Note: We use the 1B model to fit your 2.6GB available RAM
                prompt = (
                    f"OCR Text: {raw_text}. \n"
                    "Instructions: Identify DocumentType. Extract Name, FatherName (from S/O or C/O), DOB, Gender, AadhaarNo. "
                    "In 'Address', extract: {HouseNo, Street, Locality, City, State, Pincode}. "
                    "Rules: Do NOT put Names in the Address. Return ONLY valid JSON."
                )
                
                try:
                    response = ollama.generate(
                        model='llama3.2:1b', 
                        prompt=prompt, 
                        format='json',
                        system="You are an Indian Government Data Entry Specialist. Output valid JSON only."
                    )
                    
                    raw_json = SevaEngine.extract_json(response['response'])
                    if raw_json:
                        st.session_state.form_data = SevaEngine.validate_data(raw_json)
                        st.success("Entity Extraction Successful!")
                except Exception as e:
                    st.error(f"Error: {e}. Check if Llama 3.2:1b is installed.")

with col2:
    st.subheader("📝 2. Verified Form Template")
    if 'form_data' in st.session_state:
        d = st.session_state.form_data
        
        # THIS IS THE FORM MAPPING SECTION FROM YOUR PROBLEM STATEMENT
        with st.form("mapped_form"):
            st.markdown("#### **Personal Information**")
            name = st.text_input("Full Name", value=d.get("Name", ""))
            fname = st.text_input("Father / Guardian Name", value=d.get("FatherName", ""))
            dob = st.text_input("Date of Birth", value=d.get("DOB", ""))
            
            st.markdown("#### **Identity Details**")
            dtype = st.text_input("Document Detected", value=d.get("DocumentType", ""))
            # Pre-fill with whichever ID was found
            id_val = d.get("AadhaarNo", d.get("PAN_Number", d.get("IDNumber", "")))
            id_num = st.text_input("ID Number (Verified)", value=id_val)
            
            st.markdown("#### **Address Details**")
            addr_obj = d.get("Address", {})
            col_a, col_b = st.columns(2)
            with col_a:
                city = st.text_input("City", value=addr_obj.get("City", ""))
                state = st.text_input("State", value=addr_obj.get("State", "Tamil Nadu"))
            with col_b:
                loc = st.text_input("Locality", value=addr_obj.get("Locality", ""))
                pin = st.text_input("Pincode", value=addr_obj.get("Pincode", addr_obj.get("PinCode", "")))
            
            if st.form_submit_button("✅ Final Submit to Seva Kendra Portal"):
                st.balloons()
                st.success("Form submitted successfully!")
                
                # Provide JSON Download
                final_json = json.dumps(d, indent=4, ensure_ascii=False)
                st.download_button("📥 Download Submission Record", final_json, file_name="submission.json")
    else:
        st.info("The form will be pre-filled automatically once you upload and extract a document.")

st.divider()
st.caption("AI Seva Assistant | Optimized for Intel Hardware & Low Memory Systems")