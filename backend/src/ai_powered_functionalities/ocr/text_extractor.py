from backend.src.ai_powered_functionalities.utils.ai_client import GeminiClient
from backend.src.ai_powered_functionalities.models.responses import OCRResponse


class TextExtractor:
    def __init__(self):
        self.gemini_client = GeminiClient()

    async def extract_and_clean(self, image_bytes: bytes) -> OCRResponse:
        """Extract text from image using Gemini Vision"""

        prompt = """Extrage textul pseudocod românesc din această imagine.

Reguli:
1. Returnează DOAR codul pseudocod, fără explicații
2. Păstrează formatarea și structura exactă
3. Corectează eventualele erori de recunoaștere
4. Asigură-te că simbolurile speciale sunt corecte: ←, ≠, ≤, ≥
5. Nu păstra structurile: ┌, │, └ pentru blocuri de cod

Returnează codul curat, gata de utilizare."""

        # Extract text using Gemini Vision
        extracted_text = await self.gemini_client.get_vision_completion(
            image_data=image_bytes,
            prompt=prompt,
            temperature=0.1
        )

        return OCRResponse(
            extracted_text=extracted_text.strip(),
            confidence="high",
            preprocessing_applied=["Gemini Vision extraction"]
        )