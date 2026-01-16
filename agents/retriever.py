from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from .state import AgentState
import os
import json
from dotenv import load_dotenv

load_dotenv()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
embeddings = OpenAIEmbeddings(model="text-embedding-3-large") 
llm = ChatOpenAI(model="gpt-5.2", temperature=0)

JUDGE_SYSTEM_PROMPT = """Role: Content Relevance Judge.
Task: Select the most relevant content groups for a presentation slide.

Input:
1. Slide Topic
2. Candidate Groups (ID + Description)

Instructions:
- Analyze the descriptions against the topic.
- Select the top 3 groups that best cover the topic (adjust use your judgement).
- Avoid redundant groups if they cover the exact same thing (prefer the one with more detailed description).
- Return ONLY a JSON list of selected Group IDs.

Output Format:
["group-id-1", "group-id-2"]
"""

def get_group_candidates(queries):
    """Embed queries and search group index."""
    index = pc.Index("content-gen-group-index")
    candidates = {} # map id -> metadata
    
    for q in queries:
        vector = embeddings.embed_query(q)
        results = index.query(vector=vector, top_k=5, include_metadata=True)
        for match in results.matches:
            if match.score > 0.5: # threshold
                candidates[match.metadata['group_id']] = {
                    "group_id": match.metadata['group_id'],
                    "description": match.metadata.get('group_description'),
                    "claim_ids": match.metadata.get('claims', []), # Capture claim IDs
                    "score": match.score
                }
    return list(candidates.values())

def get_claims_by_ids(claim_ids):
    """Fetch specific claims by ID."""
    if not claim_ids:
        return []
        
    index = pc.Index("content-gen-claim-index")
    # Using fetch for direct ID lookup (more efficient & accurate)
    # Note: claim_ids is a list of strings
    # We might need to batch this if there are many, but for a slide it's small.
    # Pinecone fetch: index.fetch(ids=['id1', 'id2'])
    
    try:
        # Some claim lists might be stored as stringified JSON in metadata, check type
        if isinstance(claim_ids, str):
            claim_ids = json.loads(claim_ids)
            
        response = index.fetch(ids=claim_ids)
        # response is {'vectors': {'id1': {...}, 'id2': {...}}}
        # We need the metadata from each
        claims = []
        for cid in claim_ids:
            if cid in response['vectors']:
                claims.append(response['vectors'][cid]['metadata'])
        return claims
    except Exception as e:
        print(f"Error fetching claims by ID: {e}")
        return []

def retriever_node(state: AgentState):
    print("--- RETRIEVER AGENT (Search & Judge) ---")
    plan = state['deck_plan']
    global_used_claims = state.get('global_used_claims', []) or []
    
    updated_plan = []
    retriever_history = []
    
    for slide in plan:
        queries = slide.get('candidate_queries', [])
        topic = slide['page_topic']
        print(f"Processing Slide: {topic}")
        
        # 1. Broad Retrieval
        candidates = get_group_candidates(queries)
        if not candidates:
            print("   -> No candidates found.")
            updated_plan.append(slide)
            continue
            
        print(f"   Found {len(candidates)} candidates. Running Judge...")
        
        # 2. LLM Judge Reranking
        candidate_text = "\n".join([f"ID: {c['group_id']} | Desc: {c['description']}" for c in candidates])
        judge_msg = f"Topic: {topic}\n\nCandidates:\n{candidate_text}"
        
        # Capture current interaction
        current_messages = [
            SystemMessage(content=JUDGE_SYSTEM_PROMPT),
            HumanMessage(content=judge_msg)
        ]
        
        try:
            response = llm.invoke(current_messages)
            retriever_history.extend(current_messages + [response]) # Accumulate history
            
            selected_ids = json.loads(response.content.replace("```json", "").replace("```", "").strip())
        except Exception as e:
            print(f"   -> Judge Error: {e}. Fallback to top score.")
            selected_ids = [candidates[0]['group_id']]

        # 3. Fetch Content & Deduplicate
        final_selection = []
        for gid in selected_ids:
            if gid in global_used_claims:
                continue
            
            # Find the candidate object to get claim_ids
            candidate_obj = next((c for c in candidates if c['group_id'] == gid), None)
            if not candidate_obj:
                continue

            claims = get_claims_by_ids(candidate_obj.get('claim_ids', []))
            if claims:
                final_selection.append({
                    "group_id": gid,
                    "claims": claims
                })
                global_used_claims.append(gid)
        
        print(f"   -> Selected {len(final_selection)} Groups.")
        slide['selected_content'] = final_selection
        updated_plan.append(slide)
        
    return {
        "deck_plan": updated_plan,
        "global_used_claims": global_used_claims,
        "retriever_messages": retriever_history
    }
