"""
Test token extraction logic in isolation (no UE5 dependencies).

This validates the regex pattern matching for token extraction
without requiring the full AIAssistant initialization.
"""
import re

def extract_token_from_response(response: str) -> tuple:
    """
    Extract action tokens from anywhere in the response.
    
    Returns:
        (token_type, token_content, explanatory_text)
        token_type: "UE_REQUEST" | "UE_CONTEXT_REQUEST" | None
        token_content: The extracted token string
        explanatory_text: AI explanation text (if any)
    """
    # Check for UE_REQUEST token
    ue_request_match = re.search(r'\[UE_REQUEST\]\s*(\S+(?:\s+\S+)*?)(?=\s*\[|$)', response)
    if ue_request_match:
        token_content = ue_request_match.group(1).strip()
        # Extract any explanatory text before the token
        explanatory_text = response[:ue_request_match.start()].strip()
        return ("UE_REQUEST", token_content, explanatory_text)
    
    # Check for UE_CONTEXT_REQUEST token
    context_match = re.search(r'\[UE_CONTEXT_REQUEST\]\s*([^[]+?)(?=\s*\[|$)', response)
    if context_match:
        token_content = context_match.group(1).strip()
        explanatory_text = response[:context_match.start()].strip()
        return ("UE_CONTEXT_REQUEST", token_content, explanatory_text)
    
    # No token found
    return (None, None, response)

def test_token_extraction_from_start():
    """Test token at the start of response (original behavior)."""
    response = "[UE_REQUEST] describe_viewport"
    token_type, token_content, explanatory_text = extract_token_from_response(response)
    
    assert token_type == "UE_REQUEST", f"Expected UE_REQUEST, got {token_type}"
    assert token_content == "describe_viewport", f"Expected 'describe_viewport', got '{token_content}'"
    assert explanatory_text == "", f"Expected empty string, got '{explanatory_text}'"

def test_token_extraction_with_explanation():
    """Test token with AI explanation before it."""
    response = "Let me help you with that. [UE_REQUEST] describe_viewport"
    token_type, token_content, explanatory_text = extract_token_from_response(response)
    
    assert token_type == "UE_REQUEST"
    assert token_content == "describe_viewport"
    assert explanatory_text == "Let me help you with that."

def test_context_token_extraction():
    """Test context request token extraction."""
    response = "To answer that question... [UE_CONTEXT_REQUEST] project_info|What project am I working on?"
    token_type, token_content, explanatory_text = extract_token_from_response(response)
    
    assert token_type == "UE_CONTEXT_REQUEST"
    assert token_content == "project_info|What project am I working on?"
    assert explanatory_text == "To answer that question..."

def test_context_token_from_start():
    """Test context token at start (original behavior)."""
    response = "[UE_CONTEXT_REQUEST] viewport|Describe what you see"
    token_type, token_content, explanatory_text = extract_token_from_response(response)
    
    assert token_type == "UE_CONTEXT_REQUEST"
    assert token_content == "viewport|Describe what you see"
    assert explanatory_text == ""

def test_no_token_found():
    """Test response with no token (plain AI response)."""
    response = "Here's some information about Unreal Engine."
    token_type, token_content, explanatory_text = extract_token_from_response(response)
    
    assert token_type is None
    assert token_content is None
    assert explanatory_text == "Here's some information about Unreal Engine."

def test_multiline_explanation():
    """Test token with multiline explanation."""
    response = """I'll help you with that viewport description.
Let me gather the scene information now.

[UE_REQUEST] describe_viewport"""
    
    token_type, token_content, explanatory_text = extract_token_from_response(response)
    
    assert token_type == "UE_REQUEST"
    assert token_content == "describe_viewport"
    assert "I'll help you" in explanatory_text
    assert "Let me gather" in explanatory_text

def test_token_with_multiple_words():
    """Test token with multiple words in action."""
    response = "Sure! [UE_REQUEST] list_actors Blueprint"
    token_type, token_content, explanatory_text = extract_token_from_response(response)
    
    assert token_type == "UE_REQUEST"
    assert token_content == "list_actors Blueprint"
    assert explanatory_text == "Sure!"

def test_real_openai_style_response():
    """Test response that mirrors actual OpenAI output."""
    response = "To determine which project you are working on, I need to check the project information. [UE_CONTEXT_REQUEST] project_info|What project am I working on?"
    token_type, token_content, explanatory_text = extract_token_from_response(response)
    
    assert token_type == "UE_CONTEXT_REQUEST"
    assert "project_info|" in token_content
    assert "To determine" in explanatory_text

if __name__ == "__main__":
    print("Testing token extraction logic...")
    
    test_token_extraction_from_start()
    print("✅ Token at start: PASSED")
    
    test_token_extraction_with_explanation()
    print("✅ Token with explanation: PASSED")
    
    test_context_token_extraction()
    print("✅ Context token with explanation: PASSED")
    
    test_context_token_from_start()
    print("✅ Context token at start: PASSED")
    
    test_no_token_found()
    print("✅ No token found: PASSED")
    
    test_multiline_explanation()
    print("✅ Multiline explanation: PASSED")
    
    test_token_with_multiple_words()
    print("✅ Token with multiple words: PASSED")
    
    test_real_openai_style_response()
    print("✅ Real OpenAI-style response: PASSED")
    
    print("\n🎉 All token extraction tests PASSED!")
