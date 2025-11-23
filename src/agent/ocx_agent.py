import os
import json
from typing import Dict, Optional
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

OCX_SYSTEM_PROMPT = """
You are an expert Naval Architect and OCX (Open Class 3D Exchange) XML generator.
Your goal is to translate user natural language requests into valid OCX XML format.

### OCX Schema Definition (Simplified)
You must strictly follow this XML structure:

```xml
<OCX version="3.0">
  <Vessel name="[Vessel Name]">
    <Structure>
      <!-- Panels (Plates, Bulkheads, Decks) -->
      <Panel name="[Unique Name]" type="[Deck|Bulkhead|Shell|Web]">
        <Material grade="[Grade A|AH36|DH36]" thickness="[mm]"/>
        <Geometry type="Plate">
          <!-- Define 4 corner points for the plate -->
          <Point x="[mm]" y="[mm]" z="[mm]"/>
          <Point x="[mm]" y="[mm]" z="[mm]"/>
          <Point x="[mm]" y="[mm]" z="[mm]"/>
          <Point x="[mm]" y="[mm]" z="[mm]"/>
        </Geometry>
        
        <!-- Optional: Stiffeners attached to this panel -->
        <Stiffener name="[Unique Name]" type="[FlatBar|Angle|Tee|Bulb]">
            <Profile height="[mm]" width="[mm]" web_thickness="[mm]" flange_thickness="[mm]"/>
            <Location start_x="[mm]" start_y="[mm]" start_z="[mm]" end_x="[mm]" end_y="[mm]" end_z="[mm]"/>
        </Stiffener>
        
        <!-- Optional: Holes/Openings -->
        <Hole name="[Unique Name]" type="[Rectangular|Circular]">
            <Parameters width="[mm]" height="[mm]" diameter="[mm]"/>
            <Position x="[mm]" y="[mm]" z="[mm]"/>
        </Hole>
      </Panel>
    </Structure>
  </Vessel>
</OCX>
```

### Rules
1. **Coordinate System**: X=Length (L), Y=Width (B), Z=Height (D). Units are in **millimeters (mm)**.
2. **Inference**: If the user doesn't specify dimensions, infer reasonable standard ship dimensions (e.g., Deck height ~3000mm, Frame spacing ~800mm).
3. **Output**: Return ONLY the XML code. Do not include markdown backticks or explanations unless explicitly asked.
4. **Completeness**: Ensure all tags are closed and the XML is valid.

### Example
User: "Create a transverse bulkhead at x=10000, width 20m, height 10m, thickness 12mm."
Output:
<OCX version="3.0">
  <Vessel name="DesignVessel">
    <Structure>
      <Panel name="BHD_X10000" type="Bulkhead">
        <Material grade="A" thickness="12"/>
        <Geometry type="Plate">
          <Point x="10000" y="-10000" z="0"/>
          <Point x="10000" y="10000" z="0"/>
          <Point x="10000" y="10000" z="10000"/>
          <Point x="10000" y="-10000" z="10000"/>
        </Geometry>
      </Panel>
    </Structure>
  </Vessel>
</OCX>
"""

class OCXAgent:
    def __init__(self, model: str = "gpt-4o"):
        # Check if we should use LiteLLM or direct OpenAI
        base_url = os.getenv("LITELLM_BASE_URL")
        api_key = os.getenv("LITELLM_API_KEY")
        
        if not base_url or "localhost" in base_url:
            # Fallback to direct OpenAI if LiteLLM is not explicitly configured or pointing to localhost (and likely not running)
            # Check if OPENAI_API_KEY is present
            if os.getenv("OPENAI_API_KEY"):
                base_url = None # Use default OpenAI URL
                api_key = os.getenv("OPENAI_API_KEY")
            else:
                # Keep defaults if no OpenAI key (will likely fail if server not running)
                base_url = base_url or "http://localhost:4000"
                api_key = api_key or "sk-1234"
        
        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key
        )
        self.model = model
        self.system_prompt = OCX_SYSTEM_PROMPT
        self.system_prompt = OCX_SYSTEM_PROMPT

    def generate_ocx(self, user_prompt: str, history=None, context=None) -> str:
        """
        Generates OCX XML from user prompt, optional chat history, and optional context (prior XML/VLM).
        """
        messages = [{"role": "system", "content": self.system_prompt}]

        # Inject prior artifacts as assistant/system notes for continuity
        if context:
            ctx_parts = []
            if context.get("xml_content"):
                ctx_parts.append(f"Previous OCX XML:\n{context['xml_content']}")
            if context.get("validation"):
                ctx_parts.append(f"Previous validation result:\n{context['validation']}")
            if context.get("png_url"):
                ctx_parts.append(f"Previous render PNG: {context['png_url']}")
            if ctx_parts:
                messages.append({
                    "role": "assistant",
                    "content": "Use prior artifacts for incremental edits.\n" + "\n\n".join(ctx_parts)
                })

        if history:
            # only keep known roles
            for msg in history:
                if msg.role in ["user", "assistant"]:
                    messages.append({"role": msg.role, "content": msg.content})
        messages.append({"role": "user", "content": user_prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.1
        )

        content = response.choices[0].message.content
        
        # Clean up markdown code blocks if present
        if "```xml" in content:
            content = content.split("```xml")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        # Basic validation
        if "<OCX" not in content or "</OCX>" not in content:
            raise ValueError(f"LLM did not return valid OCX XML. Response: {content[:200]}")
            
        return content
