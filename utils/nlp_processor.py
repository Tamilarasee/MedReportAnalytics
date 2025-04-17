import logging
import re
import numpy as np

logger = logging.getLogger(__name__)

# Try to import transformers and torch, but handle the case where they're not installed
try:
    from transformers import AutoTokenizer, AutoModel
    import torch
    HAS_NLP_PACKAGES = True
except ImportError:
    logger.warning("Transformers or PyTorch not installed. Running with limited functionality.")
    HAS_NLP_PACKAGES = False

# Load the BiomedVLP-BioViL-T model and tokenizer
tokenizer = None
model = None

if HAS_NLP_PACKAGES:
    try:
        tokenizer = AutoTokenizer.from_pretrained("microsoft/BiomedVLP-BioViL-T")
        model = AutoModel.from_pretrained("microsoft/BiomedVLP-BioViL-T")
        logger.info("BiomedVLP-BioViL-T model loaded successfully")
    except Exception as e:
        logger.error(f"Error loading BiomedVLP-BioViL-T model: {str(e)}")
        # Fallback to avoid application crash if model can't be loaded
else:
    logger.warning("Running without NLP model capabilities. Basic text processing only.")

# Medical terms regex patterns
MEDICAL_TERMS_PATTERNS = [
    r'\b[A-Z][a-z]+ (disease|syndrome|disorder)\b',
    r'\b[0-9]+(\.[0-9]+)?\s*(mg|g|mL|L|mmol|μmol|ng|pg|IU|mcg)\b',
    r'\b(elevated|decreased|normal|abnormal|positive|negative)\b',
    r'\b(CBC|MRI|CT|PET|EKG|ECG|EEG|WBC|RBC)\b',
    r'\bhemoglobin\b',
    r'\bleukocyte\b',
    r'\bglucose\b',
    r'\bcholesterol\b',
    r'\btriglycerides\b'
]

def identify_medical_terms(text):
    """
    Identify medical terms in the text
    
    Args:
        text (str): The text to analyze
        
    Returns:
        list: List of identified medical terms
    """
    medical_terms = []
    
    for pattern in MEDICAL_TERMS_PATTERNS:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            term = match.group(0)
            if term not in medical_terms:
                medical_terms.append(term)
    
    return medical_terms

def extract_text_embeddings(text):
    """
    Extract embeddings from text using the BiomedVLP-BioViL-T model
    
    Args:
        text (str): The text to process
        
    Returns:
        dict: The embeddings and processed features
    """
    # Get basic processing results
    sections = extract_report_sections(text)
    medical_terms = identify_medical_terms(text)
    
    # Return basic processing if model isn't available
    if not HAS_NLP_PACKAGES or tokenizer is None or model is None:
        logger.warning("Model not available, returning basic text processing only")
        return {
            'sections': sections,
            'medical_terms': medical_terms,
            'embeddings': None
        }
    
    try:
        # Truncate text to fit model's max length
        max_length = tokenizer.model_max_length
        truncated_text = text[:max_length * 4]  # Approximate character limit
        
        # Prepare model input
        inputs = tokenizer(truncated_text, padding=True, truncation=True, return_tensors="pt")
        
        # Generate embeddings
        with torch.no_grad():
            outputs = model(**inputs)
            embeddings = outputs.last_hidden_state.mean(dim=1).numpy()
        
        logger.debug(f"Generated embeddings with shape {embeddings.shape}")
        
        return {
            'sections': sections,
            'medical_terms': medical_terms,
            'embeddings': embeddings
        }
    except Exception as e:
        logger.error(f"Error generating embeddings: {str(e)}")
        return {
            'sections': sections,
            'medical_terms': medical_terms,
            'embeddings': None
        }

def extract_report_sections(text):
    """
    Extract common sections from medical reports
    
    Args:
        text (str): The report text
        
    Returns:
        dict: Dictionary of section names and their content
    """
    # Common section headers in medical reports
    section_headers = [
        "CLINICAL HISTORY", "HISTORY", "FINDINGS", "IMPRESSION", 
        "DIAGNOSIS", "LABORATORY DATA", "RESULTS", "CONCLUSION", 
        "RADIOGRAPHIC FINDINGS", "PATHOLOGY FINDINGS"
    ]
    
    sections = {}
    
    # Extract text between section headers
    for i, header in enumerate(section_headers):
        pattern = f"{header}[:\s]+(.*?)(?:{'|'.join(section_headers)}|$)"
        matches = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if matches:
            content = matches.group(1).strip()
            sections[header] = content
    
    return sections

def process_text(text):
    """
    Process the text extracted from a medical report
    
    Args:
        text (str): The text to process
        
    Returns:
        dict: The processed data
    """
    try:
        logger.info("Processing medical report text")
        
        # Extract report sections
        sections = extract_report_sections(text)
        
        # Identify medical terms
        medical_terms = identify_medical_terms(text)
        
        # Get text embeddings
        embeddings = extract_text_embeddings(text)
        
        processed_data = {
            'sections': sections,
            'medical_terms': medical_terms,
            'embeddings': embeddings
        }
        
        logger.debug(f"Processed text successfully: {len(medical_terms)} medical terms identified")
        return processed_data
        
    except Exception as e:
        logger.error(f"Error processing text: {str(e)}")
        raise Exception(f"Failed to process report text: {str(e)}")

def process_query(query, processed_data, conditions, enriched_data):
    """
    Process a query about the medical report
    
    Args:
        query (str): The query to process
        processed_data (dict): The processed report data
        conditions (list): The predicted conditions
        enriched_data (dict): The enriched data
        
    Returns:
        str: The answer to the query
    """
    try:
        # Check if we have NLP capabilities
        if not HAS_NLP_PACKAGES or tokenizer is None or model is None:
            logger.warning("Model not available, providing basic response")
            return generate_basic_response(query, processed_data, conditions, enriched_data)
        
        try:
            # Encode the query
            query_inputs = tokenizer(query, padding=True, truncation=True, return_tensors="pt")
            
            # Get query embedding
            with torch.no_grad():
                query_output = model(**query_inputs)
                query_embedding = query_output.last_hidden_state.mean(dim=1).numpy()
            
            logger.debug("Generated query embedding with NLP model")
        except Exception as e:
            logger.error(f"Error using NLP model: {str(e)}")
            return generate_basic_response(query, processed_data, conditions, enriched_data)
        
        # Prepare response based on query content
        if "condition" in query.lower() or "diagnosis" in query.lower():
            return f"Based on the report, the most likely conditions are: {', '.join(conditions[:3])}"
        
        if "abnormal" in query.lower() or "concerning" in query.lower():
            if len(processed_data['medical_terms']) > 0:
                return f"The report shows several potentially important terms: {', '.join(processed_data['medical_terms'][:5])}"
        
        if "summary" in query.lower():
            if "IMPRESSION" in processed_data['sections']:
                return f"Report summary: {processed_data['sections']['IMPRESSION']}"
            elif "CONCLUSION" in processed_data['sections']:
                return f"Report summary: {processed_data['sections']['CONCLUSION']}"
        
        # Default answer
        return "I can help you interpret this medical report. You can ask about conditions, abnormal findings, or request a summary."
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return "I'm sorry, I encountered an error processing your query. Please try a different question."

def generate_basic_response(query, processed_data, conditions, enriched_data):
    """
    Generate a basic response without using the model
    
    Args:
        query (str): The query to process
        processed_data (dict): The processed report data
        conditions (list): The predicted conditions
        enriched_data (dict): The enriched data
        
    Returns:
        str: The basic answer to the query
    """
    query_lower = query.lower()
    
    if "condition" in query_lower or "diagnosis" in query_lower:
        if conditions and len(conditions) > 0:
            return f"Based on the report, possible conditions include: {', '.join(conditions[:3])}"
        else:
            return "No specific conditions were identified in this report."
            
    if "abnormal" in query_lower or "concerning" in query_lower:
        if processed_data['medical_terms'] and len(processed_data['medical_terms']) > 0:
            return f"The report contains these medical terms that may be of interest: {', '.join(processed_data['medical_terms'][:5])}"
        else:
            return "No specific abnormal findings were highlighted in this report."
            
    if "summary" in query_lower:
        for section in ["IMPRESSION", "CONCLUSION", "FINDINGS"]:
            if section in processed_data['sections'] and processed_data['sections'][section]:
                return f"Report summary: {processed_data['sections'][section]}"
                
        return "No summary section was found in this report."
        
    # Default response
    return "I can help you understand this medical report. Try asking about conditions, abnormal findings, or ask for a summary."
