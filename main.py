import sys
import argparse
from graph import build_graph

def main():
    parser = argparse.ArgumentParser(description="Solstice Slide Builder (Medical Architect)")
    parser.add_argument("query", help="User prompt for the presentation")
    args = parser.parse_args()
    
    print(f"Starting pipeline for query: {args.query}")
    
    app = build_graph()
    
    initial_state = {
        "query": args.query,
        "revision_count": 0,
        "global_used_claims": [],
        "deck_plan": [],
        "retrieved_docs": {},
        "html_output": ""
    }
    
    try:
        final_state = app.invoke(initial_state)
        
        output_html = final_state.get('html_output', "")
        
        if output_html:
            with open("output.html", "w") as f:
                f.write(output_html)
            print("\nSUCCESS! Presentation saved to 'output.html'")
        else:
            print("\nFAILED. No HTML output generated.")
            
        print(f"Final Feedback: {final_state.get('feedback')}")
        
    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
