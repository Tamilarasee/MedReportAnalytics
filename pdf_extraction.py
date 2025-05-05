# Function to extract text and tables using pdfplumber
import streamlit as st
import io
import pdfplumber
# import pytesseract # Removed
# from pdf2image import convert_from_path # Removed
# import os # Removed
# import tempfile # Removed


def extract_text_and_tables(pdf_file_obj):
    """Extracts text and tables using pdfplumber."""
    text = ""
    tables = []
    try:
        # --- Use pdfplumber (using BytesIO) ---
        pdf_file_obj.seek(0) # Ensure we read from the start
        pdf_bytes = io.BytesIO(pdf_file_obj.read())
        with pdfplumber.open(pdf_bytes) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                page_tables = page.extract_tables()
                if page_tables:
                    tables.extend(page_tables)
        print("pdfplumber extraction done.")

    except Exception as e:
        st.error(f"Error during PDF processing with pdfplumber: {e}")
        return None, None # Return None if pdfplumber fails

    return text, tables


# # pdf_text = extract_text_from_pdf(
# #     "Dataset/Lab Report/Basic Metabolic Panel.pdf")
# # print(pdf_text)
