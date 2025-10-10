import os

import openai
from fastapi import FastAPI
from pydantic import BaseModel

# ============================================================
# CONFIGURATION
# ============================================================

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI(
    title="Unreal Engine Viewport Describer",
    description=
    "Receives Unreal viewport context and returns a natural language description.",
    version="0.1.0",
)

# ============================================================
# DATA MODEL
# ============================================================


class ViewportContext(BaseModel):
    camera_location: list[float] | None = None
    camera_rotation: list[float] | None = None
    visible_actors: list[str] | None = None
    selected_actor: str | None = None
    additional_info: dict | None = None


# ============================================================
# MAIN ENDPOINT
# ============================================================


@app.post("/describe_viewport")
async def describe_viewport(context: ViewportContext):
    """
    Unreal sends viewport info here. The AI returns a natural-language description.
    """
    prompt = (
        "You are an Unreal Engine 5.6 Editor assistant. "
        "Given the following viewport data, describe what the user is likely seeing "
        "in plain language useful for debugging or level design:\n\n"
        f"{context.model_dump_json(indent=2)}")

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": prompt
            }],
        )
        summary = (response.choices[0].message.content or "").strip()
    except Exception as e:
        summary = f"Error generating description: {e}"

    print(f"\n[Viewport Received]\n{context.model_dump_json(indent=2)}")
    print(f"[Generated Description]\n{summary}\n")

    return {"description": summary, "raw_context": context}


# ============================================================
# SIMPLE HOMEPAGE
# ============================================================


@app.get("/")
async def home():
    return {"status": "online", "message": "UE5 AI Assistant running!"}
