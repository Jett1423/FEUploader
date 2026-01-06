import pandas as pd
import re
import streamlit as st

def convert_programs(df):
    df = df.copy()
    removed_prereqs = []  # 👈 collect removed prerequisites
    removed_electives = []  # 👈 collect removed elective rows

    # Clean and map Program Code
    df["Program Code"] = df["Program Code"].astype(str).apply(lambda x: re.sub(r'[^A-Za-z\s]', '', x).strip())

    # Extract only numbers from Revision ID
    df["Revision ID"] = df["Revision ID"].astype(str).apply(lambda x: ''.join(re.findall(r'\d+', x)))

    # Clean academic year and term
    df["Academic Year"] = df["Academic Year"].astype(str).apply(lambda x: ''.join(re.findall(r'\d+', x)))

    # Map term names to numeric (1, 2, 3)
    def map_term(value):
        if pd.isna(value):
            return ""
        value = str(value).strip().upper()
        if "FIRST" in value:
            return "1"
        elif "SECOND" in value:
            return "2"
        else:
            return "3"

    df["Term"] = df["Term"].apply(map_term)

    # Institute mapping
    def map_institute(value):
        value = str(value).strip().upper()
        if value in [
            "ACADEMIC : INST. OF ARTS AND SCIENCES : LANGUAGE AND LITERATURE : LANGUAGE AND LITERATURE STUDIES",
            "ACADEMIC : INST. OF ARTS AND SCIENCES : POLITICAL SCIENCE : POLITICAL SCIENCE",
            "ACADEMIC : INST. OF ARTS AND SCIENCES : INTERDISCIPLINARY STUDIES",
            "ACADEMIC : INST. OF ARTS AND SCIENCES : COMMUNICATION DEPARTMENT : COMMUNICATION",
            "ACADEMIC : INST. OF ARTS AND SCIENCES : PSYCHOLOGY : PSYCHOLOGY",
            "ACADEMIC : INST. OF ARTS AND SCIENCES : COMMUNICATION DEPARTMENT : COMMUNICATION GRADUATE PROGRAM",
            "ACADEMIC : INST. OF ARTS AND SCIENCES : LANGUAGE AND LITERATURE : LANGUAGE AND LITERATURE STUDIES GRADUATE PROGRAM",
            "ACADEMIC : INST. OF ARTS AND SCIENCES : PSYCHOLOGY : PSYCHOLOGY GRADUATE PROGRAM",
            "ACADEMIC : INST. OF ARTS AND SCIENCES : BIOLOGY DEPARTMENT : BIOLOGY GRADUATE PROGRAM",
            "ACADEMIC : INST. OF ARTS AND SCIENCES : PHYSICS & MATH : MATHEMATICS - GS",
            "ACADEMIC : INST. OF ARTS AND SCIENCES : PHYSICS & MATH : MATHEMATICS",
            "ACADEMIC : INST. OF ARTS AND SCIENCES : BIOLOGY DEPARTMENT : BIOLOGY",
            "ACADEMIC : INST. OF ARTS AND SCIENCES : INTERNATIONAL STUDIES : INTERNATIONAL STUDIES"
        ]:
            return "IAS"
        
        if value in [
            "ACADEMIC : INST. OF EDUCATION : EDUCATION: GS : EDUCATION GRADUATE PROGRAM AND TNE",
            "ACADEMIC : INST. OF EDUCATION : EDUCATION : EDUCATION"
        ]:
            return "IE"
            
        elif value in [
            "ACADEMIC : INST. ARCHITECTURE & FINE ARTS : FINE ARTS",
            "ACADEMIC : INST. ARCHITECTURE & FINE ARTS : ARCHITECTURE"
        ]:
            return "IARFA"

        elif value in [
            "ACADEMIC : INST. ACCOUNT, BUSINESS FINANCE : ACCOUNTANCY",
            "ACADEMIC : INST. ACCOUNT, BUSINESS FINANCE : BUSINESS ADMINISTRATION",
            "ACADEMIC : INST. ACCOUNT, BUSINESS FINANCE : INTERNAL AUDITING",
            "ACADEMIC : INST. ACCOUNT, BUSINESS FINANCE : ECONOMICS",
            "ACADEMIC : INST. ACCOUNT, BUSINESS FINANCE : HUMAN RESOURCES AND ORGANIZATIONAL DEVELOPMENT"
        ]:
            return "IABF"
        
        elif value in [
            "ACADEMIC : INST. OF TOURISM & HOTEL MGMT : HOTEL AND RESTAURANT MANAGEMENT",
            "ACADEMIC : INST. OF TOURISM & HOTEL MGMT : TOURISM MANAGEMENT",
            "ACADEMIC : INST. OF TOURISM & HOTEL MGMT : TOURISM AND HOSPITALITY MANAGEMENT GRADUATE PROGRAM"
        ]:
            return "ITHM"
        
        elif value in [
            "ACADEMIC : INST. OF HEALTH SCIENCES & NURSING : IN DEPT. : NURSING GRADUATE PROGRAM",
            "ACADEMIC : INST. OF HEALTH SCIENCES & NURSING : IHSN : NUTRITION AND DIETETICS",
            "ACADEMIC : INST. OF HEALTH SCIENCES & NURSING : IHSN : PHARMACY",
            "ACADEMIC : INST. OF HEALTH SCIENCES & NURSING : MEDTECH DEPT. : MEDICAL TECHNOLOGY",
            "ACADEMIC : INST. OF HEALTH SCIENCES & NURSING : IN DEPT. : NURSING"
        ]:
            return "IHSN"
        else:
            return "UNKNOWN"

    df["Institute Code"] = df["Institute Code"].apply(map_institute)

    # ⚠️ Remove elective rows with 3-letter + 4-digit course codes (e.g., ABC1234)
    if "Type" in df.columns and "Course" in df.columns:
        pattern = re.compile(r"^[A-Za-z]{3}\d{4}$")
        mask = (df["Type"].astype(str).str.strip().str.upper() == "ELECTIVE") & \
               (df["Course"].astype(str).str.match(pattern))

        # Collect removed electives
        removed_electives = df[mask][["Program Code", "Course", "Type"]].copy()
        df = df[~mask]

        if not removed_electives.empty:
            st.warning(f"⚠️ {len(removed_electives)} 'Elective' rows with 3-letter + 4-digit course codes were removed.")
            st.dataframe(removed_electives)
        else:
            st.info("✅ No invalid 'Elective' rows found.")
    else:
        st.warning("⚠️ Missing 'Type' or 'Course' column — elective validation skipped.")

    # ✅ Prerequisite alignment check
    def validate_prerequisites(sub_df):
     # 🧹 Clean numeric columns first — avoids ValueError later
        sub_df["Academic Year"] = pd.to_numeric(sub_df["Academic Year"], errors="coerce")
        sub_df["Term"] = pd.to_numeric(sub_df["Term"], errors="coerce")

    # Drop any rows without valid year or term
        sub_df = sub_df.dropna(subset=["Academic Year", "Term"])

    # Sort to ensure chronological validation
        sub_df = sub_df.sort_values(by=["Academic Year", "Term"])

        seen_courses = set()

        for idx, row in sub_df.iterrows():
            prereq_str = str(row.get("Prerequisite", "")).strip()
            if prereq_str:
            # Split and clean prerequisites (comma, slash, or semicolon separated)
                prereq_list = re.split(r'[,/;]', prereq_str)
                prereq_list = [p.strip() for p in prereq_list if p.strip()]

            year = int(row["Academic Year"])
            term = int(row["Term"])

            # Collect all courses from prior years/terms
            prior_courses = sub_df[
                (sub_df["Academic Year"] < year)
                | ((sub_df["Academic Year"] == year) & (sub_df["Term"] < term))
            ]["Course"].astype(str).tolist()

            # Check which prereqs are valid or invalid
            valid_prereqs = [p for p in prereq_list if p in prior_courses]
            invalid_prereqs = [p for p in prereq_list if p not in prior_courses]

            # Record any invalid prereqs found
            if invalid_prereqs:
                removed_prereqs.append({
                    "Program": row["Program Code"],
                    "Course": row["Course"],
                    "Removed": ", ".join(invalid_prereqs)
                })

            # Keep only the valid ones
            sub_df.at[idx, "Prerequisite"] = ", ".join(valid_prereqs)

        seen_courses.add(str(row["Course"]).strip())

        return sub_df


    # Apply per (Program Code, Revision ID)

    # 🧹 Clean up course and prerequisite spacing and symbols
    df["Course"] = df["Course"].astype(str).str.strip().replace(r"\s+", " ", regex=True)
    df["Prerequisite"] = df["Prerequisite"].astype(str).str.strip().replace(r"\s+", " ", regex=True)

    
    df = df.groupby(["Program Code", "Revision ID"], group_keys=False).apply(validate_prerequisites)

    # ⚠️ Show warning for removed prerequisites
    if removed_prereqs:
        removed_df = pd.DataFrame(removed_prereqs)
        st.warning("⚠️ Some invalid prerequisites were removed due to missing earlier courses.")
        st.dataframe(removed_df)
    else:
        st.info("✅ All prerequisites are valid and aligned with their year and term.")

    # Ensure required columns exist
    for col in [
        "Parent Elective Code(Leave blank if not an elective)",
        "Default Elective (YES/NO)",
        "Corequisite",
        "Required Units",
        "--- THIS ROW WILL BE IGNORED ON IMPORT. DO NOT DELETE THIS ROW. DO NOT REPLACE WITH ACTUAL VALUES. ---"
    ]:
        if col not in df.columns:
            df[col] = ""

    # Final column mapping
    column_mapping = {
        "Program Code": "Program Code",
        "Description": "Description",
        "Institute Code": "Institute Code",
        "Revision ID": "Revision ID",
        "Academic Year": "Academic Year(1,2,3...)",
        "Term": "Term(1,2,3...)",
        "Parent Elective Code(Leave blank if not an elective)": "Parent Elective Code(Leave blank if not an elective)",
        "Course": "Course Code(Or child elective code)",
        "Default Elective (YES/NO)": "Default Elective (YES/NO)",
        "Prerequisite": "Prerequisite",
        "Corequisite": "Corequisite",
        "Required Units": "Required Units",
        "--- THIS ROW WILL BE IGNORED ON IMPORT. DO NOT DELETE THIS ROW. DO NOT REPLACE WITH ACTUAL VALUES. ---":
            "--- THIS ROW WILL BE IGNORED ON IMPORT. DO NOT DELETE THIS ROW. DO NOT REPLACE WITH ACTUAL VALUES. ---"
    }

    converted_df = df.rename(columns=column_mapping)
    available_columns = [col for col in column_mapping.values() if col in converted_df.columns]
    converted_df = converted_df[available_columns]

    validate_final_prereqs(converted_df)
    return converted_df


def validate_final_prereqs(converted_df):
    invalid_rows = []

    for _, group in converted_df.groupby(["Program Code", "Revision ID"]):
        group = group.sort_values(by=["Academic Year(1,2,3...)", "Term(1,2,3...)"])
        course_list = group["Course Code(Or child elective code)"].astype(str).tolist()

        for _, row in group.iterrows():
            prereq_str = str(row.get("Prerequisite", "")).strip()
            if prereq_str:
                prereqs = re.split(r'[,/;]', prereq_str)
                prereqs = [p.strip() for p in prereqs if p.strip()]

                year = int(row["Academic Year(1,2,3...)"])
                term = int(row["Term(1,2,3...)"])

                prior_courses = group[
                    (group["Academic Year(1,2,3...)"].astype(int) < year)
                    | ((group["Academic Year(1,2,3...)"].astype(int) == year) & (group["Term(1,2,3...)"].astype(int) < term))
                ]["Course Code(Or child elective code)"].astype(str).tolist()

                for prereq in prereqs:
                    if prereq not in prior_courses:
                        invalid_rows.append({
                            "Program": row["Program Code"],
                            "Course": row["Course Code(Or child elective code)"],
                            "Invalid Prerequisite": prereq,
                            "Year": year,
                            "Term": term
                        })

    if invalid_rows:
        invalid_df = pd.DataFrame(invalid_rows)
        st.error("❌ Validation Failed: Some prerequisites are still invalid after conversion.")
        st.dataframe(invalid_df)
    else:
        st.success("✅ Validation Passed: All prerequisites align with their year and term.")
