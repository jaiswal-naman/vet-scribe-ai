from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
import logging
import re
from typing import Dict, List

logger = logging.getLogger(__name__)

class BioBERTProcessor:
    def __init__(self):
        """Initialize BioBERT NER processor"""
        try:
            model_name = "dmis-lab/biobert-v1.1"
            logger.info(f"Loading BioBERT model: {model_name}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForTokenClassification.from_pretrained(model_name)
            
            # Create NER pipeline
            self.ner_pipeline = pipeline(
                "ner",
                model=self.model,
                tokenizer=self.tokenizer,
                aggregation_strategy="simple"
            )
            
            logger.info("BioBERT model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load BioBERT model: {str(e)}")
            # Fallback to rule-based extraction
            self.ner_pipeline = None
    
    def extract_entities(self, text: str) -> Dict[str, str]:
        """Extract medical entities from text using rule-based approach"""
        print(f"Extracting entities from: {text[:100]}...")
        
        # Always use rule-based extraction to avoid numpy serialization issues
        return self._extract_with_rules(text)
    
    def _extract_with_biobert(self, text: str) -> Dict[str, str]:
        """Extract entities using BioBERT"""
        try:
            # Run NER
            entities = self.ner_pipeline(text)
            
            # Group entities by type
            diagnosis_terms = []
            treatment_terms = []
            
            for entity in entities:
                entity_text = entity['word'].replace('##', '')
                
                # Simple classification based on entity type
                if entity['entity_group'] in ['DISEASE', 'SYMPTOM']:
                    diagnosis_terms.append(entity_text)
                elif entity['entity_group'] in ['TREATMENT', 'DRUG', 'PROCEDURE']:
                    treatment_terms.append(entity_text)
            
            return {
                'diagnosis': ', '.join(set(diagnosis_terms)),
                'treatment': ', '.join(set(treatment_terms)),
                'all_entities': entities
            }
            
        except Exception as e:
            logger.error(f"BioBERT extraction failed: {str(e)}")
            return self._extract_with_rules(text)
    
    def _extract_with_rules(self, text: str) -> Dict[str, str]:
        """Rule-based entity extraction"""
        text_lower = text.lower()
        
        # Common veterinary diagnosis keywords
        diagnosis_keywords = [
            'fever', 'anemia', 'infection', 'inflammation', 'arthritis',
            'dermatitis', 'gastritis', 'pneumonia', 'diabetes', 'cancer',
            'tumor', 'fracture', 'wound', 'allergy', 'parasites', 'fleas',
            'ticks', 'worms', 'diarrhea', 'vomiting', 'seizure', 'lameness',
            'lethargy', 'elevated temperature', 'temperature'
        ]
        
        # Common treatment keywords
        treatment_keywords = [
            'antibiotic', 'antibiotics', 'doxycycline', 'amoxicillin',
            'prednisone', 'surgery', 'vaccination', 'medication', 'treatment',
            'therapy', 'rest', 'diet', 'exercise', 'bandage', 'cast',
            'fluids', 'pain relief', 'anti-inflammatory', 'prescribed'
        ]
        
        # Extract matching terms
        found_diagnoses = [kw for kw in diagnosis_keywords if kw in text_lower]
        found_treatments = [kw for kw in treatment_keywords if kw in text_lower]
        
        print(f"Found diagnoses: {found_diagnoses}")
        print(f"Found treatments: {found_treatments}")
        
        return {
            'diagnosis': ', '.join(found_diagnoses),
            'treatment': ', '.join(found_treatments),
            'extraction_method': 'rule-based'
        }