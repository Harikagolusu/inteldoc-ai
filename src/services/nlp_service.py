import spacy
import logging

logger = logging.getLogger(__name__)

# Try to load the spacy model. For production, ensure this is downloaded during deployment.
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    logger.warning("Spacy model 'en_core_web_sm' not found. Will download during runtime or fail if unavailable. Make sure to download it using: python -m spacy download en_core_web_sm")
    # For robust deployment, it's highly recommended to download the model as part of the build step
    # Wait for the user to run it or fallback. We'll raise it here to be explicit but ideally the environment will have it.
    nlp = None

def get_empty_entities():
    return {
        "persons": [],
        "organizations": [],
        "dates": [],
        "money": [],
        "locations": []
    }

async def extract_entities(text: str) -> dict:
    """
    Extract named entities using spaCy.
    Categorize into persons, organizations, dates, money, locations.
    Removes duplicates and returns a structured format.
    """
    entities = get_empty_entities()
    
    # If text is empty or model failed to load somehow
    if not text or not nlp:
        return entities
        
    # spaCy imposes a max string length constraint
    if len(text) > nlp.max_length:
        logger.warning(f"Text length {len(text)} exceeds spacy max length. Truncating.")
        text = text[:nlp.max_length]

    try:
        doc = nlp(text)
        
        # Temporary sets to ensure uniqueness
        extracted = {
            "persons": set(),
            "organizations": set(),
            "dates": set(),
            "money": set(),
            "locations": set()
        }
        
        # spaCy entity mapping to our structure
        entity_map = {
            "PERSON": "persons",
            "ORG": "organizations",
            "DATE": "dates",
            "MONEY": "money",
            "GPE": "locations",
            "LOC": "locations"
        }
        
        for ent in doc.ents:
            category = entity_map.get(ent.label_)
            if category:
                # Clean up the entity text slightly
                clean_ent = ent.text.strip().replace("\n", " ")
                if len(clean_ent) > 1: # Avoid single character noise
                    extracted[category].add(clean_ent)
                    
        # Convert sets back to sorted lists
        for cat in entities.keys():
            entities[cat] = sorted(list(extracted[cat]))
            
        return entities
        
    except Exception as e:
        logger.error(f"Entity extraction failed: {str(e)}")
        # Provide graceful degradation by returning empty structured dict
        return entities