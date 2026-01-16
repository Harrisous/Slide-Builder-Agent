from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from .state import AgentState

llm = ChatOpenAI(model="gpt-5.2", temperature=0)

REVIEWER_SYSTEM_PROMPT = """You are a Quality Assurance reviewer for the Solstice Project.
Review the generated HTML presentation against the User Query and the Plan.

Checklist:
1. Does the presentation address the user's query?
2. Does it follow the Medical Narrative Flow?
3. Is the content complementary of each other and visually cohesive?

If APPROVED, output exactly: "APPROVED"
If REJECTED, provide specific feedback.
"""

def reviewer_node(state: AgentState):
    print("--- REVIEWER AGENT ---")
    query = state['query']
    html = state['html_output']
    plan = state['deck_plan'] # Updated key
    
    msg = f"""
    User Query: {query}
    Plan Count: {len(plan)} slides.
    Generated HTML Length: {len(html)} chars
    
    FULL HTML CONTENT:
    {html}
    """
    
    messages = [
        SystemMessage(content=REVIEWER_SYSTEM_PROMPT),
        HumanMessage(content=msg)
    ]
    
    response = llm.invoke(messages)
    
    review_status = response.content.strip().upper()
    
    if "APPROVED" in review_status:
        return {"feedback": "APPROVED", "reviewer_messages": messages + [response]}
        
    return {"feedback": review_status, "reviewer_messages": messages + [response]}
