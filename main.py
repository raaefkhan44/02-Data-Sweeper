import streamlit as st
import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO

# App Configurations
st.set_page_config(page_title="CleanSheet", layout="wide")
st.title("CleanSheet")
st.write("Transform your CSV & Excel files with cleaning, visualization, and conversion!")

# File Upload
uploaded_files = st.file_uploader("Upload your files (CSV or Excel):", type=["csv", "xlsx"], accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()

        # Read CSV or Excel
        if file_ext == ".csv":
            df = pd.read_csv(file)
        elif file_ext == ".xlsx":
            df = pd.read_excel(file, engine="openpyxl")
        else:
            st.error(f"Unsupported file type: {file_ext}")
            continue

        # Display file information
        st.subheader(f"📂 File: {file.name}")
        st.write(f"🔹 *Rows:* {df.shape[0]}, *Columns:* {df.shape[1]}")
        st.write(f"🔹 *File Size:* {round(file.size / 1024, 2)} KB")
        st.dataframe(df.head())

        # Data Cleaning Options
        st.subheader("🧹 Data Cleaning")
        if st.checkbox(f"Clean Data for {file.name}"):

            # Remove Duplicates
            if st.button(f"Remove Duplicates for {file.name}"):
                df.drop_duplicates(inplace=True)
                st.success("✅ Duplicates Removed!")

            # Drop Selected Columns
            drop_cols = st.multiselect(f"Select columns to drop for {file.name}", df.columns)
            if st.button(f"Drop Columns for {file.name}"):
                df.drop(columns=drop_cols, inplace=True)
                st.success("✅ Selected Columns Dropped!")

            # Fill Missing Values
            if st.button(f"Fill Missing Values for {file.name}"):
                numeric_cols = df.select_dtypes(include=["number"]).columns
                df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())  # Fill numeric with mean
                st.success("✅ Missing Values Filled!")

        # Data Visualization
        st.subheader("📊 Data Visualization")
        numeric_df = df.select_dtypes(include=["number"])

        if not numeric_df.empty:
            col1, col2 = st.columns(2)

            # Bar Chart
            with col1:
                if st.checkbox(f"📊 Show Bar Chart for {file.name}"):
                    st.write("### 📉 Bar Chart")
                    fig, ax = plt.subplots(figsize=(5, 3))
                    numeric_df.iloc[:, :2].plot(kind="bar", ax=ax, color=["#3498db", "#e74c3c"])
                    ax.set_title("Bar Chart", fontsize=10)
                    ax.set_ylabel("Values")
                    ax.set_xlabel("Index")
                    st.pyplot(fig)

            # Histogram
            with col2:
                if st.checkbox(f"📊 Show Histogram for {file.name}"):
                    st.write("### 📊 Histogram")
                    fig, ax = plt.subplots(figsize=(5, 3))
                    numeric_df.hist(bins=15, ax=ax, color="#2ecc71", edgecolor="black")
                    ax.set_title("Histogram", fontsize=10)
                    st.pyplot(fig)


        else:
            st.warning("No numeric columns available for visualization.")

        # Data Conversion
        st.subheader("🔄 Convert & Download")
        conversion_type = st.radio(f"Convert {file.name} to:", ["CSV", "Excel", "JSON"], key=file.name)

        if st.button(f"Convert {file.name}"):
            buffer = BytesIO()
            mime_type = ""

            if conversion_type == "CSV":
                df.to_csv(buffer, index=False)
                mime_type = "text/csv"
                file_name = file.name.replace(file_ext, ".csv")

            elif conversion_type == "Excel":
                df.to_excel(buffer, index=False, engine="openpyxl")
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                file_name = file.name.replace(file_ext, ".xlsx")

            elif conversion_type == "JSON":
                buffer.write(df.to_json(orient="records").encode())
                mime_type = "application/json"
                file_name = file.name.replace(file_ext, ".json")

            buffer.seek(0)

            # Download Button
            st.download_button(
                label=f"Download {file.name} as {conversion_type}",
                data=buffer,
                file_name=file_name,
                mime=mime_type,
            )

st.success("✅ All files processed successfully!")