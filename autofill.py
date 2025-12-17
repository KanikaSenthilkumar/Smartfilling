from pdfrw import PdfReader, PdfWriter, PdfDict, PdfObject

input_pdf = r"C:\Users\USER\Desktop\Smartfilling\data\aadhaar_form.pdf"
output_pdf = "aadhaar_filled.pdf"

data = {
    'Applicant_Name': input("enter your name: "),
    'Applicant_DOB': input("enter your DOB: "),
    'Applicant_Mobile No': input("enter your mobile num: "),
    'District': input("enter your District: "),
    'HOF_Name': input("enter HOF_Name: "),
    'Applicant_Age': input("enter your Age: "),
    'Applicant_Email': input("enter your mail id: ")
}

pdf = PdfReader(input_pdf)

for page in pdf.pages:
    annots = page.get('/Annots') or []
    for annotation in annots:
        subtype = annotation.get('/Subtype')
        if subtype != '/Widget':
            continue

        key = annotation.get('/T')
        if not key:
            continue

        try:
            key_name = key.to_unicode()
        except Exception:
            key_name = str(key).strip('()')

        if key_name in data:
            value = data[key_name]
            annotation.update(PdfDict(V='{}'.format(value)))
            # remove the appearance so PDF viewers will regenerate it
            if '/AP' in annotation:
                annotation.pop('/AP')

# Ensure viewers regenerate appearances so filled values are visible
if not getattr(pdf, 'Root', None):
    pdf.Root = PdfDict()
if not pdf.Root.get('AcroForm'):
    pdf.Root.AcroForm = PdfDict()
pdf.Root.AcroForm.update(PdfDict(NeedAppearances=PdfObject('true')))

PdfWriter().write(output_pdf, pdf)

print("Form filled successfully!")
