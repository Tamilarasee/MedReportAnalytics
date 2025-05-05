import streamlit as st

# Function to initialize session state with default values
def initialize_session_state():
    defaults = {
        "current_page": "Upload Report",
        "user_id": None, 
        "report_text": None,
        "report_tables": None,
        "uploaded_filename": None,
        "model_choice": "OpenAI GPT-4",
        "analysis_requested": False,
        "analysis_done": False,
        "analyzed_text": None, 
        "summary": None,
        "alignment": None,
        "diagnosis_data": None,
        "raw_conditions": None,
        "messages": [],
        "pdf_buffer": None
    }
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value 