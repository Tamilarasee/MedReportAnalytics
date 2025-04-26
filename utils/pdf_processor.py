import io
import logging
import PyPDF2
from werkzeug.datastructures import FileStorage
from utils.llm_client import ask_medllama  # 👈 make sure this exists

logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_file, use_llm=False):
    """
    Extract text from a PDF file and optionally clean/process it with an LLM

    Args:
        pdf_file: A file-like object containing the PDF
        use_llm (bool): Whether to refine the extracted text with MedLLaMA

    Returns:
        str: The extracted (and possibly cleaned) text from the PDF
    """
    try:
        # Load raw bytes
        if isinstance(pdf_file, FileStorage):
            pdf_bytes = pdf_file.read()
            pdf_file.seek(0)
        else:
            pdf_bytes = pdf_file.read()

        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))

        text = ""
        for page in pdf_reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"

        if not text.strip():
            logger.warning("Extracted text is empty")
            return None

        logger.debug(f"Extracted {len(text)} characters from PDF")

        if use_llm:
            logger.info("Refining extracted PDF text using MedLLaMA")

            prompt = f"""
            The following text was extracted from a lab, radiology, or pathology report in PDF form. 
            Please clean and structure the content into a readable and coherent clinical report.
            Do not summarize — just fix formatting, remove irrelevant artifacts, and preserve important sections and medical language.

            --- Extracted Text ---
            {text.strip()}
            """

            cleaned_text = ask_medllama(prompt)
            return cleaned_text.strip()

        return text.strip()

    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise Exception(f"Failed to extract text from PDF: {str(e)}")
