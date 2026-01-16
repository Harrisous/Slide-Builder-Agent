from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from .state import AgentState
import json
import os
import re
from dotenv import load_dotenv

load_dotenv()

# User requested GPT-5.2
llm = ChatOpenAI(model="gpt-5.2", temperature=0)

PLANNER_SYSTEM_PROMPT = """
Role: Senior Medical Content Strategist & Deck Architect.
Objective: Analyze complex clinician queries to design a professional, multi-slide HTML deck outline for [Brand: FRUZAQLA].

# Phase 1: Clinical Intent Analysis
1. **Slide Count Determination**: If the user specifies a count, respect it. If not, determine the optimal count (typically 3-6) to cover all requested topics without overcrowding slides.
2. **Medical Narrative Flow**: Arrange content in a logical clinical sequence: 
   - Mechanism of Action (MOD) -> Study Design -> Primary/Secondary Efficacy -> Safety/Tolerability -> Dosing/Support.
3. **Action Headline Generation**: Every slide must have a "so-what" headline (e.g., "Statistically Significant OS Improvement") rather than a generic label (e.g., "Efficacy Results").
4. **Navigation Mapping**: Map each slide to a standard professional tab: [MOD, DESIGN, EFFICACY, SAFETY, DOSING].

# Phase 2: Retrieval Strategy Formulation
1. **Candidate Queries (Vector Search)**: Generate 3-4 "Pseudo-Claims." These are sentences that look like the clinical data you expect to find (e.g., "Median overall survival in the FRESCO trial was X months").
2. **BM25 Keywords (Lexical Search)**: Extract essential high-value entities that MUST be present (e.g., "FRESCO", "mOS", "Grade 3 ARs", "Placebo-controlled").
3. **CRITICAL DISTINCTION**: You must strictly distinguish between 'FRESCO' (China pivotal study) and 'FRESCO-2' (Global multiregional study) in both queries and keywords. Do not conflate them. Use "FRESCO" or "FRESCO-2" explicitly.

# Phase 3: Output Specification (JSON)
Output your analysis first, then a JSON object following this strict schema:

```json
{
  "deck_metadata": {
    "total_slides": number,
    "brand_focus": "string",
    "primary_study": "string"
  },
  "slides": [
    {
      "slide_id": 1,
      "navigation_tab": "DESIGN | EFFICACY | SAFETY | etc",
      "action_headline": "Professional conclusive statement",
      "page_topic": "Detailed description for the Assembler",
      "retrieval_strategy": {
        "candidate_queries": ["Pseudo-claim 1", "Pseudo-claim 2"],
        "BM25_keywords": ["Specific entity 1", "Specific entity 2"]
      }
    }
  ]
}
```
"""

def planner_node(state: AgentState):
    print("\n--- PLANNER AGENT (Content Strategist) ---")
    query = state['query']
    feedback = state.get('feedback', "")
    
    messages = [SystemMessage(content=PLANNER_SYSTEM_PROMPT)]
    if feedback:
        messages.append(HumanMessage(content=f"Previous plan feedback: {feedback}"))
    messages.append(HumanMessage(content=f"User Query: {query}"))
    
    response = llm.invoke(messages)
    
    try:
        content = response.content
        # robustly extract json block
        json_match = re.search(r"```json\s*(\{.*?\})\s*```", content, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Fallback: try to find the first { and last }
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end != -1:
                json_str = content[start:end]
            else:
                raise ValueError("No JSON object found in response")
                
        data = json.loads(json_str)
        
        # 1. Print Analysis & Plan Outline
        print("\n--- PLANNER AGENT OUTPUT ---")
        if json_match:
             # Print everything before the JSON block as analysis
             analysis_text = content[:json_match.start()].strip()
             if analysis_text:
                 print(f"Analysis:\n{analysis_text}\n")
        
        # Handle new schema from prompt
        if "slides" in data:
            raw_slides = data["slides"]
            total_slides_val = data.get("deck_metadata", {}).get("total_slides", len(raw_slides))
        else:
            # Fallback for old schema or malformed
            raw_slides = data.get("deck_plan", [])
            total_slides_val = data.get("total_slides", len(raw_slides))

        print("--- GENERATED SLIDE PLAN ---")
        
        processed_plan = []
        for slide in raw_slides:
            # Flatten retrieval strategy if present
            retrieval = slide.get("retrieval_strategy", {})
            cands = retrieval.get("candidate_queries", slide.get("candidate_queries", []))
            bm25 = retrieval.get("BM25_keywords", slide.get("BM25_keywords", []))
            
            # Map keys to SlideMetadata
            new_slide = {
                "slide_id": slide.get("slide_id"),
                "page_number": slide.get("slide_id"), # Assume 1-to-1
                "page_topic": slide.get("page_topic"),
                "candidate_queries": cands,
                "BM25_keywords": bm25,
                "active_nav_tab": slide.get("navigation_tab", "HOME"), # Map navigation_tab -> active_nav_tab
                "action_headline": slide.get("action_headline", ""),
                "selected_content": None,
                "html_content": ""
            }
            processed_plan.append(new_slide)

            print(f"Slide {new_slide['slide_id']}: {new_slide['page_topic']}")
            print(f"   Candidates: {new_slide['candidate_queries']}")
            print(f"   BM25 Keys:  {new_slide['BM25_keywords']}")
            
        print("----------------------------\n")
            
        return {
            "deck_plan": processed_plan,
            "total_slides": total_slides_val,
            "revision_count": state.get("revision_count", 0) + 1,
            "global_used_claims": [], # Reset claims for fresh generation cycle
            "planner_messages": messages + [response] # Save history
        }
    except Exception as e:
        print(f"Error parsing planner output: {e}")
        return {}
