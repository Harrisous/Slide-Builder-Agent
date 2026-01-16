from typing import TypedDict, List, Dict, Optional, Annotated
import operator
from langchain_core.messages import BaseMessage

class SlideMetadata(TypedDict):
    slide_id: int # Kept for backward compatibility
    page_number: int
    page_topic: str
    candidate_queries: List[str]
    BM25_keywords: List[str]
    active_nav_tab: str 
    action_headline: str 
    sub_banner: Optional[str] 
    retrieval_query: str 
    selected_claim_ids: List[str] 
    html_content: str
    selected_content: List[Dict] # For Assembler content groups

class AgentState(TypedDict):
    query: str # Main user query
    deck_plan: List[SlideMetadata] # Replaces global_plan
    total_slides: int
    global_used_claims: List[str] # Changed from Append-only to simple list for manual management
    retrieved_docs: Dict[int, List[Dict]]  # Mapping slide_id -> list of group data (Retriever <-> Assembler bridge)
    layout_spec: Dict[str, str] # Keep layout spec
    feedback: str
    revision_count: int
    html_output: str # Final concatenated legacy output
    
    # Isolated Message Histories
    planner_messages: List[BaseMessage]
    retriever_messages: List[BaseMessage]
    assembler_messages: List[BaseMessage]
    reviewer_messages: List[BaseMessage]
