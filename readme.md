**🧠 Smartfilling – AI-Powered Form Filling Assistant**

--> Smartfilling is an AI-powered intelligent form-filling system designed to automate the extraction of user details from Indian citizen documents (like Aadhaar, Birth Certificate, Ration Card) and populate government/service forms accurately and efficiently.

--> The project focuses on OCR + NLP + Rule-based mapping to reduce manual data entry, errors, and processing time.

**🚀 Features**

     📄 Upload documents (PDF / Image)

     🔍 OCR-based text extraction

     🧠 AI-assisted field identification

     🪪 Aadhaar, Birth Certificate & Ration Card support

     ✍️ Automatic form field mapping

     📤 Generate filled forms (PDF)

     🌐 Web-based interface (Flask)

     🗂️ Modular backend design


**🛠️ Tech Stack**

Python 3.10+

Flask – Web framework

OCR – Tesseract / PDF OCR

pdfrw / reportlab – PDF handling

Regex + NLP logic

HTML / CSS – Frontend

**📑 Supported Documents & Extracted Fields**
_🪪 Aadhaar Card_

     Name

     Date of Birth

     Gender

     Address

     Aadhaar Number

_🧾 Birth Certificate_

     Name

     Date of Birth

     Gender

_🏠 Ration Card_

     Head of Family (HOF)

     Address

**⚙️ Installation & Setup**
_1️⃣ Clone the Repository_
git clone https://github.com/KanikaSenthilkumar/Smartfilling.git
cd Smartfilling

_2️⃣ Create Virtual Environment_
python -m venv env
env\Scripts\activate   # Windows

_3️⃣ Install Dependencies_
pip install -r requirements.txt

_4️⃣ Run the Application_
python app.py


_Open browser:_

http://127.0.0.1:5000

**🧪 Example Workflow**

Upload document (PDF/Image)

OCR extracts raw text

AI logic identifies required fields

Fields mapped to form structure

Final filled PDF generated

User reviews & downloads

**🔒 Security & Privacy**

No data stored permanently

Files processed locally

Output folder excluded from Git

Designed with citizen data safety in mind

**📈 Future Enhancements**

✅ Multi-language OCR (Tamil / Hindi)

✅ Face verification

✅ Database integration

✅ API-based form submission

✅ Government form templates

✅ User authentication

**👥 Contributors**

This project is a collaborative effort with clearly defined responsibilities:

***Kanika***
      * Backend development, autofill logic, and system integration
      * Flask backend
      * Document-to-form mapping logic
      * End-to-end workflow integration

***Malleeshwar***
      * OCR, Regex processing, and Ollama integration
      * Text extraction from PDFs/images
      * Regex-based field identification
      * Local LLM (Ollama) experimentation and support
      
***Malini***
      * Frontend development
      * User interface design
      * Upload and interaction pages
      * UI flow for document processing

**🔗 GitHub** : https://github.com/KanikaSenthilkumar

**📜 License**

This project is licensed under the MIT License
