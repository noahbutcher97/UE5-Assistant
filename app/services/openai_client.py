"""OpenAI API integration for viewport description generation."""
import json
import os
from typing import Any, Dict

import openai

# Initialize OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")


def generate_viewport_description(
    filtered_data: Dict[str, Any],
    style_name: str,
    style_config: Dict[str, Any],
    model: str,
    temperature: float
) -> str:
    """
    Generate a viewport description using OpenAI based on filtered data and style.
    
    Args:
        filtered_data: Pre-filtered viewport data
        style_name: Name of the response style
        style_config: Configuration for the style
        model: OpenAI model name
        temperature: Temperature for generation
        
    Returns:
        Generated description or empty string on error
    """
    # Extract style parameters
    focus = style_config["focus"]
    style_modifier = style_config["prompt_modifier"]
    max_tokens = style_config["max_tokens"]
    
    # Use temperature override if specified
    effective_temp = style_config.get("temperature_override", temperature)
    
    # Focus instructions for different styles
    focus_instructions = {
        "essentials_only": (
            "Focus ONLY on: camera position, selected objects (if any), "
            "and total actor count. One short paragraph."
        ),
        "notable_elements": (
            "Describe what's interesting or notable in the scene. Skip "
            "mundane details. Conversational tone."
        ),
        "key_elements_summary": (
            "Summarize key elements: selected objects, main actor types, "
            "overall layout. Skip repetitive details."
        ),
        "balanced_overview": (
            "Provide a balanced overview covering camera, selection, "
            "major actors, and scene organization."
        ),
        "precision_and_specs": (
            "Provide precise technical specifications with exact "
            "coordinates, transforms, counts, and classifications."
        ),
        "comprehensive_analysis": (
            "Analyze all viewport elements comprehensively. Include "
            "spatial relationships, technical details, and complete "
            "inventories."
        ),
        "visual_narrative": (
            "Paint a vivid picture using creative language and imagery. "
            "Use metaphors, sensory details, and flowing narrative."
        )
    }
    
    focus_instruction = focus_instructions.get(
        focus, focus_instructions["balanced_overview"]
    )
    
    # Build prompt
    prompt = (
        f"Viewport data (filtered for {style_name} style):\n"
        f"{json.dumps(filtered_data, indent=2)}\n\n"
        f"Instructions: {focus_instruction}"
    )
    
    # Build system message
    system_msg = (
        "You are an AI assistant for Unreal Engine 5.6 viewport analysis. "
        "Respond based on the provided filtered data and style instructions. "
        f"{style_modifier}"
    )
    
    print(
        f"[OpenAI] Generating description with style={style_name}, "
        f"temp={effective_temp}, max_tokens={max_tokens}"
    )
    
    # Call OpenAI API
    try:
        response = openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt}
            ],
            temperature=effective_temp,
            max_tokens=max_tokens
        )
        msg_content = response.choices[0].message.content
        description = msg_content.strip() if msg_content else ""
        print(f"[OpenAI] Generated {len(description)} chars: {description[:100]}...")
        return description
    except Exception as e:
        print(f"[OpenAI Error] {e}")
        return ""


def test_openai_connection(model: str) -> Dict[str, Any]:
    """Test OpenAI API connectivity."""
    try:
        response = openai.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Say 'pong'"}]
        )
        return {
            "openai_status": "connected",
            "response": response.choices[0].message.content or "pong"
        }
    except Exception as e:
        return {"openai_status": "error", "details": str(e)}
