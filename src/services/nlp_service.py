import spacy
from spacy.cli import download
import logging

logger = logging.getLogger(__name__)

nlp = None

def load_nlp():
    global nlp
    if nlp is None:
        try:
            nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.info("Downloading en_core_web_sm model at runtime...")
            download("en_core_web_sm")
            nlp = spacy.load("en_core_web_sm")
    return nlp

def get_empty_entities():
    return {
        "persons": [],
        "organizations": [],
        "dates": [],
        "money": [],
        "locations": []
    }

async def extract_entities(text: str):
    if not text.strip():
        return get_empty_entities()

    try:
        # Load NLP lazily at runtime
        model = load_nlp()
        doc = model(text[:100000])  # limit length to avoid memory constraints
        
        entities = {
            "persons": set(),
            "organizations": set(),
            "dates": set(),
            "money": set(),
            "locations": set()
        }
        
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                entities["persons"].add(ent.text)
            elif ent.label_ == "ORG":
                entities["organizations"].add(ent.text)
            elif ent.label_ == "DATE":
                entities["dates"].add(ent.text)
            elif ent.label_ == "MONEY":
                entities["money"].add(ent.text)
            elif ent.label_ in ["GPE", "LOC"]:
                entities["locations"].add(ent.text)
                
        # convert sets to lists
        return {k: list(v) for k, v in entities.items()}
    except Exception as e:
        logger.error(f"spaCy extraction failed: {str(e)}")
        return get_empty_entities()
