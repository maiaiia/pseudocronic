from ..utils.ai_client import GeminiClient
from ..models.responses import OCRResponse


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
4. Asigură-te că simbolurile speciale sunt corecte: <-, !=, <=, >=; sageata fa-o ca semnul mai mic < si minus -; asa: <-
5. Nu păstra structurile: ┌, │, └ pentru blocuri de cod

Uite niste exemple pertinente de cum ar trebui sa arate codul extras:

exemplu 1:
citeste n\ndaca n % 2 = 0 atunci\n  scrie "Numar par"\naltfel\n    scrie "Numar impar"\nsfarsit_daca
exemplu 2:
citeste n\ns <- 0\npentru i <- 1, n executa\n   s <- s + i\nsfarsit_pentru\nscrie s
exemplu 3:
citeste n\nm <- n\nogl <- 0\ncat timp m > 0 executa\n    cifra <- m % 10\n    ogl <- ogl * 10 + cifra\n    m <- [m / 10]\nsfarsit_cat_timp\ndaca ogl = n atunci\n    scrie "Palindrom"\naltfel\n    scrie "Nu e palindrom"\nsfarsit_daca
exemplu 4:
citeste x\ncat timp x > 5 executa\n    x <- x - 1\n    daca x = 7 atunci\n        scrie \"Sapte\"\n    sfarsit_daca\nsfarsit_cat_timp
exemplu 5:
repeta\n    i <- i + 1\n    scrie i\npana cand i >= 10

Transforma ; in backslash n
Returnează codul curat, gata de utilizare.
"""

        # Extract text using Gemini Vision
        extracted_text = await self.gemini_client.get_vision_completion(
            image_data=image_bytes,
            prompt=prompt,
            temperature=0.1
        )

        return OCRResponse(
            extracted_text=extracted_text.strip().replace("```",""),
            confidence="high",
            preprocessing_applied=["Gemini Vision extraction"]
        )