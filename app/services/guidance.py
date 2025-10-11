"""Guidance service for context-aware implementation advice."""
from typing import Any, Dict, List, Optional, cast
import openai

from app.models import GuidanceRequest, ViewportContext, FileContext, ProjectProfile, BlueprintCapture


class GuidanceService:
    """Provides context-aware implementation guidance using OpenAI."""
    
    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0.7):
        """Initialize guidance service."""
        self.model = model
        self.temperature = temperature
    
    def _build_context_summary(self, request: GuidanceRequest) -> str:
        """Build a comprehensive context summary from all available sources."""
        context_parts = []
        
        if request.project_profile:
            proj = request.project_profile
            proj_info = [
                f"## Project Context",
                f"- Project: {proj.project_name}",
                f"- Engine: {proj.engine_version or 'Unknown'}",
                f"- Modules: {', '.join(proj.modules) if proj.modules else 'None'}",
                f"- Plugins: {', '.join(proj.plugins) if proj.plugins else 'None'}",
            ]
            if proj.content_stats:
                proj_info.append(f"- Content Stats: {proj.content_stats}")
            if proj.source_stats:
                proj_info.append(f"- Source Stats: {proj.source_stats}")
            context_parts.append("\n".join(proj_info))
        
        if request.viewport_context:
            vp = request.viewport_context
            vp_info = ["## Viewport Context"]
            
            if vp.camera:
                vp_info.append(f"- Camera Location: {vp.camera.get('location')}")
                vp_info.append(f"- Camera Rotation: {vp.camera.get('rotation')}")
            
            if vp.actors:
                vp_info.append(f"- Visible Actors: {vp.actors.get('total', 0)}")
                vp_info.append(f"- Level: {vp.actors.get('level')}")
            
            if vp.selection and vp.selection.get('count', 0) > 0:
                vp_info.append(f"- Selected: {vp.selection.get('actor_name')}")
            
            context_parts.append("\n".join(vp_info))
        
        if request.file_context:
            fc = request.file_context
            fc_info = [
                f"## File Context",
                f"- Root Path: {fc.root_path}",
                f"- Files: {fc.total_files} files ({fc.total_size} bytes)",
            ]
            
            if fc.search_query:
                fc_info.append(f"- Search Query: {fc.search_query}")
            
            if fc.files:
                fc_info.append("- Sample Files:")
                for file in fc.files[:10]:
                    fc_info.append(f"  * {file.name} ({file.type})")
                    if file.content and len(fc.files) <= 3:
                        preview = file.content[:200] + "..." if len(file.content) > 200 else file.content
                        fc_info.append(f"    Content preview: {preview}")
            
            context_parts.append("\n".join(fc_info))
        
        if request.blueprint_captures:
            bp_info = [f"## Blueprint Context"]
            for bp in request.blueprint_captures:
                bp_info.append(f"- Blueprint: {bp.blueprint_name}")
                bp_info.append(f"  Path: {bp.blueprint_path}")
                if bp.metadata:
                    bp_info.append(f"  Metadata: {bp.metadata}")
            context_parts.append("\n".join(bp_info))
        
        return "\n\n".join(context_parts)
    
    def generate_guidance(self, request: GuidanceRequest) -> str:
        """Generate context-aware implementation guidance."""
        
        context_summary = self._build_context_summary(request)
        
        focus_modifier = ""
        if request.focus_area:
            focus_modifier = f"\nFocus your advice specifically on {request.focus_area} aspects."
        
        system_prompt = (
            "You are an expert Unreal Engine 5 developer providing context-aware implementation guidance. "
            "Analyze the provided project context, viewport state, file information, and blueprints to give "
            "precise, actionable advice. Include specific UE5 API calls, Blueprint node suggestions, and "
            "best practices relevant to the user's exact situation."
            f"{focus_modifier}"
        )
        
        user_message = f"""# User Query
{request.query}

# Available Context
{context_summary}

Based on this context, provide detailed implementation guidance. Include:
1. Step-by-step instructions
2. Specific UE5 APIs or Blueprint nodes to use
3. Code examples where applicable
4. Potential pitfalls and how to avoid them
5. Best practices specific to this project's structure"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        response = openai.chat.completions.create(
            model=self.model,
            messages=cast(List[Any], messages),
            temperature=self.temperature,
        )
        
        return (response.choices[0].message.content or "").strip()
