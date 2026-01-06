import pandas as pd
import streamlit as st

def find_duplicate_differences(df: pd.DataFrame, id_column: str = "Student Number"):
    df = df.astype(str).fillna("")

    # Find all duplicates based on Student Number
    duplicates = df[df.duplicated(subset=[id_column], keep=False)].sort_values(by=id_column)

    if duplicates.empty:
        print("✅ No duplicate student numbers found.")
        return pd.DataFrame()

    # Select only relevant columns (Student Number + name-related + others if needed)
    name_columns = [col for col in df.columns if col.lower() in ["first name", "middle name", "last name"]]
    selected_columns = [id_column] + name_columns

    # Add other columns to show potential differences (optional)
    other_cols = [col for col in df.columns if col not in selected_columns]
    selected_columns += other_cols

    result_df = duplicates[selected_columns]

    st.write(f"⚠️ Found {len(result_df)} rows with duplicate student numbers.")
    return result_df


def check_fields(df: pd.DataFrame, id_column: str = "Student Number"):
    # Make a safe copy
    df = df.copy()

    # Columns to check
    required_cols = ["First Name", "Middle Name", "Last Name"]
    for col in required_cols:
        if col not in df.columns:
            st.error(f"Missing required column: {col}")
            return pd.DataFrame()

    # Fill only NaN with empty string
    df[required_cols] = df[required_cols].fillna("")

    # Find rows where ALL three name fields are empty
    mask = (
        (df["First Name"].str.strip() == "") &
        (df["Middle Name"].str.strip() == "") &
        (df["Last Name"].str.strip() == "")
    )

    # Handle sorting safely
    sort_col = id_column if id_column in df.columns else df.columns[0]
    try:
        # Convert to string just for sorting to avoid type comparison issues
        missing_fields = df.loc[mask].assign(
            _sort_key=df[sort_col].astype(str)
        ).sort_values(by="_sort_key").drop(columns="_sort_key")
    except Exception as e:
        st.warning(f"⚠️ Could not sort by {sort_col}: {e}")
        missing_fields = df.loc[mask]

    # Display results
    if missing_fields.empty:
        st.success("✅ No students found with all name fields empty.")
        return pd.DataFrame()

    st.warning(f"⚠️ Found {len(missing_fields)} students with missing First, Middle, and Last names.")
    return missing_fields


def check_int():

    return

