import streamlit as st
import pandas as pd
from io import StringIO

# Import your modules
from programs import convert_programs
from grades import convert_grades, validate_converted_data
from graduate_grades import check_graduate_grades
from courses import convert_courses
from course_equivalency import two_way_course_equivalency
from cleaning_equivalency import remove_reverse_duplicates
from students import convert_students
from sis import find_duplicate_differences, check_fields
from pre_req import check_prerequisites
from clean import personal_information, insti, category_bachelor, category_graduate, mob_mr_ms

st.title("🎓 ERP → Edusuite Data Converter (CSV)")

# -------------------- SELECTIONS --------------------
option = st.selectbox(
    "Select conversion type:",
    [
        "Programs",
        "Grades",
        "Graduate Grades",
        "Courses",
        "Students",
        "SIS",
        "Pre-Requisites",
        "Cleaning SIS",
        "Two-way Equivalency",
        "Cleaning Equivalency"
    ]
)

if option == "SIS":
    category = st.radio(
        "Select which applies",
        ["Check for duplicates", "Convert only", "Check Name Fields", "Select All"]
    )

elif option == "Cleaning SIS":
    category2 = st.radio(
        "Select which applies",
        ["Personal Information", "Institute", "Category Undergrad", "Category Graduate", "Mobile Phone and Mr./Ms."]
    )

# -------------------- FILE UPLOAD --------------------
uploaded_file = st.file_uploader("📂 Upload raw ERP CSV", type=["csv"])

if uploaded_file:
    # --- Read CSV normally ---
    try:
        df = pd.read_csv(uploaded_file, encoding="utf-8")
    except UnicodeDecodeError:
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file, encoding="latin1")


    # -------------------- DETERMINE CONVERSION PATH --------------------
    if option == "Programs":
        converted_df = convert_programs(df)
        file_name = "converted_programs.csv"

    elif option == "Grades":
        converted_df = convert_grades(df)
        file_name = "converted_grades.csv"

    elif option == "Graduate Grades":
        converted_df = check_graduate_grades(df)
        file_name = "graduate_grades.csv"

    elif option == "Courses":
        converted_df = convert_courses(df)
        file_name = "converted_courses.csv"

    elif option == "Students":
        converted_df = convert_students(df)
        file_name = "converted_students.csv"

    elif option == "Pre-Requisites":
        converted_df = check_prerequisites(df)
        file_name = "pre_requisites.csv"

    elif option == "Two-way Equivalency":
        converted_df = two_way_course_equivalency(df)
        file_name = "two_way_equivalency.csv"
    
    elif option == "Cleaning Equivalency":
        converted_df = remove_reverse_duplicates(df)
        file_name = "Two_way_course_equivalency_final.csv"

    elif option == "Cleaning SIS":
        if category2 == "Personal Information":
            converted_df = personal_information(df)
            file_name = "sis_personal_information.csv"

        elif category2 == "Institute":
            converted_df = insti(df)
            file_name = "sis_institute_information.csv"

        elif category2 == "Category Undergrad":
            converted_df = category_bachelor(df)
            file_name = "sis_category_bachelor.csv"
        
        elif category2 == "Category Graduate":
            converted_df = category_graduate(df)
            file_name = "sis_category_graduate.csv"

        elif category2 == "Mobile Phone and Mr./Ms.":
            converted_df = mob_mr_ms(df)
            file_name = "sis_mobilephone_mrms.csv"


    elif option == "SIS":
        if category == "Check for duplicates":
            converted_df = find_duplicate_differences(df)
            file_name = "converted_duplicate_sis.csv"

        elif category == "Convert only":
            converted_df = convert_students(df)
            file_name = "converted_sis.csv"

        elif category == "Check Name Fields":
            converted_df = check_fields(df)
            file_name = "converted_checked_fields.csv"

        else:  # "Select All"
            duplicates_df = find_duplicate_differences(df)
            converted_df = convert_students(df)
            file_name = "converted_sis_all.csv"

    # -------------------- OUTPUT --------------------
    st.subheader("✅ Converted Data Preview")
    st.dataframe(converted_df)

    # Save to CSV
    csv_buffer = StringIO()
    converted_df.to_csv(csv_buffer, index=False)

    st.download_button(
        label="⬇️ Download Converted CSV",
        data=csv_buffer.getvalue(),
        file_name=file_name,
        mime="text/csv"
    )

    st.success(f"✅ {option} conversion complete!")
