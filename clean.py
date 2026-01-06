import pandas as pd
import re
import streamlit as st


st.cache_data
def personal_information(df: pd.DataFrame) -> pd.DataFrame:
    # --- Helper Functions ---
    def clean_contact(val):
        if pd.isna(val) or str(val).strip() == "":
            return ""
        return re.sub(r'[^0-9]', '', str(val))

    def format_date(date_val):
        if pd.isna(date_val) or str(date_val).strip() == "":
            return ""
        try:
            return pd.to_datetime(str(date_val), errors='coerce').strftime('%Y-%m-%d')
        except Exception:
            return ""

    def clean_relation(val):
        if pd.isna(val) or str(val).strip() == "":
            return ""
        val = re.sub(r'[^A-Za-z\s]', '', str(val))  # Remove special chars/numbers
        return val.strip().title()

    def smart_capitalize(name):
        """Capitalize names intelligently (handles McDonald, De La Cruz, O'Connor)."""
        if pd.isna(name) or str(name).strip() == "":
            return ""
        words = str(name).strip().split()
        result = []
        for w in words:
            if w.lower().startswith("mc") and len(w) > 2:
                result.append("Mc" + w[2:].capitalize())
            elif w.lower() in ["de", "da", "del", "la", "le", "van", "von"]:
                result.append(w.lower().capitalize())
            elif "'" in w:  # O'Connor
                parts = w.split("'")
                result.append("'".join([p.capitalize() for p in parts]))
            else:
                result.append(w.capitalize())
        return " ".join(result)

    def normalize_title(val):
        """Normalize Mr./Ms. column while retaining other values."""
        if pd.isna(val) or str(val).strip() == "":
            return ""
        val_clean = str(val).strip().lower().replace(" ", "").replace(".", "")
        if val_clean == "mr":
            return "Mr."
        elif val_clean == "ms":
            return "Ms."
        else:
            return str(val).strip()  # retain original if not recognized

    # --- Apply Cleaning Rules ---
    if 'Contact No.' in df.columns:
        df['Contact No.'] = df['Contact No.'].apply(clean_contact)

    if 'Date of Birth' in df.columns:
        df['Date of Birth'] = df['Date of Birth'].apply(format_date)

    if "Guardian Name" in df.columns:
        df["Guardian Name"] = df["Guardian Name"].apply(smart_capitalize)

    if "Guardian's Contact Number" in df.columns:
        df["Guardian's Contact Number"] = df["Guardian's Contact Number"].apply(clean_contact)

    if 'Relation to Student' in df.columns:
        df['Relation to Student'] = df['Relation to Student'].apply(clean_relation)

    if 'Birth Place' in df.columns:
        df['Birth Place'] = df['Birth Place'].apply(smart_capitalize)

    if 'Language Spoken' in df.columns:
        df['Language Spoken'] = df['Language Spoken'].apply(smart_capitalize)

    if 'Foreign Language Spoken' in df.columns:
        df['Foreign Language Spoken'] = df['Foreign Language Spoken'].apply(smart_capitalize)

    if 'Mr./Ms.' in df.columns:
        df['Mr./Ms.'] = df['Mr./Ms.'].apply(normalize_title)

    return df


#institute mapping
st.cache_data
def insti(df: pd.DataFrame) -> pd.DataFrame:
    mapping = {
        "IABF": [
            "ACCOUNTANCY",
            "GE",
            "HUMAN RESOURCES AND ORGANIZATIONAL DEVELOPMENT",
            "INFORMATION TECHNOLOGY",
            "INTERNAL AUDITING",
            "BUSINESS ADMINISTRATION",
            "ECONOMICS",
            "BSA"
        ],
        "IARFA": [
            "ARCHITECTURE",
            "FINE ARTS"
        ],
        "IAS": [
            "BIOLOGY",
            "BIOLOGY DEPARTMENT",
            "BIOLOGY GRADUATE PROGRAM",
            "COMMUNICATION",
            "COMMUNICATION DEPARTMENT",
            "COMMUNICATION GRADUATE PROGRAM",
            "ENG EDERP",
            "FILIP EDERP",
            "INTERDISCIPLINARY STUDIES",
            "INTERNATIONAL STUDIES",
            "LANGUAGE AND LITERATURE STUDIES",
            "LANGUAGE AND LITERATURE STUDIES GRADUATE PROGRAM",
            "LIT & HUM EDERP",
            "MATHEMATICS",
            "MATHEMATICS - GS",
            "MEDTECH EDERP",
            "POLITICAL SCIENCE",
            "PSYCHOLOGY",
            "PSYCHOLOGY GRADUATE PROGRAM"
        ],
        "IABF-MBA": ["BUSINESS ADMINISTRATION GRADUATE PROGRAM"],
        "IE": ["EDUCATION", "EDUCATION GRADUATE PROGRAM AND TNE"],
        "IL": ["IL/JD-MBA EDERP", "JURIS DOCTOR"],
        "IN": ["IN - GS", "IN EDERP"],
        "JD-MBA": ["JD-MBA"],
        "IHSN": [
            "MEDICAL TECHNOLOGY",
            "MEDICAL TECHNOLOGY DEPARTMENT",
            "NURSING",
            "NURSING GRADUATE PROGRAM",
            "NUTRITION AND DIETETICS",
            "PHARMACY",
            "Nursing Office"
        ],
        "ITHM": [
            "HOTEL AND RESTAURANT MANAGEMENT",
            "TOURISM AND HOSPITALITY MANAGEMENT GRADUATE PROGRAM",
            "TOURISM MANAGEMENT",
            "Tourism & HM Office"
        ]
    }

    def institute_mapping(value):
        value = str(value).strip().upper().replace('\xa0', ' ')
        for inst, keywords in mapping.items():
            if any(value == k.upper() for k in keywords):  # uppercase BOTH sides
                return inst
        return "Unknown"


    if "Department" in df.columns:
        df["Institute"] = df["Department"].apply(institute_mapping)
    else:
        raise KeyError("Missing required column: 'Department'")

    return df


st.cache_data
def category_bachelor(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    def get_category(row):
        # Fetch fields safely
        transferee = str(row.get("Transferee", "")).strip().lower()
        freshman_admit = str(row.get("Freshman when Admitted", "")).strip().lower()

        shs = str(row.get("Freshman from SHS", "")).strip().lower()
        hs = str(row.get("Freshman from HS", "")).strip().lower()
        als = str(row.get("Freshman from ALS", "")).strip().lower()

        cross = str(row.get("Cross-Enrollee", "")).strip().lower()
        supplemental = str(row.get("Supplemental Course", "")).strip().lower()
        tcp = str(row.get("Teacher Certificate Program", "")).strip().lower()
        second_deg = str(row.get("Second Degree", "")).strip().lower()

        # 1️⃣ TRANSFEREE
        if transferee == "yes":
            return "Transferee - Undergraduate"

        # 2️⃣ FRESHMAN
        if freshman_admit == "yes":

            # Priority checking for SHS / HS / ALS
            if shs == "yes":
                return "Freshman - Graduate from Senior High School"

            if hs == "yes":
                return "Freshman - Graduate from High School"

            if als == "yes":
                return "Freshman - Completer from ALS/PEPT"

            # Default if Freshman but none is YES
            return "Freshman - Graduate from High School"

        # 3️⃣ NOT TRANSFEREE, NOT FRESHMAN → Check other categories
        if cross == "yes":
            return "Cross-Enrollee"

        if supplemental == "yes":
            return "Supplemental Course"

        if tcp == "yes":
            return "Teacher Certificate Program"

        if second_deg == "yes":
            return "Second Degree"

        # Nothing matched
        return "No Category found"

    # Apply the logic
    df["category"] = df.apply(get_category, axis=1)

    return df

st.cache_data
def category_graduate(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    def get_grad_category(row):
        program = str(row.get("Program", "")).strip().upper()
        transferee = str(row.get("Transferee", "")).strip().lower()
        grad_freshman = str(row.get("Graduate - Freshmen", "")).strip().lower()
        grad_transferee = str(row.get("Graduate - Transferee", "")).strip().lower()

        # 1️⃣ JD PROGRAM CHECK
        if program.startswith("JD"):
            if transferee == "yes":
                return "Transferee - Juris Doctor"
            else:
                return "Freshman - Juris Doctor"

        # 2️⃣ TCP PROGRAM CHECK
        if "TCP" in program:
            return "Teacher Certificate Program"

        # 3️⃣ SUPPLEMENTAL PROGRAM CHECK
        if "SUPPLEMENTAL" in program:
            return "Supplemental Course"

        # 4️⃣ GENERAL GRADUATE STUDIES CHECK  
        if grad_freshman == "yes":
            return "Freshman - Graduate Studies"

        if grad_transferee == "yes":
            return "Transferee - Graduate Studies"

        # 5️⃣ DEFAULT FOR GRADUATE STUDIES
        return "Freshman - Graduate Studies"

    df["category"] = df.apply(get_grad_category, axis=1)
    return df

st.cache_data
def mob_mr_ms(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # ----------------- Helper: Normalize Mr./Ms. -----------------
    def clean_title(val):
        if pd.isna(val) or str(val).strip() == "":
            return ""  # leave blank as is

        raw = str(val).strip()

        # Normalize the raw text (remove spaces and dots for checking)
        normalized = raw.lower().replace(".", "").replace(" ", "")

        # Check if it contains MR or MS
        if normalized.startswith("mr"):
            return "Mr."
        if normalized.startswith("ms"):
            return "Ms."

        # Otherwise keep value as is
        return raw

    # ----------------- Helper: Clean mobile contact fields -----------------
    def clean_mobile(val):
        if pd.isna(val) or str(val).strip() == "":
            return ""  # leave blank
        return re.sub(r'[^0-9]', '', str(val))

    # Apply to Mr./Ms.
    if "Mr./Ms." in df.columns:
        df["Mr./Ms."] = df["Mr./Ms."].apply(clean_title)

    # Columns to clean
    mobile_columns = ["Mobile Phone", "Father Mobile", "Mother Mobile"]

    for col in mobile_columns:
        if col in df.columns:
            df[col] = df[col].apply(clean_mobile)

    return df


