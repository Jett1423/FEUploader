import pandas as pd
import re
import streamlit as st

st.cache_data
def check_graduate_grades(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # ---------------------------- DROPPED ----------------------------
    df["Dropped (YES/NO)"] = df["Grade"].apply(
        lambda x: "YES" if str(x).strip().upper() == "AW" else "NO"
    )

    # ---------------------------- SCHOOL SEMESTER → YYYY-YYYY-SEM ----------------------------
    def parse_school_semester(academic_year, academic_term):
        year = re.sub(r"[^0-9\-]", "", str(academic_year)).strip()
        term = str(academic_term).strip().lower()

        if "first" in term:
            term_num = "1"
        elif "second" in term:
            term_num = "2"
        else:
            term_num = "3"

        return f"{year}-{term_num}"

    df["School Semester (Format should by YYYY-YYYY-[SEMESTER NUMBER])"] = df.apply(
        lambda row: parse_school_semester(row["Academic Year"], row["Academic Term"]),
        axis=1
    )

    # ---------------------------- REMARKS ----------------------------
    pass_list = ["1","1.00", "1.25", "1.50","1.5", "1.75", "2.00","2", "2.25", "2.50","2.5", "2.75", "3.00", "3",
                 "PASS", "A", "A-", "B+", "B", "C+", "C", "D+", "D", "P"]
    fail_list = ["5.00", "5", "FAIL", "F"]
    no_credit_list = ["AW", "IP"]

    def map_remarks(grade):
        g = str(grade).strip().upper()
        if g in [x.upper() for x in pass_list]:
            return "Pass"
        elif g in [x.upper() for x in fail_list]:
            return "Fail"
        elif g in [x.upper() for x in no_credit_list]:
            return "No Credit"
        return "No Credit"

    df["Remarks"] = df["Grade"].apply(map_remarks)

    # ---------------------------- PROGRAM + REVISION ----------------------------
    def extract_program_info(text):
        text = str(text)
        program = re.sub(r"\(\s*\d{4}\s*\)", "", text).strip()
        revision_match = re.search(r"\((\d{4})\)", text)
        revision = revision_match.group(1) if revision_match else ""
        return program, revision

    df["Program Code"], df["Program Revision ID"] = zip(*df["Program"].apply(extract_program_info))

    # ---------------------------- CURRENT PROGRAM MATCH FIX ----------------------------
    def parse_program_text(text):
        t = str(text) if pd.notna(text) else ""
        program_name = re.sub(r"\(\s*\d{4}\s*\)", "", t).strip()
        rev_m = re.search(r"\((\d{4})\)", t)
        revision = rev_m.group(1) if rev_m else ""
        return program_name, revision

    df["Current Program"] = df.get("Current Program", "").fillna("")
    curr_parsed = df["Current Program"].apply(parse_program_text)
    df["Current Program Code"] = curr_parsed.map(lambda x: x[0])
    df["Current Program Revision ID"] = curr_parsed.map(lambda x: x[1])

    def programs_match(row):
        a = str(row["Program Code"]).strip().upper()
        b = str(row["Current Program Code"]).strip().upper()
        ra = str(row["Program Revision ID"]).strip()
        rb = str(row["Current Program Revision ID"]).strip()

        name_match = (a == b)
        rev_match = (ra == rb) or (ra == "" and rb == "")
        return "YES" if (name_match and rev_match) else "NO"

    df["Is the 2 programs match?"] = df.apply(programs_match, axis=1)
    df.drop(columns=["Current Program Code", "Current Program Revision ID"], inplace=True)

    # ---------------------------- COPY "School Name" TO NEW SCHOOL COLUMN ----------------------------
    school_column_name = "School (Indicate the name of the school where the course was credited. This field is optional for credited grades.)"

    # Fuzzy lookup for 'School Name'
    possible_school_cols = [c for c in df.columns if "school" in c.lower() and "name" in c.lower()]

    if possible_school_cols:
        school_col = possible_school_cols[0]   # Pick first matched column
        df[school_column_name] = df[school_col]
        st.success(f"📌 Using column '{school_col}' as School Name")
    else:
        df[school_column_name] = ""
        st.warning("⚠️ No column resembling 'School Name' was found in the uploaded CSV.")


    # ---------------------------- CREDITED = YES IF REMARKS = PASS ----------------------------
    df["Credited"] = df["Remarks"].apply(lambda x: "YES" if x == "Pass" else "NO")

    # ---------------------------- DEFAULT FIELDS ----------------------------
    df["Overwrite existing record (YES/NO)"] = df.get("Overwrite existing record (YES/NO)", "").replace("", "NO")

    # ---------------------------- FINAL COLUMN ORDER ----------------------------
    column_mapping = [
        "Student Number",
        "Course Code",
        "Elective Code",
        "In Lieu Of (Original Course Code)",
        "In Lieu Of Parent Elective (Parent code of the original Course code)",
        "Credited",
        "Dropped (YES/NO)",
        "Grade",
        "School Semester (Format should by YYYY-YYYY-[SEMESTER NUMBER])",
        school_column_name,
        "Remarks",
        "Grade Point",
        "Program Code",
        "Program Revision ID",
        "Grading System",
        "Year Level",
        "Credited Course Code",
        "Credited Course Name",
        "Credited Course Units",
        "Credited Grade",
        "Overwrite existing record (YES/NO)",
        "Current Program",
        "Is the 2 programs match?",
    ]

    final_df = df.reindex(columns=column_mapping, fill_value="")

    validate_converted_data(final_df)
    return final_df


def validate_converted_data(df: pd.DataFrame):
    errors = []

    # 1. Validate School Semester Format
    invalid_sem = ~df["School Semester (Format should by YYYY-YYYY-[SEMESTER NUMBER])"].str.match(r"^\d{4}-\d{4}-[1-3]$")
    if invalid_sem.any():
        errors.append(f"❌ Invalid School Semester format in {invalid_sem.sum()} rows.")
    else:
        st.success("✅ School Semester is correct!")

    # 2. Remarks validity
    valid_remarks = {"Pass", "Fail", "No Credit"}
    if not set(df["Remarks"]).issubset(valid_remarks):
        errors.append("❌ Remarks column contains unexpected values.")
    else:
        st.success("✅ Remarks are good")

    # 3. Program Code must NOT be empty
    if (df["Program Code"].str.strip() == "").any():
        errors.append("❌ Some Program Code values are empty.")
    else:
        st.success("✅ Programs are validated")

    # 4. Program Revision ID validation
    invalid_revision = ~df["Program Revision ID"].str.match(r"^(\d{4})?$")
    if invalid_revision.any():
        errors.append(f"❌ Invalid Program Revision ID format in {invalid_revision.sum()} rows.")
    else:
        st.success("✅ Revisions are equal")

    # 5. YES/NO validation
    yes_no_cols = ["Dropped (YES/NO)", "Credited", "Overwrite existing record (YES/NO)"]
    for col in yes_no_cols:
        if not set(df[col].unique()).issubset({"YES", "NO"}):
            errors.append(f"❌ Column '{col}' contains values besides YES/NO.")

    if errors:
        st.error("⚠️ DATA VALIDATION FAILED:\n" + "\n".join(errors))
    else:
        st.success("✅ All validations passed. Data conversion looks correct!")

    return errors
