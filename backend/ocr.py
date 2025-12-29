import easyocr
from pdf2image import convert_from_path
import os

reader = easyocr.Reader(['en'])

def extract_text_from_file(file_path):
    text = ""

    if file_path.lower().endswith(".pdf"):
        images = convert_from_path(
            file_path,
            poppler_path=r"C:\poppler\poppler-25.12.0\Library\bin"
        )

        for img in images:
            temp_img = "temp_page.png"
            img.save(temp_img)

            result = reader.readtext(temp_img, detail=0)
            text += " ".join(result) + " "

            os.remove(temp_img)

    else:
        result = reader.readtext(file_path, detail=0)
        text = " ".join(result)

    return text

