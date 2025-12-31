"""
Smart Filling Frontend - Route Definitions
"""

from flask import render_template, request, send_file, session
import os
from utils.pdf_filler import fill_form_with_data, map_ocr_to_internal

# Import OCR processing (with fallback to mock)
try:
    from utils.ocr_processor import process_image
    USE_REAL_OCR = True
    print("Using real OCR processing from utils.ocr_processor")
except ImportError as e:
    print(f"OCR not available in main env ({e}), checking ocrenv...")
    try:
        # Try to use ocrenv for OCR
        import subprocess
        import sys
        result = subprocess.run([
            r"c:\Users\USER\OneDrive\Desktop\smartfilling-frontend\ocrenv\Scripts\python.exe",
            "-c", "from utils.ocr_processor import process_image; print('OCR_READY')"
        ], capture_output=True, text=True, cwd=r"c:\Users\USER\OneDrive\Desktop\smartfilling-frontend")

        if "OCR_READY" in result.stdout:
            USE_REAL_OCR = True
            print("Using real OCR processing via ocrenv")

            def process_image(file_path):
                """Call OCR processing via ocrenv"""
                result = subprocess.run([
                    r"c:\Users\USER\OneDrive\Desktop\smartfilling-frontend\ocrenv\Scripts\python.exe",
                    "-c", f"from utils.ocr_processor import process_image; import json, sys; data = process_image(r'{file_path}'); sys.stdout.write(json.dumps(data or {{}}))"
                ], capture_output=True, text=True, cwd=r"c:\Users\USER\OneDrive\Desktop\smartfilling-frontend")

                if result.returncode == 0 and result.stdout.strip():
                    import json
                    try:
                        data = json.loads(result.stdout.strip())
                        if data:  # Only return if we got actual data
                            return data
                    except json.JSONDecodeError:
                        pass

                # Fallback to mock data if OCR fails
                print("OCR processing failed, using mock data for testing")
                return {
                    "DocumentType": "Aadhaar",
                    "Name": "John Doe",
                    "DOB": "15/08/1990",
                    "Gender": "Male",
                    "AadhaarNo": "123456789012",
                    "Address": "123 Main Street, City, State 12345"
                }
        else:
            raise ImportError("OCR not ready in ocrenv")

    except Exception as e2:
        print(f"OCR not available in ocrenv either ({e2}), using mock data")
        USE_REAL_OCR = False

        def process_image(file_path):
            """Mock OCR processing - returns sample extracted data"""
            return {
                "DocumentType": "Aadhaar",
                "Name": "John Doe",
                "DOB": "15/08/1990",
                "Gender": "Male",
                "AadhaarNo": "123456789012",
                "Address": "123 Main Street, City, State 12345"
            }

def register_routes(app):
    """Register all application routes."""

    @app.route("/")
    def login():
        return render_template("login.html")

    @app.route("/dashboard")
    def dashboard():
        return render_template("dashboard.html")

    @app.route("/form1")
    def form1():
        return render_template("form1.html", data=None)

    @app.route("/process_aadhaar", methods=["POST"])
    def process_aadhaar():
        file = request.files.get("aadhaar_image")
        if not file:
            return "No file uploaded"

        upload_dir = app.config['UPLOAD_FOLDER']
        os.makedirs(upload_dir, exist_ok=True)

        file_path = os.path.join(upload_dir, file.filename)
        file.save(file_path)

        # OCR Processing (real OCR if available, otherwise mock)
        if USE_REAL_OCR:
            print(f"Processing {file_path} with real OCR...")
            ocr_data = process_image(file_path)
        else:
            print(f"Processing {file_path} with mock OCR (real OCR not available)")
            ocr_data = process_image(file_path)  # This will use the mock function

        # Map OCR data to internal form fields
        internal_data = map_ocr_to_internal(ocr_data)

        # Store in session for download
        session["form1_data"] = internal_data

        return render_template("form1.html",
                             data=internal_data,
                             ocr_status="Real OCR" if USE_REAL_OCR else "Mock OCR")

    @app.route("/download_form1", methods=["POST"])
    def download_form1():
        data = session.get("form1_data")
        if not data:
            return "No form data available"

        # Generate filled PDF form (like Form 2)
        filled_pdf_path = fill_form_with_data("aadhaar_form", data)

        if filled_pdf_path:
            return send_file(filled_pdf_path, as_attachment=True, download_name="filled_aadhaar_form1.pdf")
        else:
            return "Error generating filled form"

    @app.route("/form2")
    def form2():
        return render_template("form2.html", data=None)

    @app.route("/process_form2", methods=["POST"])
    def process_form2():
        file = request.files.get("aadhaar_file")
        if not file:
            return "No file uploaded"

        upload_dir = app.config['UPLOAD_FOLDER']
        os.makedirs(upload_dir, exist_ok=True)

        file_path = os.path.join(upload_dir, file.filename)
        file.save(file_path)

        # OCR Processing (real OCR if available, otherwise mock)
        if USE_REAL_OCR:
            print(f"Processing {file_path} with real OCR...")
            ocr_data = process_image(file_path)
        else:
            print(f"Processing {file_path} with mock OCR (real OCR not available)")
            ocr_data = process_image(file_path)  # This will use the mock function

        # Map OCR data to internal form fields
        internal_data = map_ocr_to_internal(ocr_data)

        # Store in session for download
        session["form2_data"] = internal_data

        # Generate filled PDF
        filled_pdf_path = fill_form_with_data("aadhaar_form", internal_data)

        if filled_pdf_path:
            # Store PDF path in session for serving
            session["form2_pdf_path"] = filled_pdf_path
            session["form2_data"] = internal_data

            print(f"DEBUG: PDF created successfully: {filled_pdf_path}")
            print(f"DEBUG: Session form2_pdf_path set to: {session.get('form2_pdf_path')}")

            # Return template with data (PDF will be served via separate route)
            return render_template("form2.html",
                                 data=internal_data,
                                 filled_pdf=True,
                                 ocr_status="Real OCR" if USE_REAL_OCR else "Mock OCR")
        else:
            print("DEBUG: PDF creation failed")
            return f"Error generating filled form. OCR data: {ocr_data}"

    @app.route("/download_form2", methods=["POST"])
    def download_form2():
        data = session.get("form2_data")
        pdf_path = session.get("form2_pdf_path")

        if not data or not pdf_path or not os.path.exists(pdf_path):
            return "No form data or PDF available"

        return send_file(pdf_path, as_attachment=True, download_name="filled_aadhaar_form.pdf")

    @app.route("/preview_form1_pdf")
    def preview_form1_pdf():
        """Serve the filled PDF for Form 1 preview"""
        data = session.get("form1_data")
        if not data:
            return "No form data available", 404

        # Generate the PDF on-the-fly for preview
        filled_pdf_path = fill_form_with_data("aadhaar_form", data)

        if filled_pdf_path:
            return send_file(filled_pdf_path, mimetype="application/pdf")
        else:
            return "Error generating PDF", 500

    @app.route("/preview_form2_pdf")
    def preview_form2_pdf():
        """Serve the filled PDF for Form 2 preview"""
        pdf_path = session.get("form2_pdf_path")
        if not pdf_path:
            print("DEBUG: No PDF path in session")
            return "No PDF path in session", 404

        if not os.path.exists(pdf_path):
            print(f"DEBUG: PDF file does not exist: {pdf_path}")
            return f"PDF file does not exist: {pdf_path}", 404

        print(f"DEBUG: Serving PDF: {pdf_path}")
        return send_file(pdf_path, mimetype="application/pdf")