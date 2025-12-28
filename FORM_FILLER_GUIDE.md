# Generic Form Filler - Usage Guide

This is now a **generic, multi-form solution**. You can fill any PDF form with the same code!

## How It Works

### File Structure
```
config/
  ├── aadhaar_mapping.json          # Aadhaar field mappings
  ├── driving_license_mapping.json  # Driving License field mappings (to create)
  └── [any_form]_mapping.json       # Add more forms here

mock/
  ├── aadhaar_ocr.json              # Aadhaar sample data
  ├── driving_license_ocr.json      # Driving License sample data (to create)
  └── [any_form]_ocr.json           # Add more forms here

data/
  ├── aadhaar.pdf                   # Input: Aadhaar form (you need to rename/place this)
  ├── aadhaar_filled.pdf            # Output: Filled Aadhaar form
  ├── driving_license.pdf           # Input: Driving License form
  ├── driving_license_filled.pdf    # Output: Filled Driving License form
  └── [any_form].pdf & [any_form]_filled.pdf

services/
  ├── fill_form.py                  # Generic form filler (core logic)
  ├── autofill.py                   # Convenience script for Aadhaar
  └── fill_driving_license.py       # Convenience script for DL (to create)
```

## Running the Code

### Option 1: Fill Aadhaar Form
```bash
python services/autofill.py
```
OR
```bash
python services/fill_form.py aadhaar
```

### Option 2: Fill Driving License Form
```bash
python services/fill_form.py driving_license
```

### Option 3: Fill Any Other Form
```bash
python services/fill_form.py <form_type>
```

## Adding a New Form (e.g., Driving License)

### Step 1: Create Form Config
Create `config/driving_license_mapping.json`:
```json
{
  "fields": {
    "applicant_name": {"pdf_field": "Full Name"},
    "dob": {"pdf_field": "Date of Birth"},
    "address": {"pdf_field": "Address"},
    // ... map all your form fields
  }
}
```

### Step 2: Create Sample OCR Data
Create `mock/driving_license_ocr.json`:
```json
{
  "Full Name": "JOHN DOE",
  "Date of Birth": "15/06/1990",
  "Address": "123 Main Street",
  // ... populate with sample data
}
```

### Step 3: Place Input PDF
Place your fillable PDF at `data/driving_license.pdf`

### Step 4: Run It
```bash
python services/fill_form.py driving_license
```

## Key Benefits

✅ **Single codebase** - Works for all forms  
✅ **Easy to add new forms** - Just add config + mock data  
✅ **Non-destructive** - Original PDFs remain untouched  
✅ **Flexible** - Change field mappings without touching code  
✅ **Scalable** - Add as many forms as needed  

## Current Files

- `services/fill_form.py` - Core generic form filler
- `services/autofill.py` - Wrapper for Aadhaar forms
- `config/aadhaar_mapping.json` - Aadhaar field mappings
- `mock/aadhaar_ocr.json` - Sample Aadhaar OCR output
