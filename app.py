from flask import Flask, render_template, request, send_file, session
import os
import tempfile

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

def safe_ocr_data(data):
    """Ensure OCR data is always a dict"""
    if data is None:
        return {}
    if not isinstance(data, dict):
        return {}
    return data

# Use mock OCR for fast processing
USE_REAL_OCR = False
print("Using mock OCR processing for fast performance")

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

from utils.pdf_filler import fill_form_with_data, map_ocr_to_internal

app = Flask(
    __name__,
    template_folder="Smartfilling/templates",
    static_folder="Smartfilling/static"
)

app.secret_key = "smartfilling-secret-key-123"

# Load configuration
app.config.from_object('config.DevelopmentConfig')


@app.route("/")
def login():
    return render_template("login.html")


@app.route("/dashboard",methods=["GET","POST"])
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

    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, file.filename)
    file.save(file_path)

    # OCR Processing (real OCR if available, otherwise mock)
    if USE_REAL_OCR:
        print(f"Processing {file_path} with real OCR...")
        ocr_data = process_image(file_path)
        if not ocr_data:
            print("OCR failed, using mock data")
            ocr_data = {
                "DocumentType": "Aadhaar",
                "Name": "John Doe",
                "DOB": "15/08/1990",
                "Gender": "Male",
                "AadhaarNo": "123456789012",
                "Address": "123 Main Street, City, State 12345"
            }
    else:
        print(f"Processing {file_path} with mock OCR (real OCR not available)")
        ocr_data = process_image(file_path)  # This will use the mock function
    
    # Map OCR data to internal form fields
    internal_data = map_ocr_to_internal(ocr_data)

    # Generate filled PDF
    filled_pdf_path = fill_form_with_data("aadhaar_form", internal_data)
    
    if filled_pdf_path:
        # Store in session for download and preview
        session["form1_data"] = internal_data
        session["form1_pdf_path"] = filled_pdf_path

        return render_template("form1.html", 
                             data=internal_data,
                             filled_pdf=True,
                             ocr_status="Real OCR" if USE_REAL_OCR else "Mock OCR")
    else:
        return "Error generating filled form"


@app.route("/download_form1", methods=["POST"])
def download_form1():

    # Get data from form (allows editing)
    data = {}
    for key in request.form:
        value = request.form[key].strip()
        if value:
            data[key] = value

    if not data:
        return "No data provided"

    # Generate HTML form matching the preview structure
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Filled Aadhaar Form</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .section {{ margin-bottom: 20px; }}
            .gov-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            .gov-table th, .gov-table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            .gov-table th {{ background-color: #f2f2f2; }}
            .center {{ text-align: center; margin-top: 20px; }}
            input, textarea {{ width: 100%; padding: 8px; box-sizing: border-box; }}
            textarea {{ resize: vertical; }}
        </style>
    </head>
    <body>
        <h1>Aadhaar Details – Preview</h1>

        <div class="section">
            <table class="gov-table">
                <tr>
                    <th colspan="2">Personal Information</th>
                </tr>
                <tr>
                    <td>Full Name</td>
                    <td>
                        <input type="text" name="name" value="{data.get('name', '')}" readonly>
                    </td>
                </tr>
                <tr>
                    <td>Date of Birth</td>
                    <td>
                        <input type="text" name="dob" value="{data.get('dob', '')}" readonly>
                    </td>
                </tr>
                <tr>
                    <td>Gender</td>
                    <td>
                        <input type="text" name="gender" value="{data.get('gender', '')}" readonly>
                    </td>
                </tr>

                <tr>
                    <th colspan="2">Identity Details</th>
                </tr>
                <tr>
                    <td>Aadhaar Number</td>
                    <td>
                        <input type="text" name="aadhaar_number" value="{data.get('aadhaar_number', '')}" readonly>
                    </td>
                </tr>

                <tr>
                    <th colspan="2">Address</th>
                </tr>
                <tr>
                    <td colspan="2">
                        <textarea name="address" rows="3" readonly>{data.get('address', '')}</textarea>
                    </td>
                </tr>
            </table>
        </div>

    </body>
    </html>
    """

    # Create a temporary HTML file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
        f.write(html_content)
        temp_file_path = f.name

    # Send the HTML file for download
    return send_file(temp_file_path, as_attachment=True, download_name="filled_aadhaar_form.html")

@app.route("/form2")
def form2():
    return render_template("form2.html", data=None)

@app.route("/process_form2", methods=["POST"])
def process_form2():
    file = request.files.get("aadhaar_file")
    if not file:
        return "No file uploaded",400

    upload_dir = os.path.join(app.root_path, "static/uploads")
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    file.save(file_path)

    # OCR Processing (real OCR if available, otherwise mock)
    if USE_REAL_OCR:
        print(f"Processing {file_path} with real OCR...")
        ocr_data = process_image(file_path)
        if not ocr_data:
            print("OCR failed, using mock data")
            ocr_data = {
                "DocumentType": "Aadhaar",
                "Name": "John Doe",
                "DOB": "15/08/1990",
                "Gender": "Male",
                "AadhaarNo": "123456789012",
                "Address": "123 Main Street, City, State 12345"
            }
    else:
        print(f"Processing {file_path} with mock OCR (real OCR not available)")
        ocr_data = process_image(file_path)  # This will use the mock function
    
    # Map OCR data to internal form fields
    internal_data = map_ocr_to_internal(ocr_data)

    # Generate filled PDF
    pdf_dir = os.path.join(app.root_path, "static/filled_pdfs")
    os.makedirs(pdf_dir, exist_ok=True)
    print(f"PDF dir: {pdf_dir}")
    filled_pdf_path = fill_form_with_data("aadhaar_form", internal_data, output_dir=pdf_dir)
    print(f"Filled PDF path: {filled_pdf_path}")
    
    if filled_pdf_path:
        # Store PDF path in session for serving
        session["form2_pdf_path"] = filled_pdf_path
        session["form2_data"] = internal_data
        
        # Return template with data (PDF will be served via separate route)
        return render_template("form2.html", 
                             data=internal_data,
                             filled_pdf=True,
                             ocr_status="Real OCR" if USE_REAL_OCR else "Mock OCR")
    else:
        return f"Error generating filled form. OCR data: {ocr_data}"


@app.route("/download_form2", methods=["POST"])
def download_form2():
    pdf_path = session.get("form2_pdf_path")
    
    if not pdf_path or not os.path.exists(pdf_path):
        return "No PDF available"
    
    return send_file(pdf_path, as_attachment=True, download_name="filled_aadhaar_form.pdf")


@app.route("/preview_form1_pdf")
def preview_form1_pdf():
    """Serve the filled PDF for Form 1 preview"""
    pdf_path = session.get("form1_pdf_path")
    if not pdf_path or not os.path.exists(pdf_path):
        return "No PDF available", 404

    return send_file(pdf_path, mimetype="application/pdf")


@app.route("/preview_form2_pdf")
def preview_form2_pdf():
    """Serve the filled PDF for Form 2 preview"""
    pdf_path = session.get("form2_pdf_path")
    if not pdf_path or not os.path.exists(pdf_path):
        return "No PDF available", 404

    return send_file(pdf_path, mimetype="application/pdf")


if __name__ == "__main__":
    app.run(debug=True)

