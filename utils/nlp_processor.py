import logging
from utils.llm_client import ask_medllama

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def process_text(text):
    """
    Full 3-step LLM Processing:
    1. Clinical Bullet Summary
    2. Important Keywords Extraction
    3. Packaging
    """
    logger.info("Starting full LLM pipeline (Summary + Keywords)...")

    try:
        # Step 1: Clinical Summary Bullets
        summary_prompt = f"""
        You are a clinical assistant.

        Instructions:
        - Extract 3 to 7 bullet points summarizing the important clinical findings from the report.
        - Each bullet point should be short, objective, and include [Evidence: "copied sentence from report"].
        - Do not guess anything not mentioned.

        --- Report Text ---
        {text}
        """

        summary_response = ask_medllama(summary_prompt)
        clinical_summary, evidence_links = parse_summary_with_evidence(
            summary_response)

        # Step 2: Extract Important Keywords
        keywords_prompt = f"""
        From the following clinical bullet points, extract all important medical findings, imaging terms, lab results, anatomical locations, abnormalities.

        - List them as comma-separated values without explanations.

        --- Bullet Points ---
        {chr(10).join([bp['bullet_point'] for bp in clinical_summary])}
        """

        keywords_response = ask_medllama(keywords_prompt)
        identified_keywords = parse_keywords(keywords_response)

        # Step 3: Package
        return {
            "clinical_summary": clinical_summary,
            "evidence_links": evidence_links,
            "identified_keywords": identified_keywords,
            "original_text": text
        }

    except Exception as e:
        logger.error(f"Error during 3-step LLM processing: {str(e)}")
        return {
            "clinical_summary": [],
            "evidence_links": [],
            "identified_keywords": [],
            "original_text": text
        }


def parse_summary_with_evidence(response_text):
    """
    Parses clinical summary bullets and their evidence from LLM output robustly.
    """
    clinical_summary = []
    evidence_links = []

    lines = response_text.splitlines()
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Look for Evidence tag
        if 'Evidence:' in line:
            try:
                parts = line.split('Evidence:')
                bullet_text = parts[0].replace('-', '').strip()

                evidence_text = parts[1]
                evidence_text = evidence_text.strip().strip(
                    '[]"').replace('Evidence', '').strip()

                clinical_summary.append({
                    "bullet_point": bullet_text,
                    "evidence": evidence_text
                })
                if evidence_text:
                    evidence_links.append(evidence_text)
            except Exception as e:
                # Fallback safe
                clinical_summary.append({
                    "bullet_point": line.replace('-', '').strip(),
                    "evidence": ""
                })
        else:
            # No evidence
            clinical_summary.append({
                "bullet_point": line.replace('-', '').strip(),
                "evidence": ""
            })

    return clinical_summary, evidence_links


def parse_keywords(response_text):
    """
    Robust keyword parser for LLM output.
    """
    keywords = []
    text = response_text.replace('\n', ',')  # Handle newlines

    for kw in text.split(','):
        kw = kw.strip()
        if kw and len(kw) < 100:
            keywords.append(kw)

    return keywords
