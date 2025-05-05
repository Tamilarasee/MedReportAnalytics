import streamlit as st
import os
from dotenv import load_dotenv
from app_components import upload_view, analyze_view, chat_view
from app_state import initialize_session_state
import time

# --- Load Environment Variables --- 
load_dotenv()

# --- App Configuration ---
st.set_page_config(layout="wide", page_title="Medical Report Analyzer")

# --- Session State Initialization (Called from app_state) --- 
initialize_session_state() 

# --- Main App Logic --- 
def main():
    # Sidebar Navigation
    with st.sidebar:
        st.title("🩺 MedReport Analyzer")
        st.divider()

        # Define button labels and corresponding page states
        pages = {
            "📄 Upload Report": "Upload Report",
            "📊 Analyze": "Analyze",
            "💬 Chat": "Chat"
        }
        
        report_loaded = bool(st.session_state.get("report_text"))

        for btn_label, page_state in pages.items():
            # Determine button type (primary if current page, secondary otherwise)
            btn_type = "primary" if st.session_state.current_page == page_state else "secondary"
            # Disable Analyze/Chat if report not loaded
            disabled = (page_state in ["Analyze", "Chat"]) and (not report_loaded)
            
            if st.button(btn_label, use_container_width=True, disabled=disabled, type=btn_type):
                if disabled:
                    st.toast("Please upload a report first.")
                elif st.session_state.current_page != page_state:
                    st.session_state.current_page = page_state
                    if page_state == "Analyze":
                         st.session_state.analysis_requested = True # Ensure analysis runs on switch
                    st.rerun()
                
    # Display the current page view by calling the imported function
    current_page_state = st.session_state.current_page
    if current_page_state == "Upload Report":
        upload_view()
    elif current_page_state == "Analyze":
        analyze_view()
    elif current_page_state == "Chat":
        chat_view()
    else:
        st.error("Invalid page state.")
        st.session_state.current_page = "Upload Report" # Reset to default
        st.rerun()

if __name__ == "__main__":
    main()