import os
import uuid
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from pypdf import PdfReader

class DocumentParser:
    """
    Parses agricultural advisory documents (PDF, TXT, MD) and decomposes them into semantic chunks.
    Extracts metadata: document name, page number, crop, disease, growth stage, source.
    """
    def parse_pdf(self, file_path: str, default_crop: str = "General", source_title: Optional[str] = None) -> List[Dict[str, Any]]:
        chunks: List[Dict[str, Any]] = []
        path = Path(file_path)
        doc_name = path.name
        title = source_title or doc_name.replace("_", " ").replace(".pdf", "").title()
        
        try:
            reader = PdfReader(file_path)
            for page_idx, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                page_num = page_idx + 1
                
                # Split page into logical paragraphs / chunks of ~300-500 words
                raw_paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 40]
                if not raw_paragraphs and text.strip():
                    raw_paragraphs = [text.strip()]

                for p_idx, paragraph in enumerate(raw_paragraphs):
                    crop_tag = self._detect_crop(paragraph, default_crop)
                    disease_tag = self._detect_disease(paragraph)
                    
                    chunks.append({
                        "chunk_id": f"CHK-{uuid.uuid4().hex[:8]}",
                        "document_name": doc_name,
                        "document_title": title,
                        "page_number": page_num,
                        "crop": crop_tag,
                        "disease": disease_tag,
                        "growth_stage": "All stages",
                        "source": f"{doc_name} (p. {page_num})",
                        "content": paragraph
                    })
        except Exception as e:
            print(f"Error parsing PDF {file_path}: {e}")

        return chunks

    def parse_text(self, text_content: str, document_name: str, crop: str = "General") -> List[Dict[str, Any]]:
        chunks: List[Dict[str, Any]] = []
        paragraphs = [p.strip() for p in text_content.split("\n\n") if len(p.strip()) > 30]
        
        for idx, p in enumerate(paragraphs):
            crop_tag = self._detect_crop(p, crop)
            disease_tag = self._detect_disease(p)
            chunks.append({
                "chunk_id": f"CHK-{uuid.uuid4().hex[:8]}",
                "document_name": document_name,
                "document_title": document_name.replace("_", " ").title(),
                "page_number": 1,
                "crop": crop_tag,
                "disease": disease_tag,
                "growth_stage": "Vegetative / Flowering",
                "source": document_name,
                "content": p
            })
        return chunks

    def _detect_crop(self, text: str, default: str) -> str:
        text_lower = text.lower()
        if "tomato" in text_lower:
            return "Tomato"
        elif "chilli" in text_lower or "pepper" in text_lower or "capsicum" in text_lower:
            return "Chilli"
        elif "rice" in text_lower or "paddy" in text_lower:
            return "Rice"
        elif "potato" in text_lower:
            return "Potato"
        elif "cotton" in text_lower:
            return "Cotton"
        return default

    def _detect_disease(self, text: str) -> Optional[str]:
        text_lower = text.lower()
        if "early blight" in text_lower or "alternaria" in text_lower:
            return "Early Blight"
        elif "late blight" in text_lower or "phytophthora" in text_lower:
            return "Late Blight"
        elif "leaf curl" in text_lower or "gemini" in text_lower or "begomovirus" in text_lower:
            return "Leaf Curl Virus"
        elif "blast" in text_lower or "magnaporthe" in text_lower:
            return "Rice Blast"
        elif "bacterial spot" in text_lower:
            return "Bacterial Spot"
        elif "thrips" in text_lower or "mite" in text_lower:
            return "Sucking Pest Complex"
        return None

document_parser = DocumentParser()
