"""
LLM Service Module

Reusable Groq API wrapper for AI-powered responses.
Used by planner, chat, and context modules.
"""

import json
import os
import re
from typing import Any, Dict

from dotenv import load_dotenv
from groq import Groq


class GroqService:
    """
    Groq LLM service for generating text and JSON responses.

    Loads configuration from environment variables:
    - GROQ_API_KEY: API key for Groq
    - GROQ_MODEL: Model name (default: llama-3.3-70b-versatile)
    """

    def __init__(self) -> None:
        """
        Initialize the Groq service.

        Loads environment variables and creates Groq client.
        Raises ValueError if API key is missing.
        """
        load_dotenv()

        self.api_key = os.getenv("GROQ_API_KEY")
        self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")

        self.client = Groq(api_key=self.api_key)

    def _extract_json(self, text: str) -> Dict[str, Any]:
        """
        Safely extract JSON from LLM response text.

        Handles cases where response includes extra text, markdown, or formatting.

        Args:
            text: Raw response text from LLM

        Returns:
            Parsed JSON dictionary

        Raises:
            ValueError: If no valid JSON can be extracted
        """
        text = text.strip()
        if not text:
            raise ValueError("Empty response text")

        # Try direct JSON parsing
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try to extract from markdown code block
        json_match = re.search(r'```json\s*\n?(.*?)\n?```', text, re.DOTALL | re.IGNORECASE)
        if json_match:
            try:
                return json.loads(json_match.group(1).strip())
            except json.JSONDecodeError:
                pass

        # Try to find JSON object between first { and last }
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start:end+1])
            except json.JSONDecodeError:
                pass

        raise ValueError("Could not extract valid JSON from LLM response")

    def generate_response(self, prompt: str) -> str:
        """
        Generate a text response from the LLM.

        Args:
            prompt: The input prompt for the LLM

        Returns:
            Clean text response from the LLM

        Raises:
            Exception: If API call fails or response is invalid
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1024
            )

            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from LLM")

            return content.strip()

        except Exception as e:
            raise Exception(f"Failed to generate response: {str(e)}")

    def generate_json_response(self, prompt: str) -> Dict[str, Any]:
        """
        Generate a JSON response from the LLM and parse it safely.

        Automatically prepends strict JSON instructions to the prompt.
        Handles extra text, markdown, and malformed responses.

        Args:
            prompt: The input prompt for the LLM (should request JSON)

        Returns:
            Parsed JSON response as dictionary

        Raises:
            ValueError: If response cannot be parsed as valid JSON
            Exception: If API call fails
        """
        # Prepend strict JSON instructions
        strict_prompt = (
            "You must return ONLY valid JSON.\n"
            "Do not include explanations, markdown, comments, or extra text.\n\n"
            f"{prompt}"
        )

        try:
            response_text = self.generate_response(strict_prompt)

            if not response_text:
                raise ValueError("Empty response from LLM")

            # Extract and parse JSON safely
            return self._extract_json(response_text)

        except ValueError as e:
            raise ValueError(f"JSON parsing failed: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to generate JSON response: {str(e)}")


# Local test block
if __name__ == "__main__":
    try:
        service = GroqService()

        # Test simple text response
        print("Testing simple response...")
        simple_response = service.generate_response("Hello, how are you?")
        print(f"Simple response: {simple_response}")

        # Test JSON response
        print("\nTesting JSON response...")
        json_prompt = 'Return a JSON object with keys "name" and "age".'
        json_response = service.generate_json_response(json_prompt)
        print(f"JSON response: {json_response}")

    except Exception as e:
        print(f"Test failed: {str(e)}")