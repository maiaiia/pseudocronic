import json
import re
from ..utils.ai_client import GeminiClient
from ..correction_pseudocode.prompts import get_correction_prompt
from ..models.responses import CodeCorrectionResponse


class CodeCorrector:
    def __init__(self):
        self.gemini_client = GeminiClient()

    async def correct_code(self, code: str) -> CodeCorrectionResponse:
        """Correct Romanian pseudocode using Gemini"""
        messages = get_correction_prompt(code)

        response = await self.gemini_client.get_completion(messages, temperature=0.2)

        # --- Clean and extract JSON safely ---
        response_clean = response.strip()

        # Regex to extract JSON inside code fences (handles ```json, ```JSON, etc.)
        code_fence_match = re.search(r"```(?:json)?\s*(.*?)\s*```", response_clean, re.DOTALL | re.IGNORECASE)
        if code_fence_match:
            response_clean = code_fence_match.group(1).strip()

        # If still wrapped in backticks or extra text, try to find first valid JSON object
        if not response_clean.startswith("{") and "{" in response_clean:
            response_clean = response_clean[response_clean.index("{"):]

        if not response_clean.endswith("}") and "}" in response_clean:
            response_clean = response_clean[:response_clean.rindex("}") + 1]

        # --- Try to parse as JSON ---
        try:
            result = json.loads(response_clean)
            return CodeCorrectionResponse(**result)
        except json.JSONDecodeError:
            return CodeCorrectionResponse(
                corrected_code=response,
                has_errors=True,
                errors_found=["Could not parse JSON response"],
                explanation=None
            )
