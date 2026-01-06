import pandas as pd
import re

def convert_students(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Date of Birth → format yyyy-MM-dd
    df["Date of Birth(Must be in yyyy-MM-dd format)"] = pd.to_datetime(
        df["Date of Birth"], errors="coerce"
    ).dt.strftime("%Y-%m-%d")

    # Gender → uppercase
    df["Sex(FEMALE,MALE)"] = df["Gender"].astype(str).str.upper()

    # Academic Term → e.g. 2022-2023-2
    df["STARTING TERM"] = (
        df["Intended Academic Year"].astype(str).str.replace(r"[^0-9-]", "", regex=True) + "-" +
        df["Intended Academic Term"].replace({
            "First Semester": "1",
            "Second Semester": "2",
            "Third Semester": "3"
        })
    )

    # Is Transferee → based on Freshman when Admitted
    df["Is Transferee(TRANSFEREE,REGULAR)"] = df["Freshman when Admitted"].apply(
        lambda x: "TRANSFEREE" if str(x).strip().lower() == "no" else "REGULAR"
    )

    # Program and Revision extraction
    df["Program Code"] = df["Program"].astype(str).str.replace(r"[^A-Za-z\s]", "", regex=True).str.strip()
    df["Program Revision"] = df["Revision"].astype(str).str.extract(r"(\d+)")

    # Ensure extra columns exist
    for col in ["Tuition Plan Name", "--- THIS ROW WILL BE IGNORED ON IMPORT. DO NOT DELETE THIS ROW. DO NOT REPLACE WITH ACTUAL VALUES. ---"]:
        if col not in df.columns:
            df[col] = ""

    # Rename columns
    rename_map = {
        "Email": "EMAIL",
        "ID": "Student Number",
        "Tuition Plan Name": "Tuition Plan Name"
    }
    df.rename(columns=rename_map, inplace=True)

    # Keep only the relevant columns
    final_columns = [
        "First Name", "Middle Name", "Last Name",
        "Date of Birth(Must be in yyyy-MM-dd format)",
        "Sex(FEMALE,MALE)", "EMAIL", "Student Number",
        "STARTING TERM", "Is Transferee(TRANSFEREE,REGULAR)",
        "Program Code", "Program Revision", "Tuition Plan Name", "--- THIS ROW WILL BE IGNORED ON IMPORT. DO NOT DELETE THIS ROW. DO NOT REPLACE WITH ACTUAL VALUES. ---"
    ]

    converted_df = df[final_columns]

    return converted_df
