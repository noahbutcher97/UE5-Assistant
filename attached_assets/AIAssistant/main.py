"""
Main entry point for UE5 AI Assistant.
Supports both sync and async modes.
"""
import time
from typing import Optional

from .api_client import get_client
from .async_client import get_async_client
from .action_executor import get_executor
from .config import get_config
from .ui_manager import get_ui_manager
from .utils import Logger


class AIAssistant:
    """Main AI Assistant orchestrator."""

    def __init__(self):
        self.config = get_config()
        self.sync_client = get_client()
        self.async_client = get_async_client()
        self.executor = get_executor()
        self.ui = get_ui_manager()
        self.logger = Logger("AIAssistant", self.config.verbose)

        # Conversation memory
        self.session_messages = [
            {
                "role": "system",
                "content": (
                    "You are a technical documentation system "
                    "for Unreal Engine 5.6. Generate structured "
                    "technical prose describing editor state and "
                    "scene contents. Use precise terminology, "
                    "include specific names and values, connect "
                    "information logically. Write in third-person "
                    "declarative style. Avoid conversational "
                    "phrasing, questions, or subjective language."
                ),
            }
        ]

        # Async state
        self._async_response: Optional[str] = None
        self._async_in_progress = False

    def process_command(
        self, user_input: str, use_async: bool = True
    ) -> str:
        """
        Main command processing flow.

        Args:
            user_input: User's command text
            use_async: If True, uses async (non-blocking) execution.
                      If False, uses sync (blocks editor).

        Returns:
            Response text (or status if async)
        """
        try:
            # Show thinking state
            self.ui.show_thinking()

            # Log user input
            self.logger.info(f"User: {user_input}")

            # Check for tokenized actions (always sync)
            if self._is_action_request(user_input):
                token = self._extract_action_token(user_input)
                response = self.executor.execute(token)
                self.ui.show_response(response)
                self.ui.log_exchange(user_input, response)
                return response

            # Process with AI
            if use_async:
                return self._process_async(user_input)
            else:
                return self._process_sync(user_input)

        except Exception as e:
            error_msg = self.ui.format_error(str(e))
            self.ui.show_response(error_msg)
            self.logger.error(f"Command failed: {e}")
            return error_msg

    def _process_sync(self, user_input: str) -> str:
        """
        Synchronous processing (blocks editor).
        Use for quick commands only.
        """
        response = self._process_with_ai_sync(user_input)

        # Handle UE_REQUEST tokens
        if response.startswith("[UE_REQUEST]"):
            token = response.replace("[UE_REQUEST]", "").strip()
            response = self.executor.execute(token)

        self.ui.show_response(response)
        self.ui.log_exchange(user_input, response)
        return response

    def _process_async(self, user_input: str) -> str:
        """
        Asynchronous processing (non-blocking).
        Returns immediately, response written to file when ready.
        """
        if self._async_in_progress:
            return "⏳ Previous request still processing..."

        self._async_in_progress = True
        self._async_response = None

        # Add user message to history
        self.session_messages.append(
            {"role": "user", "content": user_input}
        )

        # Trim history if too long
        self._trim_history()

        # Define callback
        def on_complete(response_data: dict):
            try:
                response = response_data.get("response", "")

                if not response:
                    error = response_data.get(
                        "error", "Unknown error"
                    )
                    response = self.ui.format_error(error)

                # Handle UE_REQUEST tokens
                if response.startswith("[UE_REQUEST]"):
                    token = response.replace(
                        "[UE_REQUEST]", ""
                    ).strip()
                    response = self.executor.execute(token)
                else:
                    # Add to history
                    self.session_messages.append(
                        {"role": "assistant", "content": response}
                    )

                # Write response
                self.ui.show_response(response)
                self.ui.log_exchange(user_input, response)

                self._async_response = response
                self._async_in_progress = False
                self.logger.success("Async command completed")

            except Exception as e:
                error_msg = self.ui.format_error(str(e))
                self.ui.show_response(error_msg)
                self._async_in_progress = False
                self.logger.error(f"Async callback failed: {e}")

        # Start async request
        url = self.config.execute_endpoint
        payload = {"prompt": user_input}
        self.async_client.post_json_async(
            url, payload, on_complete
        )

        return "⏳ Processing... (async mode)"

    def _process_with_ai_sync(self, user_input: str) -> str:
        """Send input to AI backend synchronously."""
        # Add user message to history
        self.session_messages.append(
            {"role": "user", "content": user_input}
        )

        # Trim history
        self._trim_history()

        # Send to API (blocking)
        response_data = self.sync_client.execute_command(user_input)

        # Extract response
        response = response_data.get("response", "")

        if not response:
            error = response_data.get("error", "Unknown error")
            return self.ui.format_error(error)

        # Add AI response to history
        if not response.startswith("[UE_REQUEST]"):
            self.session_messages.append(
                {"role": "assistant", "content": response}
            )

        return response

    def _trim_history(self) -> None:
        """Trim conversation history to max turns."""
        max_turns = self.config.get("max_context_turns", 6)
        user_assistant_msgs = [
            m
            for m in self.session_messages
            if m["role"] != "system"
        ]

        if len(user_assistant_msgs) > max_turns * 2:
            self.session_messages = (
                self.session_messages[:1]
                + user_assistant_msgs[-(max_turns * 2) :]
            )

    def _is_action_request(self, text: str) -> bool:
        """Check if input directly requests a known action."""
        lower = text.lower()
        keywords = {
            "viewport": "describe_viewport",
            "what do i see": "describe_viewport",
            "describe scene": "describe_viewport",
            "list actors": "list_actors",
            "selected": "get_selected_info",
        }

        for keyword in keywords:
            if keyword in lower:
                return True
        return False

    def _extract_action_token(self, text: str) -> str:
        """Extract action token from user input."""
        lower = text.lower()

        if any(
            k in lower
            for k in ["viewport", "what do i see", "describe"]
        ):
            return "describe_viewport"
        elif "list actors" in lower:
            return "list_actors"
        elif "selected" in lower:
            return "get_selected_info"

        return ""


# Global assistant instance
_assistant: Optional[AIAssistant] = None


def get_assistant() -> AIAssistant:
    """Get or create the global AI assistant."""
    global _assistant
    if _assistant is None:
        _assistant = AIAssistant()
    return _assistant


def send_command(user_input: str, use_async: bool = True) -> str:
    """
    Main entry point for Editor Utility Widget.

    Args:
        user_input: The user's command text
        use_async: If True (default), uses non-blocking async execution.
                   If False, blocks the editor until complete.

    Usage (Async - Recommended):
        import AIAssistant
        AIAssistant.send_command("what do I see?")
        # Returns immediately with "Processing..."
        # Response written to Saved/AIConsole/last_reply.txt when ready

    Usage (Sync - Simple but blocks):
        import AIAssistant
        response = AIAssistant.send_command(
            "what do I see?", use_async=False
        )
        # Editor freezes until response arrives
    """
    assistant = get_assistant()
    return assistant.process_command(user_input, use_async=use_async)
