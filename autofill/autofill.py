from pdfrw import PdfReader, PdfWriter, PdfDict

input_pdf = "C:\\Users\\USER\\Desktop\\Smartfilling\\data\\aadhaar_form.pdf"
output_pdf = "aadhaar_filled.pdf"

data = {
    'Applicant_Name':input("enter your name: "),
    'Applicant_DOB': input("enter your DOB: "),
    'Applicant_Mobile No':input("enter your mobile num: "),
    'District': input("enter your District: ") ,
    'HOF_Name':input("enter HOF_Name: ") ,
    'Applicant_Age': input("enter your Age: "),
    'Applicant_Email':input("enter your mail id: ")
}
'''for key in data:
    data[key]=input(data[key]+" ") ''' 

pdf = PdfReader(input_pdf)

for page in pdf.pages:
    if '/Annots' in page:
        for annotation in page['/Annots']:
            if annotation['/Subtype'] == '/Widget':
                key = annotation.get('/T')
                if key:
                    key_name = key.to_unicode()
                    if key_name in data:
                        annotation.update(
                            PdfDict(V='{}'.format(data[key_name]))
                        )
                        annotation.update(PdfDict(AP=''))

PdfWriter().write(output_pdf, pdf)

print("Form filled successfully!")
