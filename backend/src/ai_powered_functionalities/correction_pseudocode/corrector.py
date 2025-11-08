import json
from backend.src.ai_powered_functionalities.utils.ai_client import GeminiClient
from backend.src.ai_powered_functionalities.correction_pseudocode.prompts import get_correction_prompt
from backend.src.ai_powered_functionalities.models.responses import CodeCorrectionResponse


class CodeCorrector:
    def __init__(self):
        self.gemini_client = GeminiClient()

    async def correct_code(self, code: str, provide_explanation: bool = True) -> CodeCorrectionResponse:
        """Correct Romanian pseudocode using Gemini"""
        messages = get_correction_prompt(code, provide_explanation)

        response = await self.gemini_client.get_completion(messages, temperature=0.2)

        # Parse JSON response
        try:
            # Try to extract JSON from response
            # Gemini sometimes wraps JSON in markdown code blocks
            response_clean = response.strip()
            if response_clean.startswith("```json"):
                response_clean = response_clean[7:]
            if response_clean.startswith("```"):
                response_clean = response_clean[3:]
            if response_clean.endswith("```"):
                response_clean = response_clean[:-3]

            result = json.loads(response_clean.strip())
            return CodeCorrectionResponse(**result)
        except json.JSONDecodeError:
            # Fallback if not valid JSON
            return CodeCorrectionResponse(
                corrected_code=response,
                has_errors=True,
                errors_found=["Could not parse response"],
                explanation=None
            )