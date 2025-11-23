import os
from typing import Dict, List, Optional
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

OCX_CODE_SYSTEM_PROMPT = """
You are an expert generative design engineer. Produce Python code that uses the OCXBuilder SDK to generate OCX XML.

Rules:
- Never emit XML directly. Always return executable Python only.
- Import from ocx_sdk.builder: `from ocx_sdk.builder import OCXBuilder`.
- Always instantiate a builder, add geometry, and finish with `xml_output = builder.to_xml_string()`.
- Use loops instead of manual repetition for stiffeners/repeating members.
- Convert user dimensions (meters -> millimeters) explicitly if needed.
- Keep code deterministic: avoid placeholder values and avoid external I/O or network calls.
- If the request is incremental, you may read the previous XML string provided in context for reference but regenerate a fresh OCX with the new intent.

Available helpers (keep your code to these APIs):
- builder.create_plate(x, y, length, width, z=0.0, thickness=..., plate_type="Deck", material="AH36", name=None) -> plate_id
- builder.create_stiffeners_on_plate(plate_id, spacing, count, profile="Tee", orientation="y", name_prefix="STF", height=..., width=..., web_thickness=..., flange_thickness=...)
- builder.create_stiffener(name, start(x,y,z), end(x,y,z), profile, height, width, web_thickness, flange_thickness, parent_panel=None)
- builder.add_opening(plate_id, center(x,y,z), width, height, name=None, opening_type="Rectangular")
- builder.to_xml_string()

Return only Python (no markdown fences).

Example:
from ocx_sdk.builder import OCXBuilder

builder = OCXBuilder(vessel_name="DemoVessel")
plate_id = builder.create_plate(x=0, y=0, z=0, length=20000, width=10000, thickness=14, plate_type="Deck")
num_stiffeners = int(20000 // 600)
builder.create_stiffeners_on_plate(
    plate_id=plate_id,
    spacing=600,
    count=num_stiffeners,
    profile="Tee",
    height=250,
    width=12,
    web_thickness=12,
    flange_thickness=12,
)
xml_output = builder.to_xml_string()
"""


class OCXCodeAgent:
    def __init__(self, model: str = "gpt-4o"):
        base_url = os.getenv("LITELLM_BASE_URL")
        api_key = os.getenv("LITELLM_API_KEY")

        if not base_url or "localhost" in base_url:
            if os.getenv("OPENAI_API_KEY"):
                base_url = None
                api_key = os.getenv("OPENAI_API_KEY")
            else:
                base_url = base_url or "http://localhost:4000"
                api_key = api_key or "sk-1234"

        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model = model

    def generate_code(
        self,
        user_prompt: str,
        history: Optional[List[Dict[str, str]]] = None,
        context: Optional[Dict[str, str]] = None,
        feedback: Optional[str] = None,
    ) -> str:
        messages = [{"role": "system", "content": OCX_CODE_SYSTEM_PROMPT}]

        if context:
            ctx_parts = []
            if context.get("xml_content"):
                ctx_parts.append(f"Previous XML (for reference only):\n{context['xml_content']}")
            if context.get("validation"):
                ctx_parts.append(f"Validation feedback:\n{context['validation']}")
            if ctx_parts:
                messages.append({"role": "assistant", "content": "\n\n".join(ctx_parts)})

        if feedback:
            messages.append({"role": "assistant", "content": f"Previous attempt feedback: {feedback}"})

        if history:
            for msg in history:
                if msg.get("role") in {"user", "assistant"}:
                    messages.append({"role": msg["role"], "content": msg["content"]})

        messages.append({"role": "user", "content": user_prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.15,
        )

        content = response.choices[0].message.content or ""
        if "```python" in content:
            content = content.split("```python")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        return content.strip()
