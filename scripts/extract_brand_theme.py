import os
import requests
import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv

# Load env for API keys
load_dotenv()

# Configuration
TARGET_URL = "https://www.fruzaqlahcp.com/
OUTPUT_FILE = "theme.json"

THEME_ANALYSIS_PROMPT = """You are a Visual Design Expert.
Task: Analyze the provided HTML/CSS content from a brand website.
Goal: Extract the exact Brand Colors and Font Family used on the site.

Input: Truncated HTML/CSS from the website.

Output: A JSON object defining the CSS variables.
Rules:
1. Identify the **Primary Brand Color**. This is the dominant color used for the logo, main actionable buttons, or consistent headers. **distinguish this from generic hero banner backgrounds**. If there is a "fruquintinib" green, prioritize that.
2. Identify the **Secondary Brand Color**. Use for high-contrast text or deep backgrounds (e.g. Navy blue).
3. Identify the Font Family (e.g. "Roboto", "Helvetica", etc.). Priority: 1. CSS Font Stack, 2. Inferred style.
4. Return JSON ONLY:
{
  "primary_color": "Hex Code (e.g. #00723B)", 
  "secondary_color": "Hex Code (e.g. #0A2342)",
  "font_family": "Font Stack String (e.g. 'Helvetica Neue', Arial, sans-serif)"
}
"""

def extract_theme():
    print(f"Fetching content from {TARGET_URL}...")
    try:
        # User-agent to avoid being blocked
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(TARGET_URL, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Taking a chunk of the HTML (Head + partial Body) is usually enough for style
        # We don't need the whole thing, just enough to catch <style> tags or inline styles
        html_content = response.text[:20000] 
        print(f"Fetched {len(html_content)} bytes (truncated).")
        print(f"DEBUG: Preview of HTML:\n{html_content[:1000]}")
        
        print("Analyzing with LLM (gpt-5.2)...")
        llm = ChatOpenAI(model="gpt-5.2", temperature=0)
        
        messages = [
            SystemMessage(content=THEME_ANALYSIS_PROMPT),
            HumanMessage(content=f"Website Content:\n{html_content}")
        ]
        
        result = llm.invoke(messages)
        content = result.content.replace("```json", "").replace("```", "").strip()
        theme = json.loads(content)
        
        print("Extracted Theme:")
        print(json.dumps(theme, indent=2))
        
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(theme, f, indent=2)
        print(f"Saved to {OUTPUT_FILE}")
        
    except Exception as e:
        print(f"Error extracting theme: {e}")
        # Fallback
        default_theme = {
            "primary_color": "#00723B",
            "secondary_color": "#0A2342",
            "font_family": "'Helvetica Neue', Arial, sans-serif"
        }
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(default_theme, f, indent=2)

if __name__ == "__main__":
    extract_theme()
