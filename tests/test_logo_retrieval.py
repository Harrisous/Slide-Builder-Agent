from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings
import os
from dotenv import load_dotenv
import json

load_dotenv()

def test_logo_retrieval():
    print("Testing Logo Retrieval for 'FRUZAQLA'...")
    
    # Init Pinecone & Embeddings
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    index = pc.Index("content-gen-group-index")
    
    query = "card showing the FRUZAQLA logo or brand identity"
    print(f"Querying: '{query}'")
    
    # Embed
    vector = embeddings.embed_query(query)
    
    # Query Group Index
    results = index.query(vector=vector, top_k=5, include_metadata=True)
    
    print(f"\nFound {len(results.matches)} matches:\n")
    
    claim_index = pc.Index("content-gen-claim-index")
    
    for i, match in enumerate(results.matches):
        print(f"--- Match {i+1} (Score: {match.score:.4f}) ---")
        print(f"Group ID: {match.metadata['group_id']}")
        print(f"Desc: {match.metadata.get('group_description')}")
        
        # Fetch Claims to check for Image URL
        claim_ids = match.metadata.get('claims', [])
        if isinstance(claim_ids, str):
            claim_ids = json.loads(claim_ids)
            
        if claim_ids:
            print(f"  Fetching {len(claim_ids)} claims...")
            claim_resp = claim_index.fetch(ids=claim_ids)
            for cid, data in claim_resp['vectors'].items():
                meta = data['metadata']
                if meta.get('image_url'):
                    print(f"    [IMAGE FOUND in Match {i+1}]: {meta.get('image_url')}")
                    print(f"    [TEXT]: {meta.get('claim_text')[:100]}...")
                # else: pass (reduce noise)
        print("")

if __name__ == "__main__":
    test_logo_retrieval()
