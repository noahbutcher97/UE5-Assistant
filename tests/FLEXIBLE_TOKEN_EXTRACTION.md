# Flexible Token Extraction System

## Overview
The UE5 client now supports **flexible token extraction**, allowing it to detect and process action tokens from anywhere in AI responses, not just at the start. This makes the system more robust and user-friendly by supporting natural AI explanations alongside action tokens.

## How It Works

### Previous Behavior (Rigid)
```python
# Old: Token MUST be at start of response
if response.startswith("[UE_REQUEST]"):
    token = response.replace("[UE_REQUEST]", "").strip()
    execute(token)
```

**Problem:** If AI returns `"Let me help. [UE_REQUEST] describe_viewport"`, the token is NOT detected.

### New Behavior (Flexible)
```python
# New: Token can be ANYWHERE in response
token_type, token_content, explanatory_text = extract_token_from_response(response)
if token_type == "UE_REQUEST":
    execute(token_content)
    # Prepend AI explanation to result
```

**Solution:** Regex patterns find tokens anywhere, preserve AI explanations.

## Token Extraction Patterns

### UE_REQUEST Pattern
```regex
\[UE_REQUEST\]\s*([^\.\!\?\n\[]+?)(?=[\.\!\?\n\[]|$)
```

**Stops at:** Period, exclamation, question mark, newline, or bracket

**Matches:**
- `[UE_REQUEST] describe_viewport` → `describe_viewport`
- `Let me help. [UE_REQUEST] describe_viewport` → `describe_viewport`
- `[UE_REQUEST] list_actors Blueprint` → `list_actors Blueprint`
- `[UE_REQUEST] describe_viewport. Thanks!` → `describe_viewport` ✅ (excludes trailing text)

### UE_CONTEXT_REQUEST Pattern
```regex
\[UE_CONTEXT_REQUEST\]\s*([^\n\[]+?)(?=[\.\!]\s+|[\?]\s+[A-Z]|[\?]\s+[a-z]{2,}|\n|\[|$)
```
Then appends `?` if present at boundary (questions end with `?`)

**Stops at:** 
- Period or exclamation followed by space (sentence boundary)
- Question mark followed by new sentence (space + capital/lowercase word)
- Newline or bracket
- End of string

**Key Behavior:**
- **Includes `?`** at end of questions (natural ending)
- **Excludes `.` or `!`** at sentence boundaries (not part of question)

**Matches:**
- `[UE_CONTEXT_REQUEST] project_info|What project?` → `project_info|What project?` ✅ (includes ?)
- `[UE_CONTEXT_REQUEST] project_info|What project. Let me check` → `project_info|What project` ✅ (excludes . before new sentence)
- `[UE_CONTEXT_REQUEST] project_info|What project? Let me help` → `project_info|What project?` ✅ (includes ?, excludes trailing text)
- `To answer that... [UE_CONTEXT_REQUEST] viewport|Describe scene?` → `viewport|Describe scene?` ✅

## Response Flow Examples

### Example 1: Clean Token (Keyword Routing)
**Backend Response:**
```json
{
  "success": true,
  "response": "[UE_REQUEST] describe_viewport"
}
```

**UE5 Client Processing:**
1. Extract: `token_type="UE_REQUEST"`, `token_content="describe_viewport"`, `explanatory_text=""`
2. Execute: `describe_viewport`
3. Return: Action result (no prepended text)

### Example 2: Mixed Text + Token (OpenAI Response)
**Backend Response:**
```json
{
  "success": true,
  "response": "Let me gather viewport information for you.\n\n[UE_REQUEST] describe_viewport"
}
```

**UE5 Client Processing:**
1. Extract: `token_type="UE_REQUEST"`, `token_content="describe_viewport"`, `explanatory_text="Let me gather viewport information for you."`
2. Execute: `describe_viewport`
3. Return: `"Let me gather viewport information for you.\n\n<action_result>"`

### Example 3: Context Request with Explanation
**Backend Response:**
```json
{
  "success": true,
  "response": "To find out your project details, I'll collect that information.\n\n[UE_CONTEXT_REQUEST] project_info|What project am I working on?"
}
```

**UE5 Client Processing:**
1. Extract: `token_type="UE_CONTEXT_REQUEST"`, `token_content="project_info|What project am I working on?"`, `explanatory_text="To find out your project details..."`
2. Parse: `context_type="project_info"`, `original_question="What project am I working on?"`
3. Collect context from UE5
4. Send to backend `/answer_with_context`
5. Return: `"To find out your project details...\n\n<AI_answer_with_context>"`

## Testing Strategy

### Standalone Token Extraction Tests
**File:** `tests/test_token_extraction_standalone.py`

**Coverage (15 tests):**
- Token at start of response ✅
- Token with explanation before it ✅
- Context tokens with/without explanation ✅
- Multiline explanations ✅
- Multiple-word action tokens ✅
- No token found (plain AI response) ✅
- Real OpenAI-style responses ✅
- **Trailing text handling:**
  - Token with trailing period ✅
  - Token with trailing exclamation ✅
  - Token with trailing question ✅
  - Token with trailing newline ✅
  - Context token with trailing text (period) ✅
  - Context token with trailing text (question) ✅
  - Context token with lowercase continuation ✅

**Run:** `python tests/test_token_extraction_standalone.py`

### Production Backend Tests
**File:** `tests/backend/test_token_routing_production.py`

**Coverage:**
- 22 deterministic tests with mocked OpenAI
- Keyword routing (clean tokens) ✅
- OpenAI integration (mixed text + tokens) ✅
- Round-trip flows (dashboard → backend → UE5 → backend) ✅
- Error handling ✅

**Run:** `pytest tests/backend/test_token_routing_production.py`

## Real System Validation

### Actual Backend Behavior
```bash
# Test: "What project am I working on?"
# Backend returns:
{
  "success": true,
  "response": "To find out the details of your current project, I will gather the necessary information. Please allow me a moment. \n\n[UE_REQUEST] get_project_info"
}
```

### UE5 Client Handles It Correctly
1. Regex extracts token `get_project_info` from anywhere
2. Preserves explanation text
3. Executes action
4. Returns friendly response with explanation

## Benefits

### User Experience
- **Natural AI Responses:** AI can explain what it's doing before executing actions
- **Context Preservation:** Explanations are shown to users alongside results
- **Backward Compatible:** Clean token-only responses still work perfectly

### System Robustness
- **Flexible Parsing:** No strict formatting requirements for AI responses
- **Error Resilience:** Works even if OpenAI adds preambles or context
- **Deterministic Testing:** Mocked responses mirror real AI behavior

### Developer Experience
- **Easy to Test:** Standalone regex tests validate extraction logic
- **Predictable Behavior:** Both sync and async flows use same extraction
- **Well Documented:** Clear patterns and examples

## Implementation Details

### Files Modified
- `ue5_client/AIAssistant/main.py`
  - Added `_extract_token_from_response()` method
  - Updated `_process_sync()` to use flexible extraction
  - Updated `_process_async()` callback to use flexible extraction

### Files Added
- `tests/test_token_extraction_standalone.py` - Standalone regex validation
- `tests/FLEXIBLE_TOKEN_EXTRACTION.md` - This documentation

### Backward Compatibility
✅ All existing functionality preserved
✅ Clean token-only responses work as before
✅ No breaking changes to UE5 client API
✅ Production tests validate both old and new behaviors

## Future Enhancements

### Potential Improvements
1. **Trailing Text Support:** Handle tokens with text AFTER them (currently only supports text before)
2. **Multiple Tokens:** Extract and queue multiple tokens in single response
3. **Token Validation:** Validate extracted tokens against known action list
4. **Performance Metrics:** Track regex matching performance in production

### Recommendations
- Keep standalone tests in automated CI/CD pipeline
- Monitor for regex edge cases in production logs
- Consider token validation layer for security
- Document any new token patterns as they emerge
