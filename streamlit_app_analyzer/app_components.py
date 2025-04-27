import streamlit as st
import os
import re
import requests

from dotenv import load_dotenv

from sentence_transformers import SentenceTransformer, util
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain.chat_models import ChatOpenAI, ChatOllama, ChatDeepInfra
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from PIL import Image
import tempfile
import io 
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit
from reportlab.lib import colors
from pdf_extraction import extract_text_and_tables
from app_state import initialize_session_state


load_dotenv()

@st.cache_resource # Cache model loading
def load_llm_model(model_choice):
    print(f"Attempting to load model: {model_choice}") 
    try:
        if model_choice == "Llama3-ELAINE-medLLM (Radiology)":
            return None # we need to get the api endpoint for the finetuned radiology model
        elif model_choice == "OpenAI GPT-4":
            return ChatOpenAI(model_name="gpt-4", temperature=0.3, openai_api_key=os.getenv("OPENAI_API_KEY"))
        elif model_choice == "OpenAI GPT-3.5":
            return ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.3, openai_api_key=os.getenv("OPENAI_API_KEY"))
        elif model_choice == "Llama 3 Instruct (8B)":
            return ChatDeepInfra(model="meta-llama/Meta-Llama-3-8B-Instruct", api_key=os.getenv("DEEPINFRA_API_KEY"))
        elif model_choice == "Mixtral":
            return ChatDeepInfra(model="mistralai/Mixtral-8x7B-Instruct-v0.1", api_key=os.getenv("DEEPINFRA_API_KEY"))
        elif model_choice == "Llama 3 Local (Ollama)":
            # Add more specific error handling for Ollama connection
            try:
                 ollama_llm = ChatOllama(model="llama3")
                 
                 ollama_llm.invoke("Hello") 
                 return ollama_llm
            except Exception as ollama_e:
                 print(f"Ollama connection failed: {ollama_e}") # Debug print
                 st.error(f"❌ Failed to connect to Ollama: {ollama_e}. Ensure Ollama is running and the model is available.")
                 return None
        else:
            st.error(f"❌ Unknown model selected: {model_choice}")
            return None
    except Exception as e:
        st.error(f"Error loading model {model_choice}: {e}")
        return None

# --- UI View Functions --- 

def upload_view():


    st.markdown("<h1 style='text-align: center;'>🩺 Medical Report Analyzer</h1>", unsafe_allow_html=True)
    
    # Updated Introductory Text based on index.html content
    st.markdown("""
    Upload lab, radiology, or pathology reports in PDF format for AI-powered analysis. 
    Our system extracts key diagnostic elements, predicts possible medical conditions, 
    and allows you to ask questions about the report.
    
    **Key Features:**
    *   **PDF Processing:** Extracts text from PDF reports.
    *   **AI Analysis (Analyze Page):** 
        *   Uses advanced NLP for processing.
        *   Predicts potential medical conditions based on report content.
        *   Generates concise summaries highlighting key findings.
    *   **Interactive Chat (Chat Page):** Ask follow-up questions about the report.
    
    
    **How It Works:**
    1.  Select an AI model below.
    2.  Upload your medical PDF report.
    3.  Click 'Analyze Report' to process the text.
    4.  Navigate to the 'Analyze' page to review extracted information and predicted conditions.
    5.  Navigate to the 'Chat' page to ask questions about the report findings.
    """)
    st.divider()

    # --- LLM Selector ---
    st.subheader("Select AI Model")
    st.session_state.model_choice = st.selectbox(
        "Choose an AI model to analyze the report:",
        [
            "OpenAI GPT-4",
            "OpenAI GPT-3.5",
            "Llama 3 Instruct (8B)",
            "Mixtral",
            "Llama 3 Local (Ollama)",
            "Llama3-ELAINE-medLLM (Radiology)"
        ],
        key="model_selector_main",
        index=["OpenAI GPT-4", "OpenAI GPT-3.5", "Llama 3 Instruct (8B)", "Mixtral", "Llama 3 Local (Ollama)", "Llama3-ELAINE-medLLM (Radiology)"].index(st.session_state.get('model_choice', "OpenAI GPT-4"))
    )
    st.info(f"Selected Model: **{st.session_state.model_choice}**")
    st.divider()

    # --- File Uploader ---
    st.subheader("Upload PDF Report")
    uploaded_file = st.file_uploader(
        "Choose a medical report (PDF)",
        type=["pdf"],
        key="file_uploader",
        label_visibility="collapsed"
    )

    if uploaded_file is not None:
        # Reset state if it's a new file
        if st.session_state.get("uploaded_filename") != uploaded_file.name:
            st.session_state.messages = []
            st.session_state.report_text = None
            st.session_state.report_tables = None
            st.session_state.analysis_done = False
            st.session_state.analyzed_text = None
            st.session_state.uploaded_filename = uploaded_file.name
            st.session_state.summary = None
            st.session_state.diagnosis_data = None
            st.session_state.raw_conditions = None
            st.session_state.alignment = None
            st.session_state.pdf_buffer = None
            #st.info("New file detected. Processing...")

        # Process only if text hasn't been extracted yet
        if st.session_state.report_text is None:
            with st.spinner("Extracting text and tables..."):
                text, tables = extract_text_and_tables(uploaded_file)
                if text is not None:
                    st.session_state.report_text = text
                    st.session_state.report_tables = tables
                    st.success("✅ PDF content extracted!")
                else:
                    st.error("Failed to extract text from PDF.")
                    st.stop()

        # Display previews
        if st.session_state.report_text:
            st.subheader("📄 Extracted Text Preview")
            st.text_area("Raw Text Preview", value=st.session_state.report_text[:3000], height=200, key="text_preview")

            if st.session_state.report_tables:
                st.subheader("📊 Extracted Tables Preview")
                try:
                    for i, table in enumerate(st.session_state.report_tables[:3]):
                        st.write(f"Table {i + 1}")
                        st.table(table)
                    if len(st.session_state.report_tables) > 3:
                        st.write(f"... and {len(st.session_state.report_tables) - 3} more tables.")
                except Exception as e:
                    st.warning(f"Could not display tables preview: {e}")

            # Analyze Button
            st.divider()
            if st.button("➡️ Analyze Report", key="analyze_button", type="primary"):
                st.session_state.analysis_requested = True
                st.session_state.current_page = "Analyze" # Switch page state
                st.rerun()

    else:
        # Clear state if no file is selected (or deselected)
        if st.session_state.uploaded_filename is not None: 
             print("Clearing state because file was removed.")
             initialize_session_state() 
             st.session_state.current_page = "Upload Report" 

def analyze_view():
    st.title("📊 Analysis Results")

    # --- Check Prerequisites ---
    if not st.session_state.get("report_text"):
        st.warning("Please upload a report on the 'Upload Report' page first.")
        if st.button("Go to Upload Page"):
             st.session_state.current_page = "Upload Report"
             st.rerun()
        st.stop()

    st.info(f"Using model: **{st.session_state.model_choice}**")
    report_text = st.session_state.report_text
    model_choice = st.session_state.model_choice
    llm = load_llm_model(model_choice)


    summary_prompt = PromptTemplate(
        input_variables=["text"],
        template=(
            "Summarize the following medical report in a clear, concise way, "
            "highlighting key findings, diagnoses, and relevant observations. "
            "The number of lines can vary depending on the content:\n\n{text}"
        )
    )

    diagnosis_prompt = PromptTemplate(
        input_variables=["text"],
        template=(
            """Analyze the following medical report and extract possible diagnoses.

Always return the result using the following standard format for EACH diagnosis identified:

- Diagnosis: [Condition Name]
- Type: [Primary / Differential]
- Confidence: [High / Medium / Low]  # Assess confidence based on report evidence
- Rationale: [Short medical reasoning based on report]

Repeat the full block for each diagnosis if multiple.

Only use information supported by the report. Avoid making assumptions.

Medical Report:
{text}
"""
        )
    )

    @st.cache_resource
    def get_embed_model_analyze(): 
        return SentenceTransformer("all-MiniLM-L6-v2")
    embed_model = get_embed_model_analyze()

    def split_into_sentences(text):
        return [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]

    def align_summary_to_source(summary, source_text):

        summary_sents = split_into_sentences(summary)
        source_sents = split_into_sentences(source_text)
        if not summary_sents or not source_sents: return []
        try:
            summary_embeddings = embed_model.encode(summary_sents, convert_to_tensor=True)
            source_embeddings = embed_model.encode(source_sents, convert_to_tensor=True)
            alignment = []
            for i, summary_emb in enumerate(summary_embeddings):
                scores = util.cos_sim(summary_emb, source_embeddings)[0]
                best_match_idx = scores.argmax().item()
                match = source_sents[best_match_idx]
                alignment.append((summary_sents[i], match))
            return alignment
        except Exception as align_e:
            print(f"Alignment error: {align_e}")
            return [] 

    def create_pdf(summary_text, diagnosis_data, logo_path="logo.png"):

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        y = height - 50
        border_color = colors.HexColor("#28A745")
        c.setStrokeColor(border_color)
        c.setLineWidth(3)
        c.rect(20, 20, width - 40, height - 40)
        logo_drawn = False
        if os.path.exists(logo_path):
            try:
                logo = Image.open(logo_path)
                aspect_ratio = logo.width / logo.height
                logo_width = 120; logo_height = logo_width / aspect_ratio
                temp_dir = tempfile.gettempdir(); temp_logo_path = os.path.join(temp_dir, "logo_resized.png")
                logo_resized = logo.resize((int(logo_width), int(logo_height)))
                logo_resized.save(temp_logo_path)
                c.drawImage(temp_logo_path, 40, y - logo_height, width=logo_width, height=logo_height, mask='auto')
                logo_drawn = True
            except Exception as img_e: print(f"PDF Logo Error: {img_e}")
        if not logo_drawn: y += 90
        c.setFont("Helvetica-Bold", 16); c.drawString(220, y - 35, "Medical Report Summary")
        c.setFont("Helvetica", 10); y -= 90
        c.setFont("Helvetica-Bold", 12); c.drawString(40, y, "■ Summary"); y -= 20
        c.setFont("Helvetica", 10)
        if isinstance(summary_text, str):
            for line in summary_text.split('\n'):
                wrapped = simpleSplit(line, 'Helvetica', 10, width - 80)
                for wrapped_line in wrapped:
                    c.drawString(40, y, wrapped_line); y -= 15
                    if y < 40: c.showPage(); c.setFont("Helvetica", 10); y = height - 40
        y -= 10
        c.setFont("Helvetica-Bold", 12); c.drawString(40, y, "■ Diagnosis"); y -= 20
        c.setFont("Helvetica", 10)
        if isinstance(diagnosis_data, list):
            for diag in diagnosis_data:
                if isinstance(diag, dict) and all(k in diag for k in ['Diagnosis', 'Type', 'Rationale']):
                    conf_str = f" (Confidence: {diag.get('Confidence', 'N/A')})" if 'Confidence' in diag else ""
                    diag_line = f"→ {diag['Diagnosis']}{conf_str} ({diag['Type']}): {diag['Rationale']}"
                    wrapped_diag = simpleSplit(diag_line, 'Helvetica', 10, width - 80)
                    for line in wrapped_diag:
                        c.drawString(40, y, line); y -= 15
                        if y < 40: c.showPage(); c.setFont("Helvetica", 10); y = height - 40
                    y -= 5
                else: c.drawString(40, y, "→ [Invalid diagnosis data]"); y -= 15
        c.save(); buffer.seek(0); return buffer

    # --- Run Analysis --- 
    # Only run if analysis hasn't been done for this specific text
    if not st.session_state.get("analysis_done") or st.session_state.get("analyzed_text") != report_text:
        print("Running analysis...") 
        st.session_state.summary = None
        st.session_state.diagnosis_data = None
        st.session_state.alignment = None
        st.session_state.raw_conditions = None
        st.session_state.pdf_buffer = None 

        if model_choice == "Llama3-ELAINE-medLLM (Radiology)":
            st.subheader(f"🩺 Analysis by {model_choice}")
            FLASK_API_URL = "http://127.0.0.1:8080/api/analyze_rad_text"
            try:
                with st.spinner(f"Asking {model_choice} to analyze..."):
                    response = requests.post(FLASK_API_URL, json={"text": report_text}, timeout=90)
                    response.raise_for_status()
                result = response.json()
                if "summary" in result:
                    st.session_state.summary = result["summary"]
                    st.session_state.diagnosis_data = [{"Diagnosis": "See Summary", "Type": "N/A", "Confidence": "N/A", "Rationale": "Combined analysis from fine-tuned model."}]
                else:
                    st.error(f"❌ Error from API: {result.get('error', 'Unknown error')}")
            except Exception as e:
                st.error(f"❌ Failed to get analysis from {model_choice}: {e}")

        elif llm is not None: # LangChain models
            summary = None
            conditions_raw = None
            diagnosis_parsed = []
            alignment_data = []

            summary_chain = LLMChain(llm=llm, prompt=summary_prompt)
            diagnosis_chain = LLMChain(llm=llm, prompt=diagnosis_prompt)

            try:
                with st.spinner(f"Generating summary using {model_choice}..."):
                    summary = summary_chain.run({"text": report_text[:4000]}) # Limit input size
                st.session_state.summary = summary
            except Exception as e: st.error(f"Error generating summary: {e}")

            if summary:
                try:
                    with st.spinner("Aligning summary..."):
                        alignment_data = align_summary_to_source(summary, report_text)
                    st.session_state.alignment = alignment_data
                except Exception as e: st.warning(f"Could not generate alignment: {e}")

            try:
                with st.spinner(f"Predicting conditions using {model_choice}..."):
                    conditions_raw = diagnosis_chain.run({"text": report_text[:4000]}) # Limit input size
            except Exception as e: st.error(f"Error predicting conditions: {e}")

            if isinstance(conditions_raw, str):
                pattern = r"- Diagnosis: (.*?)\n- Type: (.*?)\n- Confidence: (.*?)\n- Rationale: (.*?)(?:\n\n|\n-|$)"
                for match in re.finditer(pattern, conditions_raw, re.DOTALL | re.IGNORECASE):
                    diagnosis_parsed.append({
                        "Diagnosis": match.group(1).strip(), "Type": match.group(2).strip(),
                        "Confidence": match.group(3).strip(), "Rationale": match.group(4).strip()
                    })
                st.session_state.diagnosis_data = diagnosis_parsed
                if not diagnosis_parsed: st.session_state.raw_conditions = conditions_raw
        else:
            st.error(f"Model {model_choice} not loaded. Cannot perform analysis.")

        st.session_state.analysis_done = True
        st.session_state.analyzed_text = report_text
        st.rerun() # Rerun to display the newly generated results immediately
    
    # --- Display Analysis Results --- 
    st.divider()
    st.subheader("📝 Summary ")
    summary_to_display = st.session_state.get("summary")
    alignment_to_display = st.session_state.get("alignment")
    if summary_to_display:
        st.markdown("<style>.summary-sentence:hover {background-color: #d0e0f0; color: #000;}</style>", unsafe_allow_html=True)
        if alignment_to_display:
            html_parts = []
            for summary_sent, source_sent in alignment_to_display:
                safe_source = source_sent.replace('"', '&quot;').replace("'", "&apos;").replace('\n', ' ')
                html_part = f'<span class="summary-sentence" title="Source: {safe_source}" style="cursor: help; border-bottom: 1px dotted #999;">{summary_sent}</span>'
                html_parts.append(html_part)
            full_summary_html = " ".join(html_parts)
            st.markdown(full_summary_html, unsafe_allow_html=True)
        else:
             st.write(summary_to_display)
    else:
        st.write("Summary not generated or available.")

    st.divider()
    st.subheader("🧠 Predicted Conditions/Diagnosis")
    diagnosis_to_display = st.session_state.get("diagnosis_data")
    raw_conditions_to_display = st.session_state.get("raw_conditions")
    if diagnosis_to_display:
        st.markdown("**Potential Diagnoses:**")
        for diag in diagnosis_to_display:
            diag_name = diag.get("Diagnosis", "N/A")
            diag_type = diag.get("Type", "N/A")
            diag_confidence = diag.get("Confidence", "N/A").strip().lower()
            diag_rationale = diag.get("Rationale", "N/A")
            if "high" in diag_confidence: color, symbol = "red", "▲ High"
            elif "medium" in diag_confidence: color, symbol = "orange", "● Medium"
            elif "low" in diag_confidence: color, symbol = "gray", "▼ Low"
            else: color, symbol = "gray", f"? ({diag.get('Confidence', 'N/A')})"
            safe_rationale = diag_rationale.replace('"', '&quot;').replace("'", "&apos;").replace('\n', ' ')
            hover_text = f"Type: {diag_type}\nRationale: {safe_rationale}"
            col1, col2 = st.columns([3, 1])
            with col1: st.markdown(f'- <span title="{hover_text}" style="cursor: help; border-bottom: 1px dotted #999;">{diag_name}</span>', unsafe_allow_html=True)
            with col2: st.markdown(f'<span style="color:{color}; font-weight: bold;">{symbol}</span>', unsafe_allow_html=True)
    elif raw_conditions_to_display:
        st.write("Could not parse structured diagnosis. Raw output:")
        st.write(raw_conditions_to_display)
    else:
        st.write("No condition prediction output available.")

    # --- PDF Download Button ---
    st.divider()
    st.subheader("📄 Download Report")
    pdf_summary = st.session_state.get("summary", "")
    pdf_diagnosis = st.session_state.get("diagnosis_data", [])
    pdf_ready = bool(pdf_summary or pdf_diagnosis)

    # Generate PDF when button is clicked, store buffer in session state
    if st.button("Generate PDF Summary", key="pdf_button", disabled=not pdf_ready):
        with st.spinner("Generating PDF..."):
            st.session_state.pdf_buffer = create_pdf(pdf_summary, pdf_diagnosis)
        st.success("PDF Ready for Download")
        # Rerun might be needed to enable download button if generated in same run
        # time.sleep(0.1)
        # st.rerun()

    # Show download button ONLY if buffer exists in session state
    if st.session_state.get("pdf_buffer") is not None:
        st.download_button(
            label="⬇️ Download Summary PDF",
            data=st.session_state.pdf_buffer,
            file_name="medical_summary.pdf",
            mime="application/pdf",
            key="download_pdf_button"
        )
    elif not pdf_ready:
         st.caption("Analysis must contain a summary or diagnosis to generate PDF.")

def chat_view():
    st.title("💬 Chat about the Medical Report")

    if not st.session_state.get("report_text"):
        st.warning("Please upload a report first.")
        if st.button("Go to Upload"):
             st.session_state.current_page = "Upload Report"
             st.rerun()
        st.stop()

    st.caption(f"Chatting about report: {st.session_state.get('uploaded_filename', 'N/A')}")
    with st.expander("View Full Report Text", expanded=False):
        st.text_area("Report Content", value=st.session_state.report_text, height=200, key="full_report_chat_display", disabled=True)

    model_choice = st.session_state.get("model_choice", "OpenAI GPT-4")
    llm = load_llm_model(model_choice)
    st.info(f"Using model: **{model_choice}** for chat.")

    # --- Chat Interface ---
    if "messages" not in st.session_state: st.session_state.messages = []

    # Display history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Handle Input
    if prompt := st.chat_input("Ask a follow-up question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            response = ""
            if model_choice == "Llama3-ELAINE-medLLM (Radiology)":
                response = "Chat is not supported for this model API."
                st.warning(response)
            elif llm is None:
                 response = f"Cannot respond. Model ({model_choice}) failed to load."
                 st.error(response)
            else:
                try:
                    with st.spinner(f"Thinking with {model_choice}..."):
                        # Prepare context for LangChain models
                        report_text_for_chat = st.session_state.report_text
                        # --- Retrieve and Format Summary/Diagnosis --- 
                        previous_summary = st.session_state.get("summary", "Not available.")
                        previous_diagnosis = st.session_state.get("diagnosis_data", [])
                        
                        diagnosis_context = "\n\nPREVIOUSLY IDENTIFIED DIAGNOSES:\n"
                        if previous_diagnosis:
                            for diag in previous_diagnosis:
                                name = diag.get('Diagnosis', 'N/A')
                                conf = diag.get('Confidence', 'N/A')
                                rationale = diag.get('Rationale', 'N/A')
                                diagnosis_context += f"- {name} (Confidence: {conf}): {rationale}\n"
                        else:
                            diagnosis_context += "None previously identified.\n"
                        # --- End Formatting ---
                        
                        chat_history_for_llm = [
                            SystemMessage(content=f"""You are a helpful AI assistant. The user has uploaded a medical report and you have previously analyzed it. 
Use the following information as context to answer the user's follow-up questions:

REPORT TEXT SNIPPET (Use full text if needed from history):
{report_text_for_chat[:2000]}...

PREVIOUSLY GENERATED SUMMARY:
{previous_summary}
{diagnosis_context}
Answer the user's questions based ONLY on the report context provided. If the answer isn't in the report, summary, or diagnosis info, say so clearly.
""")
                        ]
                        # Add previous messages
                        for msg in st.session_state.messages[:-1]: # Exclude current user prompt
                            if msg["role"] == "user": chat_history_for_llm.append(HumanMessage(content=msg["content"]))
                            elif msg["role"] == "assistant": chat_history_for_llm.append(AIMessage(content=msg["content"]))
                        
                        # Add the current user prompt to the history for the LLM call
                        chat_history_for_llm.append(HumanMessage(content=prompt))

                        ai_response = llm.invoke(chat_history_for_llm)
                        response = ai_response.content
                    st.markdown(response)
                except Exception as e:
                    response = f"An error occurred: {e}"
                    st.error(response)
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
