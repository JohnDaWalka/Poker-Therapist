"""
OCR Service for hand history screenshots and tracker images
Supports Tesseract (local) and Google Cloud Vision API (cloud)
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
import re

# Optional imports - gracefully degrade if not available
try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logging.warning("pytesseract/PIL not available - Tesseract OCR disabled")

try:
    from google.cloud import vision
    GCV_AVAILABLE = True
except ImportError:
    GCV_AVAILABLE = False
    logging.warning("google-cloud-vision not available - GCV OCR disabled")

logger = logging.getLogger(__name__)


class OCRError(Exception):
    """Custom exception for OCR-related errors."""
    pass


class OCRService:
    """Service for extracting text from poker screenshots using OCR."""
    
    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    
    def __init__(self, engine: str = "auto"):
        """
        Initialize OCR service.
        
        Args:
            engine: OCR engine to use ('tesseract', 'google', 'auto')
                   'auto' tries Google first, falls back to Tesseract
        """
        self.engine = engine
        
        if engine == "tesseract" and not TESSERACT_AVAILABLE:
            raise OCRError("Tesseract not available. Install pytesseract and PIL.")
        
        if engine == "google" and not GCV_AVAILABLE:
            raise OCRError("Google Cloud Vision not available. Install google-cloud-vision.")
        
        if engine == "auto":
            if not TESSERACT_AVAILABLE and not GCV_AVAILABLE:
                raise OCRError("No OCR engine available. Install pytesseract or google-cloud-vision.")
        
        # Initialize GCV client if available
        self.gcv_client = None
        if GCV_AVAILABLE and engine in ["google", "auto"]:
            try:
                self.gcv_client = vision.ImageAnnotatorClient()
                logger.info("Google Cloud Vision client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize GCV client: {e}")
                if engine == "google":
                    raise OCRError(f"Failed to initialize Google Cloud Vision: {e}")
        
        logger.info(f"OCRService initialized with engine: {engine}")
    
    def _validate_image(self, file_path: str) -> Path:
        """Validate image file."""
        path = Path(file_path)
        
        if not path.exists():
            raise OCRError(f"Image not found: {file_path}")
        
        if not path.is_file():
            raise OCRError(f"Path is not a file: {file_path}")
        
        if path.suffix.lower() not in self.SUPPORTED_FORMATS:
            raise OCRError(f"Unsupported format: {path.suffix}")
        
        file_size = path.stat().st_size
        if file_size > self.MAX_FILE_SIZE:
            raise OCRError(f"File too large: {file_size / 1024 / 1024:.2f} MB")
        
        if file_size == 0:
            raise OCRError("Image file is empty")
        
        return path
    
    def extract_text(self, file_path: str, engine: Optional[str] = None) -> Dict[str, Any]:
        """Extract text from image using OCR."""
        image_path = self._validate_image(file_path)
        selected_engine = engine or self.engine
        
        if selected_engine == "auto":
            if self.gcv_client:
                try:
                    return self._extract_with_google(image_path)
                except Exception as e:
                    logger.warning(f"GCV failed, falling back to Tesseract: {e}")
                    if TESSERACT_AVAILABLE:
                        return self._extract_with_tesseract(image_path)
                    raise OCRError("All OCR engines failed")
            elif TESSERACT_AVAILABLE:
                return self._extract_with_tesseract(image_path)
        
        if selected_engine == "google":
            return self._extract_with_google(image_path)
        elif selected_engine == "tesseract":
            return self._extract_with_tesseract(image_path)
        
        raise OCRError(f"Unknown engine: {selected_engine}")
    
    def _extract_with_tesseract(self, image_path: Path) -> Dict[str, Any]:
        """Extract text using Tesseract OCR."""
        if not TESSERACT_AVAILABLE:
            raise OCRError("Tesseract not available")
        
        try:
            logger.info(f"Extracting text with Tesseract: {image_path}")
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            confidences = [int(conf) for conf in data['conf'] if conf != '-1']
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return {
                "text": text.strip(),
                "confidence": avg_confidence / 100.0,
                "engine_used": "tesseract"
            }
        except Exception as e:
            logger.error(f"Tesseract extraction failed: {e}")
            raise OCRError(f"Tesseract failed: {str(e)}")
    
    def _extract_with_google(self, image_path: Path) -> Dict[str, Any]:
        """Extract text using Google Cloud Vision."""
        if not self.gcv_client:
            raise OCRError("Google Cloud Vision not initialized")
        
        try:
            logger.info(f"Extracting text with Google Cloud Vision: {image_path}")
            
            with open(image_path, 'rb') as image_file:
                content = image_file.read()
            
            image = vision.Image(content=content)
            response = self.gcv_client.text_detection(image=image)
            
            if response.error.message:
                raise OCRError(f"GCV API error: {response.error.message}")
            
            texts = response.text_annotations
            if not texts:
                return {
                    "text": "",
                    "confidence": 0.0,
                    "engine_used": "google"
                }
            
            full_text = texts[0].description
            confidence = texts[0].score if hasattr(texts[0], 'score') else 0.9
            
            return {
                "text": full_text.strip(),
                "confidence": confidence,
                "engine_used": "google"
            }
        except Exception as e:
            logger.error(f"Google Cloud Vision failed: {e}")
            raise OCRError(f"GCV failed: {str(e)}")
    
    def parse_hand_history(self, ocr_text: str) -> Dict[str, Any]:
        """Parse poker hand history from OCR text."""
        parsed = {
            "hero_hand": None,
            "villain_hand": None,
            "pot_size": None,
            "actions": [],
            "board": None,
            "stakes": None
        }
        
        text_lower = ocr_text.lower()
        
        hand_pattern = r'\b([AKQJT2-9]{2}[scdho]?)\b'
        hands = re.findall(hand_pattern, ocr_text, re.IGNORECASE)
        if hands:
            parsed["hero_hand"] = hands[0] if len(hands) > 0 else None
            parsed["villain_hand"] = hands[1] if len(hands) > 1 else None
        
        pot_pattern = r'pot[:\s]+\$?(\d+(?:\.\d{2})?)'
        pot_match = re.search(pot_pattern, text_lower)
        if pot_match:
            parsed["pot_size"] = f"${pot_match.group(1)}"
        
        stakes_pattern = r'\$?(\d+)/\$?(\d+)'
        stakes_match = re.search(stakes_pattern, ocr_text)
        if stakes_match:
            parsed["stakes"] = f"${stakes_match.group(1)}/${stakes_match.group(2)}"
        
        action_keywords = ['bet', 'raise', 'call', 'fold', 'check', 'all-in', 'shove']
        for action in action_keywords:
            if action in text_lower:
                parsed["actions"].append(action)
        
        board_pattern = r'board[:\s]+([AKQJT2-9♠♥♦♣scdh\s]+)'
        board_match = re.search(board_pattern, text_lower)
        if board_match:
            parsed["board"] = board_match.group(1).strip()
        
        return parsed
    
    def parse_tracker_stats(self, ocr_text: str) -> Dict[str, Any]:
        """Parse tracker statistics from OCR text."""
        stats = {
            "vpip": None,
            "pfr": None,
            "bb_100": None,
            "hands_played": None,
            "win_rate": None
        }
        
        text_lower = ocr_text.lower()
        
        vpip_pattern = r'vpip[:\s]+(\d+(?:\.\d+)?)'
        vpip_match = re.search(vpip_pattern, text_lower)
        if vpip_match:
            stats["vpip"] = float(vpip_match.group(1))
        
        pfr_pattern = r'pfr[:\s]+(\d+(?:\.\d+)?)'
        pfr_match = re.search(pfr_pattern, text_lower)
        if pfr_match:
            stats["pfr"] = float(pfr_match.group(1))
        
        bb100_pattern = r'bb/100[:\s]+(-?\d+(?:\.\d+)?)'
        bb100_match = re.search(bb100_pattern, text_lower)
        if bb100_match:
            stats["bb_100"] = float(bb100_match.group(1))
        
        hands_pattern = r'hands[:\s]+(\d+(?:,\d+)*)'
        hands_match = re.search(hands_pattern, text_lower)
        if hands_match:
            hands_str = hands_match.group(1).replace(',', '')
            stats["hands_played"] = int(hands_str)
        
        return stats


def extract_text_from_image(file_path: str, engine: str = "auto") -> str:
    """Convenience function to extract text from image."""
    service = OCRService(engine=engine)
    result = service.extract_text(file_path)
    return result["text"]
