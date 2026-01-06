import re
import pandas as pd

def convert_courses(df):

    def normalize(value: str) -> str:
        # Clean up spacing and symbols
        value = str(value).upper()
        value = re.sub(r'\s+', ' ', value)  # collapse multiple spaces
        value = re.sub(r'\s*:\s*', ' : ', value)  # normalize colons
        value = value.strip()
        return value

    def map_description(value):
        text = normalize(value)
        mapping = {
            "ACCOUNTANCY": [
                "ACADEMIC : INST. ACCOUNT, BUSINESS FINANCE : ACCOUNTANCY"
            ],
            "BUSINESS ADMINISTRATION": [
                "ACADEMIC : INST. ACCOUNT, BUSINESS FINANCE : BUSINESS ADMINISTRATION"
            ],
            "EDUCATION": [
                "ACADEMIC : INST. OF EDUCATION : EDUCATION : EDUCATION"
            ],
            "FINE ARTS": [
                "ACADEMIC : INST. ARCHITECTURE & FINE ARTS : FINE ARTS"
            ],
            "COMMUNICATION": [
                "ACADEMIC : INST. OF ARTS AND SCIENCES : COMMUNICATION DEPARTMENT : COMMUNICATION"
            ],
            "INTERNATIONAL STUDIES": [
                "ACADEMIC : INST. OF ARTS AND SCIENCES : INTERNATIONAL STUDIES : INTERNATIONAL STUDIES"
            ],
            "HOTEL AND RESTAURANT MANAGEMENT": [
                "ACADEMIC : INST. OF TOURISM & HOTEL MGMT : HOTEL AND RESTAURANT MANAGEMENT"
            ],
            "MATHEMATICS": [
                "ACADEMIC : INST. OF ARTS AND SCIENCES : PHYSICS & MATH : MATHEMATICS"
            ],
            "ARCHITECTURE": [
                "ACADEMIC : INST. ARCHITECTURE & FINE ARTS : ARCHITECTURE"
            ],
            "BIOLOGY": [
                "ACADEMIC : INST. OF ARTS AND SCIENCES : BIOLOGY DEPARTMENT : BIOLOGY"
            ],
            "LANGUAGE AND LITERATURE STUDIES": [
                "ACADEMIC : INST. OF ARTS AND SCIENCES : LANGUAGE AND LITERATURE : LANGUAGE AND LITERATURE STUDIES"
            ],
            "MEDICAL TECHNOLOGY": [
                "ACADEMIC : INST. OF HEALTH SCIENCES & NURSING : MEDTECH DEPT. : MEDICAL TECHNOLOGY"
            ],
            "NURSING": [
                "ACADEMIC : INST. OF HEALTH SCIENCES & NURSING : IN DEPT. : NURSING"
            ],
            "TOURISM MANAGEMENT": [
                "ACADEMIC : INST. OF TOURISM & HOTEL MGMT : TOURISM MANAGEMENT"
            ],
            "FILIP edERP": [
                "ACADEMIC : INST. OF ARTS AND SCIENCES : FILIPINO DEPARTMENT : FILIP edERP"
            ],
            "INTERDISCIPLINARY STUDIES": [
                "ACADEMIC : INST. OF ARTS AND SCIENCES : INTERDISCIPLINARY STUDIES"
            ],
            "WELLNESS AND RECREATIONAL PROGRAM": [
                "ACADEMIC : INST. OF EDUCATION : WELLNESS AND RECREATIONAL PROGRAM"
            ],
            "POLITICAL SCIENCE": [
                "ACADEMIC : INST. OF ARTS AND SCIENCES : POLITICAL SCIENCE : POLITICAL SCIENCE"
            ],
            "PSYCHOLOGY": [
                "ACADEMIC : INST. OF ARTS AND SCIENCES : PSYCHOLOGY : PSYCHOLOGY"
            ],
            "NATIONAL SERVICE TRAINING PROGRAM": [
                "ACADEMIC : NSTP AND COMMUNITY RELATION : NATIONAL SERVICE TRAINING PROGRAM"
            ],
            "BUSINESS ADMINISTRATION GRADUATE PROGRAM": [
                "ACADEMIC : INST. ACCOUNT, BUSINESS FINANCE : BUSINESS ADMINISTRATION GRADUATE PROGRAM"
            ],
        }

        for department, variants in mapping.items():
            if any(normalize(v) == text for v in variants):
                return department
        return "UNKNOWN"

    # Apply mapping
    df["Department Code"] = df["Department Code"].apply(map_description)

    # Create missing columns
    required_columns = [
        "Schedule Type(Input NONE if there is no schedule type)",
        "Lec Units(Must be numeric. Leave blank if not composite)",
        "Lab Units(Must be numeric. Leave blank if not composite)",
        "Grading Type",
        "Included in Overall Average (Input YES or NO)",
        "Course Capacity",
        "Overwrite existing record(YES/NO)"
    ]
    for col in required_columns:
        if col not in df.columns:
            df[col] = ""

    # Rename columns
    column_mapping = {
        "Course Code": "Course Code",
        "Display Name": "Description",
        "Schedule Type(Input NONE if there is no schedule type)": "Schedule Type(Input NONE if there is no schedule type)",
        "Department Code": "Department Code",
        "Units": "Units(Must be numeric)",
        "Lec Units(Must be numeric. Leave blank if not composite)": "Lec Units(Must be numeric. Leave blank if not composite)",
        "Lab Units(Must be numeric. Leave blank if not composite)": "Lab Units(Must be numeric. Leave blank if not composite)",
        "Grading Type": "Grading Type",
        "Included in Overall Average (Input YES or NO)": "Included in Overall Average (Input YES or NO)",
        "Course Capacity": "Course Capacity",
        "Overwrite existing record(YES/NO)": "Overwrite existing record(YES/NO)",
    }

    converted_df = df.rename(columns=column_mapping)
    converted_df = converted_df[list(column_mapping.values())]

    return converted_df
