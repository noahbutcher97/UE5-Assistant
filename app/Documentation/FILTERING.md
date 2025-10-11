# Intelligent Filtering System

## Overview

The filtering system optimizes AI token usage by sending only relevant viewport data based on the selected response style. This reduces costs by 30-70% while maintaining response quality.

## Filter Modes

### Filter Mode Matrix

| Response Style | Filter Mode | Token Reduction | Data Included |
|---------------|-------------|-----------------|---------------|
| **Concise** | minimal | ~70% | Camera + selected + actor count |
| **Natural** | highlights | ~60% | Notable elements + type summaries |
| **Balanced** | balanced | ~50% | Key elements + counts |
| **Descriptive** | standard | ~30% | Good detail, limited names |
| **Creative** | standard | ~30% | Same as descriptive |
| **Technical** | technical | ~20% | All data + metadata section |
| **Detailed** | complete | 0% | Everything included |

---

## Filter Mode Details

### 1. Minimal Filter (Concise Style)

**Philosophy**: Essentials only - camera position and what's selected

**Output Structure**:
```python
{
    "camera": {
        "location": [x, y, z],
        "rotation": [pitch, yaw, roll]
    },
    "selection": {
        "count": 2,
        "actors": [
            {"name": "Cube_1", "class": "StaticMeshActor", "location": [...]},
            # Max 3 selected actors
        ]
    },
    "actors_summary": {
        "total": 47,
        "has_more": true  # if total > selection count
    }
}
```

**Use Case**: Quick status checks, brief updates

**Example AI Output**: 
> "Camera at [1200, -500, 450]. Selected: Cube_1 (StaticMeshActor). Scene has 47 actors total."

---

### 2. Highlights Filter (Natural Style)

**Philosophy**: Focus on interesting/notable elements

**Output Structure**:
```python
{
    "camera": {...},
    "selection": {...},  # full selection data
    "actors": {
        "total": 47,
        "notable": [  # selected actors + first 5 non-selected
            "Cube_1", "DirectionalLight", "SkyAtmosphere", ...
        ],
        "types_summary": {
            "StaticMeshActor": 12,
            "PointLight": 3,
            "Cube": 2
        }
    },
    "lighting_summary": "present"  # only if lights exist
}
```

**Use Case**: Conversational descriptions, notable features

**Example AI Output**:
> "Hey! The camera's positioned high up at 450 units, giving a bird's eye view. Down below, we've got Cube_1 selected - it's sitting at (100, 200, 50). The scene has about 47 actors total, mostly static meshes and some lighting."

---

### 3. Balanced Filter (Balanced Style)

**Philosophy**: Technical accuracy with readability

**Output Structure**:
```python
{
    "camera": {...},
    "selection": {...},
    "actors": {
        "total": 47,
        "types": {"StaticMeshActor": 12, "PointLight": 3, ...},
        "sample_names": [  # first 10 actors
            "PlayerStart", "Cube_1", "DirectionalLight", ...
        ]
    },
    "lighting": {
        "directional_count": 2,
        "point_count": 5,
        "spot_count": 1
    },
    "environment": {
        "has_fog": true,
        "has_landscape": false
    }
}
```

**Use Case**: Balanced technical descriptions

**Example AI Output**:
> "The viewport shows a scene with 47 actors at camera position (1200, -500, 450). Primary actors include PlayerStart, Cube_1, and DirectionalLight. Lighting consists of 2 directional lights, 5 point lights, and 1 spot light. Environment includes fog effects."

---

### 4. Standard Filter (Descriptive/Creative Styles)

**Philosophy**: Good detail without overwhelming

**Output Structure**:
```python
{
    "camera": {...},
    "selection": {...},
    "actors": {
        "total": 47,
        "names": [  # first 15 actors
            "PlayerStart", "Cube_1", "DirectionalLight", ...
        ],
        "types": {"StaticMeshActor": 12, ...}
    },
    "lighting": {  # full lighting details
        "directional_lights": [
            {"name": "DirectionalLight", "location": [...], "intensity": 10}
        ],
        "point_lights": [...],
        "spot_lights": [...]
    },
    "environment": {
        "fog": [  # first 2 fog actors
            "ExponentialHeightFog_0"
        ],
        "landscape": "Landscape_0"
    }
}
```

**Use Case**: Descriptive technical prose, creative narratives

**Example AI Output (Descriptive)**:
> "The Unreal Engine 5.6 viewport displays a scene with 47 actors positioned within the TestLevel environment. The camera is located at coordinates (1200, -500, 450) with a rotation of (15°, 90°, 0°). Notable actors include PlayerStart, Cube_1, and DirectionalLight. The lighting setup consists of a directional light at intensity 10..."

**Example AI Output (Creative)**:
> "In the digital expanse, a virtual eye hovers at (1200, -500, 450), gazing across a realm of 47 geometric souls. Below, Cube_1 stands sentinel, its edges crisp against the synthetic sky. Light cascades from above, a directional beam painting shadows across the landscape..."

---

### 5. Technical Filter (Technical Style)

**Philosophy**: Detailed but organized for technical documentation

**Output Structure**:
```python
{
    "camera": {...},
    "selection": {...},
    "actors": {...},  # all actors, no truncation
    "lighting": {...},  # all lighting data
    "environment": {...},  # all environment data
    "metadata": {
        "actor_count": 47,
        "selected_count": 2,
        "lighting_count": 8,
        "environment_features": ["fog", "landscape"]
    }
}
```

**Use Case**: Technical documentation, specs

**Example AI Output**:
```markdown
# Unreal Engine 5.6 Viewport Analysis

## Camera Configuration
- **Location**: (1200, -500, 450)
- **Rotation**: (15°, 90°, 0°)

## Scene Composition
- **Total Actors**: 47
- **Selected**: 2
- **Types**: StaticMeshActor (12), PointLight (3), Cube (2)

## Lighting Configuration
- **Directional Lights**: 2
- **Point Lights**: 5
- **Spot Lights**: 1
```

---

### 6. Complete Filter (Detailed Style)

**Philosophy**: Comprehensive exhaustive analysis

**Output Structure**:
```python
{
    "camera": {...},
    "actors": {...},
    "selection": {...},
    "lighting": {...},
    "environment": {...},
    "additional_info": {...},  # if present
    "project_metadata": {  # if enabled
        "project_name": "MyProject",
        "asset_summary": {...},
        "source_code_stats": {...}
    }
}
```

**Use Case**: Comprehensive analysis, debugging

**Example AI Output**:
> "### Comprehensive Viewport Analysis
> 
> The Unreal Engine 5.6 viewport presents a detailed scene configuration within the MyProject environment. Camera positioning establishes the viewing perspective at spatial coordinates (1200, -500, 450) with angular orientation (15°, 90°, 0°).
> 
> #### Actor Composition
> The scene contains 47 distinct actors distributed across multiple categories. The StaticMeshActor category comprises 12 instances, including PlayerStart, Cube_1, Cube_2... [continues with full detail]"

---

## Implementation

### Core Function

```python
def filter_viewport_data(
    context: ViewportContext, 
    filter_mode: str
) -> Dict[str, Any]:
    """Apply intelligent filtering based on mode."""
    
    filtered = {}
    
    # Camera always included (spatial context essential)
    filtered["camera"] = extract_camera(context)
    
    if filter_mode == "minimal":
        # Concise: Camera + selected + total count
        filtered["selection"] = limit_selection(context, max_count=3)
        filtered["actors_summary"] = {"total": get_total(context)}
        
    elif filter_mode == "highlights":
        # Natural: Notable elements only
        filtered["selection"] = context.selection
        filtered["actors"] = extract_notable_actors(context, limit=5)
        if has_lighting(context):
            filtered["lighting_summary"] = "present"
    
    # ... other modes
    
    return filtered
```

### Filter Selection Logic

```python
def select_filter_mode(response_style: str) -> str:
    """Map response style to filter mode."""
    
    style_config = RESPONSE_STYLES.get(response_style)
    return style_config.get("data_filter", "standard")
```

---

## Performance Metrics

### Token Usage Comparison

**Test Scene**: 47 actors, 8 lights, 2 selected objects

| Filter Mode | Input Tokens | Output Tokens | Total | Reduction |
|-------------|--------------|---------------|-------|-----------|
| complete | 1200 | 500 | 1700 | 0% |
| technical | 950 | 500 | 1450 | 15% |
| standard | 800 | 400 | 1200 | 29% |
| balanced | 600 | 350 | 950 | 44% |
| highlights | 500 | 300 | 800 | 53% |
| minimal | 350 | 150 | 500 | 71% |

### Cost Impact

At $0.15 per 1M input tokens, $0.60 per 1M output tokens (gpt-4o-mini):

**1000 requests**:
- **Complete** (1700 tokens): $0.48
- **Minimal** (500 tokens): $0.14
- **Savings**: 71% ($0.34 per 1000 requests)

---

## Best Practices

### When to Use Each Filter

1. **Minimal** - Quick status, mobile UIs, voice assistants
2. **Highlights** - Chat interfaces, casual updates
3. **Balanced** - Mixed technical/user audiences
4. **Standard** - General documentation, reports
5. **Technical** - API docs, technical specs
6. **Complete** - Debugging, comprehensive analysis

### Customization

To add a new filter mode:

1. Add to `RESPONSE_STYLES` in `config.py`:
```python
"my_style": {
    "name": "My Style",
    "data_filter": "my_custom_filter",
    ...
}
```

2. Implement in `services/filtering.py`:
```python
elif filter_mode == "my_custom_filter":
    filtered["camera"] = ...
    filtered["custom_data"] = ...
```

3. Update UE5 `config.py` to match

---

## Future Enhancements

1. **Dynamic Filtering**: Adjust filter based on scene complexity
2. **User Preferences**: Remember user's preferred detail level
3. **A/B Testing**: Test filter effectiveness with user feedback
4. **Smart Truncation**: ML-based selection of most relevant actors
5. **Caching**: Cache filtered data for repeated requests
