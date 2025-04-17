import logging
import re

logger = logging.getLogger(__name__)

# Common lab/radiology findings and associated conditions
# This is a simplified mapping for demonstration
FINDINGS_TO_CONDITIONS = {
    # Common lab findings
    "elevated glucose": ["Diabetes", "Prediabetes", "Metabolic syndrome"],
    "high blood sugar": ["Diabetes", "Prediabetes", "Metabolic syndrome"],
    "elevated cholesterol": ["Hypercholesterolemia", "Atherosclerosis", "Cardiovascular disease"],
    "high ldl": ["Hypercholesterolemia", "Atherosclerosis", "Cardiovascular disease"],
    "elevated triglycerides": ["Hypertriglyceridemia", "Metabolic syndrome", "Pancreatitis"],
    "decreased hemoglobin": ["Anemia", "Blood loss", "Chronic disease"],
    "low hemoglobin": ["Anemia", "Blood loss", "Chronic disease"],
    "elevated wbc": ["Infection", "Inflammation", "Leukemia"],
    "high white blood cell": ["Infection", "Inflammation", "Leukemia"],
    "low platelet": ["Thrombocytopenia", "Bone marrow disorders", "Immune disorders"],
    "elevated tsh": ["Hypothyroidism", "Thyroid disorder"],
    "decreased tsh": ["Hyperthyroidism", "Thyroid disorder"],
    "elevated creatinine": ["Kidney disease", "Renal insufficiency", "Dehydration"],
    "elevated alt": ["Liver disease", "Hepatitis", "Medication effect"],
    "elevated ast": ["Liver disease", "Hepatitis", "Muscle damage"],
    
    # Common radiology findings
    "pulmonary nodule": ["Lung cancer", "Granuloma", "Infection"],
    "ground glass opacit": ["Pneumonia", "COVID-19", "Interstitial lung disease"],
    "pleural effusion": ["Congestive heart failure", "Pneumonia", "Malignancy"],
    "cardiomegaly": ["Heart failure", "Cardiomyopathy", "Pericardial effusion"],
    "atherosclerosis": ["Coronary artery disease", "Peripheral vascular disease", "Stroke risk"],
    "fracture": ["Trauma", "Osteoporosis", "Pathological fracture"],
    "osteophyte": ["Osteoarthritis", "Degenerative joint disease"],
    "disc herniation": ["Radiculopathy", "Back pain", "Spinal cord compression"],
    "disc buldge": ["Degenerative disc disease", "Back pain", "Spinal stenosis"],
    "mass": ["Neoplasm", "Malignancy", "Tumor"],
    "lesion": ["Neoplasm", "Infection", "Inflammation"],
    
    # Common pathology findings
    "atypical cells": ["Dysplasia", "Premalignant condition", "Cancer"],
    "malignant cells": ["Cancer", "Carcinoma", "Malignancy"],
    "hyperplasia": ["Benign growth", "Hormonal changes", "Precancerous in some contexts"],
    "dysplasia": ["Precancerous condition", "Abnormal development"],
    "metaplasia": ["Adaptive cell change", "Increased cancer risk"],
    "inflammation": ["Infection", "Autoimmune condition", "Inflammatory disease"],
    "necrosis": ["Tissue death", "Ischemia", "Tumor"],
}

def predict_conditions(processed_data):
    """
    Predict potential medical conditions based on the processed data
    
    Args:
        processed_data (dict): The processed report data
        
    Returns:
        list: List of potential conditions
    """
    try:
        logger.info("Predicting medical conditions from report")
        
        # Get the full text by combining all sections
        full_text = ""
        if 'sections' in processed_data:
            for section, content in processed_data['sections'].items():
                full_text += content + " "
        
        # Identified conditions with confidence scores
        condition_scores = {}
        
        # Check for common findings in the text
        for finding, conditions in FINDINGS_TO_CONDITIONS.items():
            if re.search(r'\b' + finding + r'\b', full_text, re.IGNORECASE):
                # If finding is found, add associated conditions
                for condition in conditions:
                    if condition in condition_scores:
                        condition_scores[condition] += 1
                    else:
                        condition_scores[condition] = 1
        
        # Sort conditions by score
        sorted_conditions = sorted(condition_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Extract condition names
        predicted_conditions = [condition for condition, score in sorted_conditions]
        
        # If no conditions found, return a default message
        if not predicted_conditions:
            logger.warning("No conditions identified from the report")
            predicted_conditions = ["No specific conditions identified"]
        
        logger.debug(f"Predicted {len(predicted_conditions)} potential conditions")
        return predicted_conditions
        
    except Exception as e:
        logger.error(f"Error predicting conditions: {str(e)}")
        return ["Error in condition prediction"]
