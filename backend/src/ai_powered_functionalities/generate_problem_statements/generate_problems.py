import json
import re
from backend.src.ai_powered_functionalities.generate_problem_statements.prompts import \
    get_problem_generation_prompt
from backend.src.ai_powered_functionalities.models.responses import GenerateProblemStatementResponse
from backend.src.ai_powered_functionalities.utils.ai_client import GeminiClient


class GenerateProblem:
    def __init__(self):
        self.__gemini_client = GeminiClient()

    async def generate_problem(self) -> GenerateProblemStatementResponse:
        """Generate a new programming problem statement"""
        messages = get_problem_generation_prompt()
        response = await self.__gemini_client.get_completion(messages, temperature=0.7)  # Higher temp for creativity

        # Clean the response
        response_clean = self._extract_json(response)

        try:
            result = json.loads(response_clean)
            return GenerateProblemStatementResponse(**result)
        except json.JSONDecodeError as e:
            print(f"JSON Decode Error: {e}")
            print(f"Raw response: {response}")
            print(f"Cleaned response: {response_clean}")

            # Fallback response
            return GenerateProblemStatementResponse(
                enunt="Eroare la generarea problemei. Te rugăm să încerci din nou.",
                date_intrare="N/A",
                date_iesire="N/A",
                exemplu_intrare="N/A",
                exemplu_iesire="N/A",
                nivel_dificultate="N/A"
            )

    def _extract_json(self, response: str) -> str:
        """Extract JSON from response, handling various formats"""
        response_clean = response.strip()

        # Method 1: Try to extract from code fences (```json ... ```)
        code_fence_match = re.search(
            r"```(?:json)?\s*(.*?)\s*```",
            response_clean,
            re.DOTALL | re.IGNORECASE
        )
        if code_fence_match:
            response_clean = code_fence_match.group(1).strip()

        # Method 2: Find JSON object boundaries
        # Find first { and last }
        first_brace = response_clean.find("{")
        last_brace = response_clean.rfind("}")

        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            response_clean = response_clean[first_brace:last_brace + 1]

        return response_clean