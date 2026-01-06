import pandas as pd
import streamlit as st

st.cache_data
def remove_reverse_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    required_cols = ["Course A", "Course B"]
    for col in required_cols:
        if col not in df.columns:
            st.error(f"Missing required column: {col}")
            return df

    seen = set()
    drop_indices = []

    for idx, row in df.iterrows():
        a, b = row["Course A"], row["Course B"]
        key = tuple(sorted([a, b]))  # order-independent key

        if key in seen:
            drop_indices.append(idx)  # duplicate pair → drop this row
        else:
            seen.add(key)

    # Show duplicates first for confirmation
    if drop_indices:
        st.warning("⚠️ These rows are REVERSE duplicates and can be removed:")
        st.dataframe(df.loc[drop_indices])

        if st.button("🗑 Remove reverse duplicates"):
            df = df.drop(index=drop_indices)
            st.success("Reverse duplicates removed.")

            st.subheader("Cleaned Data (Unique Two-Way Pairs)")
            st.dataframe(df)
        else:
            st.info("No changes made yet.")
            st.stop()

    else:
        st.success("No reverse duplicates found.")
        st.dataframe(df)

    return df
