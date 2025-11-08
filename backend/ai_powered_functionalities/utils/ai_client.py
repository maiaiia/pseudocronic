import google.generativeai as genai
from backend.ai_powered_functionalities.config import get_settings


class GeminiClient:
    def __init__(self):
        settings = get_settings()
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)

    async def get_completion(self, messages: list, temperature: float = 0.3) -> str:
        """Get completion from Gemini API

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Controls randomness (0.0 to 1.0)
        """
        try:
            # Convert OpenAI-style messages to Gemini format
            prompt = self._convert_messages(messages)

            # Generate response
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                )
            )

            return response.text
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")

    def _convert_messages(self, messages: list) -> str:
        """Convert OpenAI message format to Gemini prompt"""
        prompt_parts = []

        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")

            if role == "system":
                prompt_parts.append(f"Instructions: {content}\n")
            elif role == "user":
                prompt_parts.append(f"User: {content}\n")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}\n")

        return "\n".join(prompt_parts)

    async def get_vision_completion(self, image_data: bytes, prompt: str, temperature: float = 0.3) -> str:
        """Get completion from Gemini with image input

        Args:
            image_data: Image bytes
            prompt: Text prompt
            temperature: Controls randomness
        """
        try:
            # Import PIL for image handling
            from PIL import Image
            import io

            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))

            # Generate response with image
            response = self.model.generate_content(
                [prompt, image],
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                )
            )

            return response.text
        except Exception as e:
            raise Exception(f"Gemini Vision API error: {str(e)}")