import pandas as pd
import re
import streamlit as st

def check_prerequisites(df: pd.DataFrame):
    # Ensure correct data types
    df["Academic Year (1, 2, 3...)"] = df["Academic Year (1, 2, 3...)"].astype(int)
    df["Term (1, 2, 3...)"] = df["Term (1, 2, 3...)"].astype(int)
    df["Prerequisite"] = ""  # start empty

    def normalize_code(code):
        return re.sub(r'[^A-Za-z0-9]', '', str(code)).upper()

    def process_group(sub_df):
        # Sort by academic year and term (chronological order)
        sub_df = sub_df.sort_values(by=["Academic Year (1, 2, 3...)", "Term (1, 2, 3...)"]).reset_index(drop=True)

        for idx, row in sub_df.iterrows():
            year = row["Academic Year (1, 2, 3...)"]
            term = row["Term (1, 2, 3...)"]

            # Find all previous courses in this revision
            prior_courses = sub_df[
                (sub_df["Academic Year (1, 2, 3...)"] < year)
                | (
                    (sub_df["Academic Year (1, 2, 3...)"] == year)
                    & (sub_df["Term (1, 2, 3...)"] < term)
                )
            ].copy()

            # Pick the last (most recent) one
            if not prior_courses.empty:
                last_course = prior_courses.iloc[-1]["Course Code (Or child elective code)"]
                sub_df.at[idx, "Prerequisite"] = last_course

        return sub_df

    # Group by Program Code + Revision ID
    df = df.groupby(["Program Code", "Revision ID"], group_keys=False).apply(process_group)

    st.success("✅ Immediate prerequisites populated based on Academic Year and Term (per Revision ID).")
    st.dataframe(df[["Program Code", "Revision ID", "Course Code (Or child elective code)", "Prerequisite"]])

    return df
