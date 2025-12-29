from flask import Flask, render_template, request, send_file, session
import os

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

from backend.ocr import extract_text_from_file
from backend.llm import extract_aadhaar_fields

app = Flask(__name__)
app.secret_key = "smartfilling-secret-key-123"


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

    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, file.filename)
    file.save(file_path)

    # OCR
    raw_text = extract_text_from_file(file_path)

    # Extraction (LLM / heuristic)
    llm_data = extract_aadhaar_fields(raw_text)

    data = {
        "name": llm_data.get("name", ""),
        "dob": llm_data.get("date_of_birth", ""),
        "gender": llm_data.get("gender", ""),
        "aadhaar": llm_data.get("aadhaar_number", ""),
        "address": llm_data.get("address", "")
    }

    session["form1_data"] = data

    return render_template("form1.html", data=data)


@app.route("/download_form1", methods=["POST"])
def download_form1():

    data = session.get("form1_data")
    if not data:
        return "No form data available"

    file_path = "form1_aadhaar.pdf"

    doc = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    table_data = [
        ["Form 1 – Aadhaar Based Details", ""],

        ["Personal Information", ""],
        ["Full Name", data["name"]],
        ["Date of Birth", data["dob"]],
        ["Gender", data["gender"]],

        ["Identity Details", ""],
        ["Aadhaar Number", data["aadhaar"]],

        ["Address", data["address"]],
    ]

    table = Table(table_data, colWidths=[200, 300])

    table.setStyle(TableStyle([
        ("SPAN", (0, 0), (-1, 0)),
        ("SPAN", (0, 1), (-1, 1)),
        ("SPAN", (0, 5), (-1, 5)),
        ("SPAN", (0, 7), (-1, 7)),

        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("BACKGROUND", (0, 1), (-1, 1), colors.whitesmoke),
        ("BACKGROUND", (0, 5), (-1, 5), colors.whitesmoke),

        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
        ("FONTNAME", (0, 5), (-1, 5), "Helvetica-Bold"),

        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))

    doc.build([table])

    return send_file(file_path, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)

    

