import pandas as pd
import streamlit as st

st.cache_data
def two_way_course_equivalency(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Make sure the required columns exist
    required_cols = ["Course A", "Course B"]
    for col in required_cols:
        if col not in df.columns:
            st.error(f"Missing required column: {col}")
            return df

    # Create a set of all pairs for quick lookup
    pairs = set(zip(df["Course A"], df["Course B"]))

    # Collect rows that DO NOT have a reverse pair → these are invalid
    invalid_rows = []
    for idx, row in df.iterrows():
        a = row["Course A"]
        b = row["Course B"]

        if (b, a) not in pairs:  # reverse pair does NOT exist
            invalid_rows.append(idx)

    # If there are invalid rows → show them first for confirmation
    if invalid_rows:
        st.warning("⚠️ The following rows DO NOT have matching two-way equivalency:")
        st.dataframe(df.loc[invalid_rows])

        # Confirmation button
        if st.button("❌ Remove non two-way rows"):
            df = df.drop(index=invalid_rows)
            st.success("Removed all one-way course equivalencies.")
        else:
            st.info("Rows not removed yet. Click the button above if you want to proceed.")

    else:
        st.success("All course equivalencies are two-way. No issues found.")

    return df
