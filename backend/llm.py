import re

def extract_aadhaar_fields(text):
    data = {
        "name": "",
        "date_of_birth": "",
        "gender": "",
        "aadhaar_number": "",
        "address": ""
    }

    # ---------- Aadhaar Number ----------
    m = re.search(r"\b\d{4}\s\d{4}\s\d{4}\b", text)
    if m:
        data["aadhaar_number"] = m.group()

    # ---------- Date of Birth ----------
    m = re.search(r"\b\d{2}/\d{2}/\d{4}\b", text)
    if m:
        data["date_of_birth"] = m.group()

    # ---------- Gender ----------
    if re.search(r"\bfemale\b", text, re.IGNORECASE):
        data["gender"] = "Female"
    elif re.search(r"\bmale\b", text, re.IGNORECASE):
        data["gender"] = "Male"

    # ---------- Name Extraction (IMPROVED OLD LOGIC) ----------
    # Aadhaar names are usually near DOB / Gender
    lines = re.split(r"\n|,", text)

    for line in lines:
        line_clean = line.strip()
        # Skip noise lines
        if (
            len(line_clean) < 4 or
            "government" in line_clean.lower() or
            "unique identification" in line_clean.lower() or
            "address" in line_clean.lower()
        ):
            continue

        # Candidate name: 2–4 words, alphabets only
        if re.match(r"^[A-Za-z ]{5,40}$", line_clean):
            words = line_clean.split()
            if 1 < len(words) <= 4:
                data["name"] = line_clean
                break

    # Fallback name (never empty)
    if not data["name"]:
        caps = re.findall(r"[A-Z][a-z]+", text)
        if len(caps) >= 2:
            data["name"] = caps[0] + " " + caps[1]

    # ---------- Address Extraction (FIXED: NEVER EMPTY) ----------
    addr_match = re.search(
        r"Address[:\-]?(.*)", text, re.IGNORECASE | re.DOTALL
    )

    if addr_match:
        data["address"] = addr_match.group(1).strip()
    else:
        # Best-effort address: lines containing location keywords
        addr_lines = []
        for line in lines:
            if any(k in line.lower() for k in ["village", "district", "post", "state", "pin", "road"]):
                addr_lines.append(line.strip())

        if addr_lines:
            data["address"] = ", ".join(addr_lines[:3])
        else:
            # Absolute fallback
            data["address"] = text[:250]

    return data




