"""
Autofill script for Aadhaar update form.
This is a convenience script that uses the generic fill_form module for aadhaar forms.
"""
from services.aadhar_fill_form import fill_form

if __name__ == "__main__":
    result = fill_form("aadhaar_form")
    if result["status"] != "success":
        exit(1)