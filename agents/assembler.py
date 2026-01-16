from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from .state import AgentState
import json
import os

llm = ChatOpenAI(model="gpt-5.2", temperature=0)


ASSEMBLER_SYSTEM_PROMPT = """Role: Front-End Developer.
Task: Generate the internal HTML BODY for a slide.

Design Rules (Custom Style):
- Use variable tokens: `var(--primary)` (Brand Color), `var(--secondary)` (Contrast/Text).
- Font: Use the injected `font-family`.
- Layout: Use `class="column"` for grid layouts (2-col default). Use `class="column full-width"` for large assets.
- Components:
- Components:
  - Headlines: `class="headline"` (Bold, var(--secondary)).
  - Subheads: `class="subhead"` (var(--primary), Uppercase).
  - Cards: `class="card"` (White bg, shadow, rounded).
  - **Tables**: Render rich HTML tables. Use `style='border-collapse: collapse; width: 100%; font-size: 14px; color: var(--secondary);'`. Header row background `rgba(0,0,0,0.05)`. Borders `1px solid #ddd`. Cell padding `10px`. Do NOT use Markdown tables.

Content Rules (Strict):
1. **IGNORE** any 'html_content' or 'css_styles' provided in the source JSON. You must generate your own Code.
2. **IMAGES**: Use ONLY provided 'image_url's. Render clean `<img>` tags with `style="max-width: 90%; border-radius: 8px;"`.
3. **TEXT**: Use the `claim_text` from the JSON. Do not paraphrase key medical claims. **EXCEPTION**: You MUST omit text if it starts with "The image...", "Figure...", or describes the visual, **EVEN IF** it contains data points. Assume the image renders this data.
4. **HEADER**: Generate an "Action Headline" summarizing the content (e.g., "SUPERIOR EFFICACY vs PLACEBO") to place at the top.
5. **REFERENCES**: Format citation numbers as superscripts immediately following the text, e.g., `Statement.<sup>1,2</sup>`.
6. **IMAGE REDUNDANCY**: CRITICAL: If an image is rendered, **OMIT** the text block describing it. For example, if the text says "The image outlines the study design...", delete that entire paragraph. Keep only the image.

Input JSON:
- List of Content Groups, each containing claims and images.

Output:
- Raw HTML strings (<div>...</div>). Do not wrap in ```html```.
"""

NAVBAR_GENERATOR_PROMPT = """You are a UX copywriter designed to create concise navigation tabs for a presentation.
Task: Summarize each of the following slide topics into a SHORT, 1-2 WORD navigation label.
Rules:
1. Labels must be uppercase.
2. Labels must be extremely concise (e.g., "EFFICACY", "SAFETY", "STUDY DESIGN").
3. Return ONLY a JSON list of strings corresponding to the input topics.
4. Maintain the same order as the input.
"""



IMAGE_VETTING_PROMPT = """You are a Content Editor.
Task: Evaluate the following image for its relevance.
Criteria:
- RETURN 'TRUE' (JSON boolean) if the image is a valid visual asset (chart, graph, diagram, logo, packshot) relevant to the content.
- RETURN 'FALSE' (JSON boolean) if the image is low-value or "simple":
  - Simple commercial text banners (e.g., "FRESCO-2 Study" on a colored background).
  - Slide headers or Title cards.
  - Generic decorative icons.
  - Images that are primarily just large text without data visualization.

Output JSON ONLY: {"useful": boolean}
"""

def generate_navbar_html(active_tab, tabs, theme):
    # Dynamic tabs passed from the plan
    p_color = theme.get('primary_color', '#00723B')
    s_color = theme.get('secondary_color', '#0A2342')
    
    logo_url = "https://www.fruzaqlahcp.com/sites/default/files/2024-04/fruzaqla_logo_r_rgb.png"
    html = f'<div class="side-navigation" style="display:flex; align-items:center; gap:20px; background:#fff; padding:15px; border-bottom:1px solid #ddd; font-family:sans-serif; margin-bottom:20px; overflow-x: auto;">'
    # Add Logo
    html += f'<img src="{logo_url}" style="height:40px; margin-right:20px;" alt="FRUZAQLA">'
    
    for tab in tabs:
        style = f"color:{s_color}; flex-shrink: 0; padding: 5px 10px; cursor: pointer; text-transform: uppercase; font-size: 14px;"
        if tab == active_tab:
            style = f"color:{p_color}; text-decoration:none; border-bottom: 3px solid {p_color}; flex-shrink: 0; padding: 5px 10px; font-weight: 800; text-transform: uppercase; font-size: 14px;"
        html += f'<div class="nav-item" style="{style}">{tab}</div>'
    html += '</div>'
    return html

def filter_images(content_groups):
    """Filter out broken/low-value images. Prioritize intactness."""
    print("  - Vetting images (Intactness + Permissive Check)...")
    checked_urls = {} # Cache URL -> useful (bool)
    
    for grp in content_groups:
        for claim in grp.get('claims', []):
            url = claim.get('image_url')
            if not url:
                continue
                
            if url in checked_urls:
                if not checked_urls[url]:
                    claim['image_url'] = None
                continue
            
            # 1. Intactness Check (Is URL valid?)
            # In a real scenario, we might HEAD request it. 
            # For now, we assume if it's in Pinecone it's likely valid, 
            # but let's blindly trust existence implies intactness potential.
            
            # 2. Permissive Vetting
            try:
                msg = HumanMessage(
                    content=[
                        {"type": "text", "text": "Evaluate this image."},
                        {"type": "image_url", "image_url": {"url": url}}
                    ]
                )
                messages = [
                    SystemMessage(content=IMAGE_VETTING_PROMPT),
                    msg
                ]
                response = llm.invoke(messages)
                content = response.content.replace("```json", "").replace("```", "").strip()
                result = json.loads(content)
                is_useful = result.get('useful', False) # Default to False if unclear to respect user wish for exclusion
                
                checked_urls[url] = is_useful
                if not is_useful:
                    print(f"    [REJECT] Low-value image (Simple/Banners): {url[-15:]}")
                    claim['image_url'] = None
                else:
                    print(f"    [KEEP] Useful/Intact image: {url[-15:]}")
                    
            except Exception as e:
                print(f"    [ERROR] vetting image {url[-15:]}: {e}")
                # Keep by default on error (Intactness priority)
                checked_urls[url] = True

def assembler_node(state: AgentState):
    print("--- ASSEMBLER AGENT (Custom Style & Exact Claims) ---")
    plan = state['deck_plan']
    
    full_output_html = ""
    assembler_history = []
    
    # Extract topics and generate short labels
    topics = [s['page_topic'] for s in plan]
    
    # Load Theme from File (Strict)
    theme_file = "theme.json"
    theme = None
    if os.path.exists(theme_file):
        try:
            with open(theme_file, 'r') as f:
                theme = json.load(f)
            print(f"    [THEME] Loaded from file: {theme.get('primary_color')} | {theme.get('secondary_color')}")
        except Exception as e:
            print(f"    [ERROR] Failed to load theme file: {e}")
    
    if not theme:
        print("    [THEME] Warning: theme.json not found. Using defaults.")
        theme = {
            "primary_color": "#00723B",
            "secondary_color": "#0A2342",
            "font_family": "'Helvetica Neue', Arial, sans-serif"
        }
    
    nav_msg = f"Topics:\n{json.dumps(topics, indent=2)}"
    nav_messages = [
        SystemMessage(content=NAVBAR_GENERATOR_PROMPT),
        HumanMessage(content=nav_msg)
    ]
    
    print("Generating concise navbar labels...")
    try:
        nav_response = llm.invoke(nav_messages)
        content = nav_response.content.replace("```json", "").replace("```", "").strip()
        short_labels = json.loads(content)
        # Ensure length matches
        if len(short_labels) != len(topics):
            print("Warning: Label count mismatch. Fallback to original topics.")
            short_labels = [t.strip().upper()[:20] for t in topics]
    except Exception as e:
        print(f"Error generating nav labels: {e}")
        short_labels = [t.strip().upper()[:20] for t in topics]

    # Create Deduplicated Navbar Tabs (preserving order)
    seen_labels = set()
    navbar_tabs = []
    for lbl in short_labels:
        if lbl not in seen_labels:
            navbar_tabs.append(lbl)
            seen_labels.add(lbl)
    
    # Global CSS
    base_css = f"""
    :root {{ --primary:{theme['primary_color']}; --secondary:{theme['secondary_color']}; --font-base: {theme['font_family']}; --bg-light: #F9F9F9; }}
    body {{ margin: 0; font-family: var(--font-base); background: #fff; }}
    .slide-container {{ display: flex; flex-direction: column; min-height: 100vh; padding: 40px; page-break-after: always; box-sizing: border-box; }}
    .content-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 40px; margin-top: 20px; }}
    .column {{ display: flex; flex-direction: column; gap: 20px; }}
    .column.full-width {{ grid-column: span 2; align-items: center; }}
    .headline {{ color: var(--secondary); font-size: 2.4rem; margin: 0 0 10px 0; font-weight: 800; line-height: 1.1; }}
    .subhead {{ color: var(--primary); font-size: 1.2rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; }}
    .card {{ background: #fff; border: 1px solid #eee; border-radius: 12px; padding: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}
    .claim-text {{ font-size: 1rem; color: #333; line-height: 1.5; }}
    ul {{ padding-left: 20px; }}
    li {{ margin-bottom: 8px; }}
    """
    
    for i, slide in enumerate(plan):
        slide_id = slide['slide_id']
        topic = slide['page_topic']
        content_groups = slide.get('selected_content') 
        
        # Use corresponding short label as active tab
        active_tab = short_labels[i]
        
        if not content_groups:
             full_output_html += f"<div class='slide-container'><h1>Slide {slide_id}: No Content</h1></div>"
             continue

        # VET IMAGES
        filter_images(content_groups)

        # Prepare payload for LLM (Claims + Images only)
        # Flatten content for LLM context
        context_data = []
        for grp in content_groups:
            # Filter relevant fields
            clean_claims = []
            for c in grp['claims']:
                clean_claims.append({
                    "claim_text": c.get('claim_text', ''),
                    "image_url": c.get('image_url', None)
                })
            context_data.append({"group_id": grp['group_id'], "claims": clean_claims})
            
        msg = f"""
        Page Topic: {topic}
        Content Data:
        {json.dumps(context_data, indent=2)}
        """
        
        current_messages = [
            SystemMessage(content=ASSEMBLER_SYSTEM_PROMPT),
            HumanMessage(content=msg)
        ]
        
        response = llm.invoke(current_messages)
        assembler_history.extend(current_messages + [response])
        
        body_html = response.content.replace("```html", "").replace("```", "").strip()
        
        slide_html = f"""
        <div class="slide-container" id="slide-{slide_id}">
            {generate_navbar_html(active_tab, navbar_tabs, theme)}
            {body_html}
        </div>
        """
        
        slide['html_content'] = slide_html
        full_output_html += slide_html
        
    final_output = f"<style>{base_css}</style>\n{full_output_html}"
    
    return {
        "html_output": final_output,
        "assembler_messages": assembler_history
    }
