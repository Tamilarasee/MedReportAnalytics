import logging
import re

logger = logging.getLogger(__name__)

# Common medical term definitions
MEDICAL_TERM_DEFINITIONS = {
    # Lab test terms
    "hemoglobin": "A protein in red blood cells that carries oxygen throughout the body.",
    "wbc": "White Blood Cells, which are part of the immune system and help fight infection.",
    "rbc": "Red Blood Cells, which carry oxygen from the lungs to the rest of the body.",
    "platelet": "Cell fragments that help with blood clotting.",
    "glucose": "A type of sugar that is the body's main source of energy.",
    "hba1c": "Hemoglobin A1c, a test that measures average blood sugar levels over the past 2-3 months.",
    "creatinine": "A waste product that comes from normal muscle use and is filtered out by the kidneys.",
    "bun": "Blood Urea Nitrogen, a waste product filtered out by the kidneys.",
    "alt": "Alanine Transaminase, an enzyme found primarily in the liver that indicates liver health.",
    "ast": "Aspartate Aminotransferase, an enzyme found in various tissues that can indicate tissue damage.",
    "ldl": "Low-Density Lipoprotein, often called 'bad cholesterol'.",
    "hdl": "High-Density Lipoprotein, often called 'good cholesterol'.",
    "triglycerides": "A type of fat found in the blood that can increase risk of heart disease.",
    
    # Radiology terms
    "opacity": "An area that appears white or light gray on an X-ray, indicating something dense.",
    "nodule": "A small rounded lump that may appear in various tissues and organs.",
    "lesion": "Any abnormal damage or change in tissue, often referring to an area of disease.",
    "fracture": "A break in a bone.",
    "effusion": "Abnormal collection of fluid within a body cavity.",
    "atelectasis": "Collapse of lung tissue preventing the exchange of carbon dioxide and oxygen.",
    "infiltrate": "Substance that abnormally accumulates in tissues or cells, often referring to inflammation or infection in lungs.",
    "cardiomegaly": "Enlarged heart.",
    "pneumothorax": "Air in the space between the lung and chest wall, causing lung collapse.",
    
    # Pathology terms
    "biopsy": "Procedure to remove a piece of tissue for examination.",
    "hyperplasia": "Abnormal increase in the number of cells in an organ or tissue.",
    "dysplasia": "Abnormal development of cells that may indicate early stages of cancer.",
    "metaplasia": "Replacement of one type of cell with another type that is not normally present.",
    "neoplasm": "Abnormal growth of tissue, may be benign or malignant.",
    "malignant": "Cancerous; cells that can invade nearby tissue and spread to other parts of the body.",
    "benign": "Not cancerous; does not invade nearby tissue or spread to other parts of the body.",
    "necrosis": "Death of body tissue due to disease or injury.",
    "inflammation": "Body's response to injury or infection, characterized by redness, swelling, heat, and pain."
}

# Common condition definitions
CONDITION_DEFINITIONS = {
    "diabetes": "A chronic condition that affects how your body turns food into energy, characterized by high blood sugar levels.",
    "hypertension": "High blood pressure, a common condition that can lead to serious health problems like heart disease and stroke.",
    "anemia": "A condition in which you lack enough healthy red blood cells to carry adequate oxygen to your body's tissues.",
    "pneumonia": "An infection that inflames the air sacs in one or both lungs, which may fill with fluid.",
    "bronchitis": "Inflammation of the lining of your bronchial tubes, which carry air to and from your lungs.",
    "coronary artery disease": "Damage or disease in the heart's major blood vessels that can lead to heart attack.",
    "osteoporosis": "A condition that causes bones to become weak and brittle.",
    "arthritis": "Inflammation of one or more joints, causing pain and stiffness.",
    "hypothyroidism": "A condition in which the thyroid gland doesn't produce enough thyroid hormone.",
    "hyperthyroidism": "A condition in which the thyroid gland produces too much thyroid hormone.",
    "kidney disease": "A condition that affects the kidneys' ability to filter waste from the blood.",
    "liver disease": "A term for a variety of conditions that affect the liver's ability to function.",
    "copd": "Chronic Obstructive Pulmonary Disease, a chronic inflammatory lung disease that causes obstructed airflow from the lungs.",
    "asthma": "A condition in which your airways narrow and swell and produce extra mucus.",
    "cancer": "A disease in which abnormal cells divide uncontrollably and destroy body tissue."
}

# Reference ranges for common lab tests
REFERENCE_RANGES = {
    "hemoglobin": "Male: 13.5-17.5 g/dL; Female: 12.0-15.5 g/dL",
    "wbc": "4,500-11,000 cells/mcL",
    "rbc": "Male: 4.7-6.1 million cells/mcL; Female: 4.2-5.4 million cells/mcL",
    "platelets": "150,000-450,000/mcL",
    "glucose": "Fasting: 70-99 mg/dL",
    "hba1c": "Below 5.7%: Normal; 5.7-6.4%: Prediabetes; 6.5% or higher: Diabetes",
    "creatinine": "Male: 0.74-1.35 mg/dL; Female: 0.59-1.04 mg/dL",
    "bun": "7-20 mg/dL",
    "alt": "Male: 7-55 U/L; Female: 7-45 U/L",
    "ast": "8-48 U/L",
    "total cholesterol": "Below 200 mg/dL",
    "ldl": "Below 100 mg/dL",
    "hdl": "Male: Above 40 mg/dL; Female: Above 50 mg/dL",
    "triglycerides": "Below 150 mg/dL"
}

def enrich_data(processed_data, conditions):
    """
    Enrich the processed data with additional context
    
    Args:
        processed_data (dict): The processed report data
        conditions (list): Predicted conditions
        
    Returns:
        dict: The enriched data
    """
    try:
        logger.info("Enriching medical data")
        
        enriched_data = {
            'term_definitions': {},
            'condition_info': {},
            'reference_ranges': {}
        }
        
        # Enrich medical terms
        if 'medical_terms' in processed_data:
            for term in processed_data['medical_terms']:
                term_lower = term.lower()
                # Check if term or a substring of it exists in our definitions
                for def_term, definition in MEDICAL_TERM_DEFINITIONS.items():
                    if def_term in term_lower or re.search(r'\b' + def_term + r'\b', term_lower):
                        enriched_data['term_definitions'][term] = definition
                        break
        
        # Enrich conditions
        for condition in conditions:
            condition_lower = condition.lower()
            # Check if condition exists in our definitions
            for def_condition, definition in CONDITION_DEFINITIONS.items():
                if def_condition in condition_lower or condition_lower in def_condition:
                    enriched_data['condition_info'][condition] = definition
                    break
        
        # Add reference ranges for relevant medical terms
        if 'medical_terms' in processed_data:
            for term in processed_data['medical_terms']:
                term_lower = term.lower()
                # Check if term relates to any reference range
                for range_term, range_value in REFERENCE_RANGES.items():
                    if range_term in term_lower or re.search(r'\b' + range_term + r'\b', term_lower):
                        enriched_data['reference_ranges'][term] = range_value
                        break
        
        logger.debug(f"Enriched data with {len(enriched_data['term_definitions'])} term definitions, " +
                    f"{len(enriched_data['condition_info'])} condition definitions, " +
                    f"and {len(enriched_data['reference_ranges'])} reference ranges")
                    
        return enriched_data
        
    except Exception as e:
        logger.error(f"Error enriching data: {str(e)}")
        return {
            'term_definitions': {},
            'condition_info': {},
            'reference_ranges': {}
        }
