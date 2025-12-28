# services/verify_pdf_fields.py
from pdfrw import PdfReader

pdf_path = r"C:\Users\kanik\OneDrive\Desktop\Smartfilling\data\fresh_BC_MBC_form.pdf"
pdf = PdfReader(pdf_path)
field_names = []
print("=== PDF form fields and values ===")
for page_num, page in enumerate(pdf.pages, start=1):
    annots = page.get('/Annots')
    if not annots:
        continue
    for a in annots:
        subtype = a.get('/Subtype')
        if subtype is None:
            continue
        t = a.get('/T')
        v = a.get('/V')
        # decode name/value robustly
        try:
            name = t.to_unicode() if t else "(no name)"
        except Exception:
            name = str(t)
        try:
            value = v.to_unicode() if v else "(empty)"
        except Exception:
            value = str(v) if v else "(empty)"
        field_names.append(name)
for i in field_names:
    if i=="Widget":
        field_names.remove(i)
print(*field_names, sep="\n")