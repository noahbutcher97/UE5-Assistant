"""
Main entry point for UE5 AI Assistant.
Supports both sync and async modes.
"""
from typing import Optional

from .action_executor import get_executor
from .api_client import get_client
from .async_client import get_async_client
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
        
        # Auto-register project with backend
        self._auto_register_project()

    def process_command(
        self, user_input: str, use_async: bool = False
    ) -> str:
        """
        Main command processing flow.

        Args:
            user_input: User's command text
            use_async: If True, uses async (non-blocking) execution.
                      If False, uses sync (blocks editor).
                      Default: False (sync is safe for UE thread model)

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

        # Handle UE_REQUEST tokens (direct actions)
        if response.startswith("[UE_REQUEST]"):
            token = response.replace("[UE_REQUEST]", "").strip()
            response = self.executor.execute(token)
        
        # Handle UE_CONTEXT_REQUEST tokens (collect context, send to AI)
        elif response.startswith("[UE_CONTEXT_REQUEST]"):
            parts = response.replace("[UE_CONTEXT_REQUEST]", "").strip()
            context_type, original_question = parts.split("|", 1)
            response = self._process_context_request(
                context_type.strip(),
                original_question.strip()
            )

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

                # Handle UE_REQUEST tokens (direct actions)
                if response.startswith("[UE_REQUEST]"):
                    token = response.replace(
                        "[UE_REQUEST]", ""
                    ).strip()
                    response = self.executor.execute(token)
                
                # Handle UE_CONTEXT_REQUEST tokens (collect, send to AI)
                elif response.startswith("[UE_CONTEXT_REQUEST]"):
                    parts = response.replace(
                        "[UE_CONTEXT_REQUEST]", ""
                    ).strip()
                    context_type, original_question = parts.split("|", 1)
                    response = self._process_context_request(
                        context_type.strip(),
                        original_question.strip()
                    )
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
    
    def _process_context_request(
        self, context_type: str, original_question: str
    ) -> str:
        """
        Collect context and send to AI for natural language processing.
        
        Args:
            context_type: Type of context (e.g., 'project_info')
            original_question: User's original question
        """
        try:
            # Collect appropriate context
            context_data = {}
            
            if context_type == "project_info":
                # Get raw project metadata
                metadata_collector = self.executor.metadata_collector
                context_data = metadata_collector.collect_all_metadata()
            
            elif context_type == "blueprint_capture":
                # Capture blueprint screenshot
                from .blueprint_capture import capture_blueprint_screenshot
                result = capture_blueprint_screenshot()
                if "error" in result:
                    return self.ui.format_error(result["error"])
                context_data = result
            
            elif context_type == "browse_files":
                # Browse project files
                from .action_executor import browse_project_files
                file_tree = browse_project_files()
                context_data = {"file_tree": file_tree}
            
            else:
                return f"[UE_ERROR] Unknown context type: {context_type}"
            
            # Send to AI for interpretation
            api_client = get_client()
            payload = {
                "question": original_question,
                "context": context_data,
                "context_type": context_type
            }
            
            response_data = api_client.post_json(
                "/answer_with_context",
                payload
            )
            
            if response_data.get("error"):
                return self.ui.format_error(response_data["error"])
            
            return response_data.get("response", "")
            
        except Exception as e:
            return self.ui.format_error(
                f"Context request failed: {e}"
            )

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

        return any(keyword in lower for keyword in keywords)

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


    def _auto_register_project(self):
        """Auto-register project on initialization."""
        try:
            from .project_registration import auto_register_project
            result = auto_register_project(self.sync_client)
            if not result.get("success"):
                import unreal
                unreal.log_warning(
                    f"⚠️ Project auto-registration failed: {result.get('error', 'Unknown')}"
                )
                unreal.log_warning(
                    "💡 Run 'import AIAssistant.test_registration' to diagnose"
                )
        except Exception as e:
            import unreal
            unreal.log_error(f"❌ Project auto-registration error: {e}")
            unreal.log_warning(
                "💡 Run 'import AIAssistant.test_registration' to diagnose"
            )


# Global assistant instance
_assistant: Optional[AIAssistant] = None


def get_assistant() -> AIAssistant:
    """Get or create the global AI assistant."""
    global _assistant
    if _assistant is None:
        _assistant = AIAssistant()
    return _assistant


def send_command(user_input: str, use_async: bool = False) -> str:
    """
    Main entry point for Editor Utility Widget.

    Args:
        user_input: The user's command text
        use_async: If True, uses non-blocking async execution.
                   If False (default), blocks editor but is thread-safe.
                   
    IMPORTANT: Async mode has thread safety issues with UE API calls.
    Use sync mode (default) for reliable operation.

    Usage (Recommended - Sync):
        import AIAssistant
        AIAssistant.send_command("what do I see?")
        # Blocks briefly (~15-20s) but all UE API calls are safe
        # Response written to Saved/AIConsole/last_reply.txt

    Usage (Experimental - Async):
        import AIAssistant
        AIAssistant.send_command("what do I see?", use_async=True)
        # Non-blocking but may fail with thread errors
    """
    assistant = get_assistant()
    return assistant.process_command(user_input, use_async=use_async)
