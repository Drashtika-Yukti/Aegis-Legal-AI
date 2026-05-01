import spacy
import uuid
import re
from typing import Dict

class PrivacyVault:
    """
    Production-grade PII masking via local spaCy NER.
    """
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            self.nlp = None
            
        self.mapping: Dict[str, str] = {}
        self.pii_labels = {"PERSON", "ORG", "GPE", "DATE"}
        self.id_pattern = re.compile(r'\b[A-Z0-9-]{5,}\b')

    def mask(self, text: str) -> str:
        if not text or not self.nlp:
            return text
            
        masked_text = text
        doc = self.nlp(text)
        
        # 1. NER Masking
        for ent in reversed(doc.ents):
            if ent.label_ in self.pii_labels:
                placeholder = self._get_placeholder(ent.text, ent.label_)
                masked_text = masked_text[:ent.start_char] + placeholder + masked_text[ent.end_char:]

        # 2. Pattern Masking
        matches = self.id_pattern.findall(masked_text)
        for match in set(matches):
            if "_" not in match: # Skip already masked
                placeholder = self._get_placeholder(match, "ID")
                masked_text = masked_text.replace(match, placeholder)

        return masked_text

    def _get_placeholder(self, original: str, label: str) -> str:
        # Check if already mapped
        for p, v in self.mapping.items():
            if v == original: return p
        
        placeholder = f"<{label}_{uuid.uuid4().hex[:4].upper()}>"
        self.mapping[placeholder] = original
        return placeholder

    def unmask(self, text: str) -> str:
        unmasked_text = text
        for p, v in self.mapping.items():
            bare_id = p.strip("<>")
            pattern = re.compile(f"<{bare_id}>|{bare_id}")
            unmasked_text = pattern.sub(v, unmasked_text)
        return unmasked_text

    def reset(self):
        self.mapping = {}

vault = PrivacyVault()
