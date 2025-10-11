"""Conversation history storage with file-based persistence."""
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

CONVERSATIONS_FILE = Path("conversations.jsonl")
MAX_HISTORY_SIZE = 100

# In-memory conversation ring buffer
conversation_history: List[Dict[str, Any]] = []


def load_conversations() -> None:
    """Load conversation history from file on startup."""
    global conversation_history
    if not CONVERSATIONS_FILE.exists():
        return
    
    try:
        with open(CONVERSATIONS_FILE, 'r', encoding='utf-8') as f:
            all_conversations = [json.loads(line) for line in f if line.strip()]
            conversation_history = all_conversations[-MAX_HISTORY_SIZE:]
        print(f"[Startup] Loaded {len(conversation_history)} conversations from file")
    except Exception as e:
        print(f"[Error] Failed to load conversations: {e}")
        conversation_history = []


def add_to_history(
    user_input: str,
    response: str,
    cmd_type: str,
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """Add a conversation entry to history and persist to file."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_input": user_input,
        "assistant_response": response,
        "command_type": cmd_type,
        "metadata": metadata or {}
    }
    conversation_history.append(entry)
    
    # Keep only last MAX_HISTORY_SIZE entries in memory
    if len(conversation_history) > MAX_HISTORY_SIZE:
        conversation_history.pop(0)
    
    # Append to file (persist forever)
    try:
        with open(CONVERSATIONS_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    except Exception as e:
        print(f"[Error] Failed to persist conversation: {e}")


def get_history(limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """Get conversation history."""
    if limit is None:
        return conversation_history
    return conversation_history[-limit:]


def clear_history() -> None:
    """Clear all conversation history."""
    global conversation_history
    conversation_history = []
    
    # Clear the file
    if CONVERSATIONS_FILE.exists():
        CONVERSATIONS_FILE.unlink()
