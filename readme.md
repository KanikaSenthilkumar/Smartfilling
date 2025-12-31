# Smart Filling Frontend

A Flask-based web application for intelligent document processing and form filling using OCR and AI.

## Features

- **OCR Processing**: Extract text from Aadhaar cards and other Indian documents
- **AI-Powered Data Extraction**: Use Llama3 to intelligently parse document data
- **PDF Form Filling**: Automatically fill government forms with extracted data
- **Multi-Form Support**: Support for different types of forms (Aadhaar, PAN, etc.)
- **Web Interface**: User-friendly web interface for document upload and processing

## Project Structure

```
smartfilling-frontend/
├── app/                          # Flask application package
│   ├── __init__.py              # Application factory
│   └── routes.py                # Route definitions
├── utils/                        # Utility modules
│   ├── ocr_processor.py         # OCR processing logic
│   └── pdf_filler.py            # PDF manipulation logic
├── static/                       # Static assets
│   ├── css/                     # Stylesheets
│   │   ├── style.css
│   │   ├── dashboard.css
│   │   └── form.css
│   ├── js/                      # JavaScript files
│   ├── images/                  # Image assets
│   │   ├── logo.png
│   │   ├── image.png
│   │   └── icons/
│   └── forms/                   # PDF form templates
│       └── aadhaar_form.pdf
├── templates/                    # Jinja2 templates
│   ├── base.html                # Base template
│   ├── dashboard.html
│   ├── login.html
│   ├── form1.html
│   └── form2.html
├── data/                         # Data files
│   ├── config/                  # Configuration files
│   │   ├── aadhaar_form_mapping.json
│   │   └── data_contract.json
│   ├── mock/                    # Mock data for testing
│   │   ├── aadhaar_form_ocr.json
│   │   └── mock_ocr_output.json
│   └── output/                  # Generated PDFs
├── tests/                        # Unit tests
├── config.py                     # Application configuration
├── run.py                        # Application entry point
├── requirements.txt              # Python dependencies
├── README.md                     # This file
└── .gitignore                    # Git ignore rules
```

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd smartfilling-frontend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up OCR environment (optional):**
   ```bash
   # Create separate environment for OCR dependencies
   python -m venv ocrenv
   source ocrenv/bin/activate  # On Windows: ocrenv\Scripts\activate
   pip install easyocr ollama
   ```

## Configuration

The application uses a configuration system with different environments:

- **Development**: `config.DevelopmentConfig`
- **Production**: `config.ProductionConfig`
- **Testing**: `config.TestingConfig`

Set the environment using the `FLASK_ENV` environment variable:

```bash
export FLASK_ENV=development  # or production, testing
```

## Running the Application

### Development Mode
```bash
python run.py
```

### Production Mode
```bash
export FLASK_ENV=production
python run.py
```

The application will be available at `http://localhost:5000`

## Usage

1. **Access the application** at `http://localhost:5000`
2. **Login** to access the dashboard
3. **Choose a form** (Form 1 or Form 2)
4. **Upload a document** (Aadhaar card image/PDF)
5. **Review extracted data** and edit if necessary
6. **Download the filled PDF form**

## API Endpoints

- `GET /` - Login page
- `GET /dashboard` - Main dashboard
- `GET /form1` - Form 1 interface
- `POST /process_aadhaar` - Process uploaded document
- `POST /download_form1` - Download filled form
- `GET /form2` - Form 2 interface
- `POST /process_form2` - Process document for Form 2
- `POST /download_form2` - Download Form 2 PDF

## OCR Processing

The application supports two OCR modes:

1. **Real OCR**: Uses EasyOCR + Llama3 for accurate text extraction and parsing
2. **Mock OCR**: Uses predefined sample data for testing

The system automatically falls back to mock data if OCR dependencies are not available.

## Form Configuration

Forms are configured using JSON files in `data/config/`:

- `aadhaar_form_mapping.json` - Maps form fields to PDF fields
- `data_contract.json` - Defines data validation rules

## Testing

Run tests using pytest:

```bash
python -m pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

[Add your license information here]

## Support

For support and questions, please [add contact information or issue tracker link]
