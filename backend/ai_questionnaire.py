"""
ProduGen - AI Questionnaire Module
Uses Google Gemini API to conduct an intelligent product interview.
"""

import json
from google import genai
from google.genai import types
from backend.config import Config
from backend.prompts import QUESTIONNAIRE_SYSTEM_PROMPT


class AIQuestionnaire:
    """
    Manages an AI-driven conversation to gather product details
    from a business owner. Uses Google Gemini as the chat engine.
    """

    def __init__(self):
        """Initialize the Gemini client and configure the API."""
        if not Config.GEMINI_API_KEY or Config.GEMINI_API_KEY == "your_gemini_api_key_here":
            raise ValueError(
                "Gemini API key not configured. "
                "Get a free key at https://aistudio.google.com/apikey "
                "and add it to your .env file."
            )

        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
        self.model_name = "gemini-2.0-flash"

    def start_session(self) -> dict:
        """
        Start a new questionnaire session.

        Returns:
            dict with session chat object and the AI's greeting message.
        """
        chat = self.client.chats.create(
            model=self.model_name,
            config=types.GenerateContentConfig(
                system_instruction=QUESTIONNAIRE_SYSTEM_PROMPT,
            ),
        )

        # Get the AI's opening greeting/question
        response = chat.send_message(
            "Start the product photography consultation. "
            "Greet the user and ask your first question."
        )

        return {
            "chat": chat,
            "message": response.text,
            "history": [
                {"role": "assistant", "content": response.text}
            ],
            "brief": None,
            "is_complete": False,
        }

    def send_message(self, session: dict, user_message: str) -> dict:
        """
        Send a user message to the AI and get the next response.

        Args:
            session: The session dict from start_session or previous send_message
            user_message: The user's answer/message

        Returns:
            Updated session dict with the AI's response.
        """
        chat = session["chat"]

        # Send user message and get AI response
        response = chat.send_message(user_message)
        ai_message = response.text

        # Update history
        session["history"].append({"role": "user", "content": user_message})
        session["history"].append({"role": "assistant", "content": ai_message})

        # Check if the AI has completed the questionnaire
        # (it will include a JSON brief when done)
        brief = self._extract_brief(ai_message)
        if brief:
            session["brief"] = brief
            session["is_complete"] = True

        return {
            "chat": chat,
            "message": ai_message,
            "history": session["history"],
            "brief": session["brief"],
            "is_complete": session["is_complete"],
        }

    def _extract_brief(self, message: str) -> dict | None:
        """
        Try to extract a JSON generation brief from the AI's message.
        The AI wraps the brief in ```json``` markers when the questionnaire
        is complete.

        Args:
            message: The AI's response text

        Returns:
            Parsed brief dict if found, None otherwise.
        """
        try:
            # Look for JSON block in the message
            if "```json" in message:
                json_start = message.index("```json") + 7
                json_end = message.index("```", json_start)
                json_str = message[json_start:json_end].strip()
                brief = json.loads(json_str)

                # Validate the brief has required fields
                if brief.get("status") == "complete" and brief.get("product_name"):
                    return brief

            return None
        except (ValueError, json.JSONDecodeError):
            return None


# =============================================================================
# Standalone test
# =============================================================================
if __name__ == "__main__":
    print("=" * 50)
    print("🤖 ProduGen AI Questionnaire - Test Mode")
    print("=" * 50)
    print("Type your answers. Type 'quit' to exit.\n")

    try:
        questionnaire = AIQuestionnaire()
    except ValueError as e:
        print(f"❌ Error: {e}")
        exit(1)

    # Start a session
    session = questionnaire.start_session()
    print(f"🤖 AI: {session['message']}\n")

    while not session["is_complete"]:
        user_input = input("👤 You: ").strip()
        if user_input.lower() == "quit":
            print("\n👋 Goodbye!")
            break

        session = questionnaire.send_message(session, user_input)
        print(f"\n🤖 AI: {session['message']}\n")

    if session["is_complete"]:
        print("\n" + "=" * 50)
        print("✅ Questionnaire Complete! Generation Brief:")
        print("=" * 50)
        print(json.dumps(session["brief"], indent=2))
