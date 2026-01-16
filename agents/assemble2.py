import json
import os
from jinja2 import Environment, FileSystemLoader
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from .state import AgentState

llm = ChatOpenAI(model="gpt-5.2", temperature=0)

NAVBAR_GENERATOR_PROMPT = """You are a UX copywriter designed to create concise navigation tabs for a presentation.
Task: Summarize each of the following slide topics into a SHORT, 1-2 WORD navigation label.
Rules:
1. Labels must be uppercase.
2. Labels must be extremely concise (e.g., "EFFICACY", "SAFETY", "STUDY DESIGN").
3. Return ONLY a JSON list of strings corresponding to the input topics.
4. Maintain the same order as the input.
"""

STRUCTURER_PROMPT = """Role: Presentation Layout Specialist.
Task: Structuring content for a High-Fidelity Slide.
Input: A list of claims and images for a specific topic.
Output: A strict formatted JSON object defining the slide layout and content blocks.

Design Goals:
1. **Layout**: typical slide is 2 columns. Use "grid-cols-2". Large images can be "grid-cols-2" (full width) or "grid-cols-1".
2. **Headline**: High-impact, action-oriented summary (e.g. "FRUZAQLA DEMONSTRATES SUPERIOR OS").
3. **Subhead**: Context tag (e.g. "EFFICACY RESULTS").
4. **Content Blocks**:
   - TEXT: Summarize claims into clear, clinician-facing HTML paragraphs. Bold key data.
   - LIST: Use if multiple short points exist.
   - IMAGE: Use provided URLs. **CRITICAL**: If you use an image, DO NOT repeat the text describing what the image shows. The image speaks for itself.
5. **Vetting**:
   - EXCLUDE simple text banners / header images (e.g. "FRESCO-2" text on blue bg).
   - KEEP charts, graphs, and diagrams.

JSON Schema:
{
  "headline": "String",
  "subhead": "String",
  "layout_class": "grid-cols-2", // usually grid-cols-2
  "references": "String (citations)",
  "content_blocks": [
    {
      "type": "text", // or "image", "list"
      "col_span_class": "col-span-1", // or "col-span-2" for full width
      "content": "HTML string (for text)",
      "items": ["Item 1", "Item 2"], // required if type="list"
      "url": "URL string", // required if type="image"
      "caption": "Optional caption"
    }
  ]
}
"""

def generate_navbar_labels(topics, llm):
    """Generate short navbar labels."""
    try:
        msg = f"Topics:\n{json.dumps(topics, indent=2)}"
        messages = [
            SystemMessage(content=NAVBAR_GENERATOR_PROMPT),
            HumanMessage(content=msg)
        ]
        response = llm.invoke(messages)
        content = response.content.replace("```json", "").replace("```", "").strip()
        labels = json.loads(content)
        if len(labels) != len(topics):
            return [t.strip().upper()[:20] for t in topics]
        return labels
    except Exception:
        return [t.strip().upper()[:20] for t in topics]

def assembler_node(state: AgentState):
    print("--- ASSEMBLER 2.0 (Template-Based) ---")
    plan = state['deck_plan']
    assembler_history = []
    
    # 1. Load Theme
    theme_file = "theme.json"
    theme = {
        "primary_color": "#00723B",
        "secondary_color": "#0A2342",
        "font_family": "'Helvetica Neue', Arial, sans-serif"
    }
    if os.path.exists(theme_file):
        try:
            with open(theme_file, 'r') as f:
                theme = json.load(f)
        except Exception:
            pass

    # 2. Navbar Labels
    topics = [s['page_topic'] for s in plan]
    navbar_labels = generate_navbar_labels(topics, llm)
    
    # 3. Structure Content Per Slide
    structured_slides = []
    
    for i, slide in enumerate(plan):
        topic = slide['page_topic']
        content_groups = slide.get('selected_content', [])
        nav_label = navbar_labels[i]
        
        print(f"Structuring Slide {i+1}: {topic}")
        
        # Flatten Content for LLM
        raw_content = []
        for grp in content_groups:
            for c in grp['claims']:
                raw_content.append(c)
                
        if not raw_content:
            # Empty slide fallback
            structured_slides.append({
                "nav_label": nav_label,
                "headline": "No Content Available",
                "subhead": topic,
                "layout_class": "grid-cols-1",
                "content_blocks": []
            })
            continue

        # Invoke LLM Structurer
        msg = f"""
        Topic: {topic}
        Raw Content:
        {json.dumps(raw_content, indent=2)}
        """
        
        messages = [
            SystemMessage(content=STRUCTURER_PROMPT),
            HumanMessage(content=msg)
        ]
        
        try:
            response = llm.invoke(messages)
            assembler_history.extend(messages + [response])
            
            json_str = response.content.replace("```json", "").replace("```", "").strip()
            # Robust parsing
            json_start = json_str.find('{')
            json_end = json_str.rfind('}') + 1
            if json_start != -1 and json_end != -1:
                json_str = json_str[json_start:json_end]
                
            slide_data = json.loads(json_str)
            
            # Enrich with nav data
            slide_data['nav_label'] = nav_label
            structured_slides.append(slide_data)
            
        except Exception as e:
            print(f"Error structuring slide {i+1}: {e}")
            # Fallback
            structured_slides.append({
                "nav_label": nav_label,
                "headline": "Error Generating Slide",
                "subhead": topic,
                "layout_class": "grid-cols-1",
                "content_blocks": [{"type": "text", "col_span_class": "col-span-1", "content": f"An error occurred: {e}"}]
            })

    # 4. Render with Jinja2
    print("Rendering HTML with Jinja2...")
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('templates/slide_template.html')
    
    # Unique Navbar Tabs
    unique_tabs = []
    seen = set()
    for lbl in navbar_labels:
        if lbl not in seen:
            unique_tabs.append(lbl)
            seen.add(lbl)

    final_html = template.render(
        slides=structured_slides,
        theme=theme,
        navbar_tabs=unique_tabs
    )
    
    return {
        "html_output": final_html,
        "assembler_messages": assembler_history
    }
