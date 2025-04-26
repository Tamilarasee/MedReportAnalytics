import logging
from utils.llm_client import ask_medllama

logger = logging.getLogger(__name__)


def query_llm_for_definition(term, context_type="term"):
    """
    Ask MedLLaMA for a simple medical definition.
    """
    try:
        prompt = f"""
        You are a medical assistant helping interpret clinical reports.

        Define the following {context_type} in simple, medically accurate terms:
        "{term}"

        Respond with only a short explanation. No headers, no summaries, no extra commentary.
        """
        response = ask_medllama(prompt)
        return response.strip()
    except Exception as e:
        logger.warning(f"LLM enrichment failed for {term}: {e}")
        return None


def query_llm_for_reference_range(term):
    """
    Ask MedLLaMA for the normal reference range of a lab term.
    """
    try:
        prompt = f"""
        Provide the normal clinical reference range for the following laboratory term, if applicable:
        "{term}"

        Example format: "70-99 mg/dL" or "Below 150 mg/dL". If unknown, reply "Unknown".
        Only return the range itself, no extra text.
        """
        response = ask_medllama(prompt)
        return response.strip()
    except Exception as e:
        logger.warning(f"LLM reference range lookup failed for {term}: {e}")
        return None


def enrich_data(processed_data, conditions, use_llm=True):
    """
    Enrich the processed report data with:
    - Definitions of medical terms
    - Descriptions of predicted conditions
    - Reference ranges for lab terms

    All fallback dynamically to LLM if static definitions are unavailable.
    """
    try:
        logger.info("Starting data enrichment...")

        enriched_data = {
            'term_definitions': {},
            'condition_info': {},
            'reference_ranges': {}
        }

        # --- Enrich medical terms ---
        medical_terms = processed_data.get('medical_terms', [])
        for term in medical_terms:
            term_clean = term.strip()

            if use_llm:
                definition = query_llm_for_definition(
                    term_clean, context_type="term")
                if definition:
                    enriched_data['term_definitions'][term_clean] = definition

                range_value = query_llm_for_reference_range(term_clean)
                if range_value and range_value.lower() != "unknown":
                    enriched_data['reference_ranges'][term_clean] = range_value

        # --- Enrich predicted conditions ---
        for condition in conditions:
            condition_clean = condition.strip()

            if use_llm:
                condition_info = query_llm_for_definition(
                    condition_clean, context_type="condition")
                if condition_info:
                    enriched_data['condition_info'][condition_clean] = condition_info

        logger.debug(f"✅ Enrichment complete: {len(enriched_data['term_definitions'])} terms, "
                     f"{len(enriched_data['condition_info'])} conditions, "
                     f"{len(enriched_data['reference_ranges'])} reference ranges")

        return enriched_data

    except Exception as e:
        logger.error(f"Enrichment failed: {str(e)}")
        return {
            'term_definitions': {},
            'condition_info': {},
            'reference_ranges': {}
        }
