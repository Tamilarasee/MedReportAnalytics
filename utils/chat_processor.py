import os
import logging
import json
import requests
from typing import Dict, List, Any, Optional

# Set up logging
logger = logging.getLogger(__name__)

# Constants
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/kenyano/Llama3-ELAINE-medLLM-instruct-8B_v0.1"
HUGGINGFACE_API_KEY = os.environ.get("HUGGINGFACE_API_KEY")

def prepare_chat_prompt(user_query: str, report_text: str, report_sections: Dict[str, str], 
                        medical_terms: List[str], conditions: List[str]) -> str:
    """
    Prepare a comprehensive prompt for the medical LLM with context from the report.
    
    Args:
        user_query: The question from the user
        report_text: The full text of the medical report
        report_sections: Dictionary of report sections
        medical_terms: List of identified medical terms
        conditions: List of predicted conditions
        
    Returns:
        A formatted prompt for the medical LLM
    """
    
    # Create a summary of the medical terms and conditions identified
    terms_summary = "Key medical terms in this report include: " + ", ".join(medical_terms[:10])
    
    # Add potential conditions if available
    conditions_summary = ""
    if conditions and conditions[0] != "No specific conditions identified":
        conditions_summary = "\\nPotential conditions identified in the report include: " + ", ".join(conditions[:5])
    
    # Create a summary of the key sections of the report
    sections_summary = ""
    for section_name, section_text in report_sections.items():
        # Keep section summaries short
        if section_name in ['IMPRESSION', 'CONCLUSION', 'FINDINGS', 'ASSESSMENT', 'DIAGNOSIS']:
            sections_summary += f"\\n{section_name}: {section_text[:300]}"
            if len(section_text) > 300:
                sections_summary += "..."
    
    # Construct the prompt with all the context
    prompt = f"""<|system|>
You are Elaine, an expert medical assistant specializing in interpreting medical reports for patients and healthcare professionals.
Your answers should be accurate, helpful, and educational. Avoid technical jargon when possible, but provide specific medical details when relevant.
The following is a summary of a medical report that has been analyzed. Use this context to answer questions.

REPORT SECTIONS: {sections_summary}

{terms_summary}
{conditions_summary}

When answering:
1. Base your answers specifically on the information provided in the report
2. If the report doesn't contain information needed to answer a question, clearly state that
3. For medical terminology, provide brief explanations to help understand their meaning
4. When discussing potential diagnoses, use cautious language and explain the basis of your assessment
5. Maintain a professional, compassionate tone
<|user|>
{user_query}
<|assistant|>"""

    return prompt

def chat_with_report(query: str, report_data: Dict[str, Any]) -> str:
    """
    Process a chat query about the medical report using the Llama3-ELAINE-medLLM model.
    
    Args:
        query: The user's query about the report
        report_data: The processed report data including text, sections, terms, etc.
        
    Returns:
        The LLM's response to the query
    """
    try:
        logger.info(f"Processing chat query: {query}")
        
        # Extract required data from the report_data
        processed_data = report_data.get('processed_data', {})
        report_text = report_data.get('original_text', '')
        report_sections = processed_data.get('sections', {})
        medical_terms = processed_data.get('medical_terms', [])
        conditions = report_data.get('conditions', [])
        
        # Prepare the prompt with all the context
        prompt = prepare_chat_prompt(query, report_text, report_sections, medical_terms, conditions)
        
        # Check if we have an API key for Hugging Face
        if not HUGGINGFACE_API_KEY:
            logger.warning("No HUGGINGFACE_API_KEY found. Generating fallback response.")
            return generate_fallback_response(query, report_data)
        
        # Set up the headers with the API key
        headers = {
            "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Prepare the payload for the API call
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 1024,
                "temperature": 0.7,
                "top_p": 0.95,
                "do_sample": True
            }
        }
        
        # Make the API call
        logger.debug("Making API call to HuggingFace")
        response = requests.post(HUGGINGFACE_API_URL, headers=headers, json=payload)
        
        if response.status_code != 200:
            logger.error(f"HuggingFace API returned error: {response.status_code} - {response.text}")
            return generate_fallback_response(query, report_data)
        
        # Process the response
        response_data = response.json()
        
        # Extract the generated text from the response
        if isinstance(response_data, list) and len(response_data) > 0:
            generated_text = response_data[0].get('generated_text', '')
        else:
            generated_text = response_data.get('generated_text', '')
        
        # Extract just the assistant's response (after the <|assistant|> token)
        if '<|assistant|>' in generated_text:
            assistant_response = generated_text.split('<|assistant|>')[1].strip()
        else:
            assistant_response = generated_text.strip()
        
        logger.info("Successfully generated response from LLM")
        return assistant_response
        
    except Exception as e:
        logger.error(f"Error in chat_with_report: {str(e)}")
        return generate_fallback_response(query, report_data)

def generate_fallback_response(query: str, report_data: Dict[str, Any]) -> str:
    """
    Generate a fallback response when the LLM call fails.
    
    Args:
        query: The user's query
        report_data: The processed report data
        
    Returns:
        A fallback response based on the available data
    """
    logger.info("Generating fallback response")
    
    processed_data = report_data.get('processed_data', {})
    medical_terms = processed_data.get('medical_terms', [])
    sections = processed_data.get('sections', {})
    conditions = report_data.get('conditions', [])
    
    # Check if the query is about conditions or diagnoses
    if any(keyword in query.lower() for keyword in ['condition', 'diagnosis', 'disease']):
        if conditions and conditions[0] != "No specific conditions identified":
            return f"Based on the report analysis, potential conditions that may be relevant include: {', '.join(conditions[:5])}. However, please note that this is not a definitive diagnosis, and you should consult with your healthcare provider for a proper interpretation."
        else:
            return "I don't have enough information in the report to identify specific conditions related to your query. Please consult with your healthcare provider for a proper diagnosis and interpretation of your medical report."
    
    # Check if the query is about specific medical terms
    for term in medical_terms:
        if term.lower() in query.lower():
            return f"The term '{term}' appears in your medical report. Unfortunately, without access to the advanced medical knowledge model, I can't provide a detailed explanation. Please ask your healthcare provider about the significance of this term in your report."
    
    # Check if the query is about a specific section
    for section_name, section_text in sections.items():
        if section_name.lower() in query.lower():
            return f"The {section_name} section of your report states: '{section_text[:300]}...' For a complete interpretation, please consult with your healthcare provider."
    
    # Default response
    return "I'm currently experiencing difficulty accessing the medical knowledge model. Your question is important, but I need to recommend discussing this with your healthcare provider who can give you a proper interpretation of your medical report."