"""
Test UE5 client's flexible token extraction logic.

This validates that the UE5 client can correctly extract tokens
from anywhere in AI responses, not just at the start.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ue5_client'))

from AIAssistant.core.main import AIAssistant

def test_token_extraction_from_start():
    """Test token at the start of response (original behavior)."""
    assistant = AIAssistant()
    
    response = "[UE_REQUEST] describe_viewport"
    token_type, token_content, explanatory_text = assistant._extract_token_from_response(response)
    
    assert token_type == "UE_REQUEST"
    assert token_content == "describe_viewport"
    assert explanatory_text == ""

def test_token_extraction_with_explanation():
    """Test token with AI explanation before it."""
    assistant = AIAssistant()
    
    response = "Let me help you with that. [UE_REQUEST] describe_viewport"
    token_type, token_content, explanatory_text = assistant._extract_token_from_response(response)
    
    assert token_type == "UE_REQUEST"
    assert token_content == "describe_viewport"
    assert explanatory_text == "Let me help you with that."

def test_context_token_extraction():
    """Test context request token extraction."""
    assistant = AIAssistant()
    
    response = "To answer that question... [UE_CONTEXT_REQUEST] project_info|What project am I working on?"
    token_type, token_content, explanatory_text = assistant._extract_token_from_response(response)
    
    assert token_type == "UE_CONTEXT_REQUEST"
    assert token_content == "project_info|What project am I working on?"
    assert explanatory_text == "To answer that question..."

def test_context_token_from_start():
    """Test context token at start (original behavior)."""
    assistant = AIAssistant()
    
    response = "[UE_CONTEXT_REQUEST] viewport|Describe what you see"
    token_type, token_content, explanatory_text = assistant._extract_token_from_response(response)
    
    assert token_type == "UE_CONTEXT_REQUEST"
    assert token_content == "viewport|Describe what you see"
    assert explanatory_text == ""

def test_no_token_found():
    """Test response with no token (plain AI response)."""
    assistant = AIAssistant()
    
    response = "Here's some information about Unreal Engine."
    token_type, token_content, explanatory_text = assistant._extract_token_from_response(response)
    
    assert token_type is None
    assert token_content is None
    assert explanatory_text == "Here's some information about Unreal Engine."

def test_multiline_explanation():
    """Test token with multiline explanation."""
    assistant = AIAssistant()
    
    response = """I'll help you with that viewport description.
Let me gather the scene information now.

[UE_REQUEST] describe_viewport"""
    
    token_type, token_content, explanatory_text = assistant._extract_token_from_response(response)
    
    assert token_type == "UE_REQUEST"
    assert token_content == "describe_viewport"
    assert "I'll help you" in explanatory_text
    assert "Let me gather" in explanatory_text

def test_token_with_multiple_words():
    """Test token with multiple words in action."""
    assistant = AIAssistant()
    
    response = "Sure! [UE_REQUEST] list_actors Blueprint"
    token_type, token_content, explanatory_text = assistant._extract_token_from_response(response)
    
    assert token_type == "UE_REQUEST"
    assert token_content == "list_actors Blueprint"
    assert explanatory_text == "Sure!"

if __name__ == "__main__":
    print("Testing UE5 client token extraction...")
    
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
    
    print("\n🎉 All token extraction tests PASSED!")
