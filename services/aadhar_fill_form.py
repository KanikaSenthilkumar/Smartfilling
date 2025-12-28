from pdfrw import PdfReader, PdfWriter, PdfDict
import re, os, json, sys
from datetime import datetime
from pdfrw import PdfName
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# To fill the PDF form fields
def fill_pdf(input_path, output_path, mapped_data):
    pdf = PdfReader(input_path)
    for page in pdf.pages:
        annots = page.get('/Annots')
        if not annots:
            continue
        for annotation in annots:
            if annotation.get('/Subtype') != PdfName.Widget:
                continue
            t = annotation.get('/T')
            if not t:
                continue
            try:
                key_name = t.to_unicode()
            except Exception:
                key_name = str(t)
                if key_name.startswith('(') and key_name.endswith(')'):
                    key_name = key_name[1:-1]
                if key_name.startswith('/'):
                    key_name = key_name[1:]
            if key_name not in mapped_data:
                continue
            value = mapped_data[key_name]

            if key_name == "Applicant_DOB":
                logger.debug("Setting %s to '%s' (type: %s)", key_name, value, type(value).__name__)

            # Handle checkbox fields
            if annotation.get('/FT') == PdfName.Btn:  # Button/Checkbox field
                # Convert value to boolean-like representation
                if isinstance(value, bool):
                    checkbox_value = value
                elif isinstance(value, int):
                    checkbox_value = bool(value)
                elif isinstance(value, str):
                    checkbox_value = value.lower() in ['true', '1', 'yes', 'on', 'checked']
                elif value is None or value == "":
                    checkbox_value = False
                else:
                    checkbox_value = bool(value)

                # Set checkbox state - use /Yes for checked, /Off for unchecked
                if checkbox_value:
                    annotation.update(PdfDict(V=PdfName.Yes, AS=PdfName.Yes))
                else:
                    annotation.update(PdfDict(V=PdfName.Off, AS=PdfName.Off))
            else:
                # Regular text field
                annotation.update(PdfDict(V=value or ""))
                if key_name == "Applicant_DOB":
                    logger.debug("After update, annotation.get('/V'): %s", annotation.get('/V'))

            # Remove appearance stream to force regeneration
            if '/AP' in annotation:
                del annotation['/AP']

    PdfWriter().write(output_path, pdf)


# To validate the extracted data
def validate(data):
    errors = []

    if not data.get("name"):
        errors.append("Name is missing")

    dob = data.get("dob")
    if not dob:
        errors.append("DOB is missing")
    else:
        try:
            datetime.strptime(dob, "%d/%m/%Y")
        except Exception:
            errors.append("DOB format invalid")

    gender = data.get("gender")
    if gender and gender not in ["Male", "Female", "Other"]:
        errors.append("Invalid gender")

    aadhaar = (data.get("aadhaar_number") or "").replace(" ", "")
    if aadhaar and not re.match(r"^\d{12}$", aadhaar):
        errors.append("Invalid Aadhaar number (expect 12 digits)")
    return errors


# To map extracted data to PDF fields' names
def map_data_to_pdf(form_config, extracted_data):
    mapped = {}

    for field, config in form_config["fields"].items():
        pdf_field = config["pdf_field"]
        # Get value from extracted_data using the internal field name
        value = extracted_data.get(field)
        if value is not None:
            mapped[pdf_field] = value

    return mapped


# To run the entire pipeline
def run_pipeline(form_config, extracted_data, input_pdf, output_pdf):
    errors = validate(extracted_data)
    if errors:
        return {"status": "error", "errors": errors}

    mapped_data = map_data_to_pdf(form_config, extracted_data)
    fill_pdf(input_pdf, output_pdf, mapped_data)

    return {"status": "success", "mapped_data": mapped_data}


# Helper to pick first non-empty key from OCR payload
def first_from(src, *keys):
    for k in keys:
        v = src.get(k)
        if v not in (None, ""):
            return v
    return None


def fill_form(form_type):
    """
    Generic form filler that works with any form type.
    
    Args:
        form_type: Type of form to fill (e.g., 'aadhaar', 'driving_license')
    """
    base_path = os.path.dirname(__file__)
    config_path = os.path.normpath(
        os.path.join(base_path, "..", "config", f"{form_type}_mapping.json")
    )
    mock_path = os.path.normpath(
        os.path.join(base_path, "..", "mock", f"{form_type}_ocr.json")
    )
    input_pdf = os.path.normpath(
        os.path.join(base_path, "..", "data", f"{form_type}.pdf")
    )
    output_pdf = os.path.normpath(
        os.path.join(base_path, "..", "data", f"{form_type}_filled.pdf")
    )

    # Load configuration
    if not os.path.exists(config_path):
        logger.error(f"Form config not found: {config_path}")
        return {"status": "error", "errors": [f"Config file not found for {form_type}"]}

    with open(config_path, "r", encoding="utf-8") as fh:
        form_config = json.load(fh)

    # Load OCR data
    if not os.path.exists(mock_path):
        logger.error(f"OCR data not found: {mock_path}")
        return {"status": "error", "errors": [f"OCR data file not found for {form_type}"]}

    with open(mock_path, "r", encoding="utf-8") as fh:
        ocr_data = json.load(fh)

    # Check if input PDF exists
    if not os.path.exists(input_pdf):
        logger.error(f"Input PDF not found: {input_pdf}")
        return {"status": "error", "errors": [f"Input PDF not found for {form_type}"]}

    # Use OCR data directly
    merged_ocr = ocr_data or {}

    # Map OCR keys to internal keys expected by form config
    # The config maps internal names -> PDF field names
    # But we have PDF field names in OCR data, so we need to use them directly
    # as the mapped_data for fill_pdf
    
    # Create mapped data directly from OCR data (which already has PDF field names)
    mapped_data = {}
    for field, config in form_config["fields"].items():
        pdf_field = config["pdf_field"]
        # Try to get value from OCR data using the PDF field name
        if pdf_field in merged_ocr:
            value = merged_ocr[pdf_field]
            if value is not None:
                mapped_data[pdf_field] = value

    # Run the PDF filler directly
    result = fill_pdf(input_pdf, output_pdf, mapped_data)
    
    if result is None:  # fill_pdf returns None on success
        logger.info(f"✓ {form_type.upper()} form filled successfully!")
        logger.info(f"Output saved to: {output_pdf}")
        return {"status": "success", "mapped_data": mapped_data}
    else:
        logger.error(f"✗ Failed to fill {form_type} form")
        return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fill_form.py <form_type>")
        sys.exit(1)

    form_type = sys.argv[1]
    result = fill_form(form_type)

    if result["status"] != "success":
        sys.exit(1)